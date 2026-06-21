#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D3.2 (Version draft 2) to Zenodo.

NOTE: The PDF is explicitly labelled "Version draft 2" with incomplete
author attribution (only Muresan Mihaela named on cover/doc-info). Per your
direction the deposit lists Muresan Mihaela as the only creator and the
draft status is noted in the description. A subsequent finalized version
will need to be deposited as a new version of this record.

Usage:
    python deposit_d3_2.py --pdf ~/Downloads/MBO_D3.2_Jan-2026.pdf
    python deposit_d3_2.py --pdf ... --draft
    python deposit_d3_2.py --pdf ... --yes
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

# Cover & doc-info both use the typo'd "MFSD" (should be MSFD). Preserved
# verbatim so the deposit metadata matches the PDF; flagged for PM feedback.
METADATA = {
    "title": "Report on testing workflows generating biodiversity and environmental variables and uptake of new data into WFD, MFSD, and EV systems",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-11-11",   # Date of delivery on cover
    "version": "draft 2",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    # Per your direction: single author. Final version will list full WP3 team.
    "creators": [
        {"name": "Muresan, Mihaela",
         "affiliation": "NIRD GeoEcoMar",
         "orcid": "0000-0002-8446-1263"},
    ],
    "description": (
        "<p><strong>This is a draft version (&ldquo;draft 2&rdquo;).</strong> A finalized "
        "version with the complete WP3 author list (CNR, HEREON, SGN, UB, USE, APS contributors) "
        "is expected to be released; this record will be superseded by a new version at that "
        "time.</p>"

        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D3.2<br>"
        "Work Package Number: WP3<br>"
        "Deliverable Title: Report on testing workflows generating biodiversity and "
        "environmental variables and uptake of new data into WFD, MSFD, and EV systems<br>"
        "Due Date: 30.11.2025 (month 48)<br>"
        "Date of delivery: 11.11.2025</p>"

        "<p>This study evaluates the capacity of a number of existing monitoring programs in "
        "four European river&ndash;estuary&ndash;coastal systems (Elbe&ndash;North Sea, "
        "Danube&ndash;Black Sea, Po&ndash;Adriatic Sea, and Guadalquivir&ndash;Atlantic Ocean) "
        "to support Essential Biodiversity Variables (EBVs) and, where available, Essential "
        "Ocean Variables (EOVs). We analyzed more than 100 monitoring datasets across "
        "freshwater, transitional, and marine domains, assessing their readiness to generate "
        "EBVs based on spatial and temporal representativeness, taxonomic coverage, data "
        "accessibility, and methodological approach.</p>"

        "<p>Across all case studies, monitoring systems already provide strong foundations for "
        "EBVs related to species abundance, community composition, and ecosystem functioning. "
        "These EBVs are supported by long-term marine programs (ICES, CMEMS, LTER) and "
        "established WFD/MSFD policy. However, other EBVs &mdash; particularly trait diversity, "
        "ecosystem structure, and river-sea connectivity &mdash; are poorly represented or "
        "fragmented, especially in estuaries and wetlands.</p>"

        "<p>Marine data are generally more standardized, interoperable, and openly accessible, "
        "enabling easier integration into regional and global data infrastructures (EMODnet, "
        "ICES, CMEMS, BONs). Freshwater and estuarine data, although abundant, are often "
        "stored in restricted databases, limiting reuse and slowing EBV/EOV translation. The "
        "dominant barrier is data accessibility, not lack of data.</p>"

        "<p>All sites show high policy alignment (WFD, MSFD, Natura 2000), ensuring long-term "
        "monitoring continuity. To become EBV/EOV-ready, the systems need improved FAIR access "
        "to biological datasets, harmonized metadata and taxonomy, and better integration "
        "across freshwater&ndash;estuary&ndash;sea continuum.</p>"

        "<p>Overall, the monitoring capacity exists, but stronger interoperability is needed "
        "so that national monitoring smoothly flows into regional and global biodiversity "
        "observation systems.</p>"
    ),
    "keywords": [
        "MBO WP3", "biodiversity monitoring",
        "Essential Biodiversity Variables (EBV)",
        "Essential Ocean Variables (EOV)", "river-coastal continuum",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    "related_identifiers": [],   # Kept lite
    "dates": [
        {"start": "2025-11-11", "type": "Submitted",
         "description": "Date of delivery (draft 2)"},
        {"start": "2025-11-30", "type": "Other",
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
    print("ERROR: no Zenodo token.", file=sys.stderr); sys.exit(1)

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

    print("\n*** D3.2 DRAFT NOTICE ***")
    print("This PDF is labelled 'Version draft 2' with incomplete authorship.")
    print("Deposit lists Muresan Mihaela only; full WP3 team to be added in final version.\n")

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

if __name__ == "__main__":
    main()
