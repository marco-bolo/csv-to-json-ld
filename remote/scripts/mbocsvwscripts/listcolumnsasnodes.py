"""
listcolumnsasnodes
------------------

Converts literals of type <https://w3id.org/marco-bolo/ConvertMboIdToNode> and <https://w3id.org/marco-bolo/ConvertIriToNode> into references to nodes in the graph.

This makes up for a limitation in the CSV on the web standard, see <https://lists.w3.org/Archives/Public/public-csvw/2016Aug/0001.html>.
"""

from pathlib import Path
from urllib.parse import urlsplit

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
                # A `(URL PID)` column accepts either. An MBO identifier written bare is still an
                # MBO identifier, so resolve it against our namespace exactly as ConvertMboIdToNode
                # does; used verbatim it would be a relative IRI, and RDF would silently complete it
                # against whatever file is being processed. See issues #161, #165.
                ?s ?p ?nodePID.
                FILTER(datatype(?nodePID) = <https://w3id.org/marco-bolo/ConvertIriToNode>).
                FILTER(STRSTARTS(STR(?nodePID), "mbo_")).
                BIND (URI( CONCAT("https://w3id.org/marco-bolo/", STR(?nodePID))) as ?uriNode).
            } UNION {
                # Any other value -- https://, doi:, ftp:// -- is someone else's URL. Used verbatim.
                ?s ?p ?nodePID.
                FILTER(datatype(?nodePID) = <https://w3id.org/marco-bolo/ConvertIriToNode>).
                FILTER(!STRSTARTS(STR(?nodePID), "mbo_")).
                BIND(URI(STR(?nodePID)) as ?uriNode).
            }
        }
    """
    )

    num_remaining = _get_number_to_be_converted_in_graph(graph)
    if num_remaining != 0:
        raise Exception(f"Failed to convert {num_remaining}literals.")

    _assert_converted_iris_are_absolute(graph)

    return graph


def _assert_converted_iris_are_absolute(graph: rdflib.Graph) -> None:
    """
    A `(URL PIDs)` column is used verbatim, since it may legitimately hold any kind of URL. So an
    `mbo_` identifier which was never replaced with its UUID arrives here as a *relative* IRI
    reference, and RDF gives us no way to leave one unresolved - it is silently completed against
    whatever document is being processed. That turns a typo like `mbo_t44_data_hydrophonerraw` into
    `file:///work/out/bulk/mbo_t44_data_hydrophonerraw` in published output.

    These columns have no foreign key checks by design, so this is the only thing standing between a
    mistyped identifier and a broken link in the catalogue. Every IRI we mint must be absolute, which
    for our purposes means it carries a scheme.
    """
    relative_iris = sorted(
        {
            f"<{o}> as the object of <{p}> on <{s}>"
            for (s, p, o) in graph
            if isinstance(o, rdflib.URIRef) and not urlsplit(str(o)).scheme
        }
    )

    if any(relative_iris):
        raise Exception(
            f"Produced {len(relative_iris)} relative IRI(s); every IRI must be absolute. "
            "This usually means an mbo_ identifier in a '(URL PIDs)' column was never replaced "
            "with its UUID - look for a typo in the source sheet, or a record missing from "
            "config/uuid_mapping.json:" + "".join(f"\n  {i}" for i in relative_iris)
        )


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
