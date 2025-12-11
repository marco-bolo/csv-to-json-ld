# Instrument and Platform Classes for MARCO-BOLO LinkML Model

## Summary

This document proposes additions to your LinkML model to support scientific instruments (sensors) and the platforms they are mounted on, following ODIS schema.org patterns.

## Design Decisions

### 1. Instrument Class (`schema:Thing`)

Following ODIS guidance from the Vessels documentation:

> *"One could also build off the base Thing class, parent to all Schema.org types, then leverage the property schema.org/instrument, itself of type Thing."*

We use `schema:Thing` as the base class for instruments because:
- There is no specific `schema:Instrument` type in schema.org
- `schema:Thing` is the type expected by the `schema:instrument` property
- It provides all necessary base properties (name, description, identifier, url, etc.)

### 2. Platform Class (`schema:Vehicle`)

Following ODIS Vessels pattern:

> *"In Schema.org the type Vehicle is described as a device that is designed or used to transport people or cargo over land, water, air, or through space. We have used this broad scoping to cover research vessels."*

This covers:
- Research vessels
- Autonomous underwater vehicles (AUVs)
- Gliders
- Moorings and buoys (stationary "transport" of sensors through the water column)
- Fixed stations

### 3. Advertising "Sensor" as Synonym

Your requirement: *"some scientists call these sensors rather than instruments"*

**Solution**: Use `alternateName` slot

```yaml
alternateName:
  title: "Alternate Name"
  description: "An alternative name."
  range: string
  slot_uri: schema:alternateName
```

Example usage:
```
name: "SBE 911plus CTD #1234"
alternateName: "sensor|CTD sensor|profiling sensor"
```

This allows discovery by either "instrument" or "sensor" terminology.

### 4. Vocabulary References

