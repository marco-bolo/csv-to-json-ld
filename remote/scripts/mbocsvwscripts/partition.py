"""
partition
---------

Partitions ttl files into multiple JSON-LD files with one subject per file.
"""

from typing import Set
from pathlib import Path
from urllib.parse import urlparse

import click
import rdflib


@click.group()
def main():
    """
    Takes a BULK_TTL_FILE and splits it into one JSON-LD file per unique URI.

    Hash-URIs end up in the same file.
    """
    pass


@main.command("execute")
@click.option(
    "-o", "--out", required=False, type=click.Path(), show_default=True, default="."
)
@click.argument("bulk_ttl_file", type=click.Path(exists=True))
def partition(out: click.Path, bulk_ttl_file: click.Path):
    """
    Takes a BULK_TTL_FILE and splits it into one JSON-LD file per unique URI.

    Hash-URIs end up in the same file.
    """
    _partition_to_individual_files(Path(str(bulk_ttl_file)), Path(str(out)))


@main.command("list")
@click.option(
    "-o", "--out", required=False, type=click.Path(), show_default=True, default="."
)
@click.argument("bulk_ttl_file", type=click.Path(exists=True))
def list_partition_files_out(out: click.Path, bulk_ttl_file: click.Path):
    """
    Takes a BULK_TTL_FILE and lists the hypothetical JSON-LD files that it would be generated when the triples
    were split into one file per URI.

    Hash-URIs end up in the same file.
    """
    cwd = Path(".").absolute()
    for output_file in _list_partition_files_out(
        Path(str(bulk_ttl_file)), Path(str(out))
    ):
        print(output_file.absolute().relative_to(cwd))


def _list_partition_files_out(bulk_ttl_file: Path, out_folder: Path) -> Set[Path]:
    bulk_ttl_graph = rdflib.Graph()
    bulk_ttl_graph.parse(bulk_ttl_file, format="ttl")

    return {
        _get_partition_file_path(out_folder, partition)
        for partition in _get_partition_uri_prefixes(bulk_ttl_graph)
    }


def _partition_to_individual_files(bulk_ttl_file: Path, out_folder: Path) -> None:
    bulk_ttl_graph = rdflib.Graph()
    bulk_ttl_graph.parse(bulk_ttl_file, format="ttl")

    for partition in _get_partition_uri_prefixes(bulk_ttl_graph):
        partitioned_triples = _partition_triples(bulk_ttl_graph, partition)

        partition_file_path = _get_partition_file_path(out_folder, partition)
        partitioned_triples.serialize(partition_file_path, format="json-ld")


def _get_partition_file_path(
    out_folder: Path, partition: rdflib.term.Identifier
) -> Path:
    url_slug = Path(urlparse(str(partition)).path).parts[-1]
    return out_folder / f"{url_slug}.json"


def _partition_triples(bulk_ttl_graph: rdflib.Graph, partition: rdflib.term.Identifier):
    partitioned_triples_graph = rdflib.Graph()
    partitioned_triple_results = bulk_ttl_graph.query(
        """
            prefix schema: <https://schema.org/>
            prefix goos: <https://goosocean.org/document/>
            prefix mbo: <https://w3id.org/marco-bolo/>
            
            CONSTRUCT {
                ?s ?p ?o.
            }
            WHERE { 
                ?s ?p ?o.
                FILTER(str(?s) = ?v || strbefore(str(?s), '#') = ?v)
            }
        """,
        initBindings={"v": partition},
    )

    for partitioned_triple in partitioned_triple_results:
        partitioned_triples_graph.add(partitioned_triple)

    return partitioned_triples_graph


def _get_partition_uri_prefixes(
    bulk_ttl_graph: rdflib.Graph,
) -> Set[rdflib.term.Identifier]:
    partition_results = list(
        bulk_ttl_graph.query(
            """
                SELECT DISTINCT ?partition WHERE {
                     { 
                        # Strip the hash parts off URLs where they exist
                        ?s ?p ?o. 
                        FILTER (contains(str(?s), '#')). 
                        BIND (strbefore(str(?s), '#') as ?partition). 
                    } UNION 
                    { 
                        ?s ?p ?o. 
                        FILTER (! contains(str(?s), '#')). 
                        BIND(str(?s) as ?partition). 
                    } 
                }
            """
        )
    )
    return {r.asdict()["partition"] for r in partition_results}


if __name__ == "__main__":
    partition()
