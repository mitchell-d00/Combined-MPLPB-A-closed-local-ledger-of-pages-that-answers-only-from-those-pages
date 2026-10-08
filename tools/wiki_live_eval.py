#!/usr/bin/env python3
"""Load a small open wiki, match it to the live site, then test.

The page text is Simple English Wikipedia, CC BY-SA 4.0. Titles in
evaluation/wiki/titles.json decide the labels before the reader runs.
A question is owned only if its title was fetched. A title that was not
fetched is a refusal. A question that names two fetched titles is not a
relationship between them. Paraphrases are reported and do not count.

The code revision is pinned. Scoring starts only after each fetched page
still has the live revision id and extract hash recorded at load time.
"""
from __future__ import annotations

import hashlib
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

API = "https://simple.wikipedia.org/w/api.php"
UA = "mplpb-wiki-eval/1.0 (local ledger test; matches live revision before scoring)"
CODE = "3bac10f21a5b74e8aacbf9dada9773cfee25dcb0"
WHEN = "2026-10-08T14:20:00Z"
KIT = ROOT / "evaluation" / "wiki"
CORPUS = KIT / "corpus"
MANIFEST = KIT / "manifest.json"
TITLES = KIT / "titles.json"


def _get(titles: list[str]) -> dict:
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "redirects": 1,
        "prop": "extracts|revisions", "exintro": 1, "explaintext": 1,
        "rvprop": "ids|timestamp", "titles": "|".join(titles),
    })
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _pages(payload: dict) -> dict:
    return {p["title"]: p for p in payload["query"]["pages"].values() if "title" in p}


def _extract_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch() -> None:
    spec = json.loads(TITLES.read_text(encoding="utf-8"))
    wanted = spec["fetched"]
    live = _pages(_get(wanted))
    if CORPUS.exists():
        for child in CORPUS.rglob("*"):
            if child.is_file():
                child.unlink()
    CORPUS.mkdir(parents=True, exist_ok=True)
    records = []
    for i, title in enumerate(wanted, start=1):
        page = live[title]
        extract = page.get("extract") or ""
        rev = page["revisions"][0]
        body = (
            extract.strip()
            + "\n\nSource: Simple English Wikipedia, CC BY-SA 4.0. "
            + f"https://simple.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
        )
        rec = L.write(
            CORPUS, title=title, scope=title, when_to_use=title,
            body=body, prefix="WIKI", doc_id=f"WIKI-{i:04d}",
            origin="human", owner="Simple English Wikipedia contributors",
            when=WHEN, note=f"revid {rev['revid']}",
        )
        records.append({
            "id": rec.id, "title": title, "pageid": page["pageid"],
            "revid": rev["revid"], "timestamp": rev["timestamp"],
            "extract_sha256": _extract_hash(extract),
        })
    manifest = {
        "code_revision": CODE,
        "source": "https://simple.wikipedia.org",
        "license": "CC BY-SA 4.0",
        "independence": (
            "Page text is Wikipedia's. Labels are the fetched and absent title "
            "lists, written before the reader runs. This is not blinded human labeling."
        ),
        "pages": records,
        "absent": spec["absent"],
        "paraphrases": spec["paraphrases"],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"loaded {len(records)} pages into {CORPUS}")


def match_live(manifest: dict) -> list[str]:
    titles = [p["title"] for p in manifest["pages"]]
    live = _pages(_get(titles))
    errors = []
    for pinned in manifest["pages"]:
        page = live.get(pinned["title"])
        if not page:
            errors.append(f"{pinned['title']}: missing live")
            continue
        rev = page["revisions"][0]["revid"]
        digest = _extract_hash(page.get("extract") or "")
        if rev != pinned["revid"] or digest != pinned["extract_sha256"]:
            errors.append(
                f"{pinned['title']}: live revid {rev} hash {digest[:12]} "
                f"!= pinned {pinned['revid']} {pinned['extract_sha256'][:12]}"
            )
    return errors


def score() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["code_revision"] != CODE:
        print("code pin mismatch")
        return 2
    errors = match_live(manifest)
    if errors:
        print("live mismatch; not scored")
        for e in errors:
            print(" ", e)
        return 2
    print("live match ok")
    by_title = {p["title"]: p["id"] for p in manifest["pages"]}
    failed = 0
    for title, doc_id in by_title.items():
        answer = R.answer(CORPUS, title, R.PROFILES["external"])
        ok = answer.kind == "return" and answer.record and answer.record.id == doc_id
        print(f"title {title}: {answer.kind} {answer.record.id if answer.record else '-'} {'ok' if ok else 'FAIL'}")
        failed += not ok
    for title in manifest["absent"]:
        answer = R.answer(CORPUS, title, R.PROFILES["external"])
        ok = answer.kind == R.NOT_IN_CORPUS
        print(f"absent {title}: {answer.kind} {'ok' if ok else 'FAIL'}")
        failed += not ok
    joined = " ".join(manifest["pages"][0]["title"] for _ in range(1))
    pair = f"{manifest['pages'][0]['title']} {manifest['pages'][1]['title']}"
    answer = R.answer(CORPUS, pair, R.PROFILES["external"])
    ok = answer.kind != "return"
    print(f"two titles '{pair}': {answer.kind} {'ok (not a relationship)' if ok else 'FAIL returned one page'}")
    failed += not ok
    print("paraphrases, reported only:")
    for item in manifest["paraphrases"]:
        answer = R.answer(CORPUS, item["question"], R.PROFILES["external"])
        got = answer.record.id if answer.record else answer.kind
        print(f"  {item['question']!r} -> {got}; title page {item['title']} not required")
    print(f"scored failures: {failed}")
    return 1 if failed else 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "fetch":
        fetch()
        return 0
    if cmd == "check":
        return score()
    print("use fetch or check")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
