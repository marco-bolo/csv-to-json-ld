# The published JSON-LD

What a consumer of <https://lab.marcobolo-project.eu/csv-to-json-ld/schema-jsonld/>
receives, and what it may rely on.

## One document per entity

Every MBO Permanent Identifier (mPID) gets exactly one document, named after it:

```
mbo_1dfce83b-b558-4c42-9c70-b0e06e008cc0.json
```

The entity is the root of its document. The metadata about the spreadsheet row
that produced it - who entered it, when, from which CSV - is nested inside it
under `schema:subjectOf`:

```json
{
  "@context": { ... },
  "@id": "https://w3id.org/marco-bolo/mbo_1dfce83b-b558-4c42-9c70-b0e06e008cc0",
  "@type": "ContactPoint",
  "contactType": "Task 3.3 Contact",
  "name": "Lili Hufnagel",
  "email": "lili.hufnagel@ufz.de",
  "subjectOf": {
    "@id": "https://w3id.org/marco-bolo/mbo_1dfce83b-...-input-metadata",
    "@type": ["Dataset", "InputMetadataDescription"],
    "about": { "@id": "https://w3id.org/marco-bolo/mbo_1dfce83b-..." },
    "creator": { "@id": "https://w3id.org/marco-bolo/mbo_bf08f5c2-..." },
    "archivedAt": "https://github.com/marco-bolo/csv-to-json-ld/tree/<commit>",
    "distribution": [ ... ]
  }
}
```

The nested record carries `mbo:InputMetadataDescription` alongside
`schema:Dataset`. That type is how you tell a provenance record apart from a
research dataset - filter it out if you only want the science.

Its two `schema:distribution` entries describe where the entity came from and
where it now lives:

| `@id` suffix | `contentUrl` points at | `encodingFormat` |
|---|---|---|
| `#csv` | the source spreadsheet row | `text/csv` |
| `#jsonld` | this document | `application/ld+json` |

## The `@context` is self-contained

Every document carries its full context inline. No network fetch is required to
read one, and no remote document can change what a published document means.

It is `@vocab`-based (`https://schema.org/`), so most properties are exactly
their schema.org names. It declares two MBO vocabulary terms
(`InputMetadataDescription`, `inProgressDate`) and coerces seven properties to
`@id`:

```
archivedAt   contentUrl   inDefinedTermSet   isBasedOn
isPartOf     license      usageInfo
```

The source of truth is [`remote/mbo-context.json`](../remote/mbo-context.json),
which is used both to compact the output and as the context published inside it.
Those two must stay identical: if they diverge, values silently change shape.

See issue #316 for why this is inline rather than hosted at a URL.

## Links versus strings

A value written `{"@id": "..."}` is a **reference to a thing**. A value written
`{"@value": "..."}` is **data**. This matters: a string is not followable and
will not join to anything in a triplestore.

The distinction is not always visible in the JSON. A property coerced to `@id`
in the context appears as a bare string but is still a link:

```json
"contentUrl": "https://w3id.org/marco-bolo/mbo_0000006#row=34"
```

To be certain, expand the document with a JSON-LD processor rather than reading
the JSON. Anything appearing as `{"@type": "URL", "@value": "..."}` is a string
literal, and is a bug - see issue #313.

## What is not in a document

**Inbound links.** A document contains only triples whose subject is the entity
itself. If a Person references a ContactPoint, that statement lives in the
*Person's* document; the ContactPoint's document has no way to point back.

So a single document does not tell you what refers to an entity. To answer that,
load the corpus into a graph and query it.

## Regeneration

Documents are rebuilt by
[`build-jsonld.yaml`](../.github/workflows/build-jsonld.yaml) and committed to
[`remote/models/schema-jsonld/`](../remote/models/schema-jsonld/).

Two fields change on every build regardless of whether the data changed:
`archivedAt` (the commit being built) and `dateModified` (the build date, UTC).
