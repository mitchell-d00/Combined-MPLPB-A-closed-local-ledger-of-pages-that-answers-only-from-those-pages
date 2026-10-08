"""The kill test.

Strip the declared fields, run the same questions, and see what changes.

Three arms read the same pages:

  scoped        the reader in this package: ownership from declared fields
  stripped      the same rule and the same code, but the declared fields are
                gone, so the scope step finds nothing and only the prose step
                can decide; and status is gone, so retired pages cannot be
                told from current ones
  top1          what a plain search does with the stripped pages: return the
                page sharing the most words, refuse only when nothing shares
                any. It has no way to say "ambiguous".

Scoring is mechanical against answers fixed in the probe file. No arm is
told which arm it is, and the scorer has no branch on a probe's id.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .ledger import Ledger
from .baselines import LexicalIndex
from .reader import (
    AMBIGUOUS, NOT_IN_CORPUS, PROFILES, RETURN, Profile, answer, decide, terms,
)

ARMS = ("scoped", "stripped", "top1")
OUTCOMES = ("correct", "wrong_return", "wrong_refusal")


@dataclass(frozen=True)
class Result:
    kind: str
    doc: Optional[str]      # id of the returned page, if any


def stripped_pages(ledger: Ledger) -> Dict[str, str]:
    """path -> prose. Every mplpb field is gone, and so are index pages."""
    return {r.path: r.text for r in ledger.records if r.kind != "index"}


def write_stripped(ledger: Ledger, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = sorted(stripped_pages(ledger).items())
    for n, (_path, text) in enumerate(pages, 1):
        body = "\n".join(f"<p>{ln}</p>" for ln in text.splitlines())
        (out_dir / f"{n:04d}.html").write_text(
            f"<!doctype html>\n<html><head><meta charset=\"utf-8\"></head>\n<body>\n{body}\n</body></html>\n",
            encoding="utf-8")
    return len(pages)


def run_scoped(root: Path, q: str, profile: Profile) -> Result:
    a = answer(root, q, profile)
    return Result(a.kind, a.record.id if a.record else None)


def run_stripped(prose: Dict[str, set], path_to_id: Dict[str, str], q: str) -> Result:
    nothing_declared = {path: set() for path in prose}
    kind, keys, _step = decide(terms(q), nothing_declared, prose)
    return Result(kind, path_to_id[keys[0]] if kind == RETURN else None)


def run_top1(prose: Dict[str, set], path_to_id: Dict[str, str], q: str) -> Result:
    qt = terms(q)
    best, best_score = None, 0
    for path in sorted(prose):
        score = len(qt & prose[path])
        if score > best_score:
            best, best_score = path, score
    if best is None:
        return Result(NOT_IN_CORPUS, None)
    return Result(RETURN, path_to_id[best])


def score(expect_kind: str, expect_doc: Optional[str], got: Result) -> str:
    if got.kind == expect_kind and (expect_kind != RETURN or got.doc == expect_doc):
        return "correct"
    return "wrong_return" if got.kind == RETURN else "wrong_refusal"


def check_hash(probes_path: Path) -> str:
    side = probes_path.with_suffix(".sha256")
    if not side.exists():
        return "no hash file"
    want = side.read_text(encoding="utf-8").split()[0]
    got = hashlib.sha256(probes_path.read_bytes()).hexdigest()
    return "OK" if want == got else "MISMATCH: the probes were edited after they were frozen"


def run(root, probes_path, profile: Optional[Profile] = None) -> dict:
    root, probes_path = Path(root), Path(probes_path)
    profile = profile or PROFILES["internal"]
    spec = json.loads(probes_path.read_text(encoding="utf-8"))
    ledger = Ledger(root)
    raw = stripped_pages(ledger)
    prose = {p: terms(t) for p, t in raw.items()}
    path_to_id = {r.path: r.id for r in ledger.records}
    pools = {'stripped': raw,
             'current': {r.path: r.text for r in ledger.servable() if r.kind == 'page'
                         and (profile.max_depth is None or ledger.depth(r) <= profile.max_depth)}}
    indexes = {pool: LexicalIndex(pages) for pool, pages in pools.items()}
    lexical = {method + '_' + pool: {o: 0 for o in OUTCOMES}
               for pool in pools for method in ('bm25', 'tfidf')}
    lexical_rows = []

    classes: Dict[str, dict] = {}
    rows: List[dict] = []
    for probe in spec["probes"]:
        ranked_row = {'id': probe['id'], 'arms': {}}
        for pool, index in indexes.items():
            for method in ('bm25', 'tfidf'):
                arm = method + '_' + pool
                key = index.top(probe['q'], method)
                result = Result(RETURN if key else NOT_IN_CORPUS, path_to_id[key] if key else None)
                outcome = score(probe['expect'], probe.get('doc'), result)
                lexical[arm][outcome] += 1
                ranked_row['arms'][arm] = {'kind': result.kind, 'doc': result.doc, 'score': outcome}
        lexical_rows.append(ranked_row)
        got = {
            "scoped": run_scoped(root, probe["q"], profile),
            "stripped": run_stripped(prose, path_to_id, probe["q"]),
            "top1": run_top1(prose, path_to_id, probe["q"]),
        }
        c = classes.setdefault(probe["class"], {
            "n": 0, **{arm: {o: 0 for o in OUTCOMES} for arm in ARMS}})
        c["n"] += 1
        row = {"id": probe["id"], "class": probe["class"], "q": probe["q"],
               "expect": probe["expect"], "doc": probe.get("doc")}
        for arm in ARMS:
            s = score(probe["expect"], probe.get("doc"), got[arm])
            c[arm][s] += 1
            row[arm] = {"kind": got[arm].kind, "doc": got[arm].doc, "score": s}
        rows.append(row)

    meta = spec.get("classes", {})
    for name, c in classes.items():
        c["circular"] = list(meta.get(name, {}).get("circular", []))
        c["note"] = meta.get(name, {}).get("note", "")
        # Control at ceiling: the stripped arm is already perfect, so this
        # class can only show the declared fields doing no better or worse.
        # It stays in the totals, because "worse" is a result.
        c["void"] = c["stripped"]["correct"] == c["n"]

    # The same reader with the prose step switched off: scope or nothing.
    scope_only = Profile(profile.name + ", scope only", profile.max_depth, False)
    unheeded = Profile(profile.name + ", not-for ignored", profile.max_depth, profile.prose, False)
    no_field = {o: 0 for o in OUTCOMES}
    for probe in spec["probes"]:
        no_field[score(probe["expect"], probe.get("doc"),
                       run_scoped(root, probe["q"], unheeded))] += 1
    variant = {o: 0 for o in OUTCOMES}
    by_step = {"scope": 0, "prose": 0}
    for probe in spec["probes"]:
        variant[score(probe["expect"], probe.get("doc"),
                      run_scoped(root, probe["q"], scope_only))] += 1
        a = answer(root, probe["q"], profile)
        if a.kind == RETURN:
            by_step[a.matched_on] += 1

    return {
        "corpus": str(root), "probes": str(probes_path), "probe_hash": check_hash(probes_path),
        "profile": {"name": profile.name, "max_depth": profile.max_depth,
                    "prose": profile.prose},
        "pages": {"scoped_current": len(ledger.servable()), "stripped": len(raw)},
        "n": len(rows), "classes": classes, "scope_only": variant, "not_for_ignored": no_field,
        "returns_by_step": by_step, "rows": rows,
        "lexical_baselines": lexical, "lexical_rows": lexical_rows,
    }


def _pct(k: int, n: int) -> str:
    return f"{100.0 * k / n:5.1f}%" if n else "    -"


def render(res: dict) -> str:
    L: List[str] = []
    L.append(f"corpus   {res['corpus']}  ({res['pages']['scoped_current']} current pages served; "
             f"{res['pages']['stripped']} pages in the stripped arms)")
    L.append(f"probes   {res['n']}  hash: {res['probe_hash']}")
    p = res["profile"]
    L.append(f"profile  {p['name']} (max depth {p['max_depth']}, prose {'on' if p['prose'] else 'off'})")
    L.append("")
    L.append(f"{'class':22}{'n':>3}  {'scoped':>8}{'stripped':>10}{'top1':>8}   notes")
    L.append("-" * 78)
    tot = {arm: 0 for arm in ARMS}
    fair = {arm: 0 for arm in ARMS}
    fair_n = 0
    for name, c in res["classes"].items():
        notes = []
        if c["circular"]:
            notes.append("circular for " + ", ".join(c["circular"]))
        if c["void"]:
            notes.append("control at ceiling")
        L.append(f"{name:22}{c['n']:>3}  " + _pct(c["scoped"]["correct"], c["n"]).rjust(8)
                 + _pct(c["stripped"]["correct"], c["n"]).rjust(10)
                 + _pct(c["top1"]["correct"], c["n"]).rjust(8) + "   " + "; ".join(notes))
        for arm in ARMS:
            tot[arm] += c[arm]["correct"]
        if not c["circular"]:
            fair_n += c["n"]
            for arm in ARMS:
                fair[arm] += c[arm]["correct"]
    L.append("-" * 78)
    L.append(f"{'all probes':22}{res['n']:>3}  " + _pct(tot['scoped'], res['n']).rjust(8)
             + _pct(tot['stripped'], res['n']).rjust(10) + _pct(tot['top1'], res['n']).rjust(8))
    L.append(f"{'non-circular only':22}{fair_n:>3}  " + _pct(fair['scoped'], fair_n).rjust(8)
             + _pct(fair['stripped'], fair_n).rjust(10) + _pct(fair['top1'], fair_n).rjust(8))
    L.append("")
    L.append("what each arm got wrong, and how (all probes):")
    L.append(f"{'':22}{'wrong page or false return':>28}{'false refusal':>16}")
    for arm in ARMS:
        wr = sum(c[arm]["wrong_return"] for c in res["classes"].values())
        wf = sum(c[arm]["wrong_refusal"] for c in res["classes"].values())
        L.append(f"{arm:22}{wr:>28}{wf:>16}")
    L.append("")
    v, st = res["scope_only"], res["returns_by_step"]
    L.append(f"scoped returns decided by scope: {st['scope']}   by prose: {st['prose']}")
    L.append(f"scoped with the prose step off:  {v['correct']} correct / "
             f"{v['wrong_return']} wrong return / {v['wrong_refusal']} wrong refusal")
    n = res["not_for_ignored"]
    L.append(f"scoped with not-for ignored:     {n['correct']} correct / "
             f"{n['wrong_return']} wrong return / {n['wrong_refusal']} wrong refusal")
    if res.get('lexical_baselines'):
        L += ['', 'lexical baselines (fixed parameters; top one; no ambiguity):',
              'current = same valid current page pool; stripped = includes retired pages']
        for arm, stats in res['lexical_baselines'].items():
            L.append(f"{arm:22} {stats['correct']} correct / {stats['wrong_return']} wrong return / "
                     f"{stats['wrong_refusal']} wrong refusal")
    return "\n".join(L)
