"""
generatecsvwdefinitions
-----------------------

Generate csv-w defintions from the linkml.

N.B. There are no unit tests for this since it is designed to save development time and hence be run by a developer.
"""

import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from textwrap import dedent, indent
from dataclasses import dataclass
from urllib.parse import urljoin
from os import linesep

import click
import pandas as pd
import rdflib
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.utils.metamodelcore import URIorCURIE
from linkml_runtime.utils.schemaview import (
    SchemaView,
    ClassDefinition,
    SlotDefinition,
    TypeDefinition,
    Namespaces,
)
from rdflib import URIRef
from rdflib.namespace import XSD
from tabulate import tabulate

_PARA_METADATA_SLOT_NAMES = {"metadataPublisherId", "metadataDescribedForActionId"}
"""
The set of slot names which identify the slot as contributing to the para-metadata document (which ends up stored separately)
"""
_VIRTUAL_CSV_FILES: Dict[str, str] = {
    "PersonOrOrganization": "person-or-organization.csv"
}
"""
CSV files which don't exist as user inputs, but are instead generated as part of the build process.

We currently assume that they all follow the `unioned-identifiers.schema.json` table schema.
"""
_REMOTE_DIR_NAME: str = "remote"

_UNIONED_IDENTIFIERS_SCHEMA_FILE_NAME = "unioned-identifiers.schema.json"
"""
The schema file for the unioned identifiers table structure.
"""

_SEPARATOR_CHAR: str = "|"
_SCHEMA_ORG_PREFIX = "https://schema.org/"
_MBO_PREFIX = "https://w3id.org/marco-bolo/"


_LINKML_EXTENSION_ABOUT_URL = "csvw_about_url"
"""
A linkml extension key for overriding the `about_url` of a CSV-W column definiton of a slot.
"""
_LINKML_EXTENSION_VIRTUAL_TRIPLES = "csvw_virtual_triples"
"""
A linkml extension key for adding triples to CSV-Ws as virtual columns.
"""

_TWO_LINES: str = os.linesep + os.linesep
_TABLE_FORMAT: str = "pipe"
_NON_TITLE_CHARS = re.compile("\\W+")
_NEW_LINES_REGEX = re.compile("\\n")
_PIPES_REGEX = re.compile("\\|")

_MAP_CSV_NAME_TO_PID_URI: Dict[str, str] = {
    "Action.csv": f"{_MBO_PREFIX}mbo_0000004",
    "Audience.csv": f"{_MBO_PREFIX}mbo_0000005",
    "ContactPoint.csv": f"{_MBO_PREFIX}mbo_0000006",
    "DataDownload.csv": f"{_MBO_PREFIX}mbo_0000007",
    "DatasetComment.csv": f"{_MBO_PREFIX}mbo_0000008",
    "Dataset.csv": f"{_MBO_PREFIX}mbo_0000009",
    "DefinedTerm.csv": f"{_MBO_PREFIX}mbo_0000010",
    "EmbargoStatement.csv": f"{_MBO_PREFIX}mbo_0000011",
    "GeoShape.csv": f"{_MBO_PREFIX}mbo_0000012",
    "HowTo.csv": f"{_MBO_PREFIX}mbo_0000013",
    "HowToStep.csv": f"{_MBO_PREFIX}mbo_0000014",
    "HowToTip.csv": f"{_MBO_PREFIX}mbo_0000015",
    "License.csv": f"{_MBO_PREFIX}mbo_0000016",
    "MonetaryGrant.csv": f"{_MBO_PREFIX}mbo_0000017",
    "Organization.csv": f"{_MBO_PREFIX}mbo_0000018",
    "Person.csv": f"{_MBO_PREFIX}mbo_0000019",
    "Place.csv": f"{_MBO_PREFIX}mbo_0000020",
    "PropertyValue.csv": f"{_MBO_PREFIX}mbo_0000021",
    "PublishingStatusDefinedTerm.csv": f"{_MBO_PREFIX}mbo_0000022",
    "Service.csv": f"{_MBO_PREFIX}mbo_0000023",
    "SoftwareApplication.csv": f"{_MBO_PREFIX}mbo_0000024",
    "SoftwareSourceCode.csv": f"{_MBO_PREFIX}mbo_0000025",
    "Taxon.csv": f"{_MBO_PREFIX}mbo_0000026"
}
"""
Mapping each of the model names to their CSV file's PID URI.

If you add a new class/model you need to create the above mapping. The PID needs to be generated and correctly redirected
in the w3id configuration.
"""


@dataclass
class ManualForeignKeyCheckConfig:
    child_table_path: Path
    child_table_column: str
    parent_table_path: Path
    parent_table_column: str
    separator: Optional[str]


