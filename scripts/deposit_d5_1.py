#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D5.1 to Zenodo.

16 authors per cover/doc-info (V1.0 history row excludes Deneudt + Debusschere
but doc-info Author(s) field includes them as official authors — using doc-info
form per Stephen's pick).

Florian Kokoszka has dual affiliation (CNR + SZN per cover footnotes 5,3).
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

METADATA = {
    "title": "Scientific document determining biodiversity trends, underlying drivers and essential observations for predictive modelling",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-11-17",
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    "creators": [
        {"name": "Peredo Arce, Andrés",
         "affiliation": "Senckenberg Gesellschaft für Naturforschung",
         "orcid": "0000-0002-6353-9121"},
        {"name": "Nowe, Johannes",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0009-0000-1555-5867"},
        {"name": "Muñiz, Carlota",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0001-9584-3833"},
        {"name": "Deneudt, Klaas",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0002-8559-3508"},
        {"name": "Debusschere, Elisabeth",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0002-5595-0295"},
        {"name": "Iudicone, Daniele",
         "affiliation": "Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0002-7473-394X"},
        {"name": "Mariani, Patrizio",
         "affiliation": "Danmarks Tekniske Universitet",
         "orcid": "0000-0002-8015-1583"},
        {"name": "Haase, Peter",
         "affiliation": "Senckenberg Gesellschaft für Naturforschung",
         "orcid": "0000-0002-9340-0438"},
        {"name": "Cano-Barbacil, Carlos",
         "affiliation": "Senckenberg Gesellschaft für Naturforschung",
         "orcid": "0000-0002-6482-5103"},
        {"name": "Kokoszka, Florian",
         "affiliation": "Consiglio Nazionale delle Ricerche; Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0001-5346-3058"},
        {"name": "Asdar, Sarah",
         "affiliation": "Consiglio Nazionale delle Ricerche",
         "orcid": "0009-0002-6251-4456"},
        {"name": "Lefebvre, Camil",
         "affiliation": "École centrale de Nantes"},
        {"name": "Buongiorno Nardelli, Bruno",
         "affiliation": "Consiglio Nazionale delle Ricerche",
         "orcid": "0000-0002-3416-7189"},
        {"name": "Mercogliano, Paola",
         "affiliation": "Centro Euro-Mediterraneo sui Cambiamenti Climatici",
         "orcid": "0000-0001-7236-010X"},
        {"name": "Ribera d'Alcalá, Maurizio",
         "affiliation": "Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0002-5492-9961"},
        {"name": "Margiotta, Francesca",
         "affiliation": "Stazione Zoologica Anton Dohrn",
         "orcid": "0000-0003-0757-5934"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D5.1<br>"
        "Work Package Number: WP5<br>"
        "Deliverable Title: Scientific document determining biodiversity trends, underlying "
        "drivers and essential observations for predictive modelling<br>"
        "Due Date: 30.11.2025<br>"
        "Submission Date: 17.11.2025</p>"

        "<p>The main goal of this report is to assess biodiversity trends and their drivers "
        "in marine and coastal European ecosystems. To this end, we analysed community-level "
        "biodiversity trends and species-level habitat use during the last decades using data "
        "from open sources. Biodiversity trends are paired with environmental parameters and "
        "projected into the future using Habitat Suitability Models and Random Forest "
        "Regressions. Three complementary studies are presented.</p>"

        "<p><strong>Study 1 &mdash; Time series analysis:</strong> European time series for "
        "six biotic groups (birds, fish, invertebrates, macroalgae, phytoplankton, "
        "zooplankton) were analysed to estimate temporal trends (1956&ndash;2022) in "
        "richness, diversity, and abundance across regions. A total of 2,359 time series "
        "comprising 552,475 observations of 4,718 coastal and marine taxa in 2,246 different "
        "sites were assembled from open-access databases (BioTIME, EMODnet, REPHY, FishGlob, "
        "Continuous Plankton Recorder Survey). Most communities showed no significant change, "
        "suggesting no further widespread biodiversity loss during the observation period. "
        "Positive trends were found for birds and invertebrates in the Baltic, and negative "
        "ones for fish in the Atlantic. However, uneven data coverage limits this "
        "generalization, highlighting the lack of sufficient rigorous monitoring of "
        "biodiversity and of accessibility to existing data.</p>"

        "<p><strong>Study 2 &mdash; Habitat suitability modelling:</strong> Habitat "
        "suitability was predicted for coastal and marine species protected under the "
        "Habitats and Birds Directives, under current and future Shared Socioeconomic "
        "Pathways (SSP) climate scenarios. Projections were made for four marine mammal "
        "species (harbour porpoise, harbour seal, common dolphin, bottlenose dolphin) in "
        "OSPAR regions II&ndash;IV using EurOBIS data (2000&ndash;2019) and environmental "
        "predictors. Results revealed clear spatial and seasonal patterns in projected "
        "suitable habitats: a southward shift for porpoises in winter, seals remaining "
        "coastal, and dolphins concentrating in the Iberian region. Future projections "
        "suggest an overall reduction in suitable habitats for all four species. While "
        "limited by sampling biases and data inconsistencies, the study demonstrates the "
        "value of open-access biodiversity data for large-scale ecological modelling.</p>"

        "<p><strong>Study 3 &mdash; Causal relationships in coastal ecosystems:</strong> "
        "Climate change impacts on coastal ecosystems were examined at the Gulf of Naples "
        "(LTER Mare Chiara site). Combining long-term data, reanalysis, and machine learning, "
        "the study found salinity to be a key driver of chlorophyll (phytoplankton) "
        "variability, linking land-based freshwater inputs and ocean dynamics. Using "
        "Representative Concentration Pathways to 2070 (RCP4.5, RCP8.5), the model predicts "
        "increasing salinity and declining chlorophyll, largely driven by reduced rainfall "
        "and runoff. The findings stress the importance of long-term monitoring and indicate "
        "that land-driven changes may affect coastal productivity more than ocean warming "
        "alone.</p>"

        "<p>This report highlights the usefulness of publicly available data but also its "
        "limitations. As biodiversity open-source data increases in quantity and quality, "
        "the potential of future analyses will grow with it.</p>"
    ),
    "keywords": [
        "MBO WP5", "biodiversity trends", "habitat suitability modelling",
        "climate projections", "time series analysis",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    "related_identifiers": [],
    "dates": [
        {"start": "2025-11-17", "type": "Submitted",
         "description": "Submission date"},
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
