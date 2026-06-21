#!/usr/bin/env python3
"""
Deposit MARCO-BOLO Deliverable D1.2 to Zenodo.

Workflow:
    1. Creates a new draft deposit
    2. Uploads the PDF
    3. Sets the metadata
    4. Prints a review URL and asks before publishing (irreversible)
    5. Publishes if you confirm; otherwise leaves it as a draft you can
       review and publish manually on the Zenodo web UI.

Authentication:
    Reads token from ZENODO_TOKEN env var or ~/.zenodo_token (just the token,
    one line). Create one at:
      https://zenodo.org/account/settings/applications/tokens/new/
    Required scopes: deposit:write, deposit:actions

Usage:
    python deposit_d1_2.py --pdf MBO_D1_2_Dec-2025.pdf
    python deposit_d1_2.py --pdf MBO_D1_2_Dec-2025.pdf --sandbox  # test first
    python deposit_d1_2.py --pdf MBO_D1_2_Dec-2025.pdf --draft    # don't publish
    python deposit_d1_2.py --pdf MBO_D1_2_Dec-2025.pdf --yes      # publish, no prompt

The script is verbose so you can see what happens at each step. The metadata
is in the METADATA dict near the top — edit it there before running if needed.
"""
import argparse, json, os, ssl, sys
import urllib.request, urllib.error
from pathlib import Path

# ===========================================================================
# Metadata — edit here before running if any value needs to change.
# ===========================================================================
METADATA = {
    "title": "Revised Project Data Management Plan, Associated Specification and Supporting Tools for Data Generation and Exchange (WP1)",
    "upload_type": "publication",
    "publication_type": "deliverable",
    "publication_date": "2025-12-30",
    "version": "1.0",
    "language": "eng",
    "access_right": "open",
    "license": "cc-by-4.0",
    "creators": [
        {"name": "Lear, Dan",
         "affiliation": "Marine Biological Association of the United Kingdom",
         "orcid": "0000-0002-5806-0837"},
        {"name": "Formel, Stephen",
         "affiliation": "IOC-UNESCO",
         "orcid": "0000-0001-7418-1244"},
        {"name": "Exter, Katrina",
         "affiliation": "VLIZ",
         "orcid": "0000-0002-5911-1536"},
        {"name": "Tagliolato Acquaviva D'Aragona, Paolo",
         "affiliation": "CNR",
         "orcid": "0000-0002-0261-313X"},
        {"name": "Figueroa Ashforth, Chloe",
         "affiliation": "Marine Biological Association of the United Kingdom",
         "orcid": "0009-0007-9889-5090"},
        {"name": "Buttigieg, Pier Luigi",
         "affiliation": "Alfred Wegener Institute Helmholtz Centre for Polar and Marine Research",
         "orcid": "0000-0002-4366-3088"},
    ],
    "description": (
        "<p>Grant Agreement: 101082021<br>"
        "Project Acronym: MARCO-BOLO<br>"
        "Project Title: MARine COastal BiOdiversity Long-term Observations<br>"
        "Deliverable Number: D1.2<br>"
        "Work Package Number: WP1<br>"
        "Deliverable Title: Revised Project Data Management Plan, Associated Specification and Supporting Tools for Data Generation and Exchange (WP1)<br>"
        "Due Date: 30.12.2025<br>"
        "Submission Date: 30.12.2025</p>"
        "<p>D1.2 updates and augments "
        "<a href=\"https://doi.org/10.5281/zenodo.17537386\">D1.1 (Lear et al., 2025)</a> "
        "by reporting concrete progress, decisions, and remaining actions to operationalise "
        "MARCO-BOLO&rsquo;s data and information management processes and provide support to "
        "Work Packages 2&ndash;5 in the description and publication of their knowledge outputs.</p>"
        "<p>The approach remains aligned to the UN Ocean Decade and the program components of "
        "IOC-UNESCO including <strong>ODIS</strong> and <strong>OBIS</strong>, in addition to "
        "<strong>EMODnet</strong> as the European data gateway, through the use of "
        "<em>schema.org</em>-based JSON-LD. We now provide an operational authoring pathway via "
        "<em>Google Sheets &rarr; CSV &rarr; JSON-LD</em> with validations and examples, plus "
        "clearer guidance on repository pathways and protocol DOIs.</p>"
    ),
    "keywords": [
        "MBO WP1", "data management", "FAIR", "marine biodiversity",
        "linked open data", "JSON-LD", "schema.org", "ODIS",
        "persistent identifiers", "W3ID",
    ],
    "communities": [{"identifier": "marco-bolo"}],
    "grants": [{"id": "10.13039/501100000780::101082021"}],
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.17537386",
         "relation": "continues",
         "scheme": "doi"},
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
    ap.add_argument("--pdf", required=True,
                    help="Path to the PDF to deposit")
    ap.add_argument("--sandbox", action="store_true",
                    help="Use sandbox.zenodo.org instead of zenodo.org (test deposits)")
    ap.add_argument("--draft", action="store_true",
                    help="Create the deposit but do NOT publish")
    ap.add_argument("--yes", action="store_true",
                    help="Publish without confirmation prompt")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        print(f"ERROR: file not found: {pdf}", file=sys.stderr); sys.exit(1)
    if pdf.suffix.lower() != ".pdf":
        print(f"WARNING: {pdf.name} is not a .pdf — continuing anyway", file=sys.stderr)

    token = load_token()
    ctx = make_ssl_context()
    base = "https://sandbox.zenodo.org" if args.sandbox else "https://zenodo.org"
    where = "SANDBOX" if args.sandbox else "LIVE"
    print(f"Target: {where} ({base})")
    print(f"File:   {pdf}  ({pdf.stat().st_size:,} bytes)")
    print(f"Title:  {METADATA['title']}\n")

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
        ans = input(f"\nPublish now to {where}? This generates a permanent DOI. [y/N]: ")
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
