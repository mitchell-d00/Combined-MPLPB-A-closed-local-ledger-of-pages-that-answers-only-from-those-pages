#!/usr/bin/env python3
"""Search an open wiki, then build a local MPLPB copy.

The search is the site's own search. Each hit becomes one page. A page is
not marked human or machine unless the source says so. Otherwise the page
carries a percent and the reasons for that percent, and external delivery
is withheld.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mplpb_combined import ledger as L  # noqa: E402
from mplpb_combined import reader as R  # noqa: E402
from mplpb_combined.record import upsert_meta  # noqa: E402

API = "https://simple.wikipedia.org/w/api.php"
UA = "mplpb-web-clone/1.0 (open-wiki search, local copy)"
WHEN = "2026-10-08T15:10:00Z"


def _get(params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search(query: str, limit: int = 3) -> list[str]:
    data = _get({"action": "opensearch", "format": "json", "limit": limit, "search": query})
    return list(data[1])


def origin_support(declared: str) -> tuple[str, int, str]:
    if declared in {"human", "machine"}:
        return declared, 100, "source declared this origin; not independently verified"
    reasons = ["no human or machine declaration in the source"]
    score = 0
    if declared:
        reasons.append(f"source said {declared!r}, which is neither human nor machine")
        score = 20
    return "unverified", score, "; ".join(reasons)


def build(query: str, dest: Path, limit: int = 3) -> None:
    titles = search(query, limit)
    if not titles:
        raise SystemExit("search returned nothing")
    data = _get({
        "action": "query", "format": "json", "redirects": 1,
        "prop": "extracts|revisions", "exintro": 1, "explaintext": 1,
        "rvprop": "ids|timestamp", "titles": "|".join(titles),
    })
    dest.mkdir(parents=True, exist_ok=True)
    pages = []
    for page in data["query"]["pages"].values():
        title = page.get("title") or "untitled source"
        extract = (page.get("extract") or "").strip()
        label, percent, why = origin_support("")
        body = (
            f"{extract}\n\nSource: https://simple.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}\n"
            "License: CC BY-SA 4.0\n"
            f"Origin declared: {label}. Origin confidence: {percent}%. Support: {why}.\n"
            "Loaded beside other sources. Co-presence does not establish a relationship."
        )
        rec = L.write(
            dest, title=title, scope=title, when_to_use=title,
            not_for="relationship; other source", body=body, prefix="WEB",
            origin="machine", owner="unknown", when=WHEN, note=query,
            external="no", source_authorship="unknown",
        )
        pages.append({"id": rec.id, "title": title, "origin_declared": label, "origin_confidence": percent, "support": why, "external": False})
    (dest / "clone-manifest.json").write_text(json.dumps({"query": query, "pages": pages}, indent=2) + "\n")
    print(f"search {query!r} -> {', '.join(titles)}")
    for row in pages:
        answer = R.answer(dest, row["title"], R.PROFILES["external"])
        got = answer.record.id if answer.record else answer.kind
        print(f"  {row['id']} {row['title']} origin {row['origin_confidence']}% ({row['support']}) external -> {got}")


def main() -> int:
    if len(sys.argv) < 3:
        print("use: web_clone.py <search> <corpus-dir>")
        return 2
    build(sys.argv[1], Path(sys.argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