@click.command()
@click.argument("CLASSES_YAML", type=click.Path(exists=True))
@click.option("-o", "--output-dir", type=click.Path(), default=".")
def main(classes_yaml: click.Path, output_dir: click.Path):
    """
    Generates CSV-W files from the given all_classes.yaml configuration.

    If you're unsure whether you should be using this, you probably shouldn't.
    """
    classes_yaml_path = Path(str(classes_yaml))
    out_dir = Path(str(output_dir))
    out_dir.mkdir(exist_ok=True)

    schema_view = SchemaView(classes_yaml_path, merge_imports=True)
    all_classes = schema_view.all_classes()
    all_slots = schema_view.all_slots()
    all_literal_types = schema_view.all_types()

    remote_dir = out_dir / _REMOTE_DIR_NAME
    remote_dir.mkdir(exist_ok=True)

    class_csv_map: Dict[str, Path] = {}
    class_schema_map: Dict[str, Path] = {}
    map_class_name_to_csv_dependencies: Dict[str, Set[Path]] = {}
    class_manual_foreign_key_checks: Dict[str, List[ManualForeignKeyCheckConfig]] = {}
    for _, clazz in all_classes.items():
        slots_for_class = _get_slots_for_class(clazz, all_classes, all_slots)
        if any(slots_for_class) and not clazz.abstract:
            _generate_csv_and_schema_for_class(
                clazz,
                slots_for_class,
                schema_view,
                all_slots,
                all_classes,
                all_literal_types,
                out_dir,
                class_csv_map,
                class_schema_map,
                class_manual_foreign_key_checks,
                map_class_name_to_csv_dependencies,
            )

    _generate_unioned_identifiers_schema(out_dir)

    _perform_transitive_dependency_closure(
        map_class_name_to_csv_dependencies, class_csv_map
    )

    _generate_csv_metadata_documents(
        class_csv_map, class_schema_map, out_dir, map_class_name_to_csv_dependencies
    )

    with open(out_dir / "remote" / "foreign-keys.mk", "w+") as f:
        f.writelines(
            _generate_makefile_manual_foreign_key_checks(
                class_manual_foreign_key_checks, out_dir
            )
        )

    with open(out_dir / "class-descriptions.md", "w+") as f:
        f.writelines(
            _generate_user_documentation_markdown(
                all_classes,
                all_literal_types,
                all_slots,
                schema_view.namespaces(),
                schema_view.schema,
            )
        )


def _expand_curie(uri_or_curie: URIorCURIE, namespaces: Namespaces) -> str:
    """
    Causes an exception rather than quietly failing where it can't look the prefix up in `namespaces`.
    """
    if URIorCURIE.is_curie(uri_or_curie):
        return str(namespaces.uri_for(uri_or_curie))

    return str(uri_or_curie)


def _perform_transitive_dependency_closure(
    map_class_name_to_csv_dependencies: Dict[str, Set[Path]], map_class_name_to_csv_path
) -> None:
    """
    This is NOT efficient.
    """
    map_csv_path_to_class_name: Dict[Path, str] = {
        csv_path: class_name
        for class_name, csv_path in map_class_name_to_csv_path.items()
    }

    changed_in_last_cycle: bool = True
    cycle_counter: int = 0
    while changed_in_last_cycle:
        changed_in_last_cycle = False
        cycle_counter += 1
        if cycle_counter > 1000:
            raise Exception(
                f"Reached cycle {cycle_counter} in transitive dependency closure. This means we probably won't ever complete the closure. Giving up."
            )

        for class_name, dependency_paths in list(
            map_class_name_to_csv_dependencies.items()
        ):
            unmet_transitive_dependencies = _get_unmet_transitive_dependencies(
                dependency_paths,
                map_class_name_to_csv_dependencies,
                map_csv_path_to_class_name,
            )
            if any(unmet_transitive_dependencies):
                changed_in_last_cycle = True
                map_class_name_to_csv_dependencies[class_name] = (
                    dependency_paths | unmet_transitive_dependencies
                )


def _get_unmet_transitive_dependencies(
    existing_csv_dependencies: Set[Path],
    map_class_name_to_csv_dependencies: Dict[str, Set[Path]],
    map_csv_path_to_class_name: Dict[Path, str],
) -> Set[Path]:
    dependent_on_classes = {
        map_csv_path_to_class_name[csv_path]
        for csv_path in existing_csv_dependencies
        if csv_path in map_csv_path_to_class_name
    }

    transitive_csv_dependency_paths: Set[Path] = set()
    for dependent_class_name in dependent_on_classes:
        transitive_csv_dependency_paths |= map_class_name_to_csv_dependencies[
            dependent_class_name
        ]

    return existing_csv_dependencies ^ transitive_csv_dependency_paths


