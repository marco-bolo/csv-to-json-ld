#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D3.4 to Zenodo.

D3.4 references D3.1. Run deposit_d3_1.py first, then pass D3.1's DOI here:

    python deposit_d3_4.py \\
        --pdf ~/Downloads/MBO_D3.4_Jan-2026.pdf \\
        --d31-doi 10.5281/zenodo.XXXXXXX

If --d31-doi is omitted, the script warns and proceeds without that reference
(you can add it manually in the Zenodo UI later).

Title note: doc-info Annex I form is used (includes "and Ecosystem Services"),
per your direction. The cover renders a shorter form ("Report on effects of...").
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

METADATA = {
    "title": "Effects of Existing and Future Terrestrial and Freshwater Conservation Areas on Coastal and Marine Biodiversity and Ecosystem Services",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-11-26",   # V1.1 (original authors' submission)
    "version": "1.2",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    # 10 creators: 2 lead authors (UB) + 8 contributing authors. Order on cover.
    "creators": [
        {"name": "Adamescu, Mihai",
         "affiliation": "University of Bucharest",
         "orcid": "0000-0002-3056-8444"},
        {"name": "Arhire, Georgia",
         "affiliation": "University of Bucharest"},
        {"name": "Bergami, Caterina",
         "affiliation": "CNR",
         "orcid": "0000-0002-5284-1317"},
        {"name": "Keuter, Sabine",
         "affiliation": "HEREON",
         "orcid": "0000-0001-8902-4882"},
        {"name": "Hufnagel, Lili",
         "affiliation": "UFZ"},
        {"name": "Madon, Bénédicte",
         "affiliation": "Universidad de Sevilla",
         "orcid": "0000-0001-8608-3895"},
        {"name": "Muresan, Mihaela",
         "affiliation": "GeoEcoMar",
         "orcid": "0000-0002-8446-1263"},
        {"name": "Peredo, Andres",
         "affiliation": "Senckenberg Gesellschaft für Naturforschung",
         "orcid": "0000-0002-6353-9121"},
        {"name": "Igescu, Denisa",
         "affiliation": "University of Bucharest",
         "orcid": "0009-0001-8189-5074"},
        {"name": "Haase, Peter",
         "affiliation": "Senckenberg Gesellschaft für Naturforschung",
         "orcid": "0000-0002-9340-0438"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D3.4<br>"
        "Work Package Number: WP3<br>"
        "Deliverable Title: Effects of Existing and Future Terrestrial and Freshwater "
        "Conservation Areas on Coastal and Marine Biodiversity and Ecosystem Services<br>"
        "Due Date: 30.11.2025<br>"
        "Submission Date: 26.11.2025 (V1.1, authors); updated 30.01.2026 (V1.2, reviewer)"
        "</p>"

        "<p>This deliverable assesses how terrestrial and freshwater conservation areas "
        "across four major European land&ndash;river&ndash;sea systems &mdash; the "
        "Danube&ndash;Black Sea, Po&ndash;Adriatic Sea, Elbe&ndash;North Sea, and "
        "Guadalquivir&ndash;Atlantic Ocean &mdash; influence downstream coastal and marine "
        "biodiversity and ecosystem services. Using the source-to-sea paradigm and a "
        "conceptual model linking upstream ecosystem service supply, mediating flows, and "
        "downstream ecological conditions, we analyse spatially distributed protected-area "
        "coverage, ecological quality (WFD EQR-based EQC), chlorophyll-a and nutrient "
        "concentrations. Complementary storylines co-developed with case-study teams "
        "summarise the narrative pathways through which upstream protection affects coastal "
        "outcomes (see "
        "<a href=\"https://arcg.is/1OmDji3\">Storyline &ndash; Terrestrial protected areas "
        "effects on marine ecosystems</a>).</p>"

        "<p>Across all basins, the extent of protected areas has increased substantially since "
        "1990, often in parallel with EU environmental policies. Statistical analyses reveal "
        "highly significant associations between upstream protected-area coverage, lower "
        "nitrogen and phosphorus concentrations, and improved ecological status &mdash; "
        "supporting the hypothesis that conservation enhances nutrient retention, hydrological "
        "buffering and habitat quality, with measurable positive signals along the "
        "freshwater&ndash;marine continuum.</p>"

        "<p>However, a key challenge remains the lack of integrated data systems across "
        "freshwater and marine monitoring frameworks. Discontinuities in temporal resolution, "
        "indicator definitions, and ecosystem typologies limit the ability to fully capture "
        "cumulative effects along the land-to-sea continuum. Each basin presents unique "
        "hydrological, ecological, and governance contexts that require system-specific "
        "approaches &mdash; but within a harmonised, interoperable monitoring infrastructure. "
        "Addressing this integration gap is essential for building robust cross-domain "
        "evidence bases, aligning Water Framework Directive (WFD) and Marine Strategy "
        "Framework Directive (MSFD) assessments, and advancing the EU Biodiversity Strategy "
        "for 2030.</p>"

        "<p>Strengthened basin-to-coast planning, integration of terrestrial/freshwater and "
        "marine policies, improved monitoring, and systematic inclusion of protected-area "
        "scenarios in modelling frameworks are essential for enhancing coastal biodiversity "
        "and ecosystem services. This deliverable supports MARCO-BOLO&rsquo;s broader objective "
        "of building an integrated evidence base to inform cross-domain management and the "
        "design of coherent conservation strategies across Europe&rsquo;s land-to-sea "
        "continuum.</p>"
    ),
    "keywords": [
        "MBO WP3", "protected areas", "land-sea continuum",
        "ecosystem services", "nutrient dynamics",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    # D3.1 reference appended at runtime via --d31-doi
    "related_identifiers": [],
    "dates": [
        {"start": "2025-11-26", "type": "Submitted",
         "description": "V1.1 submission (Adamescu, Arhire)"},
        {"start": "2026-01-30", "type": "Updated",
         "description": "V1.2 reviewer edits (Nicholas Pade)"},
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
    ap.add_argument("--d31-doi",
                    help="D3.1 DOI to add as a 'references' related_identifier "
                         "(e.g. 10.5281/zenodo.XXXXXXX). Run deposit_d3_1.py first.")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        print(f"ERROR: file not found: {pdf}", file=sys.stderr); sys.exit(1)

    if args.d31_doi:
        doi = args.d31_doi.strip()
        if doi.startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/"):]
        METADATA["related_identifiers"].append({
            "identifier": doi, "relation": "references", "scheme": "doi"})
        print(f"Added D3.1 as 'references': {doi}")
    else:
        print("WARNING: --d31-doi not provided. Depositing without D3.1 ref.")

    token = load_token()
    ctx = make_ssl_context()
    base = "https://zenodo.org"
    print(f"\nTarget: LIVE ({base})")
    print(f"File:   {pdf}  ({pdf.stat().st_size:,} bytes)")
    print(f"Title:  {METADATA['title'][:80]}...")
    print(f"Authors: {len(METADATA['creators'])}")
    print(f"Related identifiers: {len(METADATA['related_identifiers'])}\n")

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
