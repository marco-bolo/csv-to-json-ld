#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D5.3 to Zenodo.

Note: D5.3 was submitted 4-5 months past its 31.05.2025 due date — submitted
17.10.2025. publication_date uses Submission Date per convention.
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

METADATA = {
    "title": "Scientific document describing potential for satellite remote sensing to estimate blue carbon at regional scales within European coastal systems",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-10-17",
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    "creators": [
        {"name": "Gallo, Natalya D.",
         "affiliation": "Norwegian Research Centre (NORCE)",
         "orcid": "0000-0001-5168-4244"},
        {"name": "Chemello, Silvia",
         "affiliation": "CIIMAR – Interdisciplinary Centre of Marine and Environmental Research",
         "orcid": "0000-0001-6151-891X"},
        {"name": "Sanders, Richard",
         "affiliation": "Norwegian Research Centre (NORCE)",
         "orcid": "0000-0002-6884-7131"},
        {"name": "Sousa Pinto, Isabel",
         "affiliation": "CIIMAR – Interdisciplinary Centre of Marine and Environmental Research",
         "orcid": "0000-0002-9231-0553"},
        {"name": "Blix, Katalin",
         "affiliation": "Norwegian Research Centre (NORCE)",
         "orcid": "0009-0001-3994-1559"},
        {"name": "Haarpaintner, Jörg",
         "affiliation": "Norwegian Research Centre (NORCE)",
         "orcid": "0000-0002-9681-9269"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D5.3<br>"
        "Work Package Number: WP5<br>"
        "Deliverable Title: Scientific document describing potential for satellite remote "
        "sensing to estimate blue carbon at regional scales within European coastal "
        "systems<br>"
        "Due Date: 31.05.2025<br>"
        "Submission Date: 17.10.2025<br>"
        "Ares ref: Ref. Ares(2025)8980017 dated 21/10/2025</p>"

        "<p>MARCO-BOLO <strong>Task 5.3</strong> &ldquo;Spatial mapping of blue carbon "
        "benefits&rdquo; evaluates how satellite remote sensing can advance the mapping of "
        "blue carbon stocks across Europe, with a particular focus on seagrass meadows due to "
        "their importance for the European region. This work responds to the urgent need for "
        "robust, scalable approaches to quantify and monitor carbon stocks in European "
        "coastal habitats, supporting emerging policy and reporting requirements.</p>"

        "<p>Our approach integrated five core activities:</p>"
        "<ol>"
        "<li>Synthesising the scientific literature on remote sensing applications for "
        "seagrass carbon mapping.</li>"
        "<li>Collaborating with MPA-EUROPE to compile and publish the EURO-CARBON database, "
        "the most comprehensive collection of organic carbon measurements for coastal "
        "habitats in Europe.</li>"
        "<li>Pairing large-scale environmental datasets from NASA and Copernicus with in situ "
        "sediment carbon measurements, enabling spatially explicit modelling.</li>"
        "<li>Engaging stakeholders through co-design sessions to ensure scientific outputs "
        "align with policy and management needs.</li>"
        "<li>Developing and testing predictive models for seagrass carbon stocks using "
        "environmental variables.</li>"
        "</ol>"

        "<p>Our models demonstrated high explanatory power (R&sup2; &gt; 0.8), identifying "
        "bottom temperature, sea surface wave height, phosphate concentration, near-surface "
        "pH, and remote sensing reflectance at 443 nm as key predictors. Notably, using "
        "organic carbon density as the response variable improved model performance and "
        "policy relevance.</p>"

        "<p>We conclude that satellite remote sensing and global oceanographic data products "
        "already provide substantial opportunities for evaluating and monitoring blue carbon "
        "services in seagrass beds. Anticipated advances &mdash; including new satellite "
        "missions and enhanced computational capabilities &mdash; will further increase "
        "these opportunities. Currently, no countries in Europe have included seagrass beds "
        "in their emission inventories and climate plans, despite the prevalence of "
        "seagrasses along many coastlines. From 2026, reporting of wetlands under LULUCF may "
        "become mandatory for EU member states, but whether this will apply to seagrass beds "
        "depends on if member states consider them as &ldquo;managed&rdquo; marine "
        "ecosystems. Either way, policy needs for reporting carbon stocks are growing, and "
        "we show that remote sensing and global oceanographic data products can contribute "
        "substantially to mapping blue carbon benefits in Europe.</p>"
    ),
    "keywords": [
        "MBO WP5", "blue carbon", "seagrass", "remote sensing",
        "coastal ecosystems",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    "related_identifiers": [],
    "dates": [
        {"start": "2025-10-17", "type": "Submitted",
         "description": "Submission date"},
        {"start": "2025-05-31", "type": "Other",
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