def _generate_unioned_identifiers_schema(out_dir: Path):
    with open(
        out_dir / _REMOTE_DIR_NAME / _UNIONED_IDENTIFIERS_SCHEMA_FILE_NAME, "w+"
    ) as f:
        unioned_identifiers_schema = {
            "@context": "http://www.w3.org/ns/csvw",
            "columns": [
                {
                    "name": "id",
                    "required": True,
                    "titles": {"en": ["MBO Permanent Identifier*"]},
                    "suppressOutput": True,
                }
            ],
            "aboutUrl": "https://w3id.org/marco-bolo/{+id}",
            "primaryKey": ["id"],
        }
        f.writelines(json.dumps(unioned_identifiers_schema, indent=4))


def _generate_makefile_manual_foreign_key_checks(
    class_manual_foreign_key_checks: Dict[str, List[ManualForeignKeyCheckConfig]],
    out_dir: Path,
) -> str:
    makefile_config = dedent(
        f"""
        MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT	:= {" ".join(sorted([_get_csv_name_for_class(class_name) for class_name in class_manual_foreign_key_checks]))}
        MANUAL_FOREIGN_KEY_VALIDATION_LOGS			:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.success.log)
        MANUAL_FOREIGN_KEY_VALIDATION_LOGS_ERRORS	:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.err.log)

    """
    )

    for (
        class_name,
        manual_foreign_key_checks,
    ) in sorted(class_manual_foreign_key_checks.items()):
        csv_file_name = _get_csv_name_for_class(class_name)
        success_log_file_name = (
            csv_file_name.removesuffix(".csv") + "-csv-list-column-foreign-key.success.log"
        )
        error_log_file_name = (
            csv_file_name.removesuffix(".csv") + "-csv-list-column-foreign-key.err.log"
        )

        success_log_file_path = f"out/validation/{success_log_file_name}"
        error_log_file_path = f"out/validation/{error_log_file_name}"

        dependent_files = {
            str(manual_fk_check.parent_table_path.relative_to(out_dir))
            for manual_fk_check in manual_foreign_key_checks
        }

        makefile_config += f"{success_log_file_path}: {" ".join(dependent_files)} out/validation\n"
        makefile_config += indent(f'@rm -f "{error_log_file_path}" "{success_log_file_path}"', "	")
        makefile_config += indent(
            "\n".join(
                [
                    _get_makefile_config_for_foreign_key_check(manual_fk_check, out_dir, error_log_file_path)
                    for manual_fk_check in manual_foreign_key_checks
                ]
            ),
            "	",
        )
        makefile_config += indent(
            dedent(
                f"""
                @if [ -f "{error_log_file_path}" ]; then \\
                   echo ""; \\
                   printf '\033[0;31m'; # Red \\
                   echo "Foreign Key errors detected:"; \\
                   cat "{error_log_file_path}"; \\
                   printf '\033[0m'; # Reset colour \\
                 else \\
                   touch "{success_log_file_path}"; \\
                 fi
                @echo ""
            """
            ),
            "	",
        )

    return makefile_config


def _get_makefile_config_for_foreign_key_check(
    manual_foreign_key_check: ManualForeignKeyCheckConfig, out_dir: Path, err_log_file_path: str
) -> str:
    child_table_path = manual_foreign_key_check.child_table_path.relative_to(out_dir)
    parent_table_path = manual_foreign_key_check.parent_table_path.relative_to(out_dir)

    foreign_key_check_command = (
        f'$(LIST_COLUMN_FOREIGN_KEY_CHECK) "{child_table_path}" "{manual_foreign_key_check.child_table_column}" '
        f'"{parent_table_path}" "{manual_foreign_key_check.parent_table_column}"'
    )

    if manual_foreign_key_check.separator is not None:
        foreign_key_check_command += (
            f' --separator "{manual_foreign_key_check.separator}"'
        )

    foreign_key_check_command = f'@RES=$$({foreign_key_check_command}) && echo "$$RES" || echo "$$RES" >> "{err_log_file_path}"'

    return dedent(
        f"""
            @echo "=============================== Validating values in {child_table_path}['{manual_foreign_key_check.child_table_column}'] ==============================="
            {foreign_key_check_command}
        """
    )


