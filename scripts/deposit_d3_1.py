#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D3.1 (V3.0) to Zenodo.

Usage:
    python deposit_d3_1.py --pdf ~/Downloads/MBO_Deliverable3.1_V3.0.pdf
    python deposit_d3_1.py --pdf ... --draft
    python deposit_d3_1.py --pdf ... --yes
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

METADATA = {
    "title": "Assessment and analysis of current marine, coastal, freshwater and terrestrial biodiversity observation variables, methods/protocols and tools",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-04-01",   # V3.0 date
    "version": "3.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    "creators": [
        {"name": "Caruso, Valerio",
         "affiliation": "CNR",
         "orcid": "0009-0000-8394-0142"},
        {"name": "Bergami, Caterina",
         "affiliation": "CNR",
         "orcid": "0000-0002-5284-1317"},
        {"name": "Pugnetti, Alessandra",
         "affiliation": "CNR",
         "orcid": "0000-0002-7346-6675"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D3.1<br>"
        "Work Package Number: WP3<br>"
        "Deliverable Title: Assessment and analysis of current marine, coastal, freshwater "
        "and terrestrial biodiversity observation variables, methods/protocols and tools<br>"
        "Due Date: 31.05.2024<br>"
        "Submission Date: 19.06.2024 (V1.0); revised 02.12.2024 (V2.0); current 01.04.2025 (V3.0)"
        "</p>"

        "<p>The primary aim of this deliverable is to gather comprehensive information on the "
        "key methodologies and protocols used for biodiversity monitoring across Europe. The "
        "key steps of the deliverable are: (1) outline the process for systematically "
        "gathering and analyzing information from various resources to ensure comprehensive "
        "information retrieval; (2) provide an overview of the collected information, "
        "including biodiversity monitoring variables, methods, protocols, and tools across "
        "different countries and ecosystems; and (3) identify commonalities and gaps and use "
        "this analysis to recommend actions for aligning and harmonizing land&ndash;sea "
        "biodiversity monitoring efforts.</p>"

        "<p>By leveraging the collective expertise of all partners, a comprehensive set of "
        "resources was selected, including European legislations (Habitats and Birds "
        "Directives, Water Framework Directive, Marine Strategy Framework Directive) as well "
        "as ESFRI Research Infrastructures and other global and international initiatives.</p>"

        "<p>The study identifies macro-regions and countries that are the most frequently "
        "monitored. Abundance, species composition, and biomass are commonly observed "
        "variables. Monitoring methods are better shared within marine ecosystems under the "
        "MSFD. The diversity in method descriptions across countries and ecosystems poses "
        "challenges for direct comparisons, highlighting the need for standardised protocols. "
        "Biodiversity tools are dispersed across various sources, with genetic data analysis "
        "tools prevalent but image analysis and sampling support tools underrepresented. "
        "Non-EU countries struggle to align with EU frameworks, resulting in incomplete "
        "information. Citizen science initiatives, while valuable for expanding monitoring "
        "coverage, often lack detailed methodological integration, reducing reliability.</p>"

        "<p>This study offers a valid approach to assess the status of biodiversity monitoring "
        "methods across the land&ndash;sea continuum in Europe. Recommendations for improving "
        "biodiversity monitoring in Europe are structured around three pillars:</p>"
        "<ul>"
        "<li><strong>Information Systems and Access</strong> &mdash; Information convergence "
        "(WISE-Marine serves as a model for MSFD monitoring; similar portals for other domains "
        "could be beneficial; a centralised portal for biodiversity-analysis tools would be a "
        "valuable resource) and improved accessibility for researchers, policymakers, and "
        "the public.</li>"
        "<li><strong>Standardization and Harmonization</strong> &mdash; Semantic harmonisation "
        "via standardized semantic labels (controlled vocabularies and thesauri) and methods "
        "harmonisation (e.g., the Ocean Best Practices System for the marine realm), with "
        "standardized metadata describing protocols.</li>"
        "<li><strong>Collaboration and Sharing</strong> &mdash; promoting collaboration among "
        "monitoring networks, research institutions, and governmental bodies to share best "
        "practices, methodologies, and resources.</li>"
        "</ul>"
    ),
    "keywords": [
        "MBO WP3", "biodiversity monitoring", "monitoring protocols",
        "land-sea continuum", "WFD/MSFD",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    "related_identifiers": [],   # First WP3 deliverable; no priors
    "dates": [
        {"start": "2024-06-19", "type": "Submitted",
         "description": "Original submission (V1.0)"},
        {"start": "2024-12-02", "type": "Updated",
         "description": "Revision to V2.0"},
        {"start": "2025-04-01", "type": "Updated",
         "description": "Revision to V3.0 (current)"},
        {"start": "2024-05-31", "type": "Other",
         "description": "Due date"},
    ],
}

# ---------------------------------------------------------------------------
# HTTP plumbing
# ---------------------------------------------------------------------------
def make_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()

def load_token():
    tok = os.environ.get("ZENODO_TOKEN")
    if tok: return tok.strip()
    tok_file = Path.home() / ".zenodo_token"
    if tok_file.exists():
        return tok_file.read_text().strip()
    print("ERROR: no Zenodo token (ZENODO_TOKEN env or ~/.zenodo_token).",
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
        if content_type: headers["Content-Type"] = content_type
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        print(f"ERROR: file not found: {pdf}", file=sys.stderr); sys.exit(1)

    token = load_token()
    ctx = make_ssl_context()
    base = "https://zenodo.org"
    print(f"Target: LIVE ({base})")
    print(f"File:   {pdf}  ({pdf.stat().st_size:,} bytes)")
    print(f"Title:  {METADATA['title'][:80]}...")
    print(f"Authors: {len(METADATA['creators'])}\n")

    print("Step 1/4: creating draft deposit ...")
    status, dep = request("POST", f"{base}/api/deposit/depositions", token, ctx,
                          json_body={})
    deposit_id = dep["id"]
    bucket_url = dep["links"]["bucket"]
    html_url = dep["links"].get("html") or f"{base}/deposit/{deposit_id}"
    print(f"  deposit id: {deposit_id}\n  review URL: {html_url}")

    print(f"\nStep 2/4: uploading {pdf.name} ...")
    with open(pdf, "rb") as fh: body = fh.read()
    status, fileinfo = request("PUT", f"{bucket_url}/{pdf.name}", token, ctx,
                               raw_body=body,
                               content_type="application/octet-stream")
    print(f"  uploaded ({fileinfo.get('size','?')} bytes)")

    print("\nStep 3/4: setting metadata ...")
    status, dep = request("PUT", f"{base}/api/deposit/depositions/{deposit_id}",
                          token, ctx, json_body={"metadata": METADATA})
    print(f"  metadata saved. Reserved DOI: "
          f"{dep['metadata'].get('prereserve_doi',{}).get('doi','(unknown)')}")

    if args.draft:
        print(f"\nStep 4/4: SKIPPED (--draft). Review/publish at:\n  {html_url}")
        return
    if not args.yes:
        print(f"\nReview the draft here before publishing:\n  {html_url}")
        ans = input("\nPublish now to LIVE? Permanent DOI. [y/N]: ")
        if ans.strip().lower() not in ("y", "yes"):
            print(f"Not publishing. Draft saved at:\n  {html_url}")
            return

    print("\nStep 4/4: publishing ...")
    status, dep = request(
        "POST", f"{base}/api/deposit/depositions/{deposit_id}/actions/publish",
        token, ctx)
    final_doi = dep.get("doi") or dep["metadata"].get("doi")
    final_url = dep["links"].get("record_html") or dep["links"].get("html")
    print("\n✓ Published.")
    print(f"  DOI:    {final_doi}")
    print(f"  URL:    {final_url}")
    print(f"\nNext: run deposit_d3_4.py with --d31-doi {final_doi}")

if __name__ == "__main__":
    main()
