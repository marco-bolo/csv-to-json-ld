"""
processparametadata
-------------------

Generate metadata describing the JSON-LD output. Augment (and improve the structure of input metadata that already exists.)
"""

from datetime import date
from pathlib import Path
from typing import Optional, Tuple, List

import click
import rdflib
from rdflib.namespace import Namespace, RDF
from rdflib.term import Node, URIRef, Literal
from rdflib.util import guess_format

MBO: Namespace = Namespace("https://w3id.org/marco-bolo/")
SCHEMA: Namespace = Namespace("https://schema.org/")

"""
The MBO URI Prefix.
"""
INPUT_METADATA_DATA_TYPE_URI: URIRef = MBO.InputMetadataDescription
"""
The rdf:type URI we use to easily identify which subject has the input metadata attached to it.
"""
MBO_ORGANIZATION_URI: URIRef = MBO.mbo_todo_organization_mbo
"""
The URI Persistent Identifier for the MARCO-BOLO Organization.
"""


@click.command("augment")
@click.argument("metadata_file", type=click.Path(exists=True))
@click.argument("para_metadata_file_out", type=click.Path())
@click.option("-g", "--git_repo_commit_file_url", type=str, required=False)
def main(
    metadata_file: click.Path,
    para_metadata_file_out: click.Path,
    git_repo_commit_file_url: Optional[str] = None,
) -> None:
    """
    1. Generates metadata describing the JSON-LD output generated in this build process.
    2. Augments (and improve the structure of) input metadata that already exists.
    3. Splits the input-metadata/para-metadata into a separate file `PARA_METADATA_FILE_OUT`.
    """
    _process_para_metadata(
        Path(str(metadata_file)),
        Path(str(para_metadata_file_out)),
        date.today(),
        git_repo_commit_file_url,
    )


def _process_para_metadata(
    metadata_file: Path,
    para_metadata_file_out: Path,
    dt_stamp: date,
    git_repo_commit_file_url: Optional[str] = None,
) -> None:
    input_graph, input_metadata_triples = _extract_input_metadata_triples_and_remove(
        metadata_file
    )

    uri_described_in_original_metadata = _get_uri_described_in_original_metadata(
        input_metadata_triples
    )

    para_metadata_graph = _build_para_metadata_graph(
        uri_described_in_original_metadata,
        input_metadata_triples,
        dt_stamp,
        git_repo_commit_file_url,
    )

    # Write everything out to disk now that we're confident it'll work.
    para_metadata_graph.serialize(
        para_metadata_file_out, format=guess_format(str(para_metadata_file_out))
    )
    # Do this last, incase something fails earlier and the user needs to retry.
    input_graph.serialize(metadata_file, format=guess_format(str(metadata_file)))


def _build_para_metadata_graph(
    uri_described_in_original_metadata: URIRef,
    input_metadata_triples: List[Tuple[Node, Node, Node]],
    date_created: date,
    git_repo_commit_file_url: str,
):
    dataset_uri = URIRef(f"{uri_described_in_original_metadata}-input-metadata")
    csv_data_download_uri = URIRef(
        f"{uri_described_in_original_metadata}-input-metadata#csv"
    )
    jsonld_data_download_uri = URIRef(
        f"{uri_described_in_original_metadata}-input-metadata#jsonld"
    )
    dataset_triples = [
        # The schema:Dataset record should have URI dataset_uri but copies most of its properties from the
        # existing CSV record.
        (dataset_uri, p, o)
        for (_, p, o) in input_metadata_triples
        # We of course don't bring the type/CSV URL along.
        if p not in {SCHEMA.contentUrl, RDF.type}
    ]
    dataset_triples += [
        (dataset_uri, RDF.type, SCHEMA.Dataset),
        (dataset_uri, SCHEMA.distribution, csv_data_download_uri),
        (dataset_uri, SCHEMA.distribution, jsonld_data_download_uri),
    ]
    if git_repo_commit_file_url is not None:
        dataset_triples.append(
            (dataset_uri, SCHEMA.archivedAt, URIRef(git_repo_commit_file_url))
        )

    csv_data_download_triples = [
        (csv_data_download_uri, p, o)
        for (_, p, o) in input_metadata_triples
        if p != RDF.type
    ]
    csv_data_download_triples += [
        (csv_data_download_uri, RDF.type, SCHEMA.DataDownload),
        (csv_data_download_uri, SCHEMA.encodesCreativeWork, dataset_uri),
        (csv_data_download_uri, SCHEMA.encodingFormat, Literal("text/csv")),
    ]

    json_data_download_triples = [
        (jsonld_data_download_uri, RDF.type, SCHEMA.DataDownload),
        (
            jsonld_data_download_uri,
            SCHEMA.dateCreated,
            Literal(date_created.isoformat(), datatype=SCHEMA.Date),
        ),
        (jsonld_data_download_uri, SCHEMA.creator, MBO_ORGANIZATION_URI),
        (jsonld_data_download_uri, SCHEMA.about, uri_described_in_original_metadata),
        (jsonld_data_download_uri, SCHEMA.encodesCreativeWork, dataset_uri),
        (
            jsonld_data_download_uri,
            SCHEMA.contentUrl,
            uri_described_in_original_metadata,
        ),
        (
            jsonld_data_download_uri,
            SCHEMA.encodingFormat,
            Literal("application/ld+json"),
        ),
    ]
    para_metadata_graph = rdflib.Graph()
    para_metadata_graph += dataset_triples
    para_metadata_graph += csv_data_download_triples
    para_metadata_graph += json_data_download_triples

    return para_metadata_graph


def _get_uri_described_in_original_metadata(
    input_metadata_triples: List[Tuple[Node, Node, Node]],
) -> URIRef:
    para_metadata_about_triples = [
        o for (_, p, o) in input_metadata_triples if p == SCHEMA.about
    ]
    if len(para_metadata_about_triples) != 1:
        raise Exception(
            f"Found para-metadata with {len(para_metadata_about_triples)} triples using the predicate {SCHEMA.about}. Expected only one."
        )
    uri_described_in_metadata = para_metadata_about_triples[0]
    return uri_described_in_metadata  # type: ignore


def _extract_input_metadata_triples_and_remove(
    metadata_file: Path,
) -> Tuple[rdflib.Graph, List[Tuple[Node, Node, Node]]]:
    input_graph = rdflib.Graph()
    input_graph.parse(metadata_file)
    input_metadata_triples = list(
        input_graph.query(
            f"""
        prefix mbo: <https://w3id.org/marco-bolo/>
        prefix schema: <https://schema.org/>
        
        CONSTRUCT {{
            ?inputMetadata ?p ?o.
        }}
        WHERE {{
            ?inputMetadata a <{INPUT_METADATA_DATA_TYPE_URI}>;
                           ?p ?o.
        }}
    """
        )
    )

    input_graph.update(
        f"""
        DELETE 
        WHERE {{
            ?inputMetadata a <{INPUT_METADATA_DATA_TYPE_URI}>;
                           ?p ?o.
        }}
    """
    )

    return input_graph, input_metadata_triples


if __name__ == "__main__":
    main()
