# Experimental CSV-W representation of data for MBO

## To add your metadata to the CSVs via a browser
* Go to the [editing dashboard](https://docs.google.com/spreadsheets/d/1PBFK3LW3DAdvXdbk2v8bSdtTf87mBhabeeegwRjOBRg/edit?usp=drive_link)
* Edit the files
* Your data is automatically synchronized with the processing system nightly
* You can view the resulting JSON files at: https://lab.marcobolo-project.eu/csv-to-json-ld/schema-jsonld/.
* Logs from the process are attached to the GitHub Actions, WP1  monitors data validation and will contact you if any issues need resolution.
* Validated data becomes part of the MARCO-BOLO metadata catalog andw will be made discoverable through international research platforms, beginning with ODIS.

# Stand-alone Use

This tool was originally designed to be used by independent users to generate JSON-LD that could then be published where they deemed appropriate. MARCO-BOLO is not following that workflow; the instructions below remain for future users who might want to take a different approach.

## To add your metadata and validate via the command line
That is, to pull the CSVs, edit them via your favourite CSV app, push them back, and then run validation, all from the command line. 

### Prerequisites

N.B. This requires that the build system has [make](https://www.gnu.org/software/make/) and [docker](https://www.docker.com/) installed.

### Data CSVs

End-users should ignore (or perhaps not see) all of the other files which arecurrently stored in [remote](./remote/). But they're necessary for validating the data and converting it to an RDF representation.

For detailed information about the CSV files and definitions of the columns they contain, see [class-descriptions.md](./class-descriptions.md).

### Before doing anything

Make sure you run the `init` command so that it can create the right output directories as well as pulling the required docker containers.

```bash
$ make init
```

### Validating the data

#### CSV-W and Manual Foreign Key Constraints

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

#### The SHACL Report

There are some forms of invalid data which can only be detected when looking at the data in its entirety. For instance we check to ensure that an MBO Identifier hasn't been (accidentally) reused in different CSV files; further, we want to generate a report of entities which have been defined but don't seem to be referenced anywhere else in the dataset. These constraints are applied via SHACL constraints (see [remote/shacl.ttl](./remote/shacl.ttl)). Violations cause the build to fail, warnings do not cause the build to fail.

```bash
$ make shacl-report

The SHACL Report:

First looking for any violations:

+----------+
| Conforms |
+----------+
|   True   |
+----------+


Now looking for any warnings or info:

+----------+
| Conforms |
+----------+
|  False   |
+----------+

+-----+----------+---------------------------+-------------+---------------------------+---------------------------+---------------------------+---------------------------+
| No. | Severity | Focus Node                | Result Path | Message                   | Component                 | Shape                     | Value                     |
+-----+----------+---------------------------+-------------+---------------------------+---------------------------+---------------------------+---------------------------+
| 1   | Warning  | https://w3id.org/marco-bo | -           | All entities should be re | SPARQLConstraintComponent | http://w3id.org/marco-bol | MBO Identifier 'mbo_todo_ |
|     |          | lo/mbo_todo_license_4     |             | ferenced somewhere else;  |                           | o/ShaclConstraints/Entit  | license_4' in License.csv |
|     |          |                           |             | this is a warning, it is  |                           | iesShouldBeReferenced     |  doesn't appear to be ref |
|     |          |                           |             | not enforced.             |                           |                           | erenced anywhere else.    |
|     |          |                           |             |                           |                           |                           |                           |
....

```

Pay attention to the `Focus Node` field which tells you which entity is the problem, as well as the `Message` and `Value` columns which tell you what the problem is.
### Generating schema.org JSON-LD representation

```bash
$ make
....
```

#### Running Everything Locally

1. Make sure you have installed docker on your machine. Installing [Docker Desktop](https://docs.docker.com/desktop/) may be the easiest way.
2. Make sure that you have GNU Make, Bash and [jq](https://jqlang.org/) installed . 
3. Make sure you have installed [git](https://git-scm.com/downloads) on your machine. then clone the repository locally with the following command:

```bash
$ git clone https://github.com/marco-bolo/csv-to-json-ld.git
```
4. Make the changes to the CSV files inside the `csv-to-json-ld` folder.
5. Open a terminal in the repo you have just cloned and run the following:

```bash
$ make init check validate shacl-report
```

This may take a bit of time as it will pull 4 substantially sized docker images from the internet. But it will eventually perform all of the validations (without actually generating the JSON-LD outputs)

5. Alternatively you can run the whole process which will perform the checks, validation and generate the resulting JSON-LD files in a directory called 'out'.

```bash
$ make
```

#### Speed build

If you want speedy outputs, have multiple cores at your disposal, and don't mind incoherently timed log outputs then consider running make with a degree of parallelism (`p`): 

```bash
$ p=4 && make -j "$p" init && make -j "$p" validate shacl-report jsonld
```

Files are output in the `out` directory.

### <https://w3id.org/marco-bolo/ConvertMboIdToNode>

This is an identifier which is used in CSV-W metadata documents and is necessary due to limitations in the CSV on the web standard. The CSV-W standard supports delimited list columns, however only supports the serialisation of these to RDF literals and does not allow them to point to RDF Nodes. As a result, we use <https://w3id.org/marco-bolo/ConvertMboIdToNode> as the datatype in the CSV-W and later convert all of these literals into resource/node references in the build process. This process also sticks `https://w3id.org/marco-bolo/` on front of the value in the column.

N.B. <https://w3id.org/marco-bolo/ConvertIriToNode> provides a similar function but more generally for IRIs.

### <https://w3id.org/marco-bolo/InputMetadataDescription>

This is an identifier which is used to internally track the parametadata describing who input the metadata about something, when it was done, etc. 

### <https://w3id.org/marco-bolo/isResultOf>

An internal MBO predicate which effectively provides an inverse of <https://schema.org/result>. This allows us to specify the relationship `mbo:SomeAction schema:result mbo:SomeParaMetadata.` without having to modify create-action.csv or any of the outputs therefrom which would create an unhelpfully complex build dependencies graph. The resulting triple is represented in JSON-LD as a [@reverse](https://www.w3.org/TR/json-ld11/#reverse-properties) property.

Only to be used in a triple where the subject is an instance of <https://w3id.org/marco-bolo/InputMetadataDescription> and the object is an action defined in create-action.csv

