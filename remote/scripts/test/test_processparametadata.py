import shutil
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple, Optional

import pytest
import rdflib
from rdflib.compare import isomorphic

from mbocsvwscripts.processparametadata import (
    _process_para_metadata,
    INPUT_METADATA_DATA_TYPE_URI,
    MBO_ORGANIZATION_URI,
    MBO,
)
from .utils import (
    TEST_CASES_DIR,
    assert_file_contains_only_these_triples,
    assert_file_contains_these_triples,
)


def test_input_file_is_not_modified():
    """Build steps get re-run; a step that edits its own input is a landmine."""
    source = TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json"
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        input_file, _ = _augment_input_metadata_tmp_dir(
            source, "mbo_TODO_LICENSE_1-merged.json", tmp_dir
        )

        assert input_file.read_bytes() == source.read_bytes()


def test_rerunning_over_its_own_output_is_a_no_op():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        _, first_output = _augment_input_metadata_tmp_dir(
            TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json",
            "mbo_TODO_LICENSE_1-merged.json",
            tmp_dir,
        )

        second_output = tmp_dir / "second-pass.json"
        _process_para_metadata(
            first_output, second_output, date.fromisoformat("2020-01-01")
        )

        first_graph = rdflib.Graph()
        first_graph.parse(first_output)
        second_graph = rdflib.Graph()
        second_graph.parse(second_output)

        assert isomorphic(first_graph, second_graph)


def test_entity_links_to_its_para_metadata():
    """The entity is the subject of its own para-metadata record."""
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        _, output_file = _augment_input_metadata_tmp_dir(
            TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json",
            "mbo_TODO_LICENSE_1-merged.json",
            tmp_dir,
        )

        assert_file_contains_these_triples(
            output_file,
            """
                prefix schema: <https://schema.org/>
                prefix mbo: <https://w3id.org/marco-bolo/>
            """,
            "mbo:mbo_TODO_LICENSE_1 schema:subjectOf mbo:mbo_TODO_LICENSE_1-input-metadata.",
        )


def test_expected_output_triples_present():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        input_file, output_file = _augment_input_metadata_tmp_dir(
            TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json",
            "mbo_TODO_LICENSE_1-merged.json",
            tmp_dir,
            date_created=date.fromisoformat("2024-12-13"),
        )

        assert_file_contains_only_these_triples(
            output_file,
            f"""
            @prefix schema: <https://schema.org/>.
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
            
            mbo:mbo_TODO_LICENSE_1 a schema:CreativeWork;
                                   schema:name "Creative Commons Zero v1.0 Universal";
                                   schema:url <https://spdx.org/licenses/CC0-1.0>;
                                   schema:subjectOf mbo:mbo_TODO_LICENSE_1-input-metadata.

            mbo:mbo_TODO_LICENSE_1-input-metadata a schema:Dataset, mbo:InputMetadataDescription;
                                                  schema:dateCreated "2019-01-01"^^schema:Date;
                                                  schema:about mbo:mbo_TODO_LICENSE_1;
                                                  schema:creator mbo:mbo_todo_organization_mbo;
                                                  schema:distribution <{MBO['mbo_TODO_LICENSE_1-input-metadata#csv']}>,
                                                                      <{MBO['mbo_TODO_LICENSE_1-input-metadata#jsonld']}>.
                                                                      
            <{MBO['mbo_TODO_LICENSE_1-input-metadata#csv']}> a schema:DataDownload;
                                                             schema:dateCreated "2019-01-01"^^schema:Date;
                                                             schema:creator mbo:mbo_todo_organization_mbo;
                                                             schema:about mbo:mbo_TODO_LICENSE_1;
                                                             schema:encodesCreativeWork mbo:mbo_TODO_LICENSE_1-input-metadata;
                                                             schema:contentUrl <https://w3id.org/marco-bolo/mbo_TODO_license.csv#row=1>;
                                                             schema:encodingFormat "text/csv".
            
            <{MBO['mbo_TODO_LICENSE_1-input-metadata#jsonld']}> a schema:DataDownload;
                                                                schema:dateModified "2024-12-13"^^schema:Date;
                                                                schema:creator <{MBO_ORGANIZATION_URI}>;
                                                                schema:about mbo:mbo_TODO_LICENSE_1;
                                                                schema:encodesCreativeWork mbo:mbo_TODO_LICENSE_1-input-metadata;
                                                                schema:contentUrl <https://w3id.org/marco-bolo/mbo_TODO_LICENSE_1>;
                                                                schema:encodingFormat "application/ld+json".
                                                                
            mbo:mbo_some_action a schema:CreateAction;
                                schema:result mbo:mbo_TODO_LICENSE_1-input-metadata,
                                              <{MBO['mbo_TODO_LICENSE_1-input-metadata#csv']}>, 
                                              <{MBO['mbo_TODO_LICENSE_1-input-metadata#jsonld']}>.
        """,
        )


def test_github_output_triples_present():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        github_repo_commit_file_url = "https://github.com/marco-bolo/csv-to-jsonld/bb2dd7bc813d264c43089be26d2db9fd2cd99aa7/TODO"
        input_file, output_file = _augment_input_metadata_tmp_dir(
            TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json",
            "mbo_TODO_LICENSE_1-merged.json",
            tmp_dir,
            git_repo_commit_file_url=github_repo_commit_file_url,
        )

        assert_file_contains_these_triples(
            output_file,
            """
                prefix schema: <https://schema.org/>
                prefix mbo: <https://w3id.org/marco-bolo/>
            """,
            f"mbo:mbo_TODO_LICENSE_1-input-metadata schema:archivedAt <{github_repo_commit_file_url}>.",
        )


def _augment_input_metadata_tmp_dir(
    input_file: Path,
    output_file_name: str,
    tmp_dir: Path,
    date_created: date = date.fromisoformat("2020-01-01"),
    git_repo_commit_file_url: Optional[str] = None,
) -> Tuple[Path, Path]:
    """
    We don't want to overwrite our test cases file. So this copies it to the given temporary dir for us.
    """

    tmp_input_file = tmp_dir / input_file.name
    shutil.copy(input_file, tmp_input_file)
    output_file = tmp_dir / output_file_name
    _process_para_metadata(
        tmp_input_file,
        output_file,
        date_created,
        git_repo_commit_file_url=git_repo_commit_file_url,
    )

    return tmp_input_file, output_file


def _ask_graph(graph: rdflib.Graph, ask_query: str) -> bool:
    results = list(graph.query(ask_query))
    return isinstance(results[0], bool) and results[0]


if __name__ == "__main__":
    pytest.main()
