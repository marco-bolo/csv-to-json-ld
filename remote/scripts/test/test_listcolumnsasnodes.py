import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import rdflib

from mbocsvwscripts.listcolumnsasnodes import (
    _convert_literals_to_nodes_in_file,
    _get_number_to_be_converted_in_graph,
)
from .utils import TEST_CASES_DIR


def test_mbo_list_columns_values_converted_to_node_references():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        tmp_dataset_ttl = tmp_dir / "dataset.ttl"
        shutil.copy(TEST_CASES_DIR / "dataset.ttl", tmp_dataset_ttl)

        _convert_literals_to_nodes_in_file(tmp_dataset_ttl)

        graph = rdflib.Graph()
        graph = graph.parse(tmp_dataset_ttl, format="ttl")

        # The below effectively asserts that all of the triples listed are in the graph.
        # This tests that all of the literals which are in dataset.ttl which should be converted are correctly converted.
        results = graph.query(
            """
            PREFIX schema:  <https://schema.org/>
            PREFIX mbo:     <https://w3id.org/marco-bolo/>

            ASK
            WHERE {
                mbo:mbo_TODO_DATASET_10 schema:url <https://example.com/some-landing-page>,
                                                   <https://example.com/some-other-landing-page>;
                                        schema:variableMeasured mbo:MBO_variable_measured_1;
                                        schema:isBasedOn <https://example.com/some-existing-dataset>.

                mbo:mbo_TODO_DATASET_2 schema:url <https://example.com/some-further-landing-page>;
                                       schema:variableMeasured mbo:MBO_variable_measured_1;
                                       schema:isBasedOn <https://example.com/some-existing-dataset>,
                                                        <https://w3id.org/marco-bolo/mbo_TODO_DATASET_1>.

                mbo:mbo_TODO_DATASET_5 schema:url <https://example.com/some-even-further-landing-page>;
                                       schema:variableMeasured mbo:MBO_variable_measured_1.
            }
        """
        )

        assert list(results) == [True]


def test_bare_mbo_identifier_in_url_pids_column_resolves_to_a_pid():
    """
    A `(URL PID)` column takes either form, and a bare MBO identifier is still an MBO identifier.
    Used verbatim it would be relative and resolve against the build directory, which is how real
    references to real records shipped as `file:///work/out/bulk/mbo_...`. See issues #161, #165.
    """
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        ttl_file = tmp_dir / "action.ttl"
        ttl_file.write_text(
            """
            @prefix schema: <https://schema.org/>.
            @prefix mbo:    <https://w3id.org/marco-bolo/>.

            mbo:mbo_TODO_ACTION_1 schema:object
                "mbo_00c37bee-0fd8-42c6-adf5-fd13dfa7a1f1"^^<https://w3id.org/marco-bolo/ConvertIriToNode>.
            """
        )

        _convert_literals_to_nodes_in_file(ttl_file)

        graph = rdflib.Graph().parse(ttl_file, format="ttl")
        assert {str(o) for o in graph.objects()} == {
            "https://w3id.org/marco-bolo/mbo_00c37bee-0fd8-42c6-adf5-fd13dfa7a1f1"
        }


def test_bare_mbo_identifier_and_external_urls_coexist_in_one_column():
    """The column is multivalued and mixes both kinds, so each value is treated on its own terms."""
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        ttl_file = tmp_dir / "action.ttl"
        ttl_file.write_text(
            """
            @prefix schema: <https://schema.org/>.
            @prefix mbo:    <https://w3id.org/marco-bolo/>.

            mbo:mbo_TODO_ACTION_1 schema:object
                "mbo_55ca5c88-e466-4fef-af2a-b9137d799136"^^<https://w3id.org/marco-bolo/ConvertIriToNode>,
                "https://example.com/someone-elses-dataset"^^<https://w3id.org/marco-bolo/ConvertIriToNode>,
                "doi:10.1000/example123"^^<https://w3id.org/marco-bolo/ConvertIriToNode>.
            """
        )

        _convert_literals_to_nodes_in_file(ttl_file)

        graph = rdflib.Graph().parse(ttl_file, format="ttl")
        assert {str(o) for o in graph.objects()} == {
            "https://w3id.org/marco-bolo/mbo_55ca5c88-e466-4fef-af2a-b9137d799136",
            "https://example.com/someone-elses-dataset",
            "doi:10.1000/example123",
        }


def test_unsubstituted_mbo_id_in_url_pids_column_is_rejected():
    """
    A value which is neither an MBO identifier nor an absolute URL cannot be resolved into anything
    meaningful. Used verbatim it is a relative IRI, which RDF completes against the build directory,
    shipping as `file:///work/out/bulk/...`.

    Note this is no longer where a mistyped *MBO* identifier is caught: `mbo_t44_data_hydrophonerraw`
    now resolves to an absolute PID and fails the foreign key check at `make validate` instead,
    which is both earlier and a clearer message. The two checks ask different questions -- "is this
    an address?" here, "does this record exist?" there.
    """
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        ttl_file = tmp_dir / "dataset.ttl"
        ttl_file.write_text(
            """
            @prefix schema: <https://schema.org/>.
            @prefix mbo:    <https://w3id.org/marco-bolo/>.

            mbo:mbo_TODO_DATASET_1 schema:isBasedOn
                "www.example.com/missing-scheme"^^<https://w3id.org/marco-bolo/ConvertIriToNode>.
            """
        )

        with pytest.raises(Exception, match="relative IRI"):
            _convert_literals_to_nodes_in_file(ttl_file)


def test_absolute_iris_in_url_pids_column_are_accepted():
    """The same column legitimately holds any absolute URL, so those must pass untouched."""
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        ttl_file = tmp_dir / "dataset.ttl"
        ttl_file.write_text(
            """
            @prefix schema: <https://schema.org/>.
            @prefix mbo:    <https://w3id.org/marco-bolo/>.

            mbo:mbo_TODO_DATASET_1 schema:isBasedOn
                "https://example.com/a"^^<https://w3id.org/marco-bolo/ConvertIriToNode>,
                "doi:10.1000/example123"^^<https://w3id.org/marco-bolo/ConvertIriToNode>,
                "ftp://ftp.example.org/data"^^<https://w3id.org/marco-bolo/ConvertIriToNode>.
            """
        )

        _convert_literals_to_nodes_in_file(ttl_file)

        graph = rdflib.Graph().parse(ttl_file, format="ttl")
        assert {str(o) for o in graph.objects()} == {
            "https://example.com/a",
            "doi:10.1000/example123",
            "ftp://ftp.example.org/data",
        }


def test_number_literals_to_be_converted_in_graph():
    graph = rdflib.Graph()
    graph = graph.parse(TEST_CASES_DIR / "dataset.ttl", format="ttl")

    num_to_be_converted = _get_number_to_be_converted_in_graph(graph)

    assert num_to_be_converted == 10


if __name__ == "__main__":
    pytest.main()
