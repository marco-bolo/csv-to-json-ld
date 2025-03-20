"""
sparqlwhere
-----------

Finds the input files matching a glob which also match a provided SPARQL query.
"""

from pathlib import Path
from typing import Iterable

import click
import rdflib


@click.command("execute")
@click.option(
    "-d",
    "--dir",
    required=False,
    type=click.Path(),
    show_default=True,
    default=".",
    help="Directory in which to search for the glob pattern.",
)
@click.argument("glob", type=str)
@click.argument("sparql_query", type=str)
def main(dir: click.Path, glob: str, sparql_query: str):
    """
    Takes a BULK_TTL_FILE and splits it into one JSON-LD file per unique URI.

    Hash-URIs end up in the same file.
    """
    for matching_file in _find_files_matching_sparql_query(
        Path(str(dir)), glob, sparql_query
    ):
        print(matching_file.absolute().relative_to(dir))


def _find_files_matching_sparql_query(
    search_dir: Path, glob: str, sparql_query: str
) -> Iterable[Path]:
    for file in search_dir.rglob(glob):
        graph = rdflib.Graph()
        graph.parse(file)
        results = list(graph.query(sparql_query))
        if any(results):
            if isinstance(results[0], bool) and results[0]:
                # If an ASK query returns `True` then the file matches the query.
                yield file
            else:
                # If a SELECT query returns any results then we consider that the file matches the query.
                yield file


if __name__ == "__main__":
    main()
