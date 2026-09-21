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


def test_unsubstituted_mbo_id_in_url_pids_column_is_rejected():
    """
    A `(URL PIDs)` value is used verbatim, so an mbo_ id which never got replaced with its UUID is a
    relative IRI. Left alone it resolves against the build directory and ships as
    `file:///work/out/bulk/...`. This is the real typo that reached published output: the mapping
    has `mbo_t44_data_hydrophoneraw`, the sheet had `hydrophone` + `rraw`.
    """
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        ttl_file = tmp_dir / "dataset.ttl"
        ttl_file.write_text(
            """
            @prefix schema: <https://schema.org/>.
            @prefix mbo:    <https://w3id.org/marco-bolo/>.

            mbo:mbo_TODO_DATASET_1 schema:isBasedOn
                "mbo_t44_data_hydrophonerraw"^^<https://w3id.org/marco-bolo/ConvertIriToNode>.
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