| Entity | Your Field | Vocabulary | NERC Collection |
|--------|------------|------------|-----------------|
| Instrument | `instrumentTypeId` | SeaVoX Device Catalogue | [L22](https://vocab.nerc.ac.uk/collection/L22/current/) |
| Instrument | (category) | Device Categories | [L05](https://vocab.nerc.ac.uk/collection/L05/current/) |
| Platform | `platformTypeId` | Platform Categories | [L06](https://vocab.nerc.ac.uk/collection/L06/current/) |
| Platform | (instances) | ICES Platform Codes | [C17](https://vocab.nerc.ac.uk/collection/C17/current/) |

### 5. Linking to HowToSteps

Add `instrumentMboIds` slot to `HowToStep` class:

```yaml
instrumentMboIds:
  title: "Instruments Used (mPIDs)"
  slot_uri: schema:instrument
  range: Instrument
  multivalued: true
```

This follows the schema.org definition: *"The object that helped the agent perform the action."*

## Field Mapping

### Your Requirements → Proposed Slots

| Your Requirement | Slot Name | Schema.org Property | Notes |
|------------------|-----------|---------------------|-------|
| Instrument (local) name | `name` | `schema:name` | Required |
| "Sensor" synonym | `alternateName` | `schema:alternateName` | Pipe-delimited |
| Instrument (local) ID | `identifiers` | `schema:identifier` | Existing slot |
| Instrument type vocab | `instrumentTypeId` | `schema:additionalType` | NERC L22 URI |
| Instrument type name | `instrumentTypeName` | `schema:category` | Human-readable |
| Platform (local) name | `name` | `schema:name` | On Platform class |
| Platform (local) ID | `identifiers` | `schema:identifier` | IMO, MMSI, etc. |
| Platform type vocab | `platformTypeId` | `schema:additionalType` | NERC L06 URI |

## CSV Structure

### Instrument.csv

| Column | Required | Description |
|--------|----------|-------------|
| `id` | ✓ | MBO permanent identifier (e.g., `mbo_inst_001`) |
| `metadataPublisherId` | ✓ | Who entered this row |
| `metadataDescribedForActionId` | ✓ | Which Action this relates to |
| `name` | ✓ | Local instrument name |
| `alternateName` | | Alternative names including "sensor" |
| `description` | | Extended description |
| `identifiers` | | Local IDs, serial numbers |
| `instrumentTypeId` | | NERC L22 URI |
| `instrumentTypeName` | | Human-readable type |
| `instrumentManufacturer` | | Manufacturer name |
| `instrumentModel` | | Model designation |
| `instrumentSerialNumber` | | Serial number |
| `mountedOnPlatformMboId` | | Reference to Platform |
| `ownerId` | | Owner organization/person |
| `maintainerId` | | Maintainer organization/person |
| `url` | | Instrument info page |
| `subjectOfDocumentMboIds` | | Detailed metadata documents (pipe-delimited) |
| `keywords` | | Pipe-delimited keywords |

### Platform.csv

| Column | Required | Description |
|--------|----------|-------------|
| `id` | ✓ | MBO permanent identifier |
| `metadataPublisherId` | ✓ | Who entered this row |
| `metadataDescribedForActionId` | ✓ | Which Action this relates to |
| `name` | ✓ | Platform name (e.g., "RV Ocean Explorer") |
| `alternateName` | | Alternative names |
| `description` | | Extended description |
| `identifiers` | | IMO, MMSI, Call Sign, etc. (pipe-delimited) |
| `platformTypeId` | | NERC L06 URI |
| `platformTypeName` | | Human-readable type |
| `platformIdentifierType` | | Type of primary ID (IMO, MMSI, etc.) |
| `operatorOrganizationMboId` | | Operating organization |
| `ownerId` | | Owner organization |
| `url` | | Platform info page |
| `subjectOfDocumentMboIds` | | Detailed metadata documents (pipe-delimited) |
| `keywords` | | Pipe-delimited keywords |

## Example Records

### Instrument Example

```
id: mbo_inst_001
metadataPublisherId: mbo_person_001
metadataDescribedForActionId: mbo_action_001
name: SBE 911plus CTD System A
alternateName: sensor|CTD sensor|primary CTD
description: Sea-Bird SBE 911plus CTD system for full water column profiling
identifiers: LOCAL-CTD-001
instrumentTypeId: http://vocab.nerc.ac.uk/collection/L22/current/TOOL0058/
instrumentTypeName: CTD
instrumentManufacturer: Sea-Bird Scientific
instrumentModel: SBE 911plus
instrumentSerialNumber: 4567
mountedOnPlatformMboId: mbo_plat_001
ownerId: mbo_org_001
maintainerId: mbo_org_002
url: https://example.org/instruments/ctd-system-a
keywords: CTD|conductivity|temperature|depth|oceanography
```

### Platform Example

```
id: mbo_plat_001
metadataPublisherId: mbo_person_001
metadataDescribedForActionId: mbo_action_001
name: RV Ocean Explorer
description: Multi-purpose research vessel for oceanographic surveys
identifiers: IMO9876543|MMSI123456789|ICES-OEX
platformTypeId: http://vocab.nerc.ac.uk/collection/L06/current/31/
platformTypeName: research vessel
platformIdentifierType: IMO
operatorOrganizationMboId: mbo_org_001
ownerId: mbo_org_001
url: https://example.org/vessels/ocean-explorer
keywords: vessel|research|oceanography
```

## Integration with HowToStep

After adding `instrumentMboIds` to the HowToStep class, you can reference instruments in your methodology:

```
# In HowToStep.csv
id: mbo_step_001
name: CTD Water Column Profile
instrumentMboIds: mbo_inst_001|mbo_inst_002
...
```

This generates the triple:
```turtle
<mbo_step_001> schema:instrument <mbo_inst_001>, <mbo_inst_002> .
```

## JSON-LD Output Example

The resulting JSON-LD for an instrument would look like:

```json
{
  "@context": {
    "@vocab": "https://schema.org/"
  },
  "@id": "https://w3id.org/marco-bolo/mbo_inst_001",
  "@type": "Thing",
  "name": "SBE 911plus CTD System A",
  "alternateName": ["sensor", "CTD sensor", "primary CTD"],
  "description": "Sea-Bird SBE 911plus CTD system for full water column profiling",
  "identifier": "LOCAL-CTD-001",
  "additionalType": "http://vocab.nerc.ac.uk/collection/L22/current/TOOL0058/",
  "category": "CTD",
  "manufacturer": "Sea-Bird Scientific",
  "model": "SBE 911plus",
  "serialNumber": "4567",
  "isPartOf": {
    "@id": "https://w3id.org/marco-bolo/mbo_plat_001",
    "@type": "Vehicle"
  },
  "keywords": ["CTD", "conductivity", "temperature", "depth", "oceanography"]
}
```

## References

- [ODIS Vessels Pattern](https://book.odis.org/thematics/vessels/index.html)
- [ODIS EOV Pattern (Instruments)](https://book.odis.org/thematics/variables/index.html)
- [NERC L22 SeaVoX Device Catalogue](https://vocab.nerc.ac.uk/collection/L22/current/)
- [NERC L06 Platform Categories](https://vocab.nerc.ac.uk/collection/L06/current/)
- [NERC L05 Device Categories](https://vocab.nerc.ac.uk/collection/L05/current/)
- [schema.org/instrument property](https://schema.org/instrument)
- [schema.org/Vehicle type](https://schema.org/Vehicle)