def _generate_csv_metadata_documents(
    class_csv_map: Dict[str, Path],
    class_schema_map: Dict[str, Path],
    out_dir: Path,
    map_class_name_to_csv_dependencies: Dict[str, Set[Path]],
) -> None:
    def _get_relative_path_from_remote_dir(p: Path) -> str:
        return str(p.relative_to(out_dir / _REMOTE_DIR_NAME, walk_up=True))

    for parent_class_name, parent_csv_file_path in class_csv_map.items():
        csv_dependencies_for_class: Set[Path] = map_class_name_to_csv_dependencies[
            parent_class_name
        ]

        metadata_document: Dict[str, Any] = {
            "@context": "http://www.w3.org/ns/csvw",
            "tables": [],
        }

        for dependency_class_name, dependency_csv_file_path in class_csv_map.items():
            if dependency_csv_file_path in csv_dependencies_for_class:
                dependency_schema_file_path = class_schema_map[dependency_class_name]

                metadata_document["tables"].append(
                    {
                        "url": _get_relative_path_from_remote_dir(
                            dependency_csv_file_path
                        ),
                        "tableSchema": _get_relative_path_from_remote_dir(
                            dependency_schema_file_path
                        ),
                        "suppressOutput": dependency_csv_file_path
                        != parent_csv_file_path,
                    }
                )

        for dependency_class_name, csv_file_name in _VIRTUAL_CSV_FILES.items():
            dependency_csv_file_path = _get_virtual_file_path(
                out_dir, dependency_class_name
            )
            if dependency_csv_file_path in csv_dependencies_for_class:
                dependency_schema_file_path = (
                    out_dir / _REMOTE_DIR_NAME / _UNIONED_IDENTIFIERS_SCHEMA_FILE_NAME
                )

                metadata_document["tables"].append(
                    {
                        "url": _get_relative_path_from_remote_dir(
                            dependency_csv_file_path
                        ),
                        "tableSchema": _get_relative_path_from_remote_dir(
                            dependency_schema_file_path
                        ),
                        "suppressOutput": True,
                    }
                )

        with open(
            out_dir
            / _REMOTE_DIR_NAME
            / _get_metadata_file_name_for_class(parent_class_name),
            "w+",
        ) as f:
            f.writelines(json.dumps(metadata_document, indent=4))


def _generate_csv_and_schema_for_class(
    clazz: ClassDefinition,
    slots_for_class: List[SlotDefinition],
    schema_view: SchemaView,
    all_slots: Dict[str, SlotDefinition],
    all_classes: Dict[str, ClassDefinition],
    all_literal_types: Dict[str, TypeDefinition],
    output_dir: Path,
    class_csv_map: Dict[str, Path],
    class_schema_map: Dict[str, Path],
    class_manual_foreign_key_checks: Dict[str, List[ManualForeignKeyCheckConfig]],
    map_class_name_to_csv_dependencies: Dict[str, Set[Path]],
) -> None:
    # Create Basic CSV
    namespaces = schema_view.namespaces()

    csv_starter = pd.DataFrame(
        {_get_csv_col_title_for_slot(slot): [] for slot in slots_for_class}
    )
    csv_name_for_class = _get_csv_name_for_class(clazz.name)
    csv_file_path = output_dir / csv_name_for_class
    class_csv_map[clazz.name] = csv_file_path
    csv_starter.to_csv(csv_file_path, index=False, quoting=csv.QUOTE_STRINGS)

    foreign_key_definitions: List[Dict[str, Any]] = []
    primary_key_definition: List[str] = []
    identifier_slot = _get_primary_key_identifier_slot_definition(
        clazz, slots_for_class
    )

    manual_build_foreign_key_checks: List[ManualForeignKeyCheckConfig] = []

    csv_dependencies_for_class = {csv_file_path}

    column_definitions = [
        _get_column_definition_for_slot(
            clazz,
            identifier_slot,
            slot,
            all_classes,
            all_slots,
            all_literal_types,
            primary_key_definition,
            foreign_key_definitions,
            namespaces,
            manual_build_foreign_key_checks,
            output_dir,
            csv_dependencies_for_class,
        )
        for slot in slots_for_class
    ]

    map_class_name_to_csv_dependencies[clazz.name] = csv_dependencies_for_class

    if any(manual_build_foreign_key_checks):
        class_manual_foreign_key_checks[clazz.name] = manual_build_foreign_key_checks

    identifier_template_uri_for_row = f"{_MBO_PREFIX}{{+{identifier_slot.name}}}"
    input_metadata_uri = f"{identifier_template_uri_for_row}#input-metadata"

    if not any([s for s in slots_for_class if s.designates_type is True]):
        column_definitions.append(
            {
                "virtual": True,
                "propertyUrl": "rdf:type",
                "valueUrl": _expand_curie(clazz.class_uri, namespaces),
            }
        )


    column_definitions += [
        {
            "virtual": True,
            "aboutUrl": input_metadata_uri,
            "propertyUrl": "rdf:type",
            "valueUrl": f"{_SCHEMA_ORG_PREFIX}DataDownload",
        },
        {
            "virtual": True,
            "aboutUrl": input_metadata_uri,
            "propertyUrl": "rdf:type",
            "valueUrl": f"{_MBO_PREFIX}InputMetadataDescription",
        },
        {
            "virtual": True,
            "aboutUrl": input_metadata_uri,
            "propertyUrl": f"{_SCHEMA_ORG_PREFIX}about",
            "valueUrl": identifier_template_uri_for_row,
        }
    ]

    if csv_name_for_class in _MAP_CSV_NAME_TO_PID_URI:
        column_definitions.append({
            "virtual": True,
            "aboutUrl": input_metadata_uri,
            "propertyUrl": f"{_SCHEMA_ORG_PREFIX}contentUrl",
            "valueUrl": f"{_MAP_CSV_NAME_TO_PID_URI[csv_name_for_class]}#row={{_row}}",
        })
    else:
        raise Exception(f"Could not find PID for CSV model '{csv_name_for_class}' - is this a new model/class?")

    if _LINKML_EXTENSION_VIRTUAL_TRIPLES in clazz.extensions:
        column_definitions += _add_user_defined_virtual_columns_for_triples(
            clazz, identifier_template_uri_for_row, namespaces
        )

    basic_schema = {
        "@context": "http://www.w3.org/ns/csvw",
        "columns": column_definitions,
        "aboutUrl": f"{_MBO_PREFIX}{{+{identifier_slot.name}}}",
        "primaryKey": primary_key_definition,
        "foreignKeys": list(foreign_key_definitions),
    }

    schema_file_path = (
        output_dir / _REMOTE_DIR_NAME / _get_schema_file_name_for_class(clazz.name)
    )
    with open(schema_file_path, "w+") as f:
        class_schema_map[clazz.name] = schema_file_path
        f.writelines(json.dumps(basic_schema, indent=4))


