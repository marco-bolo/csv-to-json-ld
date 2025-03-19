from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

import rdflib
import pytest

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


def test_number_literals_to_be_converted_in_graph():
    graph = rdflib.Graph()
    graph = graph.parse(TEST_CASES_DIR / "dataset.ttl", format="ttl")

    num_to_be_converted = _get_number_to_be_converted_in_graph(graph)

    assert num_to_be_converted == 10


if __name__ == "__main__":
    pytest.main()
