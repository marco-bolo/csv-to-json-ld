#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D6.2 to Zenodo.

D6.2 is the WP6 stakeholder-engagement deliverable summarising three
Co-design/Co-creation Workshops. It references three Zenodo records that are
the full workshop reports (added as 'references' related_identifiers).

Note: McKee's ORCID was not provided so her creator entry is ORCID-less.
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

METADATA = {
    "title": "Three co-design/co-creation/stakeholder consultation workshop reports, with recommendations/decisions for the project workplan",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-12-03",   # Ares date
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    "creators": [
        {"name": "Benedetti, Lisa",
         "affiliation": "UNESCO",
         "orcid": "0009-0001-3827-7318"},
        {"name": "Larkin, Kate",
         "affiliation": "Seascape Belgium (SSBE)",
         "orcid": "0000-0002-5713-6465"},
        {"name": "McKee, Kara",
         "affiliation": "Seascape Belgium (SSBE)"},
        {"name": "Sousa Pinto, Isabel",
         "affiliation": "CIIMAR – Interdisciplinary Centre of Marine and Environmental Research",
         "orcid": "0000-0002-9231-0553"},
        {"name": "Salas Leitón, Emilio A.",
         "affiliation": "CIIMAR – Interdisciplinary Centre of Marine and Environmental Research",
         "orcid": "0000-0003-2133-1581"},
        {"name": "Lear, Dan",
         "affiliation": "Marine Biological Association",
         "orcid": "0000-0002-5806-0837"},
        {"name": "Figueroa Ashforth, Chloe",
         "affiliation": "Marine Biological Association",
         "orcid": "0009-0007-9889-5090"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D6.2<br>"
        "Work Package Number: WP6<br>"
        "Deliverable Title: Three co-design/co-creation/stakeholder consultation workshop "
        "reports, with recommendations/decisions for the project workplan<br>"
        "Due Date: 31.07.2025<br>"
        "Date of delivery (cover): 03.11.2025<br>"
        "Submission (Ares ref): 03.12.2025</p>"

        "<p>The MARCO-BOLO project aims to structure and strengthen European coastal and "
        "marine biodiversity observation capabilities, linking these to global efforts to "
        "understand and restore ocean health, hence ensuring that outputs respond to explicit "
        "stakeholder needs from policy, planning and industry. To this end, MARCO-BOLO has "
        "established and is engaging regularly with a Community of Practice (CoP) made up of "
        "(Marine and Coastal) Biodiversity Data Generators and Data users from marine "
        "observatories, data infrastructures, and other relevant stakeholders across the EU "
        "and internationally.</p>"

        "<p>The project has 7 Work Packages (WPs), with WP6 responsible for facilitating "
        "stakeholder engagement amongst the technical WPs 1&ndash;5 through the CoP, as well "
        "as developing Knowledge Transfer material from WP Deliverables and wider outputs. "
        "To enable stakeholder engagement and consultation, two major CoP events and three "
        "Co-design/Co-creation Workshops were planned. In the first two years of MARCO-BOLO, "
        "WP6 convened the first CoP and three Co-design/Co-creation Workshops, all held "
        "mainly online, with the exception of the second workshop. The aim was to bring "
        "together relevant partners and end-users through a phased approach to set up "
        "necessary feedback loops for the development of products that consider end-user "
        "needs and requirements.</p>"

        "<p>This report is Deliverable 6.2 of the project, which provides a summary of the "
        "three co-design/co-creation/stakeholder consultation workshops and weblinks to the "
        "full workshop reports, with main conclusions and recommendations/decisions for the "
        "project workplan that have and are being considered by the MARCO-BOLO Coordination "
        "team and Project Implementation Committee (PIC) composed of WP (co)leaders.</p>"

        "<p>The three workshops covered:</p>"
        "<ol>"
        "<li><strong>1st CoP Event &amp; 1st Co-design/Co-creation Workshop</strong> "
        "(23 May 2024, online): <em>Making Marine and Coastal Biodiversity Observations "
        "Policy Relevant</em> &mdash; over 70 experts, focused on policymaker engagement and "
        "DMP/EOV/EBV uptake. Full report: "
        "<a href=\"https://doi.org/10.5281/zenodo.17244601\">10.5281/zenodo.17244601</a>.</li>"
        "<li><strong>2nd Co-design/Co-creation Workshop</strong> (6 November, Sitges, "
        "Spain): <em>Solutions for Improving Marine Biodiversity Monitoring</em> &mdash; "
        "approximately 50 in-person stakeholders, held jointly with OBAMA-NEXT and "
        "GES4SEAS as part of the JRC's <em>Future of Marine Biodiversity Monitoring in "
        "Europe</em> initiative. Covered DMP, eDNA, AI/3D imaging tools. Full report: "
        "<a href=\"https://doi.org/10.5281/zenodo.17244778\">10.5281/zenodo.17244778</a>.</li>"
        "<li><strong>3rd Co-design/Co-creation Workshops</strong> (last week of June 2025, "
        "online targeted sessions): three sessions targeting D2.4 (eDNA-based EBVs), T2.3 + "
        "T5.2 (eDNA &amp; AI imaging), and T5.3 (Blue Carbon spatial mapping). Full report: "
        "<a href=\"https://doi.org/10.5281/zenodo.17244832\">10.5281/zenodo.17244832</a>.</li>"
        "</ol>"

        "<p>Cumulatively the three workshops brought almost fifty external biodiversity and "
        "marine data experts and other stakeholders including representatives from DG ENV, "
        "DG RTD, DG MARE, CINEA, Regional Sea Conventions, GOOS BioEco Panel, sister EU "
        "Horizon projects (Biodiversa+, EuropaBON, OBAMA-NEXT, BioEcoOcean), national "
        "institutions, academia and research, private sector, and other organizations "
        "responsible for marine biodiversity monitoring across the EU, UK and "
        "internationally.</p>"

        "<p>Lessons learned include: (1) the connection across natural and social sciences "
        "via the CoP has been a strength, attracting high-level policy maker engagement; "
        "(2) outputs from the stakeholder profiling exercise (D6.1) became available late in "
        "year one, limiting their use for early CoP design but are now being taken up by "
        "Task 6.3 Knowledge Transfer; (3) technical-WP products needed a certain level of "
        "maturity before useful co-design discussions could happen, so the third (later) "
        "workshop achieved a truer co-design interaction; (4) leveraging key EU events as "
        "engagement opportunities was effective; (5) ongoing engagement with Biodiversa+ "
        "and EuropaBON as core CoP members has been particularly fruitful. Further "
        "stakeholder engagement &mdash; including a Spring 2026 industry-focused event and "
        "the Final CoP Stakeholder event tentatively scheduled for September 2026 &mdash; "
        "will inform development of knowledge transfer plans and custom materials for "
        "target audiences (industry, policy makers, researchers).</p>"
    ),
    "keywords": [
        "MBO WP6", "stakeholder engagement", "Community of Practice",
        "co-design workshops", "marine biodiversity policy",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.17244601",
         "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.17244778",
         "relation": "references", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.17244832",
         "relation": "references", "scheme": "doi"},
    ],
    "dates": [
        {"start": "2025-11-03", "type": "Created",
         "description": "Date on cover"},
        {"start": "2025-12-03", "type": "Submitted",
         "description": "Submission date (Ares ref)"},
        {"start": "2025-07-31", "type": "Other",
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