def _add_user_defined_virtual_columns_for_triples(
    clazz: ClassDefinition, identifier_template_uri_for_row: str, namespaces: Namespaces
) -> List[Dict[str, str]]:
    additional_virtual_columns = []
    this_row_temp_identifier_uri = f"{_MBO_PREFIX}IdentifierForThisRow"
    virtual_triples_txt = clazz.extensions[_LINKML_EXTENSION_VIRTUAL_TRIPLES].value
    """
    For example:
        <> schema:amount <#MonetaryAmount>.
        <#MonetaryAmount> a schema:MonetaryAmount.
    """

    virtual_triples_graph = rdflib.Graph()
    prefixes = [f"@prefix {key}: <{value}>." for key, value in namespaces.items()]
    prefixes.append(f"@base <{this_row_temp_identifier_uri}>.")
    ttl_data = linesep.join(prefixes) + linesep + virtual_triples_txt
    virtual_triples_graph.parse(data=ttl_data, format="ttl")
    for s, p, o in sorted(virtual_triples_graph):
        if not isinstance(o, URIRef):
            raise Exception(
                f"Object '{o}' must be a URI reference to a node in the graph. Arbitrary expression of literals is not supported by the CSV-W spec."
            )

        additional_virtual_column = {
            "virtual": True,
            "propertyUrl": str(p).replace(
                this_row_temp_identifier_uri, identifier_template_uri_for_row
            ),
            "valueUrl": str(o).replace(
                this_row_temp_identifier_uri, identifier_template_uri_for_row
            ),
        }

        subject_str = str(s)
        if subject_str != this_row_temp_identifier_uri:
            additional_virtual_column["aboutUrl"] = subject_str.replace(
                this_row_temp_identifier_uri, identifier_template_uri_for_row
            )
        additional_virtual_columns.append(additional_virtual_column)

    return additional_virtual_columns


def _get_slots_for_class(
    clazz: ClassDefinition,
    all_classes: Dict[str, ClassDefinition],
    all_slots: Dict[str, SlotDefinition],
) -> List[SlotDefinition]:
    inherited_slots = []
    if clazz.is_a:
        parent_class = all_classes[str(clazz.is_a)]
        inherited_slots = _get_slots_for_class(parent_class, all_classes, all_slots)

    return inherited_slots + [all_slots[slot_name] for slot_name in clazz.slots]


def _get_csv_name_for_class(class_name: str) -> str:
    return f"{class_name}.csv"


def _get_schema_file_name_for_class(class_name: str) -> str:
    return f"{class_name}.schema.json"


def _get_metadata_file_name_for_class(class_name: str) -> str:
    return f"{class_name}.csv-metadata.json"


