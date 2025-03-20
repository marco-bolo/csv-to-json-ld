"""
listcolumnsasnodes
------------------

Converts literals of type <https://w3id.org/marco-bolo/ConvertMboIdToNode> and <https://w3id.org/marco-bolo/ConvertIriToNode> into references to nodes in the graph.

This makes up for a limitation in the CSV on the web standard, see <https://lists.w3.org/Archives/Public/public-csvw/2016Aug/0001.html>.
"""

from pathlib import Path

import click
import rdflib


@click.command()
@click.argument("ttl_file", type=click.Path(exists=True))
def main(ttl_file: click.Path):
    """
    Loads the TTL_FILE and transforms all literals of type <https://w3id.org/marco-bolo/ConvertMboIdToNode> and
        <https://w3id.org/marco-bolo/ConvertIriToNode> into references to nodes in the graph.
    """
    _convert_literals_to_nodes_in_file(Path(str(ttl_file)))


def _convert_literals_to_nodes_in_file(ttl_file: Path) -> None:
    ttl_file = ttl_file.resolve()

    graph = rdflib.Graph()
    graph = graph.parse(ttl_file, format="ttl")

    num_to_be_converted = _get_number_to_be_converted_in_graph(graph)

    if num_to_be_converted > 0:
        graph = _update_literals_to_nodes_in_graph_assert_success(graph)
        graph.serialize(ttl_file, format="ttl")


def _update_literals_to_nodes_in_graph_assert_success(
    graph: rdflib.Graph,
) -> rdflib.Graph:
    graph.update(
        """
        DELETE {
            ?s ?p ?nodePID.
        }
        INSERT {
            ?s ?p ?uriNode.
        }
        WHERE {
            {
                # Map literals of type <https://w3id.org/marco-bolo/ConvertMboIdToNode> into full MBO PIDs pointing at resources.
                ?s ?p ?nodePID.
                FILTER(datatype(?nodePID) = <https://w3id.org/marco-bolo/ConvertMboIdToNode>).
                BIND (URI( CONCAT("https://w3id.org/marco-bolo/", STR(?nodePID))) as ?uriNode).
            } UNION {
                # Map literals of type <https://w3id.org/marco-bolo/ConvertIriToNode> into IRIs pointing at resources.
                ?s ?p ?nodePID.
                FILTER(datatype(?nodePID) = <https://w3id.org/marco-bolo/ConvertIriToNode>).
                BIND(URI(STR(?nodePID)) as ?uriNode).
            }
        }
    """
    )

    num_remaining = _get_number_to_be_converted_in_graph(graph)
    if num_remaining != 0:
        raise Exception(f"Failed to convert {num_remaining}literals.")

    return graph


def _get_number_to_be_converted_in_graph(graph: rdflib.Graph) -> int:
    results = list(
        graph.query(
            """
        SELECT *
        WHERE {
            ?s ?p ?mboNodePID.
            FILTER(datatype(?mboNodePID) IN (<https://w3id.org/marco-bolo/ConvertMboIdToNode>, <https://w3id.org/marco-bolo/ConvertIriToNode>)).
        }
        """
        )
    )

    return len(results)


if __name__ == "__main__":
    main()
