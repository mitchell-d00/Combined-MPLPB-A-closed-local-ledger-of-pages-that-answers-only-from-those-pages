"""A record is one HTML page that carries its own identity.

    R = (id, scope, status, hash, derived_from, origin_depth)

The page is authoritative. Everything else in this package is derived from
the files under a root directory and can be thrown away and rebuilt.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PREFIX = "mplpb:"

# Every field the format knows. Order here is the order they are written.
FIELDS = (
    "document-id", "kind", "scope", "when-to-use", "not-for", "status", "hash",
    "origin", "origin-depth", "derived-from", "supersedes", "ratified-by",
    "points-to", "owner", "updated", "category",
)
# The hash covers every field except the two that must be able to change
# without altering what the page says: its status, and the hash itself.
UNHASHED = ("status", "hash")
# Fields added after the first release enter the hash only when a page uses
# them, so every page written before they existed keeps the hash it had.
LATE = ("not-for",)
HASHED = tuple(f for f in FIELDS if f not in UNHASHED and f not in LATE)

INDEX_NAMES = ("index.html", "_index.html")
_SKIP_TOKENS = {"", "-", "\u2014", "\u2013", "none", "n/a"}


# Earlier MPLPB tools spelled some fields differently. They are read as one.
ALIASES = {"id": "document-id", "version": "updated", "taught-from": "derived-from"}


def norm_name(name: str) -> str:
    """mplpb:origin_depth and mplpb:origin-depth are the same field."""
    n = name.strip().lower().replace("_", "-")
    return ALIASES.get(n, n)


@dataclass(frozen=True)
class Ref:
    """A pointer at another record: its id, and optionally the hash it had."""
    id: str
    hash: str = ""

    def __str__(self) -> str:
        return f"{self.id}@{self.hash}" if self.hash else self.id


def parse_refs(value: str) -> List[Ref]:
    out: List[Ref] = []
    for token in re.split(r"[\s,;]+", value or ""):
        if token.lower() in _SKIP_TOKENS:
            continue
        if "@" in token:
            rid, _, h = token.partition("@")
            if h and not h.startswith("sha256:"):
                h = "sha256:" + h
            out.append(Ref(rid, h))
        else:
            out.append(Ref(token))
    return out


def format_refs(refs: List[Ref]) -> str:
    return " ".join(str(r) for r in refs)


class _Head(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: Dict[str, str] = {}
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            a = dict(attrs)
            name = (a.get("name") or "").strip().lower()
            if name.startswith(PREFIX):
                key = norm_name(name[len(PREFIX):])
                value = (a.get("content") or "").strip()
                if value or key not in self.meta:
                    self.meta[key] = value

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


class _Text(HTMLParser):
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "tr", "br", "pre",
             "section", "ul", "ol", "table"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


_BODY = re.compile(r"<body[^>]*>(.*)</body>", re.I | re.S)


def body_of(text: str) -> str:
    m = _BODY.search(text)
    raw = m.group(1) if m else ""
    return raw.replace("\r\n", "\n").replace("\r", "\n").strip()


def text_of(body_html: str) -> str:
    p = _Text()
    p.feed(body_html)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in "".join(p.parts).split("\n")]
    return "\n".join(ln for ln in lines if ln)


def compute_hash(fields: Dict[str, str], title: str, body_html: str) -> str:
    hashed = {k: fields.get(k, "") for k in HASHED}
    hashed.update({k: fields[k] for k in LATE if fields.get(k, "")})
    canon = json.dumps(
        {"fields": hashed, "title": title.strip(), "body": body_html},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


@dataclass
class Record:
    path: str                       # posix path relative to the root
    fields: Dict[str, str]
    title: str
    body_html: str
    hash_actual: str
    text: str = ""
    problems: List[Tuple[str, str]] = field(default_factory=list)

    # -- the six fields of the formula ------------------------------------
    @property
    def id(self) -> str:
        return self.fields.get("document-id", "")

    @property
    def scope(self) -> str:
        return self.fields.get("scope", "")

    @property
    def status(self) -> str:
        return self.fields.get("status", "").lower()

    @property
    def hash(self) -> str:
        return self.fields.get("hash", "")

    @property
    def derived_from(self) -> List[Ref]:
        return parse_refs(self.fields.get("derived-from", ""))

    @property
    def depth_declared(self) -> Optional[int]:
        v = self.fields.get("origin-depth", "")
        return int(v) if re.fullmatch(r"\d+", v) else None

    # -- the rest ---------------------------------------------------------
    @property
    def when_to_use(self) -> str:
        return self.fields.get("when-to-use", "")

    @property
    def not_for(self) -> str:
        return self.fields.get("not-for", "")

    @property
    def supersedes(self) -> List[Ref]:
        return parse_refs(self.fields.get("supersedes", ""))

    @property
    def origin(self) -> str:
        return (self.fields.get("origin", "") or "human").lower()

    @property
    def ratified_by(self) -> str:
        return self.fields.get("ratified-by", "")

    @property
    def points_to(self) -> str:
        return self.fields.get("points-to", "")

    @property
    def kind(self) -> str:
        k = self.fields.get("kind", "").lower()
        if k:
            return k
        name = self.path.rsplit("/", 1)[-1].lower()
        if name in INDEX_NAMES or "index" in self.fields.get("category", "").lower():
            return "index"
        return "page"

    @property
    def intact(self) -> bool:
        return bool(self.hash) and self.hash == self.hash_actual

    def short_hash(self) -> str:
        return (self.hash_actual or "").replace("sha256:", "")[:12]


def parse_page(text: str, relpath: str) -> Record:
    head = _Head()
    try:
        head.feed(text)
    except Exception:  # a page that cannot be parsed is a page with no fields
        pass
    body = body_of(text)
    fields = dict(head.meta)
    return Record(
        path=relpath, fields=fields, title=head.title.strip(), body_html=body,
        hash_actual=compute_hash(fields, head.title, body), text=text_of(body),
    )


def read_page(root: Path, path: Path) -> Record:
    rel = path.relative_to(root).as_posix()
    return parse_page(path.read_text(encoding="utf-8", errors="replace"), rel)


def plain_to_html(body: str) -> str:
    paras = [p.strip() for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
    return "\n".join(
        "<p>" + html.escape(" ".join(p.split()), quote=False) + "</p>" for p in paras
    )


def render_page(fields: Dict[str, str], title: str, body_html: str) -> str:
    """Write a page whose declared hash matches what a reader will recompute."""
    fields = {norm_name(k): " ".join((v or "").split()) for k, v in fields.items()}
    title = " ".join(title.split())
    body_html = body_html.replace("\r\n", "\n").strip()
    fields["hash"] = compute_hash(fields, title, body_html)
    metas = "\n".join(
        f'<meta name="{PREFIX}{k}" content="{html.escape(fields[k], quote=True)}">'
        for k in FIELDS if fields.get(k, "") != ""
    )
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{html.escape(title, quote=False)}</title>\n{metas}\n</head>\n<body>\n"
        f"{body_html}\n</body>\n</html>\n"
    )


def _meta_tag(name: str) -> "re.Pattern[str]":
    alt = "[-_]".join(re.escape(part) for part in name.split("-"))
    return re.compile(
        r"<meta\b[^>]*\bname\s*=\s*[\"']" + re.escape(PREFIX) + alt + r"[\"'][^>]*>", re.I
    )


def upsert_meta(text: str, name: str, content: str) -> str:
    """Set one mplpb: field in a page's head and touch nothing else."""
    tag = f'<meta name="{PREFIX}{name}" content="{html.escape(content, quote=True)}">'
    pat = _meta_tag(name)
    if pat.search(text):
        return pat.sub(lambda _m: tag, text, count=1)
    m = re.search(r"</head\s*>", text, re.I)
    if not m:
        raise ValueError("page has no </head>; cannot record a field in it")
    return text[: m.start()] + tag + "\n" + text[m.start():]