def _get_csv_col_title_for_slot(slot: SlotDefinition) -> str:
    col_title = slot.title or slot.name
    if slot.required is True:
        col_title += "*"

    return col_title


def _get_column_definition_for_slot(
    clazz: ClassDefinition,
    identifier_slot: SlotDefinition,
    slot: SlotDefinition,
    all_classes: Dict[str, ClassDefinition],
    all_slots: Dict[str, SlotDefinition],
    all_literal_types: Dict[str, TypeDefinition],
    primary_key_definition: List[str],
    foreign_key_definitions: List[Dict[str, Any]],
    namespaces: Namespaces,
    manual_build_foreign_key_checks: List[ManualForeignKeyCheckConfig],
    output_dir: Path,
    csv_dependencies_for_class: Set[Path],
) -> Dict[str, Any]:
    slot_column_title = _get_csv_col_title_for_slot(slot)

    column_definition: Dict[str, Any] = {
        "name": slot.name,
        "titles": {"en": [slot_column_title]},
    }

    if slot.identifier is True:
        primary_key_definition.append(slot.name)

    if slot.required is True:
        column_definition["required"] = True

    if slot.slot_uri is None:
        column_definition["suppressOutput"] = True
    else:
        column_definition["propertyUrl"] = _expand_curie(slot.slot_uri, namespaces)

    if slot.name in _PARA_METADATA_SLOT_NAMES:
        column_definition["aboutUrl"] = (
            f"{_MBO_PREFIX}{{+{identifier_slot.name}}}#input-metadata"
        )

    if _LINKML_EXTENSION_ABOUT_URL in slot.extensions:
        column_definition["aboutUrl"] = urljoin(
            f"{_MBO_PREFIX}{{+{identifier_slot.name}}}",
            slot.extensions[_LINKML_EXTENSION_ABOUT_URL].value,
        )

    if slot.range in all_classes:
        _define_related_class_column(
            all_classes,
            all_slots,
            clazz,
            column_definition,
            foreign_key_definitions,
            slot,
            slot_column_title,
            manual_build_foreign_key_checks,
            output_dir,
            csv_dependencies_for_class,
        )
    elif slot.range == "uri" and slot.slot_uri is not None and not slot.multivalued:
        # Represent URIs as node values in the graph rather than as literal/primitive data types like strings.
        # Multivalued things still need to go via the <https://w3id.org/marco-bolo/ConvertIriToNode> conversion
        # route so should not have this specified.
        if slot.implicit_prefix:
            if not slot.implicit_prefix in namespaces:
                raise Exception(
                    f"Unable to find prefix definition for implicit_prefix '{slot.implicit_prefix}'."
                )
            prefix = namespaces.get(slot.implicit_prefix)
            column_definition["valueUrl"] = f"{prefix}{{+{slot.name}}}"
        else:
            column_definition["valueUrl"] = f"{{+{slot.name}}}"

        if slot.pattern is not None:
            column_definition["datatype"] = {"base": "string", "format": slot.pattern}

    else:
        # Primitive data type
        data_type: Dict[str, Any] = _map_linkml_data_type_to_csvw(
            slot, all_literal_types, namespaces
        )
        if slot.pattern:
            data_type["format"] = slot.pattern

        if slot.minimum_value:
            data_type["minimum"] = slot.minimum_value

        if slot.maximum_value:
            data_type["maximum"] = slot.maximum_value

        if slot.multivalued:
            column_definition["separator"] = _SEPARATOR_CHAR
            if slot.range == "uri":
                data_type = {"@id": f"{_MBO_PREFIX}ConvertIriToNode", "base": "string"}

        if slot.implicit_prefix:
            if slot.multivalued:
                raise Exception(
                    f"Unable to currently support implicit_prefix on multivalued slot."
                )
            else:
                raise Exception(
                    f"Unexpected/unhandled implicit_prefix value '{slot.implicit_prefix}'."
                )

        column_definition["datatype"] = data_type

    return column_definition


def _map_linkml_built_in_data_type_to_csvw(linkml_built_in_data_type: str) -> str:

    raise Exception(
        f"Unmatched linkml base literal datatype '{linkml_built_in_data_type}'"
    )


