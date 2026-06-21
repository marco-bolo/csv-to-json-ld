#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D4.1 to Zenodo.

D4.1 is the *Preliminary* report on advanced data processing, geolocation,
and export format (WP4, T4.1). Note: the PDF cover spells one author
"Motjaba Masoudi" — that's a typo. The catalog already has him correctly
as Mojtaba Masoudi (mbo_59174), and this Zenodo deposit uses the correct
spelling. The typo is on the PM-feedback list to fix in any future revision.

Usage:
    python deposit_d4_1.py --pdf ~/Downloads/MBO_D4.1_Jun-2024.pdf
    python deposit_d4_1.py --pdf ... --draft
    python deposit_d4_1.py --pdf ... --yes
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

METADATA = {
    "title": "Preliminary report on progress for advanced data processing, geolocation and export format",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2024-06-25",   # Ares submission date (EU)
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    # 7 creators in cover order. Masoudi spelled correctly (cover has typo).
    "creators": [
        {"name": "Robidart, Julie",
         "affiliation": "National Oceanography Centre",
         "orcid": "0000-0001-9805-3570"},
        {"name": "Thompson, Fletcher",
         "affiliation": "DTU Aqua",
         "orcid": "0000-0002-0639-9871"},
        {"name": "Mariani, Patrizio",
         "affiliation": "DTU Aqua",
         "orcid": "0000-0002-8015-1583"},
        {"name": "Giering, Sarah",
         "affiliation": "National Oceanography Centre",
         "orcid": "0000-0002-3090-1876"},
        {"name": "Masoudi, Mojtaba",
         "affiliation": "National Oceanography Centre",
         "orcid": "0000-0002-0007-0362"},
        {"name": "Muñiz, Carlota",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0001-9584-3833"},
        {"name": "Debusschere, Elisabeth",
         "affiliation": "Flanders Marine Institute",
         "orcid": "0000-0002-5595-0295"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D4.1<br>"
        "Work Package Number: WP4<br>"
        "Deliverable Title: Preliminary report on progress for advanced data processing, "
        "geolocation and export format<br>"
        "Due Date: 01.07.2024<br>"
        "Date of creation (cover): 31.03.2024<br>"
        "Submission Date (Ares ref): 25.06.2024</p>"

        "<p>Sustainable monitoring of organisms and their habitats is imperative during the "
        "biodiversity crisis, and is especially important in marine waters where fisheries "
        "alone feed approximately 3 billion people globally while multiple threats change "
        "ecosystem dynamics. MARCO BOLO&rsquo;s WP4 aims to create a direct pipeline from "
        "non-invasive, in situ monitoring of marine life, to ocean users and managers. WP4 "
        "aims to achieve this through adoption of workflows developed in WP1, FAIR data "
        "reporting, automated classification of high-volume datasets, and geolocation of "
        "sensed data in near-real-time.</p>"

        "<p>The first 18 months of MARCO BOLO resulted in the development of several new "
        "deployable technologies to measure biodiversity, enabling geolocation in the field, "
        "simplicity in interacting with the software and datasets, automated classification "
        "and data processing, and enabling data flows from high-volume datasets to public "
        "repositories. While not yet field-tested, the developments described here already "
        "enable the reporting of biodiversity datasets for mapping and response, detecting "
        "ecosystems and their prey, and counting and communicating species data from the "
        "field. One publication describing these new biodiversity systems is open-access and "
        "another has been submitted. The WP4 team aims to demonstrate these developments in "
        "June 2025 in the Belgian North Sea.</p>"

        "<p>This report describes the progress made in the first 18 months of MARCO BOLO WP4, "
        "<strong>Task 4.1</strong>, to <em>&ldquo;develop autonomous systems to deliver "
        "georeferenced maps of biodiversity attributes including genomic, taxonomic and "
        "habitat characteristics.&rdquo;</em> Deliverable 4.1 is achieved through seven "
        "complementary technologies targeting diverse biodiversity variables, organized "
        "across four sub-objectives:</p>"
        "<ul>"
        "<li><strong>Genomics:</strong> upgrading the Robotic Cartridge Sampling Instrument "
        "(RoCSI) sampler and the LAMPTRON eDNA sensor to facilitate geolocation, data "
        "delivery, and usability.</li>"
        "<li><strong>Particulate and plankton imaging:</strong> integrating the UVP6 into "
        "autonomous vehicles with on-board image processing using a miniaturized AI system "
        "for real-time image classification.</li>"
        "<li><strong>Fish and benthos:</strong> integrating Ultra Short Base Line (USBL) "
        "acoustics for positioning of an open-source BlueROV2 ROV with a new "
        "high-definition multi-camera system; outputs include processed large-scale seafloor "
        "images and annotations of identified animals.</li>"
        "<li><strong>Bioacoustics:</strong> developing a stand-alone mooring accommodating "
        "an acoustic fish receiver, a broadband hydrophone, and a C-POD/F-POD device for "
        "long-term recording at sea, with a data pipeline for detection and classification "
        "of harbour porpoise (Phocoena phocoena) echolocation click trains and export to "
        "EMODnet Biology and EurOBIS following FAIR principles.</li>"
        "</ul>"
    ),
    "keywords": [
        "MBO WP4", "biodiversity monitoring", "autonomous sensors",
        "geolocation", "marine instrumentation",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    "related_identifiers": [],   # D4.1 doesn't cite any other deliverables
    "dates": [
        {"start": "2024-03-31", "type": "Created",
         "description": "Date on cover"},
        {"start": "2024-06-25", "type": "Submitted",
         "description": "Submission date (Ares ref)"},
        {"start": "2024-07-01", "type": "Other",
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

if __name__ == "__main__":
    main()
