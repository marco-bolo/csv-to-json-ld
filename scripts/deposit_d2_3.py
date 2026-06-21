#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D2.3 to Zenodo.

Same structure as deposit_d1_2.py / deposit_d2_2.py.

Usage:
    python deposit_d2_3.py --pdf ~/Downloads/MBO_D2.3_Jan-2026.pdf
    python deposit_d2_3.py --pdf ~/Downloads/MBO_D2.3_Jan-2026.pdf --draft
    python deposit_d2_3.py --pdf ~/Downloads/MBO_D2.3_Jan-2026.pdf --yes

Reads token from ZENODO_TOKEN env or ~/.zenodo_token.
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

# ===========================================================================
# Metadata
# ===========================================================================
METADATA = {
    "title": "Final report on the congruence between traditional and eDNA-based biodiversity observations, and their robustness across bioinformatics issues and diversity metrics",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-11-28",
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    # 15 creators in cover-page order
    "creators": [
        {"name": "Warwick-Dugdale, Joanna",
         "affiliation": "Marine Biological Association",
         "orcid": "0000-0001-5242-6706"},
        {"name": "Boulanger, Emilie",
         "affiliation": "UNESCO-OBIS",
         "orcid": "0000-0002-6446-7342"},
        {"name": "Suominen, Saara",
         "affiliation": "UNESCO-OBIS",
         "orcid": "0000-0001-9401-8460"},
        {"name": "Heynderickx, Hanneloor",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0002-5611-837X"},
        {"name": "Jensen, Mads Reinholdt",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0001-8240-1083"},
        {"name": "Ciarlini Junger, Pedro",
         "affiliation": "CNRS-IBENS",
         "orcid": "0000-0001-8774-0738"},
        {"name": "Bowler, Chris",
         "affiliation": "CNRS-IBENS",
         "orcid": "0000-0003-3835-6187"},
        {"name": "Jee, Haesung",
         "affiliation": "CNRS-IBENS"},
        {"name": "Not, Fabrice",
         "affiliation": "Sorbonne Université",
         "orcid": "0000-0002-9342-195X"},
        {"name": "Beatty, Jennifer",
         "affiliation": "Sorbonne Université"},
        {"name": "Onoufriou, Aubrie",
         "affiliation": "Marine Directorate, Scottish Government",
         "orcid": "0000-0002-4605-1896"},
        {"name": "Matejusová, Iveta",
         "affiliation": "Marine Directorate, Scottish Government",
         "orcid": "0000-0002-3241-043X"},
        {"name": "D'Alelio, Domenico",
         "affiliation": "Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0002-2189-503X"},
        {"name": "Kumazawa Morais, Daniel",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0003-3328-7848"},
        {"name": "Cunliffe, Michael",
         "affiliation": "Marine Biological Association",
         "orcid": "0000-0002-6716-3555"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D2.3<br>"
        "Work Package Number: WP2<br>"
        "Deliverable Title: Report on the congruence between traditional and eDNA-based "
        "biodiversity observations, and their robustness across bioinformatics issues and "
        "diversity metrics<br>"
        "Due Date: 30.11.2025<br>"
        "Submission Date: 28.11.2025</p>"

        "<p>Here, we present the outcomes of Task 2.3: <em>&ldquo;Comparison of spatial and "
        "temporal eDNA-based vs traditional observations&rdquo;</em>. The report summarises the "
        "level of agreement between traditional and eDNA-based biodiversity observations and "
        "evaluates how stable these comparisons remain when different analytical decisions are "
        "applied. <strong>Performance</strong> (or <strong>congruence</strong>) refers to the "
        "extent to which eDNA observations reproduce the ecological patterns detected by "
        "traditional methods, including seasonal cycles, interannual trends and diversity "
        "gradients. <strong>Robustness</strong> refers to the consistency of these eDNA-derived "
        "patterns when analytical choices vary, for example the choice of bioinformatic "
        "workflow or the use of different diversity metrics.</p>"

        "<p>The work was conducted in conjunction with Tasks 2.1 and 2.2, building on the "
        "<a href=\"https://doi.org/10.5281/zenodo.17517691\">meta-analysis of eDNA-based "
        "approaches (D2.1)</a> and the long-term time-series datasets curated under "
        "<a href=\"https://doi.org/10.5281/zenodo.20766608\">D2.2</a>. Three main analyses "
        "were performed: (A) comparison of complementary plankton datasets spanning 20 years "
        "(2001&ndash;2021) at coastal station &lsquo;L4&rsquo; (Western English Channel) "
        "between eDNA (18S-V9 metabarcoding) and microscopy counts; (B) assessment of "
        "phytoplankton diversity values from different metabarcoding methods and microscopy "
        "in the global Tara Oceans dataset; and (C) a &lsquo;Data Analysis Challenge&rsquo; "
        "inviting the global eDNA community to run their preferred pipelines on a shared "
        "SOMLIT-Astan dataset, allowing assessment of pipeline-driven variation in diversity "
        "outputs.</p>"

        "<p>Across the three analyses, the degree of congruence between eDNA (metabarcoding) "
        "and traditional (microscopy) datasets was most dependent on the diversity metric "
        "applied; both the methods employed in data production and processing, and the nature "
        "of the community being observed, further impacted similarity. Long-term seasonal "
        "diversity patterns were more congruent between data types than interannual changes. "
        "Estimators that accounted for relative abundance (e.g. Shannon; Hill numbers q = 1.5) "
        "produced more congruent patterns than richness-only metrics. Designation of taxa into "
        "major plankton/phytoplankton groups revealed group-dependent differences in diversity "
        "patterns between data types. Pipeline choice was more important than season or year "
        "to the community structure of eDNA samples in the Data Analysis Challenge results.</p>"

        "<p>These findings indicate that, despite innate differences between data types, there "
        "is partial congruence in seasonal diversity patterns and total diversity values "
        "obtained from eDNA and traditional microscopy data &mdash; supporting integration of "
        "eDNA-based approaches into established marine plankton monitoring frameworks, "
        "particularly when using evenness-aware diversity metrics.</p>"
    ),
    "keywords": [
        "MBO WP2", "eDNA", "metabarcoding", "biodiversity comparison", "diversity metrics",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    # Both predecessor WP2 deliverables explicitly built upon in the abstract
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.17517691",
         "relation": "references",
         "scheme": "doi"},
        {"identifier": "10.5281/zenodo.20766608",
         "relation": "references",
         "scheme": "doi"},
    ],
    "dates": [
        {"start": "2025-11-28", "type": "Submitted",
         "description": "Submission date"},
        {"start": "2025-11-30", "type": "Other",
         "description": "Due date"},
    ],
}

# ===========================================================================
# HTTP plumbing (identical across the deposit scripts)
# ===========================================================================
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
    print(f"\nNext step: run deposit_d2_4.py with --d23-doi {final_doi}")

if __name__ == "__main__":
    main()