def _map_linkml_data_type_to_csvw(
    slot: SlotDefinition,
    all_literal_types: Dict[str, TypeDefinition],
    namespaces: Namespaces,
) -> Dict[str, str]:
    if slot.range in all_literal_types:
        literal_type = all_literal_types[slot.range]
        literal_type_base = (literal_type.base or "str").lower()
        data_type_def = {}

        if literal_type.uri is not None:
            data_type_uri = _expand_curie(literal_type.uri, namespaces)
            if not data_type_uri.startswith(str(XSD)):
                # Can't stick built-in-types here.
                data_type_def["@id"] = data_type_uri

        if literal_type_base == "str":
            data_type_def["base"] = "string"
        elif literal_type_base == "uri":
            data_type_def["base"] = "string"
        elif literal_type_base == "xsddate":
            data_type_def["base"] = "date"
            # Overrides anything already defined
            data_type_def["@id"] = f"{_SCHEMA_ORG_PREFIX}Date"
        elif literal_type_base == "xsddatetime":
            data_type_def["base"] = "datetime"
            # Overrides anything already defined
            data_type_def["@id"] = f"{_SCHEMA_ORG_PREFIX}DateTime"
        elif literal_type_base == "int":
            data_type_def["base"] = "int"
        elif literal_type_base == "decimal":
            data_type_def["base"] = "decimal"
        else:
            raise Exception(f"Unhandled literal data type '{slot.range}'")

        return data_type_def

    raise Exception(f"Unhandled literal datatype '{slot.range}'")


def _define_related_class_column(
    all_classes: Dict[str, ClassDefinition],
    all_slots: Dict[str, SlotDefinition],
    clazz: ClassDefinition,
    column_definition: Dict[str, Any],
    foreign_key_definitions: List[Dict[str, Any]],
    slot: SlotDefinition,
    slot_column_title: str,
    manual_build_foreign_key_checks: List[ManualForeignKeyCheckConfig],
    out_dir: Path,
    csv_dependencies_for_class: Set[Path],
) -> None:
    range_class = all_classes[slot.range]
    class_csv_name = _get_csv_name_for_class(clazz.name)
    class_csv_path = out_dir / class_csv_name

    remote_dir_path = out_dir / _REMOTE_DIR_NAME
    range_csv_location = (
        _get_virtual_file_path(out_dir, range_class.name)
        if range_class.name in _VIRTUAL_CSV_FILES
        else out_dir / _get_csv_name_for_class(range_class.name)
    )
    csv_dependencies_for_class.add(range_csv_location)
    range_class_pk_slot = _get_primary_key_identifier_slot_definition(
        range_class, _get_slots_for_class(range_class, all_classes, all_slots)
    )

    if slot.multivalued:
        column_definition["separator"] = _SEPARATOR_CHAR
        column_definition["datatype"] = {
            "@id": f"{_MBO_PREFIX}ConvertMboIdToNode",
            "base": "string",
        }

        manual_build_foreign_key_checks.append(
            _generate_manual_foreign_key_checks(
                class_csv_path,
                slot_column_title,
                range_csv_location,
                range_class_pk_slot,
                separator=_SEPARATOR_CHAR,
            )
        )
    else:
        column_definition["valueUrl"] = f"{_MBO_PREFIX}{{+{slot.name}}}"

        if slot.required:
            foreign_key_definitions.append(
                {
                    "columnReference": slot.name,
                    "reference": {
                        "resource": str(
                            range_csv_location.relative_to(
                                remote_dir_path, walk_up=True
                            )
                        ),
                        "columnReference": range_class_pk_slot.name,
                    },
                }
            )
        else:
            manual_build_foreign_key_checks.append(
                _generate_manual_foreign_key_checks(
                    class_csv_path,
                    slot_column_title,
                    range_csv_location,
                    range_class_pk_slot,
                )
            )


def _generate_manual_foreign_key_checks(
    class_csv_path: Path,
    slot_column_title: str,
    range_csv_path: Path,
    range_class_pk_slot: SlotDefinition,
    separator: Optional[str] = None,
) -> ManualForeignKeyCheckConfig:
    return ManualForeignKeyCheckConfig(
        child_table_path=class_csv_path,
        child_table_column=slot_column_title,
        parent_table_path=range_csv_path,
        parent_table_column=_get_csv_col_title_for_slot(range_class_pk_slot),
        separator=separator,
    )


def _get_virtual_file_path(output_dir: Path, virtual_class_name: str) -> Path:
    return output_dir / "out" / "validation" / _VIRTUAL_CSV_FILES[virtual_class_name]


def _get_primary_key_identifier_slot_definition(
    clazz: ClassDefinition, slots_for_class: List[SlotDefinition]
):
    identifier_slots = [s for s in slots_for_class if s.identifier is True]
    if len(identifier_slots) != 1:
        raise Exception(
            f"Expected to find 1 identifier slots in {clazz.name} but found {len(identifier_slots)}"
        )
    return identifier_slots[0]


