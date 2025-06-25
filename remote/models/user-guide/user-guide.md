# CSV-to-JSON-LD User Guide

*This is a place to organize information to teach and guide the casual user.*

#### License

This project is open source and licensed under the MIT License.


## What is the tool?

This is a metadata publishing tool developed for **[Work Package 1 (WP1)](https://marcobolo-project.eu/work-packages/work-package-1)** of the [**MARCO-BOLO** project](https://marcobolo-project.eu/) (MARine COastal BiOdiversity Long-term Observations). WP1 focuses on data literacy and metadata flow across the project. This tool helps researchers and data managers transform metadata from CSV files into **JSON-LD** conforming to **Schema.org** and ready for harvesting by the [ODIS Catalog](https://catalog.odis.org/).

Why was this tool created? [Answer]

## 🛠 How the Tool Works

This tool helps you turn metadata stored in **CSV files** into a format that can be read by machines and shared widely across the web — specifically, in a format called **JSON-LD**, which follows the **Schema.org** standard.

### Documentation

- [Rendered model documentation](http://lab.marcobolo-project.eu/csv-to-json-ld/index.html)

To make all this possible, the tool brings together four key technologies:

### Step By Step Explanation

---

#### 📘 1. LinkML: The Blueprint

**LinkML** (Linked Modeling Language) is used to define a _schema_ — basically, a blueprint that tells us:
- what kinds of metadata we expect (e.g., dataset title, creator, location)
- what format each field should have (e.g., a date, a URL, a number)
- which fields are required

We use LinkML to write these rules in a way that can be both human- and machine-readable. This schema ensures that everyone entering metadata is using the same structure.

---

#### 📄 2. CSV-W: Structured Spreadsheets

Most people are comfortable using spreadsheets, so we use **CSV files** to collect metadata. But plain CSV files don’t include descriptions of what each column means. That’s where **CSV-W** (CSV on the Web) comes in.

CSV-W adds a **metadata file** alongside each CSV, which explains:
- what each column represents
- how to interpret the data (e.g., what kind of value it is, which field in the schema it maps to)

This lets us treat CSV files like structured, interoperable datasets — not just a bunch of text.

---

#### 🌐 3. W3IDs: Persistent Links

Each field or class in the schema — like `creator`, `identifier`, or `dataset` — is assigned a **W3ID** (Web Identifier).

W3IDs are **permanent URLs** that act as stable identifiers for these concepts. For example:

`https://w3id.org/marco-bolo/Dataset`


Even if we update the website or move things around, this W3ID will always point to the current definition of “Dataset” in our schema. It’s like giving every concept a permanent name tag.

---

#### 🧩 4. Schema.org: Speaking a Common Language

When we convert metadata into **JSON-LD**, we map it to **Schema.org** — a vocabulary used by Google, Bing, and many others to understand web content.

This means the metadata you publish:
- can be discovered by search engines
- fits into global data-sharing platforms like the [ODIS Catalog](https://catalog.odis.org)
- supports automated reuse and integration across domains

Schema.org helps your dataset "speak the same language" as other data on the internet.

---

## 🧬 Bringing It All Together

1. **You fill in CSV templates** based on the LinkML schema.
2. **CSV-W files describe** what each column in those spreadsheets means.
3. **GitHub Actions validate** your data against the schema to catch any problems.
4. **The tool converts** your metadata into Schema.org-compliant JSON-LD.
5. **W3IDs make sure** all terms have stable, referenceable definitions.
6. **You publish** the JSON-LD on the web, and it can be harvested into global catalogs.


## Suggested approach

There are multiple ways you could use this tool on GitHub and on your local machine, but we are going to focus on the workflow that we think works best across MARCO-BOLO WPs. Here are the general steps, we'll walk through each of them in detail, below.

1. Fork the GitHub Repository.
1. Add your task information (e.g. dataset) to the CSV files.
1. Submit a Pull Request to the original MARCO-BOLO repository.
1. Your work will be reviewed and merged with this central repository, which will be registered with ODIS.


### 1. Fork the GitHub Repository.


1. If you don't have one, Create a GitHub Account: https://github.com/signup
1. Create a copy of the repository, or 'fork', in which to do your work. 
	1. Click the 'fork' button, or go to https://github.com/marco-bolo/csv-to-json-ld/fork
	1. Select yourself as the owner.
	1. Click 'Create fork'.
	1. You should now have a copy of the repository at `https://github.com/your-github-username/csv-to-json-ld/`

### 2. Add your task information (e.g. dataset) to the CSV files.

*This section are merely suggestions that should be under constant revision based on what seems to be easiest for MBO users.*

1. There are a variety of ways you can do this. Here are our recommendations:
	1. If you are savvy with GitHub, clone your copy locally, use your editor of choice to update the CSV files and push the updates to your fork.
	1. If you are unfamiliar with GitHub, download a local zip file of the repo, by clicking the green `Code` button and selecting `Download ZIP`. Alternatively you can go to: `https://github.com/your-github-username/csv-to-json-ld/archive/refs/heads/main.zip`
	1. Unzip the downloaded file, and use your editor of choice to make updates to the CSV files.
	1. Upload the CSV files that have changed to your GitHub fork by clicking the `Add file` button and selecting `Upload files`. Include a meaningful 'commit' message describing the changes you have made. As long as the file name is the same, it will overwrite the copy that is hosted on GitHub.

### 3 Submit a Pull Request to the original MARCO-BOLO repository.

1. To merge your changes with the original MARCO-BOLO repository and the WP1 team, you need to make a Pull Request (PR)
1. On your GitHub fork, click the `Contribute` button and select 'Open pull request'.
1. Add a meaningful title and description of the changes you have made.
1. Click `Reviewers` to select a WP1 Team member to review and approve your changes.
1. Click `Create pull request`

### 4. Your work will be reviewed and merged with this central repository, which will be registered with ODIS.

*Very much in development*

1. A WP1 Team member will review your changes and communicate with you via GitHub about any changes that need to be made. 
1. From here, we need to figure out if the JSON-LD files should have been generated on their fork, or if we do them after merging.
1. If the latter, this would be part of the review process since it will have to clear validation to create the JSON-LD.

### GitHub.dev approach

1. GitHub offers an environment for editing the CSV files. The advantage of working in this space is you avoid local copies of the files. The disadvantage is you have a limited set of CSV editing functions.
1. To access this environment, go to `https://github.dev/your-github-username/csv-to-json-ld`
1. Sign in to GitHub when prompted and authorize GitHub.dev to access your account.
1. If this is your first time, click on the `Extensions` icon (a group of stacked squares) and install the “Excel Viewer” extension from MESCIUS. This enables spreadsheet-style editing of CSV files.
1. Tick the box: “Use this profile as the default for new windows”. This configures your browser to open CSVs with a table-based view.
1. You may need to open the CSV by right-clicking on the file and clicke `open with` > `CSV Editor Excel Viewer`. You and can make this the default open option for CSVs via the same menu.


## Validating through GitHub Actions

*This is most relevant to the WP1 team, who will likely be supervising validation*

The workflow for validating the CSVs and generating the JSON-LD can be found here: https://github.com/marco-bolo/csv-to-json-ld/blob/main/.github/workflows/build-jsonld.yaml  Currently it runs in response to any push or pull request. We may eventually switch to a manual trigger to give us more control over validation and iteration.

When the workflows are triggered, it will be logged in the GitHub `Actions` tab. If you click on `Actions` you will see the various workflows on the left hand side.  Click on `Build JSON-LD` to view any runs of this workflow. Your run will be titled by the commit title. If you are unsure if it is *your* build, you can filter by `Actor` on the right hand side of the table.

A green check mark (✅) to the left of your build means your changes passed validation. A red cross (❌) means there were errors.

### I passed validation (✅), what next?

Download Your JSON-LD Output. If you click on the build title, it will bring you to the page for that build. At the bottom are `Artifacts`, or files that were produced by the GitHub Action.  In the build results, click `schema-org-jsonld-outputs` to download the output as a zip file. 

Note: These artifacts are temporary and will expire after 90 days. Be sure to store the files elsewhere for long-term access.

*we need to decide what happens next*

### I failed validation (❌), what next?

Review the build logs. If you click on the build title, it will bring you to the page for that build. At the bottom of a failed GitHub Action are `Annotations`. If you click on the item(s) under annotations, it will bring you to the log of the build. You will be brought to the last error in the log and can scroll to review. You can also expand other sections of the log by clicking on the title of the section (e.g. 'Post Checkout').

The log should include a summary of the erros that looks like this:

```
Errors detected:

When validating remote/Person.csv-metadata.json

ERROR Type: Required in CSV 'file:/work/Person.csv', Row: 3, Column: '4'
ERROR Type: Required in CSV 'file:/work/Person.csv', Row: 3, Column: '5'
```

For example, the above message indicates that the 4th and 5th column of the 3rd row (header == row 1) are invalid because they are required fields, but are empty.

## Hosting and Registering JSON-LD with ODIS

*This is is development, as we may have a single endpoint, the MBO GitHub repo, for all MBO JSON-LD to be crawled by ODIS.*

To make your metadata discoverable by ODIS:

1. **Host the generated JSON-LD** at a stable public URL (e.g., through GitHub Pages).
2. **Register the URL with ODIS** so it can be harvested and indexed.

## 🤬 What could go wrong?


### Required Fields and Validation Rules

Each CSV template has fields marked as **required**, and some fields must also follow **validation rules** (e.g., format restrictions or uniqueness constraints). These ensure your metadata is structured correctly and interoperable with global catalogs like [ODIS](https://catalog.odis.org).

#### Required Fields by CSV Template

Before filling out any table, note that most templates **inherit common required fields**. These include:

**Universal Required Fields**

| Field                        | Meaning                                                                 |
|-----------------------------|-------------------------------------------------------------------------|
| `id`                        | A unique permanent identifier (e.g. `mbo_abc123`)                        |
| `metadataPublisherId`       | The ID of a Person or Organization who is publishing this metadata      |
| `metadataDescribedForActionId` | The ID of an Action that this record is describing (except for `Action.csv` itself) |


> These fields are required in nearly every table. If they are missing or point to invalid IDs, validation will fail.

---

#### 🔎 Additional Required Fields by Table

<details><summary><strong>Action.csv</strong></summary>

- `actionStatus`
- `resultStatus`  
*(Note: `metadataDescribedForActionId` is not required here because this is the root action being described)*

</details>

<details><summary><strong>Audience.csv</strong></summary>

- `audienceType`

</details>

<details><summary><strong>ContactPoint.csv</strong></summary>

- `contactType`

</details>

<details><summary><strong>DataDownload.csv</strong></summary>

- `contentUrl`
- `encodingFormat`

</details>

<details><summary><strong>Dataset.csv</strong></summary>

- `name`
- `description`
- `keywords`

</details>

<details><summary><strong>DatasetComment.csv</strong></summary>

- `text`

</details>

<details><summary><strong>DefinedTerm.csv</strong></summary>

- `name`

</details>

<details><summary><strong>EmbargoStatement.csv</strong></summary>

- `embargoDate`

</details>

<details><summary><strong>GeoShape.csv</strong></summary>

- `containedInPlace`

</details>

<details><summary><strong>HowTo.csv</strong></summary>

- `name`
- `description`

</details>

<details><summary><strong>HowToStep.csv</strong></summary>

- `position`
- `text`

</details>

<details><summary><strong>HowToTip.csv</strong></summary>

- `text`

</details>

<details><summary><strong>License.csv</strong></summary>

- `name`
- `url`

</details>

<details><summary><strong>MonetaryGrant.csv</strong></summary>

- `name`
- `amount`

</details>

<details><summary><strong>Organization.csv</strong></summary>

- `name`

</details>

<details><summary><strong>Person.csv</strong></summary>

- `name`

</details>

<details><summary><strong>Place.csv</strong></summary>

- `name`
- `address`

</details>

<details><summary><strong>PropertyValue.csv</strong></summary>

- `propertyID`
- `value`

</details>

<details><summary><strong>PublishingStatusDefinedTerm.csv</strong></summary>

- `name`

</details>

<details><summary><strong>Service.csv</strong></summary>

- `serviceType`

</details>

<details><summary><strong>SoftwareApplication.csv</strong></summary>

- `name`
- `applicationCategory`

</details>

<details><summary><strong>SoftwareSourceCode.csv</strong></summary>

- `codeRepository`

</details>

<details><summary><strong>Taxon.csv</strong></summary>

- `scientificName`

</details>

> ✅ **Tip:** If any required field is missing, the GitHub Action will fail validation during the `validate-csvws-build-jsonld` step.


---

### 🔍 Validation Rules (SHACL Constraints)

The system also applies additional validation rules using [SHACL](https://www.w3.org/TR/shacl/). These rules ensure the integrity of the metadata graph:

| Rule | Type | Description |
|------|------|-------------|
| **MBO Identifier Must Be Unique** | ❌ Violation | Each `id` (e.g. `mbo_tool_001`) must appear in only one CSV file. It cannot represent multiple entities across files. |
| **Entity Should Be Referenced** | ⚠️ Warning | Any entity you define (e.g. a `Person`, `Place`, or `SoftwareApplication`) should be referenced somewhere else in the metadata (e.g. as a `creator`, `location`, or `usedSoftware`). |

> ⚠️ Warnings won’t stop your JSON-LD from being generated, but violations will.

### Required Table Relationships

Before filling out any MARCO-BOLO CSV tables, it's important to understand how they depend on each other. 

---

### 🧱 Minimum Required Files for a Dataset

To create a valid `Dataset.csv` row, you must also provide records in:

| File                  | Why it's needed                                     |
|-----------------------|-----------------------------------------------------|
| `Dataset.csv`         | The dataset record itself                           |
| `Action.csv`          | To define the `metadataDescribedForActionId` value |
| `Person.csv` **or** `Organization.csv` | To define the `metadataPublisherId` value      |

---

These relationships apply to *every other table* as well. No table stands alone — they all describe a resource that must be attributed (publisher) and scoped (action).

### Required Cross-Table Dependencies

| Table               | Depends on Table     | Field                            | Multivalued   |
|:--------------------|:---------------------|:---------------------------------|:--------------|
| Action              | Action               | metadataDescribedForActionId     | No            |
| Action              | PersonOrOrganization | agentId                          | No            |
| Action              | PersonOrOrganization | metadataPublisherId              | No            |
| Audience            | Action               | metadataDescribedForActionId     | No            |
| Audience            | PersonOrOrganization | metadataPublisherId              | No            |
| ContactPoint        | Action               | metadataDescribedForActionId     | No            |
| ContactPoint        | PersonOrOrganization | metadataPublisherId              | No            |
| DataDownload        | Action               | metadataDescribedForActionId     | No            |
| DataDownload        | Dataset              | datasetMboId                     | No            |
| DataDownload        | PersonOrOrganization | metadataPublisherId              | No            |
| Dataset             | Action               | metadataDescribedForActionId     | No            |
| Dataset             | PersonOrOrganization | metadataPublisherId              | No            |
| Dataset             | PropertyValue        | containsVariablesMboIds          | Yes           |
| DatasetComment      | Action               | metadataDescribedForActionId     | No            |
| DatasetComment      | Dataset              | commentAboutDatasetMboId         | No            |
| DatasetComment      | PersonOrOrganization | metadataPublisherId              | No            |
| DefinedTerm         | Action               | metadataDescribedForActionId     | No            |
| DefinedTerm         | PersonOrOrganization | metadataPublisherId              | No            |
| EmbargoStatement    | Action               | metadataDescribedForActionId     | No            |
| EmbargoStatement    | Dataset              | embargoedDatasetMboId            | No            |
| EmbargoStatement    | PersonOrOrganization | metadataPublisherId              | No            |
| GeoShape            | Action               | metadataDescribedForActionId     | No            |
| GeoShape            | PersonOrOrganization | metadataPublisherId              | No            |
| HowTo               | Action               | metadataDescribedForActionId     | No            |
| HowTo               | HowToStep            | howToStepMboId                   | No            |
| HowTo               | PersonOrOrganization | metadataPublisherId              | No            |
| HowToStep           | Action               | metadataDescribedForActionId     | No            |
| HowToStep           | PersonOrOrganization | metadataPublisherId              | No            |
| HowToTip            | Action               | metadataDescribedForActionId     | No            |
| HowToTip            | PersonOrOrganization | metadataPublisherId              | No            |
| License             | Action               | metadataDescribedForActionId     | No            |
| License             | PersonOrOrganization | metadataPublisherId              | No            |
| MonetaryGrant       | Action               | metadataDescribedForActionId     | No            |
| MonetaryGrant       | PersonOrOrganization | metadataPublisherId              | No            |
| Organization        | Action               | metadataDescribedForActionId     | No            |
| Organization        | PersonOrOrganization | metadataPublisherId              | No            |
| Person              | Action               | metadataDescribedForActionId     | No            |
| Person              | PersonOrOrganization | metadataPublisherId              | No            |
| Place               | Action               | metadataDescribedForActionId     | No            |
| Place               | PersonOrOrganization | metadataPublisherId              | No            |
| PropertyValue       | Action               | metadataDescribedForActionId     | No            |
| PropertyValue       | PersonOrOrganization | metadataPublisherId              | No            |
| Service             | Organization         | serviceProviderOrganizationMboId | No            |
| Service             | PersonOrOrganization | metadataPublisherId              | No            |
| SoftwareApplication | Action               | metadataDescribedForActionId     | No            |
| SoftwareApplication | PersonOrOrganization | metadataPublisherId              | No            |
| SoftwareSourceCode  | Action               | metadataDescribedForActionId     | No            |
| SoftwareSourceCode  | PersonOrOrganization | metadataPublisherId              | No            |
| Taxon               | Action               | metadataDescribedForActionId     | No            |
| Taxon               | PersonOrOrganization | metadataPublisherId              | No            |


#### Optional Cross-Table Dependencies

| Table               | Depends on Table            | Field                         | Multivalued   |
|:--------------------|:----------------------------|:------------------------------|:--------------|
| Action              | Action                      | childActionMboIds             | Yes           |
| Action              | Dataset                     | resultingDatasetMboIds        | Yes           |
| Action              | HowTo                       | howToPerformActionMboId       | No            |
| Action              | PersonOrOrganization        | participantIds                | Yes           |
| DataDownload        | Audience                    | audienceMboIds                | Yes           |
| DataDownload        | License                     | licenseMboId                  | No            |
| DataDownload        | PersonOrOrganization        | authorId                      | No            |
| DataDownload        | PersonOrOrganization        | contributorIds                | Yes           |
| DataDownload        | PersonOrOrganization        | maintainerId                  | No            |
| DataDownload        | PersonOrOrganization        | ownerId                       | No            |
| DataDownload        | PersonOrOrganization        | publisherId                   | No            |
| DataDownload        | PublishingStatusDefinedTerm | publishingStatusMboId         | No            |
| Dataset             | Audience                    | audienceMboIds                | Yes           |
| Dataset             | DataDownload                | dataDownloadMboIds            | Yes           |
| Dataset             | EmbargoStatement            | embargoStatementMboId         | No            |
| Dataset             | License                     | licenseMboId                  | No            |
| Dataset             | PersonOrOrganization        | authorId                      | No            |
| Dataset             | PersonOrOrganization        | contributorIds                | Yes           |
| Dataset             | PersonOrOrganization        | maintainerId                  | No            |
| Dataset             | PersonOrOrganization        | ownerId                       | No            |
| Dataset             | PersonOrOrganization        | publisherId                   | No            |
| Dataset             | Place                       | spatialCoveragePlaceMboId     | No            |
| Dataset             | PublishingStatusDefinedTerm | publishingStatusMboId         | No            |
| Dataset             | Taxon                       | aboutTaxonMboIds              | Yes           |
| DatasetComment      | PersonOrOrganization        | authorId                      | No            |
| HowToStep           | Audience                    | audienceMboIds                | Yes           |
| HowToStep           | HowToStep                   | childStepMboIds               | Yes           |
| HowToStep           | HowToTip                    | howToImplementTipMboIds       | Yes           |
| HowToStep           | PersonOrOrganization        | contributorIds                | Yes           |
| HowToStep           | PersonOrOrganization        | providerId                    | No            |
| HowToStep           | Service                     | citeServiceMboIds             | Yes           |
| HowToStep           | SoftwareApplication         | citeSoftwareApplicationMboIds | Yes           |
| HowToStep           | SoftwareSourceCode          | citeSourceCodeMboIds          | Yes           |
| HowToTip            | Audience                    | audienceMboIds                | Yes           |
| MonetaryGrant       | Organization                | funderOrganizationMboIds      | Yes           |
| MonetaryGrant       | Organization                | sponsorOrganizationMboIds     | Yes           |
| Organization        | ContactPoint                | contactPointMboIds            | Yes           |
| Organization        | MonetaryGrant               | fundingGrantMboIds            | Yes           |
| Organization        | Organization                | departmentMboIds              | Yes           |
| Organization        | Organization                | memberOfOrganizationMboIds    | Yes           |
| Organization        | Organization                | parentOrganizationMboId       | No            |
| Person              | ContactPoint                | contactPointMboIds            | Yes           |
| Person              | Organization                | affiliatedOrganizationMboIds  | Yes           |
| Person              | Organization                | worksForOrganizationMboIds    | Yes           |
| Place               | GeoShape                    | geoShapeMboId                 | No            |
| PropertyValue       | PropertyValue               | isTypeOfPropertyValueMboId    | Yes           |
| Service             | Audience                    | audienceMboIds                | Yes           |
| Service             | Place                       | placesServedMboIds            | Yes           |
| SoftwareApplication | PersonOrOrganization        | authorId                      | No            |
| SoftwareApplication | PersonOrOrganization        | contributorIds                | Yes           |
| SoftwareApplication | PersonOrOrganization        | maintainerId                  | No            |
| SoftwareApplication | PersonOrOrganization        | ownerId                       | No            |
| SoftwareApplication | PersonOrOrganization        | providerId                    | No            |
| SoftwareApplication | PersonOrOrganization        | publisherId                   | No            |
| SoftwareApplication | PublishingStatusDefinedTerm | publishingStatusMboId         | No            |
| SoftwareSourceCode  | PersonOrOrganization        | authorId                      | No            |
| SoftwareSourceCode  | PersonOrOrganization        | contributorIds                | Yes           |
| SoftwareSourceCode  | PersonOrOrganization        | maintainerId                  | No            |
| SoftwareSourceCode  | PersonOrOrganization        | ownerId                       | No            |
| SoftwareSourceCode  | PersonOrOrganization        | publisherId                   | No            |
| SoftwareSourceCode  | PublishingStatusDefinedTerm | publishingStatusMboId         | No            |
