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
import subprocess
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
MISMATCH = KIT / "live-mismatch.json"
PINS = KIT / "pins.json"


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


def payload_hash(page: dict) -> str:
    """Hash the revision fields the check depends on, not the extract alone."""
    rev = (page.get("revisions") or [{}])[0]
    body = json.dumps({
        "pageid": page.get("pageid"),
        "ns": page.get("ns"),
        "title": page.get("title"),
        "revid": rev.get("revid"),
        "parentid": rev.get("parentid"),
        "timestamp": rev.get("timestamp"),
        "extract": page.get("extract") or "",
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _extract_hash(body)


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
            "raw_extract_sha256": _extract_hash(extract),
            "stripped_extract_sha256": _extract_hash(extract.strip()),
            "served_page_sha256": _extract_hash(local_extract(rec.id)),
            "payload_sha256": payload_hash(page),
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



def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def engine_hash() -> str:
    h = hashlib.sha256()
    for path in sorted((ROOT / "mplpb_combined").glob("*.py")):
        h.update(path.name.encode())
        h.update(b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def code_status() -> dict:
    """Engine bytes and checker bytes are pinned separately.

    3bac10f predates this checker. Adding the checker must not make the
    engine pin unattainable.
    """
    pins = json.loads(PINS.read_text(encoding="utf-8")) if PINS.is_file() else {}
    engine = engine_hash()
    checker = file_hash(Path(__file__))
    return {
        "engine_pin": pins.get("engine_sha256", ""),
        "engine_running": engine,
        "engine_ok": engine == pins.get("engine_sha256"),
        "checker_pin": pins.get("checker_sha256", ""),
        "checker_running": checker,
        "checker_ok": checker == pins.get("checker_sha256"),
        "code_revision": pins.get("code_revision", ""),
    }


def page_path(doc_id: str) -> Path:
    return next(CORPUS.glob(doc_id.lower() + ".html"))


def local_extract(doc_id: str) -> str:
    return page_path(doc_id).read_text(encoding="utf-8")


def match_live(manifest: dict) -> tuple[list[str], list[dict]]:
    titles = [p["title"] for p in manifest["pages"]]
    live = _pages(_get(titles))
    errors = []
    rows = []
    for pinned in manifest["pages"]:
        page = live.get(pinned["title"])
        raw_pin = pinned.get("raw_extract_sha256") or pinned.get("extract_sha256")
        row = {"title": pinned["title"], "pinned_revid": pinned["revid"], "pinned_raw_sha256": raw_pin, "pinned_served_page_sha256": pinned.get("served_page_sha256", "")}
        if not page:
            row["error"] = "missing live"
            errors.append(f"{pinned['title']}: missing live")
            rows.append(row)
            continue
        rev = page["revisions"][0]["revid"]
        raw = page.get("extract") or ""
        digest = _extract_hash(raw)
        stripped = _extract_hash(raw.strip())
        payload = payload_hash(page)
        payload_pin = pinned.get("payload_sha256", "")
        row.update({
            "live_revid": rev, "live_raw_sha256": digest, "live_stripped_sha256": stripped,
            "live_payload_sha256": payload, "revid_match": rev == pinned["revid"],
            "raw_match": digest == raw_pin, "stripped_match": stripped == pinned.get("stripped_extract_sha256", stripped),
            "payload_match": bool(payload_pin) and payload == payload_pin,
        })
        if not payload_pin:
            errors.append(f"{pinned['title']}: snapshot has no payload hash; provenance incomplete")
        elif not row["revid_match"] or not row["raw_match"] or not row["payload_match"]:
            errors.append(
                f"{pinned['title']}: live revid {rev} raw {digest[:12]} payload {payload[:12]} "
                f"!= pinned {pinned['revid']} {raw_pin[:12]}"
            )
        rows.append(row)
    return errors, rows


def local_source_errors(manifest: dict) -> list[str]:
    errors = []
    for pinned in manifest["pages"]:
        try:
            got = _extract_hash(local_extract(pinned["id"]))
        except StopIteration:
            errors.append(f"{pinned['id']}: local page missing")
            continue
        served_pin = pinned.get("served_page_sha256", "")
        if not served_pin:
            errors.append(f"{pinned['id']}: snapshot has no full-page pin")
        elif got != served_pin:
            errors.append(f"{pinned['id']}: served page hash {got[:12]} != pinned page {served_pin[:12]}")
    return errors


def score() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    code = code_status()
    code_ok = code["engine_ok"] and code["checker_ok"]
    print(f"engine {code['engine_running'][:12]} pin {code['engine_pin'][:12]} ok={code['engine_ok']}")
    print(f"checker {code['checker_running'][:12]} pin {code['checker_pin'][:12]} ok={code['checker_ok']}")
    if not code_ok:
        print("engine or checker bytes differ from their own pins; not a pinned evaluation")
    local_errors = local_source_errors(manifest)
    if local_errors:
        print("local page does not match pinned extract; not scored")
        for e in local_errors:
            print(" ", e)
    try:
        errors, rows = match_live(manifest)
    except Exception as exc:
        errors, rows = [f"live request failed: {exc}"], []
    record = {"snapshot": "preserved", "code": code, "local_errors": local_errors, "live": rows, "errors": errors}
    MISMATCH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MISMATCH}")
    if errors:
        print("live mismatch; snapshot preserved; not scored")
        for e in errors:
            print(" ", e)
        return 2
    if not code_ok or local_errors:
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
