"""
generatecsvwdefinitions
-----------------------

Generate csv-w defintions from the linkml.

N.B. There are no unit tests for this since it is designed to save development time and hence be run by a developer.
"""
import csv
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from textwrap import dedent, indent
from dataclasses import dataclass

import click
import pandas as pd
from linkml_runtime.utils.schemaview import (
    SchemaView,
    ClassDefinition,
    SlotDefinition,
    TypeDefinition,
    Namespaces,
)
from rdflib.namespace import XSD

_PARA_METADATA_SLOT_NAMES = {"metadataPublisherId", "metadataDescribedForActionId"}
"""
The set of slot names which identify the slot as contributing to the para-metadata document (which ends up stored separately)

TODO: This list isn't currently complete, there will be other columns
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

    if any(class_manual_foreign_key_checks):
        print(
            _generate_makefile_manual_foreign_key_checks(
                class_manual_foreign_key_checks, out_dir
            )
        )


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
        The following needs to be placed inside the top-level Makefile:

        # Keep MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT up to date with the files it's necessary to perform list-column
        # foreign key validation on.
        MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT	:= {" ".join(sorted([_get_csv_name_for_class(class_name) for class_name in class_manual_foreign_key_checks]))}
        MANUAL_FOREIGN_KEY_VALIDATION_LOGS			:= $(MANUAL_FOREIGN_KEY_VALIDATION_LOGS_SHORT:%.csv=out/validation/%-csv-list-column-foreign-key.log)

    """
    )

    for (
        class_name,
        manual_foreign_key_checks,
    ) in sorted(class_manual_foreign_key_checks.items()):
        csv_file_name = _get_csv_name_for_class(class_name)
        log_file_name = (
            csv_file_name.removesuffix(".csv") + "-csv-list-column-foreign-key.log"
        )

        dependent_files = {
            str(manual_fk_check.parent_table_path.relative_to(out_dir))
            for manual_fk_check in manual_foreign_key_checks
        }

        makefile_config += f"out/validation/{log_file_name}: {" ".join(dependent_files)} out/validation"
        makefile_config += indent(
            "\n".join([_get_makefile_config_for_foreign_key_check(manual_fk_check, out_dir) for manual_fk_check in manual_foreign_key_checks]),
            "	"
        )
        makefile_config += indent(
            dedent(f"""
                @echo "" > out/validation/{log_file_name} # Let the build know we've done this validation now.
                @echo ""
            """),
            "	"
        )

    return makefile_config


def _get_makefile_config_for_foreign_key_check(
    manual_foreign_key_check: ManualForeignKeyCheckConfig, out_dir: Path
) -> str:
    child_table_path = manual_foreign_key_check.child_table_path.relative_to(out_dir)
    parent_table_path = manual_foreign_key_check.parent_table_path.relative_to(out_dir)

    foreign_key_check_command = f'@$(LIST_COLUMN_FOREIGN_KEY_CHECK) "{child_table_path}" "{manual_foreign_key_check.child_table_column}" "{parent_table_path}" "{manual_foreign_key_check.parent_table_column}"'

    if manual_foreign_key_check.separator is not None:
        foreign_key_check_command += (
            f' --separator "{manual_foreign_key_check.separator}"'
        )

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

    input_metadata_uri = f"{_MBO_PREFIX}{{+{identifier_slot.name}}}#input-metadata"

    if not any ([s for s in slots_for_class if s.designates_type is True]):
        column_definitions.append({
            "virtual": True,
            "propertyUrl": "rdf:type",
            "valueUrl": clazz.class_uri.as_uri(namespaces),
        })

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
            "valueUrl": f"{_MBO_PREFIX}{{+{identifier_slot.name}}}",
        },
        {
            "virtual": True,
            "aboutUrl": input_metadata_uri,
            "propertyUrl": f"{_SCHEMA_ORG_PREFIX}contentUrl",
            # todo: Properly sort these URIs out.
            "valueUrl": f"{_MBO_PREFIX}mbo_TODO_{csv_name_for_class}#row={{_row}}",
        },
    ]

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

    if slot.slot_uri is not None:
        column_definition["propertyUrl"] = slot.slot_uri.as_uri(namespaces)

    if slot.name in _PARA_METADATA_SLOT_NAMES:
        column_definition["aboutUrl"] = (
            f"{_MBO_PREFIX}{{+{identifier_slot.name}}}#input-metadata"
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
    else:
        # Primitive data type
        data_type: Dict[str, Any] = _map_linkml_data_type_to_csvw(slot, all_literal_types, namespaces)
        if slot.pattern:
            data_type["format"] = slot.pattern

        if slot.minimum_value:
            data_type["minimum"] = slot.minimum_value

        if slot.maximum_value:
            data_type["maximum"] = slot.maximum_value

        if slot.designates_type:
            column_definition["propertyUrl"] = "rdf:type"
            column_definition["valueUrl"] = f"{_SCHEMA_ORG_PREFIX}{{+{slot.name}}}"

        if slot.multivalued:
            column_definition["separator"] = _SEPARATOR_CHAR
            if slot.range == "uri":
                data_type = {"@id": f"{_MBO_PREFIX}ConvertIriToNode", "base": "string"}

        if slot.range == "uri" and not slot.multivalued:
            # Represent URIs as node values in the graph rather than as literal/primitive data types like strings.
            # Multivalued things still need to go via the <https://w3id.org/marco-bolo/ConvertIriToNode> conversion
            # route so should not have this specified.
            if slot.implicit_prefix:
                if not slot.implicit_prefix in namespaces:
                    raise Exception(f"Unable to find prefix definition for implicit_prefix '{slot.implicit_prefix}'.")
                prefix = namespaces.get(slot.implicit_prefix)
                column_definition["valueUrl"] = f"{prefix}{{+{slot.name}}}"
            else:
                column_definition["valueUrl"] = f"{{+{slot.name}}}"

        if slot.multivalued and slot.implicit_prefix:
            raise Exception(f"Unable to currently support implicit_prefix on multivalued slot.")

        column_definition["datatype"] = data_type

    return column_definition

def _map_linkml_built_in_data_type_to_csvw(linkml_built_in_data_type: str) -> str:


    raise Exception(f"Unmatched linkml base literal datatype '{linkml_built_in_data_type}'")

def _map_linkml_data_type_to_csvw(slot: SlotDefinition, all_literal_types: Dict[str, TypeDefinition], namespaces: Namespaces) -> Dict[str, str]:
    if slot.range in all_literal_types:
        literal_type = all_literal_types[slot.range]
        literal_type_base = (literal_type.base or "str").lower()
        data_type_def = {}

        if literal_type.uri is not None:
            data_type_uri = literal_type.uri.as_uri(namespaces)
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


if __name__ == "__main__":
    main()
