from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple, Optional
import shutil
from datetime import datetime

import pytest
import rdflib

from mbocsvwscripts.processparametadata import (
    _process_para_metadata,
    INPUT_METADATA_DATA_TYPE_URI,
    MBO_ORGANIZATION_URI, MBO,
)
from .utils import TEST_CASES_DIR, assert_file_contains_only_these_triples, assert_file_contains_these_triples


def test_removal_of_triples_from_input():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        input_file, output_file = _augment_input_metadata_tmp_dir(
            TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json",
            "mbo_TODO_LICENSE_1-input-metadata.json",
            tmp_dir,
        )

        graph = rdflib.Graph()
        graph.parse(input_file)

        assert not _ask_graph(
            graph,
            f"""
            ASK 
            WHERE {{
                [] a <{INPUT_METADATA_DATA_TYPE_URI}>
            }}
        """,
        )


def test_expected_output_triples_present():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        input_file, output_file = _augment_input_metadata_tmp_dir(
            TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json",
            "mbo_TODO_LICENSE_1-input-metadata.json",
            tmp_dir,
            dt_stamp=datetime.fromisoformat("2024-12-13T01:02:03Z"),
        )

        assert_file_contains_only_these_triples(
            output_file,
            f"""
            @prefix schema: <https://schema.org/>.
            @prefix mbo: <https://w3id.org/marco-bolo/>.
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
            
            mbo:mbo_TODO_LICENSE_1-input-metadata a schema:Dataset;
                                                  schema:dateCreated "2019-01-01T00:00:00Z";
                                                  schema:about mbo:mbo_TODO_LICENSE_1;
                                                  schema:creator mbo:mbo_todo_organization_mbo;
                                                  schema:distribution <{MBO['mbo_TODO_LICENSE_1-input-metadata#csv']}>,
                                                                      <{MBO['mbo_TODO_LICENSE_1-input-metadata#jsonld']}>.
                                                                      
            <{MBO['mbo_TODO_LICENSE_1-input-metadata#csv']}> a schema:DataDownload;
                                                             schema:dateCreated "2019-01-01T00:00:00Z";
                                                             schema:creator mbo:mbo_todo_organization_mbo;
                                                             schema:about mbo:mbo_TODO_LICENSE_1;
                                                             schema:encodesCreativeWork mbo:mbo_TODO_LICENSE_1-input-metadata;
                                                             schema:contentUrl <https://w3id.org/marco-bolo/mbo_TODO_license.csv#row=1>.
            
            <{MBO['mbo_TODO_LICENSE_1-input-metadata#jsonld']}> a schema:DataDownload;
                                                                schema:dateCreated "2024-12-13T01:02:03+00:00";
                                                                schema:creator <{MBO_ORGANIZATION_URI}>;
                                                                schema:about mbo:mbo_TODO_LICENSE_1;
                                                                schema:encodesCreativeWork mbo:mbo_TODO_LICENSE_1-input-metadata;
                                                                schema:contentUrl mbo:mbo_TODO_LICENSE_1.
        """,
        )


def test_github_output_triples_present():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        github_repo_commit_file_url = "https://github.com/marco-bolo/csv-to-jsonld/bb2dd7bc813d264c43089be26d2db9fd2cd99aa7/TODO"
        input_file, output_file = _augment_input_metadata_tmp_dir(
            TEST_CASES_DIR / "parametadata" / "mbo_TODO_LICENSE_1.json",
            "mbo_TODO_LICENSE_1-input-metadata.json",
            tmp_dir,
            git_repo_commit_file_url=github_repo_commit_file_url
        )

        assert_file_contains_these_triples(
            output_file,
            """
                prefix schema: <https://schema.org/>
                prefix mbo: <https://w3id.org/marco-bolo/>
            """,
            f"mbo:mbo_TODO_LICENSE_1-input-metadata schema:archivedAt <{github_repo_commit_file_url}>."
        )


def _augment_input_metadata_tmp_dir(
    input_file: Path,
    output_file_name: str,
    tmp_dir: Path,
    dt_stamp: datetime = datetime.fromisoformat("2020-01-01T01:02:03Z"),
    git_repo_commit_file_url: Optional[str] = None
) -> Tuple[Path, Path]:
    """
    We don't want to overwrite our test cases file. So this copies it to the given temporary dir for us.
    """

    tmp_input_file = tmp_dir / input_file.name
    shutil.copy(input_file, tmp_input_file)
    output_file = tmp_dir / output_file_name
    _process_para_metadata(tmp_input_file, output_file, dt_stamp, git_repo_commit_file_url=git_repo_commit_file_url)

    return tmp_input_file, output_file


def _ask_graph(graph: rdflib.Graph, ask_query: str) -> bool:
    results = list(graph.query(ask_query))
    return isinstance(results[0], bool) and results[0]


if __name__ == "__main__":
    pytest.main()
