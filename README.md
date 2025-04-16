# Experimental CSV-W representation of data for MBO

## Prerequisites

N.B. This requires that the build system has [make](https://www.gnu.org/software/make/) and [docker](https://www.docker.com/) installed.

## Data CSVs

End-users should ignore (or perhaps not see) all of the other files which arecurrently stored in [remote](./remote/). But they're necessary for validating the data and converting it to an RDF representation.

For detailed information about the CSV files and definitions of the columns they contain, see [class-descriptions.md](./class-descriptions.md).

## Before doing anything

Make sure you run the `init` command so that it can create the right output directories as well as pulling the required docker containers.

```bash
$ make init
```

## Validating the data

```bash
$ make validate
=============================== Pulling latest required docker images. ===============================
...

=============================== Validating remote/dataset-metadata.json ===============================
Valid CSV-W

=============================== Validating remote/eov-metadata.json ===============================
Valid CSV-W
```

It will (hopefully) tell you if you get something wrong, for instance referencing an EOV which isn't defined.

## Generating schema.org JSON-LD representation

```bash
$ make
....
```

### Speed build

If you want speedy outputs, have multiple cores at your disposal, and don't mind incoherently timed log outputs then consider running make with a degree of parallelism (`p`): 

```bash
$ p=4 && make -j "$p" init && make -j "$p" validate jsonld
```

Files are output in the `out` directory.

## <https://w3id.org/marco-bolo/ConvertMboIdToNode>

This is an identifier which is used in CSV-W metadata documents and is necessary due to limitations in the CSV on the web standard. The CSV-W standard supports delimited list columns, however only supports the serialisation of these to RDF literals and does not allow them to point to RDF Nodes. As a result, we use <https://w3id.org/marco-bolo/ConvertMboIdToNode> as the datatype in the CSV-W and later convert all of these literals into resource/node references in the build process. This process also sticks `https://w3id.org/marco-bolo/` on front of the value in the column.

N.B. <https://w3id.org/marco-bolo/ConvertIriToNode> provides a similar function but more generally for IRIs.

## <https://w3id.org/marco-bolo/InputMetadataDescription>

This is an identifier which is used to internally track the parametadata describing who input the metadata about something, when it was done, etc. 

## <https://w3id.org/marco-bolo/isResultOf>

An internal MBO predicate which effectively provides an inverse of <https://schema.org/result>. This allows us to specify the relationship `mbo:SomeAction schema:result mbo:SomeParaMetadata.` without having to modify create-action.csv or any of the outputs therefrom which would create an unhelpfully complex build dependencies graph. The resulting triple is represented in JSON-LD as a [@reverse](https://www.w3.org/TR/json-ld11/#reverse-properties) property.

Only to be used in a triple where the subject is an instance of <https://w3id.org/marco-bolo/InputMetadataDescription> and the object is an action defined in create-action.csv

