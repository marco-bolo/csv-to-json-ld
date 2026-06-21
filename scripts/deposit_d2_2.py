#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D2.2 to Zenodo.

Same shape as deposit_d1_2.py — see that script's docstring for full usage.

Quick usage:
    python deposit_d2_2.py --pdf ~/Downloads/MBO_D2.2_Jan-2026.pdf
    python deposit_d2_2.py --pdf ~/Downloads/MBO_D2.2_Jan-2026.pdf --draft

Reads token from ZENODO_TOKEN env var or ~/.zenodo_token.
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

# ===========================================================================
# Metadata — edit here before running if any value needs to change.
# ===========================================================================
METADATA = {
    "title": "Datasets, databases and softwares/pipelines facilitating the implementation of eDNA-based monitoring",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2026-01-15",
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    # 17 creators in PDF order. Jennifer Beatty has no ORCID on file — omitted
    # for that entry rather than sent as empty string.
    "creators": [
        {"name": "Jensen, Mads Reinholdt",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0001-8240-1083"},
        {"name": "Præbel, Kim",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0002-0681-1854"},
        {"name": "Ciarlini Junger, Pedro",
         "affiliation": "CNRS-IBENS",
         "orcid": "0000-0001-8774-0738"},
        {"name": "Bowler, Chris",
         "affiliation": "CNRS-IBENS",
         "orcid": "0000-0003-3835-6187"},
        {"name": "Warwick-Dugdale, Joanna",
         "affiliation": "Marine Biological Association",
         "orcid": "0000-0001-5242-6706"},
        {"name": "Cunliffe, Michael",
         "affiliation": "Marine Biological Association",
         "orcid": "0000-0002-6716-3555"},
        {"name": "Beatty, Jennifer",
         "affiliation": "Sorbonne Université"},
        {"name": "Not, Fabrice",
         "affiliation": "Sorbonne Université",
         "orcid": "0000-0002-9342-195X"},
        {"name": "Onoufriou, Aubrie",
         "affiliation": "Marine Directorate, Scottish Government",
         "orcid": "0000-0002-4605-1896"},
        {"name": "Matejusová, Iveta",
         "affiliation": "Marine Directorate, Scottish Government",
         "orcid": "0000-0002-3241-043X"},
        {"name": "Bellardini, Daniele",
         "affiliation": "Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0002-3319-7036"},
        {"name": "D'Alelio, Domenico",
         "affiliation": "Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0002-2189-503X"},
        {"name": "Formel, Stephen",
         "affiliation": "UNESCO-OBIS",
         "orcid": "0000-0001-7418-1244"},
        {"name": "Suominen, Saara",
         "affiliation": "UNESCO-OBIS",
         "orcid": "0000-0001-9401-8460"},
        {"name": "Boulanger, Emilie",
         "affiliation": "UNESCO-OBIS",
         "orcid": "0000-0002-6446-7342"},
        {"name": "Heynderickx, Hanneloor",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0002-5611-837X"},
        {"name": "Kumazawa Morais, Daniel",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0003-3328-7848"},
    ],
    "description": (
        # MBO Zenodo boilerplate block
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D2.2<br>"
        "Work Package Number: WP2<br>"
        "Deliverable Title: Datasets, databases and softwares/pipelines facilitating the implementation of eDNA-based monitoring<br>"
        "Due Date: 30.11.2025<br>"
        "Submission Date: 15.01.2026</p>"
        # Executive Summary, verbatim, broken into paragraphs for readability
        "<p>Work package 2 (WP2) of the MARCO-BOLO project focused on validating and enabling "
        "environmental DNA (eDNA)-based approaches for biodiversity monitoring in aquatic and "
        "terrestrial systems. In task 2.2, these objectives were addressed through the exploration "
        "and comparison of datasets, databases, software, and bioinformatic pipelines to facilitate "
        "the implementation of eDNA-based monitoring.</p>"

        "<p>While this task was initially envisioned to build on existing infrastructure (specific "
        "pipelines, datasets, and customized databases), the departure of the creator of these "
        "preexisting tools, who was involved in the initial application, led to a shift in focus. "
        "This deliverable was likely originally intended to result in a single, standardized approach "
        "to working with eDNA-derived biomonitoring data. However, we collectively concluded that no "
        "single database, software, or pipeline can address the diverse practical use cases within "
        "eDNA. Therefore, this report provides a broader context on existing approaches, databases, "
        "and pipelines, their applications, and how they compare.</p>"

        "<p>The main body of work carried out under this task was a comparison of bioinformatic "
        "pipelines for two types of metabarcoding data (eukaryote 18S and 12S, 16S and COI for "
        "fishes), where we invited people around the world to contribute results from running their "
        "respective pipelines on the same datasets (Dataset 1). We also generated eDNA metabarcoding "
        "data for time series samples collected by institutions involved in this task. The statuses "
        "of Datasets 2-7, where new data was generated, are presented here, each accompanied by a "
        "&ldquo;readme&rdquo; in varying formats. These data products will contribute to deliverables "
        "D2.3 and D2.4 but are presented here alongside their metadata.</p>"

        "<p>As this is a data deliverable rather than a narrative report, we focused on implementing "
        "WP1&rsquo;s data model for reporting on data and metadata. While this model is not yet "
        "finalized, we here use Dataset 2 to demonstrate its potential, transforming information "
        "from Google Sheets into JSON format and generating standardized readme files using a large "
        "language model (LLM). Currently, each dataset has its own readme format, but will be "
        "standardized under WP1&rsquo;s model during the project&rsquo;s final year.</p>"

        "<p>Dataset 8-9 are based on data generated prior to MARCO-BOLO and here primarily serve to "
        "indicate the locations of all utilized data products, as results from these are presented "
        "under D2.3 and D2.4. Under this task, we also engaged with the existing literature and here "
        "provide a comprehensive overview of what we consider to be widely used primer sets for eDNA "
        "metabarcoding, pipelines run for different marker genes, and reference databases used to "
        "assign taxonomy (Dataset 10). This work complements the data analysis challenge, where we "
        "aimed to include as many pipelines as possible, and is here presented as a standalone data "
        "product.</p>"

        "<p>Finally, we showcase two custom-built reference databases tailored for Nordic eDNA "
        "metabarcoding applications (Dataset 11), targeting the &ldquo;Leray&rdquo; fragment (COI) "
        "and the &ldquo;MiFish&rdquo; fragment (12S rRNA). These databases integrate and harmonize "
        "data from multiple repositories while incorporating rigorous curation steps to ensure "
        "high-quality references for eDNA research. They remain a work in progress, with ongoing "
        "efforts to refine and expand their scope to support diverse research applications.</p>"
    ),
    "keywords": [
        "MBO WP2", "eDNA", "environmental DNA", "metabarcoding",
        "biodiversity monitoring", "bioinformatic pipelines",
        "reference databases", "18S rRNA", "12S MiFish", "COI Leray-XT", "ddPCR",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    # Related identifiers explicitly named in the deliverable body
    "related_identifiers": [
        # Dataset 1 = MARCO-BOLO Data Analysis Challenge (already a Zenodo record)
        {"identifier": "10.5281/zenodo.17739996",
         "relation": "references",
         "scheme": "doi"},
        # D7.2 Project Data Management Plan (cited in Dataset 2 section)
        {"identifier": "10.5281/zenodo.8208410",
         "relation": "references",
         "scheme": "doi"},
    ],
    # Structured dates — surface what's also written in the abstract boilerplate
    "dates": [
        {"start": "2026-01-15", "type": "Submitted",
         "description": "Submission date"},
        {"start": "2025-11-30", "type": "Other",
         "description": "Due date"},
    ],
}

# ===========================================================================
# HTTP plumbing (identical to deposit_d1_2.py)
# ===========================================================================
def make_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()

def load_token():
    tok = os.environ.get("ZENODO_TOKEN")
    if tok:
        return tok.strip()
    tok_file = Path.home() / ".zenodo_token"
    if tok_file.exists():
        return tok_file.read_text().strip()
    print("ERROR: no Zenodo token found.\n"
          "  Either: export ZENODO_TOKEN=your_token\n"
          "  Or:     echo 'your_token' > ~/.zenodo_token && chmod 600 ~/.zenodo_token\n"
          "  Create one at https://zenodo.org/account/settings/applications/tokens/new/\n"
          "  Scopes needed: deposit:write, deposit:actions",
          file=sys.stderr)
    sys.exit(1)

def request(method, url, token, ctx, json_body=None, raw_body=None,
            content_type=None):
    headers = {"Authorization": f"Bearer {token}"}
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif raw_body is not None:
        data = raw_body
        if content_type:
            headers["Content-Type"] = content_type
    else:
        data = None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
            body = r.read().decode("utf-8") if r.length != 0 else ""
            return r.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"\nHTTP {e.code} {e.reason} on {method} {url}", file=sys.stderr)
        print(f"Response body:\n{err_body}", file=sys.stderr)
        sys.exit(2)
    except ssl.SSLCertVerificationError:
        print("\nSSL cert verification failed.\n"
              "  Fix: /Applications/Python\\ 3.13/Install\\ Certificates.command\n"
              "  Or:  pip install certifi", file=sys.stderr)
        sys.exit(3)

# ===========================================================================
# Main flow
# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, help="Path to the PDF to deposit")
    ap.add_argument("--draft", action="store_true",
                    help="Create the deposit but do NOT publish")
    ap.add_argument("--yes", action="store_true",
                    help="Publish without confirmation prompt")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        print(f"ERROR: file not found: {pdf}", file=sys.stderr); sys.exit(1)

    token = load_token()
    ctx = make_ssl_context()
    base = "https://zenodo.org"
    print(f"Target: LIVE ({base})")
    print(f"File:   {pdf}  ({pdf.stat().st_size:,} bytes)")
    print(f"Title:  {METADATA['title']}")
    print(f"Authors: {len(METADATA['creators'])}\n")

    # 1) Create empty deposit
    print("Step 1/4: creating draft deposit ...")
    status, dep = request("POST", f"{base}/api/deposit/depositions", token, ctx,
                          json_body={})
    deposit_id = dep["id"]
    bucket_url = dep["links"]["bucket"]
    html_url = dep["links"].get("html") or f"{base}/deposit/{deposit_id}"
    print(f"  deposit id: {deposit_id}")
    print(f"  review URL: {html_url}")

    # 2) Upload the file via bucket
    print(f"\nStep 2/4: uploading {pdf.name} ...")
    with open(pdf, "rb") as fh:
        body = fh.read()
    status, fileinfo = request("PUT", f"{bucket_url}/{pdf.name}", token, ctx,
                               raw_body=body,
                               content_type="application/octet-stream")
    print(f"  uploaded ({fileinfo.get('size','?')} bytes, "
          f"checksum {fileinfo.get('checksum','?')})")

    # 3) Set metadata
    print("\nStep 3/4: setting metadata ...")
    status, dep = request("PUT", f"{base}/api/deposit/depositions/{deposit_id}",
                          token, ctx, json_body={"metadata": METADATA})
    print(f"  metadata saved. Reserved DOI: {dep['metadata'].get('prereserve_doi',{}).get('doi','(not shown)')}")

    # 4) Publish (or stop here)
    if args.draft:
        print(f"\nStep 4/4: SKIPPED (--draft set). Review and publish at:\n  {html_url}")
        return
    if not args.yes:
        print(f"\nReview the draft here before publishing:\n  {html_url}")
        ans = input(f"\nPublish now to LIVE? This generates a permanent DOI. [y/N]: ")
        if ans.strip().lower() not in ("y", "yes"):
            print(f"Not publishing. Draft saved — review and publish at:\n  {html_url}")
            return

    print("\nStep 4/4: publishing ...")
    status, dep = request("POST",
                          f"{base}/api/deposit/depositions/{deposit_id}/actions/publish",
                          token, ctx)
    final_doi = dep.get("doi") or dep["metadata"].get("doi")
    final_url = dep["links"].get("record_html") or dep["links"].get("html")
    print("\n✓ Published.")
    print(f"  DOI:    {final_doi}")
    print(f"  URL:    {final_url}")
    print(f"  Concept DOI (version-independent): {dep.get('conceptdoi','-')}")

if __name__ == "__main__":
    main()
