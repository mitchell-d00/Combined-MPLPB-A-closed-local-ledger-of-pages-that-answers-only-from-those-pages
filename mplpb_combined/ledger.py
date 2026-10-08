"""The ledger is the folder.

Crawl it, and every rule in the formula can be decided from what the pages
say about themselves: which are current, what each was derived from, how
many generations stand between a page and a source, and whether any page
was altered after it was written.

Writes never overwrite. A change writes a new page, then retires the old
one. The order matters: a crash between the two steps leaves a new page
that names its predecessor, and the reader already treats a named
predecessor as retired.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence

from .record import (
    Record, Ref, format_refs, parse_page, plain_to_html, read_page, render_page,
    upsert_meta,
)

LOG_DIR = "_log"
LOG_NAME = "ledger.jsonl"
LOCK_NAME = ".lock"
STATUSES = ("current", "retired")
ORIGINS = ("human", "machine")
REQUIRED = ("document-id", "scope", "status", "hash", "origin-depth")


@dataclass(frozen=True)
class Finding:
    level: str      # "error" or "warning"
    code: str       # C1 .. C14
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():7} {self.code:4} {self.path}: {self.message}"


class LedgerBusy(RuntimeError):
    pass


def utc_now() -> str:
    fixed = os.environ.get("MPLPB_NOW")
    return fixed or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


class Ledger:
    """A read-only view of one root, rebuilt from the files each time."""

    def __init__(self, root) -> None:
        self.root = Path(root)
        if not self.root.is_dir():
            raise FileNotFoundError(f"not a directory: {self.root}")
        self.records: List[Record] = []
        self.strays: List[str] = []
        for path in sorted(self.root.rglob("*.html")):
            rel = path.relative_to(self.root)
            if any(part.startswith(".") for part in rel.parts):
                continue
            rec = read_page(self.root, path)
            if rec.id:
                self.records.append(rec)
            elif rec.kind != "index":
                self.strays.append(rec.path)
        self.by_id: Dict[str, List[Record]] = {}
        for r in self.records:
            self.by_id.setdefault(r.id, []).append(r)
        # Only a valid successor may retire a predecessor. Broken, unsealed,
        # duplicate or cyclic records have no authority over other records.
        # Valid successors still make a half-finished revision safe to read.
        self.superseded_by: Dict[str, List[Record]] = {}
        self._depth: Dict[str, int] = {}
        for r in self.records:
            if not self._status_authority(r):
                continue
            for ref in r.supersedes:
                if ref.id != r.id:
                    self.superseded_by.setdefault(ref.id, []).append(r)

    def _status_authority(self, r: Record) -> bool:
        """Validate the complete dependency graph before trusting supersession.

        Status itself is intentionally not hashed. A retired valid successor
        still proves that its predecessor was superseded; it must not revive.
        A hash pin must resolve exactly, never through resolve's legacy fallback.
        """
        stack = [(r, frozenset())]
        checked = []
        while stack:
            cur, seen = stack.pop()
            if cur.path in seen or self.quarantine_reason(cur):
                return False
            if len(self.by_id.get(cur.id, [])) != 1:
                return False
            if cur.origin not in ORIGINS or cur.depth_declared is None:
                return False
            trail = seen | {cur.path}
            checked.append(cur)
            for ref in list(cur.derived_from) + list(cur.supersedes):
                targets = self.by_id.get(ref.id, [])
                if len(targets) != 1 or not ref.hash:
                    return False
                target = targets[0]
                if target.hash_actual != ref.hash:
                    return False
                stack.append((target, trail))
        return all(cur.depth_declared == self.derived_depth(cur) for cur in checked)

    # -- status ------------------------------------------------------------
    def effective_status(self, r: Record) -> str:
        if r.id in self.superseded_by:
            return "retired"
        return r.status

    def quarantine_reason(self, r: Record) -> str:
        """Why a record may not be served, or '' if it may."""
        if r.kind == "index":
            return "index"
        for f in REQUIRED:
            if not r.fields.get(f, ""):
                return "unsealed" if f == "hash" else f"missing {f}"
        if r.status not in STATUSES:
            return "bad status"
        if not r.intact:
            return "altered"
        return ""

    def servable(self) -> List[Record]:
        """Current, intact records that are allowed to own a question."""
        return [
            r for r in self.records
            if not self.quarantine_reason(r) and self.effective_status(r) == "current"
        ]

    def quarantined(self) -> List[Record]:
        return [r for r in self.records
                if self.quarantine_reason(r) not in ("", "index")]

    # -- lineage -----------------------------------------------------------
    def resolve(self, ref: Ref) -> Optional[Record]:
        cands = self.by_id.get(ref.id, [])
        if ref.hash:
            for c in cands:
                if c.hash_actual == ref.hash:
                    return c
        return cands[0] if cands else None

    def depth(self, r: Record) -> int:
        """Generations between this record and a source.

        A human source is 0. A machine page written from nothing is 1.
        A derivation is one more than its deepest parent. A revision is at
        least as deep as what it replaces. A named ratification resets to 0.
        The served depth is never lower than the depth the page declares.
        """
        return self._depth_of(r, frozenset(), use_declared=True)

    def derived_depth(self, r: Record) -> int:
        """The depth the lineage implies, ignoring what this page declares."""
        return self._depth_of(r, frozenset(), use_declared=False)

    def _depth_of(self, r: Record, seen: frozenset, use_declared: bool) -> int:
        if use_declared and r.path in self._depth:
            return self._depth[r.path]
        if r.ratified_by:
            d = 0
        else:
            seen = seen | {r.path}

            def parent_depths(refs: List[Ref]) -> List[int]:
                out = []
                for ref in refs:
                    p = self.resolve(ref)
                    if p is not None and p.path not in seen:
                        out.append(self._depth_of(p, seen, True))
                return out

            if r.derived_from:
                d_src = 1 + max(parent_depths(r.derived_from), default=0)
            else:
                d_src = 0 if r.origin == "human" else 1
            d = max(d_src, max(parent_depths(r.supersedes), default=0))
            if use_declared:
                d = max(d, r.depth_declared or 0)
        if use_declared:
            self._depth[r.path] = d
        return d

    def history(self, doc_id: str) -> List[Record]:
        """Walk the supersession chain through an id, oldest first."""
        start = self.by_id.get(doc_id, [])
        if not start:
            return []
        chain = [start[0]]
        seen = {start[0].path}
        cur = start[0]
        while cur.supersedes:                       # back to the first version
            p = self.resolve(cur.supersedes[0])
            if p is None or p.path in seen:
                break
            chain.insert(0, p); seen.add(p.path); cur = p
        cur = start[0]
        while cur.id in self.superseded_by:         # forward to the head
            nxt = self.superseded_by[cur.id][0]
            if nxt.path in seen:
                break
            chain.append(nxt); seen.add(nxt.path); cur = nxt
        return chain

    # -- validation --------------------------------------------------------
    def findings(self) -> List[Finding]:
        out: List[Finding] = []

        def add(level, code, path, msg):
            out.append(Finding(level, code, path, msg))

        for path in self.strays:
            add("warning", "C13", path, "no mplpb:document-id; not a record, never read")
        for doc_id, recs in sorted(self.by_id.items()):
            if len(recs) > 1:
                for r in recs:
                    add("error", "C3", r.path, f"duplicate id {doc_id}")
        current_successors: Dict[str, List[Record]] = {}
        for r in self.records:
            if r.kind == "index":
                continue
            for f in REQUIRED:
                if not r.fields.get(f, ""):
                    add("error", "C1", r.path, f"missing mplpb:{f}")
            if r.fields.get("status", "") and r.status not in STATUSES:
                add("error", "C4", r.path, f"status is '{r.status}', not current or retired")
            if r.hash and not r.intact:
                add("error", "C2", r.path, "content does not match its hash; altered after writing")
            if r.fields.get("origin", "") and r.origin not in ORIGINS:
                add("error", "C4", r.path, f"origin is '{r.origin}', not human or machine")
            for label, refs in (("derived-from", r.derived_from), ("supersedes", r.supersedes)):
                for ref in refs:
                    target = self.by_id.get(ref.id, [])
                    if not target:
                        add("error", "C5", r.path, f"{label} names {ref.id}, which is not in this folder")
                    elif not ref.hash:
                        add("warning", "C7", r.path, f"{label} names {ref.id} without its hash")
                    elif not any(t.hash_actual == ref.hash for t in target):
                        add("error", "C6", r.path,
                            f"{label} pins {ref.id} at a hash no page has; the parent changed")
            if self._has_cycle(r):
                add("error", "C12", r.path, "lineage loops back on itself")
            elif r.depth_declared is not None:
                implied = self.derived_depth(r)
                if r.depth_declared != implied:
                    add("error", "C8", r.path,
                        f"declares depth {r.depth_declared}; its lineage implies {implied}")
            if r.id in self.superseded_by and r.status == "current":
                by = ", ".join(s.id for s in self.superseded_by[r.id])
                add("warning", "C9", r.path,
                    f"still says current but is superseded by {by}; read as retired")
            if r.not_for:
                from .reader import declared_terms, terms
                both = sorted(terms(r.not_for) & declared_terms(r))
                if both:
                    add("warning", "C15", r.path,
                        "not-for repeats words the page declares; they are ignored: " + ", ".join(both))
            if r.kind == "pointer":
                if not r.points_to:
                    add("error", "C11", r.path, "pointer has no mplpb:points-to")
                elif not (self.root / r.points_to).is_dir():
                    add("warning", "C11", r.path, f"pointer target {r.points_to} is not reachable")
            if self.effective_status(r) == "current":
                for ref in r.supersedes:
                    current_successors.setdefault(ref.id, []).append(r)
        for pred, succs in sorted(current_successors.items()):
            if len(succs) > 1:
                names = ", ".join(s.id for s in succs)
                for s in succs:
                    add("error", "C10", s.path, f"fork: {names} are all current and all supersede {pred}")
        out.extend(verify_log(self))
        return out

    def _has_cycle(self, r: Record) -> bool:
        stack = [(r, frozenset([r.path]))]
        while stack:
            cur, seen = stack.pop()
            for ref in list(cur.derived_from) + list(cur.supersedes):
                p = self.resolve(ref)
                if p is None:
                    continue
                if p.path in seen:
                    return True
                stack.append((p, seen | {p.path}))
        return False


# ---------------------------------------------------------------------------
# The log: an append-only, hash-chained list of what was written and when.
# ---------------------------------------------------------------------------

def log_path(root: Path) -> Path:
    return Path(root) / LOG_DIR / LOG_NAME


def read_log(root: Path) -> List[dict]:
    p = log_path(root)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                out.append({"_unreadable": line})
    return out


def _entry_hash(entry: dict) -> str:
    body = {k: v for k, v in entry.items() if k != "entry_hash"}
    canon = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _append_log(root: Path, event: str, rec_id: str, rec_hash: str, path: str,
                when: str, note: str = "") -> None:
    p = log_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    prior = read_log(root)
    entry = {
        "seq": len(prior) + 1, "time": when, "event": event, "id": rec_id,
        "hash": rec_hash, "path": path, "note": note,
        "prev": prior[-1].get("entry_hash", "") if prior else "",
    }
    entry["entry_hash"] = _entry_hash(entry)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")


def verify_log(ledger: Ledger) -> List[Finding]:
    out: List[Finding] = []
    rel = f"{LOG_DIR}/{LOG_NAME}"
    entries = read_log(ledger.root)
    prev = ""
    logged = set()
    for i, e in enumerate(entries, 1):
        if "_unreadable" in e:
            out.append(Finding("error", "C14", rel, f"line {i} is not readable"))
            break
        if e.get("prev", "") != prev or e.get("entry_hash") != _entry_hash(e) or e.get("seq") != i:
            out.append(Finding("error", "C14", rel, f"chain breaks at line {i}; the log was edited"))
            break
        prev = e["entry_hash"]
        logged.add((e.get("id"), e.get("hash")))
    for r in ledger.records:
        if r.kind == "index" or not r.hash:
            continue
        if (r.id, r.hash) not in logged:
            out.append(Finding("warning", "C14", r.path, "page is not in the log; written by hand or outside this tool"))
    return out


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

@contextmanager
def ledger_lock(root: Path, ttl: float = 30.0, wait: float = 5.0) -> Iterator[None]:
    """One writer at a time. A lock file older than ttl belonged to a dead writer."""
    d = Path(root) / LOG_DIR
    d.mkdir(parents=True, exist_ok=True)
    lock = d / LOCK_NAME
    deadline = time.time() + wait
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {time.time():.0f}\n".encode())
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > ttl:
                    lock.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.time() > deadline:
                raise LedgerBusy(f"another writer holds {lock}")
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def _atomic_write(path: Path, text: str, *, must_be_new: bool) -> None:
    if must_be_new and path.exists():
        raise FileExistsError(f"{path} exists; a ledger page is never overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(str(tmp), str(path))


def _id_prefix(doc_id: str) -> str:
    m = re.match(r"^(.*?)-\d+$", doc_id)
    return m.group(1) if m else doc_id


def allocate_id(ledger: Ledger, prefix: str) -> str:
    """Identifiers are allocated, not chosen. Call only while holding the lock."""
    pat = re.compile(r"^" + re.escape(prefix) + r"-(\d+)$")
    seen = [int(m.group(1)) for i in ledger.by_id for m in [pat.match(i)] if m]
    seen += [int(m.group(1)) for e in read_log(ledger.root)
             for m in [pat.match(str(e.get("id", "")))] if m]
    return f"{prefix}-{max(seen, default=0) + 1:04d}"


def _must_resolve(ledger: Ledger, ids: Iterable[str], why: str) -> List[Record]:
    out = []
    for i in ids:
        recs = ledger.by_id.get(i, [])
        if not recs:
            raise KeyError(f"{why}: no record {i} in this folder")
        if len(recs) > 1:
            raise ValueError(f"{why}: id {i} is held by more than one page")
        if ledger.quarantine_reason(recs[0]):
            raise ValueError(f"{why}: {i} is {ledger.quarantine_reason(recs[0])}; refusing to build on it")
        out.append(recs[0])
    return out


def write(root, *, title: str, scope: str, when_to_use: str = "", not_for: str = "",
          body: str = "",
          body_html: Optional[str] = None, doc_id: Optional[str] = None,
          prefix: str = "DOC", directory: str = "", origin: str = "human",
          owner: str = "", derived_from: Sequence[str] = (), supersedes: Sequence[str] = (),
          ratified_by: str = "", kind: str = "page", points_to: str = "",
          when: Optional[str] = None, event: str = "write", note: str = "",
          _locked: bool = False) -> Record:
    """Write one new page. Nothing that exists is changed except the status
    line of a page this one supersedes, and that happens last."""
    root = Path(root)
    if origin not in ORIGINS:
        raise ValueError("origin must be human or machine")
    if not scope.strip():
        raise ValueError("a record must declare a scope")
    when = when or utc_now()

    def go() -> Record:
        ledger = Ledger(root)
        parents = _must_resolve(ledger, derived_from, "derived-from")
        olds = _must_resolve(ledger, supersedes, "supersedes")
        for o in olds:
            if ledger.effective_status(o) != "current":
                raise ValueError(f"{o.id} is already retired; revise its current successor")
        new_id = doc_id or allocate_id(ledger, prefix)
        if new_id in ledger.by_id:
            raise ValueError(f"id {new_id} is taken")
        if ratified_by:
            depth = 0
        else:
            d_src = (1 + max(ledger.depth(p) for p in parents)) if parents else (1 if origin == "machine" else 0)
            d_rev = max((ledger.depth(o) for o in olds), default=0)
            depth = max(d_src, d_rev)
        fields = {
            "document-id": new_id, "kind": "" if kind == "page" else kind,
            "scope": scope, "when-to-use": when_to_use, "not-for": not_for,
            "status": "current",
            "origin": origin, "origin-depth": str(depth),
            "derived-from": format_refs([Ref(p.id, p.hash_actual) for p in parents]),
            "supersedes": format_refs([Ref(o.id, o.hash_actual) for o in olds]),
            "ratified-by": ratified_by, "points-to": points_to,
            "owner": owner, "updated": when,
        }
        inner = body_html if body_html is not None else plain_to_html(body)
        page_body = f"<h1>{html.escape(' '.join(title.split()), quote=False)}</h1>\n{inner}".strip()
        target = root / directory / f"{new_id.lower()}.html"
        _atomic_write(target, render_page(fields, title, page_body), must_be_new=True)
        rec = read_page(root, target)
        _append_log(root, event, rec.id, rec.hash, rec.path, when, note)
        for o in olds:                                  # retire last
            _retire_in_place(root, o, when, f"superseded by {rec.id}")
        return rec

    if _locked:
        return go()
    with ledger_lock(root):
        return go()


def _retire_in_place(root: Path, old: Record, when: str, note: str) -> None:
    p = root / old.path
    text = p.read_text(encoding="utf-8")
    _atomic_write(p, upsert_meta(text, "status", "retired"), must_be_new=False)
    _append_log(root, "retire", old.id, old.hash, old.path, when, note)


def _current(ledger: Ledger, doc_id: str) -> Record:
    recs = _must_resolve(ledger, [doc_id], "revise")
    if ledger.effective_status(recs[0]) != "current":
        heads = [h.id for h in ledger.history(doc_id)[-1:]]
        raise ValueError(f"{doc_id} is retired; its current successor is {', '.join(heads)}")
    return recs[0]


def revise(root, doc_id: str, *, title: Optional[str] = None, scope: Optional[str] = None,
           when_to_use: Optional[str] = None, not_for: Optional[str] = None,
           body: Optional[str] = None,
           origin: str = "human", owner: str = "", ratified_by: str = "",
           when: Optional[str] = None, note: str = "", new_id: Optional[str] = None,
           _event: str = "revise") -> Record:
    """A change writes a new page and retires the old one. It does not overwrite."""
    root = Path(root)
    with ledger_lock(root):
        old = _current(Ledger(root), doc_id)
        inner = None
        if body is None:
            inner = re.sub(r"^\s*<h1>.*?</h1>\s*", "", old.body_html, count=1, flags=re.S)
        return write(
            root, title=title if title is not None else old.title,
            scope=scope if scope is not None else old.scope,
            when_to_use=when_to_use if when_to_use is not None else old.when_to_use,
            not_for=not_for if not_for is not None else old.not_for,
            body=body or "", body_html=inner, doc_id=new_id, prefix=_id_prefix(old.id),
            directory=os.path.dirname(old.path), origin=origin,
            owner=owner or old.fields.get("owner", ""),
            derived_from=[r.id for r in old.derived_from], supersedes=[old.id],
            ratified_by=ratified_by, kind=old.kind, points_to=old.points_to,
            when=when, event=_event, note=note, _locked=True,
        )


def derive(root, from_ids: Sequence[str], *, title: str, scope: str, when_to_use: str = "",
           body: str = "", origin: str = "machine", **kw) -> Record:
    """A derivation writes a new page and adds one to the depth."""
    if not from_ids:
        raise ValueError("a derivation names at least one parent")
    if not kw.get("prefix"):
        kw["prefix"] = _id_prefix(from_ids[0])
    return write(root, title=title, scope=scope, when_to_use=when_to_use, body=body,
                 origin=origin, derived_from=list(from_ids), event="derive", **kw)


def ratify(root, doc_id: str, who: str, *, when: Optional[str] = None, note: str = "",
           new_id: Optional[str] = None) -> Record:
    """A named person stands behind a page. Depth returns to 0; the lineage stays."""
    if not who.strip():
        raise ValueError("ratification needs a name")
    old = _current(Ledger(Path(root)), doc_id)
    return revise(root, doc_id, origin=old.origin, ratified_by=who.strip(), when=when,
                  note=note or f"ratified by {who.strip()}", new_id=new_id, _event="ratify")


def withdraw(root, doc_id: str, *, when: Optional[str] = None, note: str = "") -> None:
    """Retire a page with no successor. It stays in the folder."""
    root = Path(root)
    with ledger_lock(root):
        old = _current(Ledger(root), doc_id)
        _retire_in_place(root, old, when or utc_now(), note or "withdrawn")


def seal(root, *, when: Optional[str] = None) -> List[str]:
    """Adopt pages that were written by hand or by an earlier MPLPB tool.

    A page that declares an id but no hash gets one, its references are
    pinned to the hashes of the pages they name, and its depth is recorded.
    A page whose declared hash does not match is never re-sealed.
    """
    root = Path(root)
    when = when or utc_now()
    sealed: List[str] = []
    with ledger_lock(root):
        final = False
        while True:
            ledger = Ledger(root)
            todo = [r for r in ledger.records if r.kind != "index" and not r.hash]
            if not todo:
                break
            progressed = False
            for r in todo:
                refs = list(r.derived_from) + list(r.supersedes)
                waiting = [x for x in refs
                           if any(not t.hash and t.path != r.path for t in ledger.by_id.get(x.id, []))]
                if waiting and not final:
                    continue
                p = root / r.path
                text = p.read_text(encoding="utf-8")

                def pin(refs_: List[Ref]) -> str:
                    out = []
                    for x in refs_:
                        t = ledger.resolve(x)
                        out.append(Ref(x.id, t.hash_actual) if (t and t.hash and t.intact) else Ref(x.id))
                    return format_refs(out)

                if r.derived_from:
                    text = upsert_meta(text, "derived-from", pin(r.derived_from))
                if r.supersedes:
                    text = upsert_meta(text, "supersedes", pin(r.supersedes))
                if not r.fields.get("origin", ""):
                    text = upsert_meta(text, "origin", "human")
                elif r.origin not in ORIGINS:        # taught, derived, ratified
                    text = upsert_meta(text, "origin", "machine")
                text = upsert_meta(text, "origin-depth", str(ledger.depth(r)))
                if not r.fields.get("status", ""):
                    text = upsert_meta(text, "status", "current")
                text = upsert_meta(text, "hash", parse_page(text, r.path).hash_actual)
                _atomic_write(p, text, must_be_new=False)
                done = read_page(root, p)
                _append_log(root, "adopt", done.id, done.hash, done.path, when, "sealed")
                sealed.append(done.path)
                progressed = True
                break                       # re-crawl so later pins see this hash
            if not progressed:
                if final:
                    break
                final = True
    return sealed


def build_index(root, title: str = "Main Index") -> Path:
    """Write index.html: a derived page for people. The reader never answers from it."""
    root = Path(root)
    ledger = Ledger(root)
    rows_cur, rows_ret = [], []
    for r in ledger.records:
        if r.kind == "index":
            continue
        row = (f'<li><a href="{html.escape(r.path, quote=True)}">{html.escape(r.title)}</a> '
               f'<code>{html.escape(r.id)}</code> &middot; depth {ledger.depth(r)}<br>'
               f'{html.escape(r.scope)}</li>')
        (rows_cur if ledger.effective_status(r) == "current" else rows_ret).append(row)
    body = (f"<h1>{html.escape(title)}</h1>\n<p>Derived from the pages below. "
            "Rebuild it at any time; it carries no authority.</p>\n"
            f"<h2>Current</h2>\n<ul>\n" + "\n".join(rows_cur) + "\n</ul>\n"
            f"<h2>Retired</h2>\n<ul>\n" + "\n".join(rows_ret) + "\n</ul>")
    text = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<title>{html.escape(title)}</title>\n"
            '<meta name="mplpb:kind" content="index">\n</head>\n<body>\n' + body + "\n</body>\n</html>\n")
    target = root / "index.html"
    _atomic_write(target, text, must_be_new=False)
    return target
