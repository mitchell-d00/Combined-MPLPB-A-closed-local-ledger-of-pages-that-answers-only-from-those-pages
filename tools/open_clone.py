#!/usr/bin/env python3
"""Clone loose open-web records into an MPLPB folder.

One source becomes one page. The page scope is the source title only.
The body is not promoted into scope, and two pages are not given a parent
just because they were loaded together. Shared presence is not a relationship.

Missing titles stay untitled. They are still sealed, cited, and refused
when a question does not belong to them.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mplpb_combined import ledger as L  # noqa: E402
from mplpb_combined import reader as R  # noqa: E402

TITLE_KEYS = ("title", "name", "heading", "label")
BODY_KEYS = ("body", "text", "extract", "blurb", "content", "summary")
SOURCE_KEYS = ("source", "url", "from", "origin_url")
LICENSE_KEYS = ("license", "licence", "rights")
WHEN = "2026-10-08T14:30:00Z"


def _first(obj: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    return ""


def _from_json(text: str, name: str) -> list[dict]:
    data = json.loads(text)
    rows = data if isinstance(data, list) else [data]
    out = []
    for i, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            row = {"body": str(row)}
        out.append({
            "title": _first(row, TITLE_KEYS),
            "body": _first(row, BODY_KEYS) or json.dumps(row, ensure_ascii=False),
            "source": _first(row, SOURCE_KEYS) or name,
            "license": _first(row, LICENSE_KEYS) or "unspecified",
            "file": f"{name}#{i}",
        })
    return out


def _from_text(text: str, name: str) -> dict:
    title = ""
    body = text.strip()
    match = re.match(r"(?i)^title\s*:\s*(.+)\n+", body)
    if match:
        title = " ".join(match.group(1).split())
        body = body[match.end():].strip()
    source = name
    for line in body.splitlines()[:8]:
        found = re.match(r"(?i)^(source|url)\s*:\s*(\S+)", line.strip())
        if found:
            source = found.group(2)
            body = "\n".join(
                ln for ln in body.splitlines() if ln.strip() != line.strip()
            ).strip()
            break
    return {"title": title, "body": body, "source": source, "license": "unspecified", "file": name}


def read_loose(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in {".json", ".jsonl"}:
        if path.suffix.lower() == ".jsonl":
            rows = []
            for i, line in enumerate(text.splitlines(), start=1):
                if line.strip():
                    rows.extend(_from_json(line, f"{path.name}#{i}"))
            return rows
        return _from_json(text, path.name)
    return [_from_text(text, path.name)]


def clone(src: Path, dest: Path) -> list[dict]:
    dest.mkdir(parents=True, exist_ok=True)
    items = []
    for path in sorted(p for p in src.rglob("*") if p.is_file() and not p.name.startswith(".")):
        items.extend(read_loose(path))
    written = []
    for item in items:
        titled = bool(item["title"])
        title = item["title"] or "untitled source"
        scope = title if titled else "untitled source"
        footer = (
            f"Source: {item['source']}\n"
            f"License: {item['license']}\n"
            "Loaded beside other sources. Co-presence does not establish a relationship."
        )
        rec = L.write(
            dest, title=title, scope=scope, when_to_use=scope,
            not_for="relationship; other source",
            body=(item["body"] or "(empty source)") + "\n\n" + footer,
            prefix="ALIEN", origin="human",
            owner=item["source"] or "unspecified", when=WHEN,
            note=item["file"],
        )
        written.append({
            "id": rec.id, "title": title, "scope": scope, "titled": titled,
            "source": item["source"], "license": item["license"],
            "file": item["file"], "hash": rec.hash,
        })
    subprocess.run([sys.executable, "-m", "mplpb_combined", "index", str(dest), "--title", "Alien sources"], check=True, cwd=ROOT)
    manifest = {
        "rule": "one source, one page; scope is the source title only; no cross-source parent",
        "pages": written,
    }
    (dest / "clone-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return written


def show(dest: Path, questions: list[str]) -> None:
    print(f"{len(list(dest.glob('alien-*.html')))} pages in {dest}")
    for question in questions:
        answer = R.answer(dest, question, R.PROFILES["external"])
        got = answer.record.id if answer.record else answer.kind
        print(f"  {question!r} -> {got} ({answer.reason})")


def main() -> int:
    if len(sys.argv) < 3:
        print("use: open_clone.py <loose-dir> <corpus-dir> [question ...]")
        return 2
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    written = clone(src, dest)
    for row in written:
        flag = "" if row["titled"] else " untitled"
        print(f"{row['id']} {row['title']}{flag} <= {row['file']}")
    show(dest, sys.argv[3:] or ["Cat", "Dog", "Cat Dog", "Tokyo"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
