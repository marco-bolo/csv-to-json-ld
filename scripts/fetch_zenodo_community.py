#!/usr/bin/env python3
"""
Fetch every record in the Zenodo MARCO-BOLO community.

Unauthenticated requests are capped at 25 per page, so this paginates until
we've collected all hits, then writes a single consolidated JSON file.

Usage:
    python fetch_zenodo_community.py                 # writes zenodo_marco-bolo.json
    python fetch_zenodo_community.py --token TOKEN   # uses your Zenodo token (faster, 100/page)
    python fetch_zenodo_community.py --community foo --out foo.json
"""
import argparse, json, sys, time
import urllib.request, urllib.parse, urllib.error

def fetch_page(community: str, page: int, size: int, token: str | None):
    params = {
        "communities": community,
        "size": size,
        "page": page,
        "all_versions": "false",
        "sort": "newest",
    }
    url = "https://zenodo.org/api/records?" + urllib.parse.urlencode(params)
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--community", default="marco-bolo")
    ap.add_argument("--token", default=None,
                    help="Optional Zenodo personal access token (raises page size to 100)")
    ap.add_argument("--out", default=None,
                    help="Output filename (default: zenodo_<community>.json)")
    args = ap.parse_args()

    size = 100 if args.token else 25
    out_path = args.out or f"zenodo_{args.community}.json"

    all_hits, page, total = [], 1, None
    while True:
        try:
            d = fetch_page(args.community, page, size, args.token)
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code} on page {page}: {e.read().decode()[:300]}", file=sys.stderr)
            sys.exit(1)
        hits = d.get("hits", {}).get("hits", [])
        if total is None:
            total = d.get("hits", {}).get("total")
            print(f"Community '{args.community}' reports {total} total records.")
        all_hits.extend(hits)
        print(f"  page {page}: {len(hits)} record(s) (running total {len(all_hits)})")
        if len(hits) < size:
            break
        page += 1
        time.sleep(0.5)  # polite

    out = {"meta": {"community": args.community, "fetched_records": len(all_hits),
                    "reported_total": total},
           "hits": {"hits": all_hits, "total": total}}
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(all_hits)} records to {out_path}")
    if total is not None and len(all_hits) != total:
        print(f"⚠️  Got {len(all_hits)} but Zenodo reports {total}. "
              "Check pagination or re-run.", file=sys.stderr)

if __name__ == "__main__":
    main()