def _generate_user_documentation_markdown(
    all_classes: Dict[str, ClassDefinition],
    all_literals: Dict[str, TypeDefinition],
    all_slots: Dict[str, SlotDefinition],
    namespaces: Namespaces,
    schema: SchemaDefinition,
) -> str:
    ordered_classes = sorted(all_classes.values(), key=lambda c: c.name)
    markdown = "# MARCO-BOLO CSV Models" + _TWO_LINES
    markdown += (
        "This has been automatically generated by a python script. You should not attempt to edit it manually."
        + _TWO_LINES
    )

    if schema.description:
        markdown += schema.description + _TWO_LINES

    table_of_contents = [
        {"Contents": f"[{clazz.name}](#{_get_anchor_tag_identifier(clazz.name)})"}
        for clazz in ordered_classes
    ]
    table_of_contents.append({"Contents": "[Prefixes](#prefixes)"})
    markdown += (
        tabulate(table_of_contents, tablefmt=_TABLE_FORMAT, headers="keys") + _TWO_LINES
    )
    markdown += _TWO_LINES.join(
        [
            _get_markdown_docs_for_class(
                clazz, all_classes, all_slots, all_literals, namespaces
            )
            for clazz in ordered_classes
        ]
    ) + _TWO_LINES

    markdown += _generate_prefixes_section_markdown(namespaces) + _TWO_LINES
    return markdown


def _escape_description_strings_table_cell(description: str) -> str:

    return _NEW_LINES_REGEX.sub(
    "<br/>",
        _PIPES_REGEX.sub("\\|", description)
    )


def _generate_prefixes_section_markdown(namespaces: Namespaces) -> str:
    prefixes_markdown = "## Prefixes" + _TWO_LINES
    prefixes_markdown += tabulate(
        [
            {"Prefix": prefix, "Base URI": str(namespace)}
            for (prefix, namespace) in namespaces.items()
        ],
        tablefmt=_TABLE_FORMAT,
        headers="keys",
    )
    return prefixes_markdown


def _get_range_str_for_slot(
    slot: SlotDefinition,
    all_classes: Dict[str, ClassDefinition],
    all_literals: Dict[str, TypeDefinition],
    namespaces: Namespaces,
) -> str:
    if slot.range in all_classes:
        range_clazz = all_classes[slot.range]
        class_anchor_tag_id = _get_anchor_tag_identifier(range_clazz.name)

        return f"[{range_clazz.name}](#{class_anchor_tag_id}) identifer"

    if slot.range == "date":
        return "Date (YYYY-mm-DD)"

    if slot.range == "datetime":
        return "Date Time (YYYY-mm-DDTHH:mm:SSZ)"

    if slot.range == "string":
        if slot.pattern:
            return "Text matching the pattern"

        return "Free Text"

    if slot.range == "uri":
        if slot.implicit_prefix:
            base_uri = namespaces.get(slot.implicit_prefix)
            return f"[{slot.implicit_prefix}]({base_uri}) identifier slug."
        else:
            return "URL Persistent Identifier"

    if slot.range in all_literals:
        range_literal = all_literals[slot.range]
        return f"{range_literal.title or range_literal.name}"

    return slot.range


def _get_anchor_tag_identifier(title: str) -> str:
    return _NON_TITLE_CHARS.sub("", title.lower())


def _get_markdown_docs_for_class(
    clazz: ClassDefinition,
    all_classes: Dict[str, ClassDefinition],
    all_slots: Dict[str, SlotDefinition],
    all_literals: Dict[str, TypeDefinition],
    namespaces: Namespaces,
) -> str:
    class_markdown = f"## {clazz.name}{_TWO_LINES}"

    csv_file_name = _get_csv_name_for_class(clazz.name)

    if clazz.abstract:
        class_markdown += (
            "This CSV is auto-generated. You cannot edit this yourself." + _TWO_LINES
        )
    else:
        class_markdown += (
                f"File location: [{csv_file_name}](./{csv_file_name})" + _TWO_LINES
        )

    if clazz.description:
        class_markdown += clazz.description + _TWO_LINES

    class_markdown += tabulate(
        [
            [
                _get_csv_col_title_for_slot(slot),
                "Yes" if slot.required else "No",
                _get_range_str_for_slot(slot, all_classes, all_literals, namespaces),
                "Yes" if slot.multivalued else "No",
                _get_slot_description(slot),
            ]
            for slot in _get_slots_for_class(clazz, all_classes, all_slots)
        ],
        tablefmt=_TABLE_FORMAT,
        headers=["Column Title", "Required", "Contains", "Multivalued", "Description"],
    )

    return class_markdown


def _get_slot_description(slot: SlotDefinition) -> str:
    description = slot.description or ""
    if slot.multivalued:
        if any(description):
            description += os.linesep

        description += "Use the pipe symbol `|` to separate multiple values."

    return _escape_description_strings_table_cell(description)


if __name__ == "__main__":
    main()
