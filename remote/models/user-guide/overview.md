# MARCO-BOLO CSV-to-JSON-LD Overview

## What is this tool?

This is a metadata publishing tool developed for **Work Package 1 (WP1)** of the [MARCO-BOLO project](https://marcobolo-project.eu/) (MARine COastal BiOdiversity Long-term Observations). The tool helps researchers transform marine biodiversity metadata into machine-readable formats that can be discovered and reused by global research catalogs.

This system demonstrates that comprehensive metadata doesn't require expensive infrastructure - it uses standard tools and automated processing to produce publication-ready, semantically rich outputs that are easily shared across the internet.

## Why does this exist?

The MARCO-BOLO project aims to align with IOC Data Architecture and will ensure research outputs are discoverable through the [ODIS Catalogue](https://catalogue.odis.org/search) (note that this is still being developed). Rather than requiring researchers to learn complex semantic web technologies, this tool provides:

- **User-friendly data entry** through Google Sheets
- **Automated validation** to catch errors early  
- **Rich semantic metadata** that exceeds typical project standards
- **Resource-efficient approach** using minimal infrastructure
- **Standards compliance** with Schema.org and JSON-LD

## How it works (simplified)

1. **Researchers enter data** into structured Google Sheets with built-in validation
2. **Semi-Automated systems** sync the data and validate it against schemas
3. **Processing pipeline** converts data to semantic web formats (JSON-LD)
4. **Published metadata** becomes discoverable by research catalogs worldwide (e.g. ODIS)

## Key Benefits

- **Lean approach**: Minimal resources, maximum metadata quality
- **Familiar tools**: Google Sheets interface with enhanced validation
- **Automatic processing**: No manual format conversion needed
- **Standards compliant**: Meets international semantic web standards
- **Collaborative**: Multiple researchers can contribute simultaneously

## Getting Started

New users should begin with the [Data Entry Guide](data-entry-guide.md) for step-by-step instructions on contributing data to the project.

Technical users interested in the system architecture can review the [Technical Architecture](technical-architecture.md) documentation.
