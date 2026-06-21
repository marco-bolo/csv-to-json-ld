#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D2.4 to Zenodo.

Important: D2.4 references D2.3 in addition to D2.1 and D2.2. Pass D2.3's
fresh DOI (from running deposit_d2_3.py first) via --d23-doi:

    python deposit_d2_4.py \\
        --pdf ~/Downloads/MBO_D2.4_Jan-2026.pdf \\
        --d23-doi 10.5281/zenodo.XXXXXXXX

If you omit --d23-doi the script will warn and proceed with only D2.1 + D2.2
as references (you can add D2.3 manually in the Zenodo UI later).

Reads token from ZENODO_TOKEN env or ~/.zenodo_token.
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

# ===========================================================================
# Metadata
# ===========================================================================
METADATA = {
    "title": "Final report on the definition of eDNA-based EBVs with associated eDNA-based EBV datasets and efficiency of eDNA for detecting/quantifying taxa/species of interest",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-11-29",
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    # 19 creators in cover-page order. Daniele Iudicone's catalog mPID is
    # currently mbo_dludicone with a typo'd familyName — separate cleanup pass
    # tracks renaming; the Zenodo deposit uses the correct spelling.
    "creators": [
        {"name": "Ciarlini Junger, Pedro",
         "affiliation": "CNRS",
         "orcid": "0000-0001-8774-0738"},
        {"name": "Zinger, Lucie",
         "affiliation": "CNRS",
         "orcid": "0000-0002-3400-5825"},
        {"name": "Kumazawa Morais, Daniel",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0003-3328-7848"},
        {"name": "Jensen, Mads Reinholdt",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0001-8240-1083"},
        {"name": "Warwick-Dugdale, Joanna",
         "affiliation": "Marine Biological Association",
         "orcid": "0000-0001-5242-6706"},
        {"name": "Cunliffe, Michael",
         "affiliation": "Marine Biological Association",
         "orcid": "0000-0002-6716-3555"},
        {"name": "Heynderickx, Hanneloor",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0002-5611-837X"},
        {"name": "Beatty, Jennifer",
         "affiliation": "Sorbonne Université"},
        {"name": "Not, Fabrice",
         "affiliation": "Sorbonne Université",
         "orcid": "0000-0002-9342-195X"},
        {"name": "Afonso, Luís",
         "affiliation": "CIIMAR – Interdisciplinary Centre of Marine and Environmental Research",
         "orcid": "0000-0003-3978-1388"},
        {"name": "Sousa Pinto, Isabel",
         "affiliation": "CIIMAR – Interdisciplinary Centre of Marine and Environmental Research"},
        {"name": "Onoufriou, Aubrie",
         "affiliation": "Marine Scotland",
         "orcid": "0000-0002-4605-1896"},
        {"name": "Matejusová, Iveta",
         "affiliation": "Marine Scotland",
         "orcid": "0000-0002-3241-043X"},
        {"name": "D'Alelio, Domenico",
         "affiliation": "Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0002-2189-503X"},
        {"name": "Iudicone, Daniele",
         "affiliation": "Stazione Zoologica Anton Dohrn"},
        {"name": "Suominen, Saara",
         "affiliation": "UNESCO",
         "orcid": "0000-0001-9401-8460"},
        {"name": "Boulanger, Emilie",
         "affiliation": "UNESCO",
         "orcid": "0000-0002-6446-7342"},
        {"name": "Præbel, Kim",
         "affiliation": "UiT – The Arctic University of Norway",
         "orcid": "0000-0002-0681-1854"},
        {"name": "Bowler, Chris",
         "affiliation": "CNRS",
         "orcid": "0000-0003-3835-6187"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D2.4<br>"
        "Work Package Number: WP2<br>"
        "Deliverable Title: Report on the definition of eDNA-based EBVs with associated "
        "eDNA-based EBV datasets and efficiency of eDNA for detecting/quantifying "
        "taxa/species of interest<br>"
        "Due Date: 30.11.2025<br>"
        "Submission Date: 29.11.2025</p>"

        "<p>Work Package 2 (WP2) aims to enable environmental DNA (eDNA)-based methods for "
        "standardized biodiversity monitoring. This report (D2.4) presents the outcomes of "
        "Task 2.4, which focused on defining eDNA-based Essential Variables &mdash; namely "
        "<strong>Essential Ocean Variables (EOVs)</strong> and <strong>Essential Biodiversity "
        "Variables (EBVs)</strong> &mdash; and evaluating their utility for European policy "
        "frameworks, including the Marine Strategy Framework Directive (MSFD), the Water "
        "Framework Directive (WFD), and the Habitats Directive.</p>"

        "<p>Building on other WP2 deliverables "
        "(<a href=\"https://doi.org/10.5281/zenodo.17517691\">D2.1</a>, "
        "<a href=\"https://doi.org/10.5281/zenodo.20766608\">D2.2</a>, and D2.3), we identified "
        "and generated a suite of eDNA-based EOVs from multiple case-study datasets, including "
        "a global survey (Tara Oceans), three coastal time-series (SOMLIT-Astan, LTER-MC/NEREA, "
        "the EMO BON UiT genomic observatory), and a dedicated cetacean dataset from the "
        "Portuguese coast (CIIMAR). This report demonstrates that EOVs are currently the most "
        "operational product directly derivable from eDNA data. The candidate eDNA-based EOVs "
        "presented here were formatted to Darwin Core standards and will be deposited in "
        "public repositories, providing the foundation for fully functional eDNA-based EOVs. "
        "These EOVs serve as standardized building blocks and EBV candidates that can, with "
        "expanded sampling and modelling, be transformed into full EBVs. These essential "
        "variables (EOVs/EBVs) can work as biological indicators aligned with European "
        "frameworks, such as the WFD and the MSFD, and regional conventions, such as OSPAR "
        "(Northeast Atlantic), or UNEP-MAP (Mediterranean Sea).</p>"

        "<p>Across the case studies, we demonstrate the usefulness of eDNA for generating EOVs "
        "and detecting policy-relevant taxa and species:</p>"
        "<ul>"
        "<li><strong>Phytoplankton &amp; Harmful algal bloom (HABs) events:</strong> eDNA "
        "metabarcoding from time-series data successfully captured seasonal phytoplankton "
        "dynamics and HABs events. Generated EOVs are relevant for assessing eutrophication "
        "and ecosystem function in marine environments.</li>"
        "<li><strong>Fish communities:</strong> eDNA metabarcoding revealed seasonal patterns "
        "in fish diversity and community composition, while targeted species-specific digital "
        "droplet PCR (ddPCR) assays provided quantitative information for sentinel species "
        "such as the European anchovy, directly supporting regional indicator frameworks.</li>"
        "<li><strong>Marine mammals:</strong> eDNA detected multiple cetacean species, "
        "including those protected under the EU Habitats Directive, with seasonal occurrences "
        "of species validated against visual surveys.</li>"
        "<li><strong>Invasive Alien Species (IAS):</strong> eDNA expanded the known "
        "distribution of several OSPAR-listed invasive species, demonstrating strong "
        "potential for early detection in data-deficient areas.</li>"
        "<li><strong>Species of conservation concern:</strong> eDNA detected several fish "
        "species listed as threatened, near-threatened, or vulnerable on the IUCN Red List, "
        "highlighting its value for monitoring vulnerable species.</li>"
        "</ul>"

        "<p>Since dedicated performance-evaluation experiments were not available, the "
        "efficiency (or usefulness) of eDNA-derived variables was evaluated by comparing them "
        "with expected biodiversity signals from conventional observations, and global "
        "biodiversity databases (GBIF, OBIS, iNaturalist). These comparisons showed that eDNA "
        "patterns were largely congruent with standard methods, while also providing "
        "additional insight into taxonomic diversity and species distributions.</p>"

        "<p>In conclusion, this deliverable provides a practical scheme and a set of validated "
        "case studies showing that eDNA-based EOVs offer a powerful and scalable tool for "
        "producing policy-relevant biodiversity indicators. These eDNA-based EOVs are a "
        "stepwise improvement from simple raw eDNA observations of individual species and fit "
        "the information needs of European and regional environmental directives, paving the "
        "way for more comprehensive, standardized, and efficient biodiversity monitoring.</p>"
    ),
    "keywords": [
        "MBO WP2", "eDNA", "Essential Ocean Variables (EOV)",
        "Essential Biodiversity Variables (EBV)", "biodiversity monitoring",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    # D2.1 + D2.2 (D2.3 is appended by main() when --d23-doi is provided)
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.17517691",
         "relation": "references",
         "scheme": "doi"},
        {"identifier": "10.5281/zenodo.20766608",
         "relation": "references",
         "scheme": "doi"},
    ],
    "dates": [
        {"start": "2025-11-29", "type": "Submitted",
         "description": "Submission date"},
        {"start": "2025-11-30", "type": "Other",
         "description": "Due date"},
    ],
}

# ===========================================================================
# HTTP plumbing
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
    ap.add_argument("--d23-doi",
                    help="D2.3 DOI to add as a 'references' related_identifier "
                         "(e.g. 10.5281/zenodo.XXXXXXX). Run deposit_d2_3.py "
                         "first to get this.")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        print(f"ERROR: file not found: {pdf}", file=sys.stderr); sys.exit(1)

    # Append D2.3 reference if provided
    if args.d23_doi:
        doi = args.d23_doi.strip()
        # Accept either '10.5281/zenodo.XXX' or 'https://doi.org/10.5281/zenodo.XXX'
        if doi.startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/"):]
        METADATA["related_identifiers"].append({
            "identifier": doi, "relation": "references", "scheme": "doi"})
        print(f"Added D2.3 as 'references': {doi}")
    else:
        print("WARNING: --d23-doi not provided. Depositing without D2.3 ref. "
              "You can add it manually in the Zenodo UI after publishing.")

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
