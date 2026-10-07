"""The answer rule.

    A(q) = R               if exactly one current R owns q
           ambiguous       if two or more own q
           not in corpus   if none own q

Ownership is decided from what pages declare about themselves, in their
scope and when-to-use fields, and from nothing else. Page prose is what is
returned. It is never what is matched. There is no ranking, no score, and
no fill from outside the folder.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .ledger import Ledger
from .record import Record

RETURN = "return"
AMBIGUOUS = "ambiguous"
NOT_IN_CORPUS = "not_in_corpus"

STOPWORDS = frozenset("""
a an the and or but nor of to in on at for from by with without within into onto
is are was were be been being am it its this that these those as if then than so
do does did doing can could should would will shall may might must i my me mine we
our us you your they their them he she his her what which who whom whose when
where why how there here not no yes about over under after before while during
up down out off again each any all some more most other such only own same too
very just also have has had having get got please tell need want use used using
""".split())

MAX_HOPS = 4


def fold(token: str) -> str:
    """The only normalisation: a trailing plural s. No stemmer, no synonyms."""
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def terms(text: str) -> Set[str]:
    words = re.findall(r"[a-z0-9]+", re.sub(r"['\u2019]s\b", "", (text or "").lower()))
    return {fold(t) for t in words if t not in STOPWORDS}


def declared_terms(r: Record) -> Set[str]:
    return terms(r.scope + " " + r.when_to_use)


@dataclass(frozen=True)
class Profile:
    """What a deployment is willing to serve.

    max_depth     records deeper than this are withheld (None: no limit)
    min_coverage  share of a question's content words that must be declared
                  somewhere in the corpus before any page may own it
    """
    name: str
    max_depth: Optional[int]
    min_coverage: float


PROFILES: Dict[str, Profile] = {
    "lab": Profile("lab", 2, 0.34),
    "internal": Profile("internal", 1, 0.5),
    "external": Profile("external", 0, 1.0),
}
DEFAULT_PROFILE = "internal"


@dataclass
class Answer:
    kind: str
    question: str
    profile: Profile
    root: str
    record: Optional[Record] = None
    depth: int = 0
    candidates: List[Tuple[Record, List[str]]] = field(default_factory=list)
    reason: str = ""
    known: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    common: List[str] = field(default_factory=list)
    withheld: List[Tuple[Record, int]] = field(default_factory=list)
    quarantined: int = 0
    route: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.record.text if (self.kind == RETURN and self.record) else ""

    def citation(self) -> str:
        return cite(self.record, self.depth) if self.record else ""

    def to_dict(self) -> dict:
        return {
            "kind": self.kind, "question": self.question, "profile": self.profile.name,
            "root": self.root, "reason": self.reason,
            "id": self.record.id if self.record else None,
            "path": self.record.path if self.record else None,
            "hash": self.record.hash if self.record else None,
            "depth": self.depth if self.record else None,
            "text": self.text,
            "candidates": [{"id": r.id, "path": r.path, "scope": r.scope, "matched": m}
                           for r, m in self.candidates],
            "known": self.known, "unknown": self.unknown, "common": self.common,
            "withheld": [{"id": r.id, "depth": d} for r, d in self.withheld],
            "quarantined": self.quarantined, "route": self.route,
        }


def cite(r: Record, depth: int) -> str:
    """Longer than anyone wants. There is no shorter form."""
    parts = [r.id, r.path, r.status or "?", f"origin {r.origin} d{depth}"]
    if r.ratified_by:
        parts.append(f"ratified by {r.ratified_by}")
    parts += [f"sha256:{r.short_hash()}", "local"]
    return "[" + " \u00b7 ".join(parts) + "]"


def decide(known: Set[str], declared: Dict[str, Set[str]]) -> Tuple[str, List[str]]:
    """The rule itself, on bare sets. Shared by the reader and the kill test.

    declared maps a key to the terms that key declares. Returns the outcome
    and the keys involved: the owner, the contenders, or nothing.
    """
    if not known:
        return NOT_IN_CORPUS, []
    claimants = [k for k, t in declared.items() if t & known]
    owners = [k for k in claimants if known <= declared[k]]
    if len(owners) == 1:
        return RETURN, owners
    if len(owners) > 1:
        return AMBIGUOUS, owners
    if claimants:
        return AMBIGUOUS, claimants          # each owns part; none owns all
    return NOT_IN_CORPUS, []


def vocabulary(declared: Dict[str, Set[str]]) -> Tuple[Set[str], Set[str]]:
    """Words the corpus declares, and the ones too common to mean anything.

    A word declared by more than half the pages cannot tell them apart, so
    it grants no claim. The rule applies once there are four pages.
    """
    df = Counter(t for ts in declared.values() for t in ts)
    n = len(declared)
    common = {t for t, c in df.items() if n >= 4 and c > n / 2}
    return set(df) - common, common


def answer(root, question: str, profile: Optional[Profile] = None,
           _route: Sequence[str] = (), _visited: Sequence[str] = ()) -> Answer:
    profile = profile or PROFILES[DEFAULT_PROFILE]
    ledger = Ledger(root)
    servable = ledger.servable()
    depth = {r.path: ledger.depth(r) for r in servable}
    within = [r for r in servable
              if profile.max_depth is None or depth[r.path] <= profile.max_depth]
    kept = {r.path for r in within}
    over = [r for r in servable if r.path not in kept]
    declared = {r.path: declared_terms(r) for r in within}
    by_path = {r.path: r for r in within}
    vocab, common = vocabulary(declared)

    q = terms(question)
    content = q - common
    known = content & vocab
    out = Answer(
        kind=NOT_IN_CORPUS, question=question, profile=profile, root=str(ledger.root),
        known=sorted(known), unknown=sorted(content - known), common=sorted(q & common),
        quarantined=len(ledger.quarantined()), route=list(_route),
    )
    # A page over the depth limit is reported only where it would have
    # changed the outcome: it declares everything the served pages know of
    # the question, or, when they know nothing, any word of it.
    for r in over:
        d = declared_terms(r)
        if (known and known <= d) or (not known and d & q):
            out.withheld.append((r, ledger.depth(r)))
    visited = list(_visited) + [str(ledger.root.resolve())]
    pointers = [r for r in within if r.kind == "pointer"]
    if not content:
        out.reason = "the question has no content words"
        return out
    if not known:
        out.reason = "no current page declares any word in the question"
        return _fan_out(out, ledger, pointers, question, profile, visited)
    coverage = len(known) / len(content)
    if coverage < profile.min_coverage:
        out.reason = (f"only {len(known)} of {len(content)} content words are declared by any page; "
                      f"profile {profile.name} requires {profile.min_coverage:.0%}")
        return _fan_out(out, ledger, pointers, question, profile, visited)

    kind, keys = decide(known, declared)
    out.kind = kind
    out.candidates = [(by_path[k], sorted(declared[k] & known)) for k in keys]
    if kind == AMBIGUOUS:
        whole = all(known <= declared[k] for k in keys)
        out.reason = ("two or more current pages own this question" if whole
                      else "no single page owns the whole question; each of these owns part")
        return out
    if kind == NOT_IN_CORPUS:
        out.reason = "no current page declares any word in the question"
        return out

    rec = by_path[keys[0]]
    out.record, out.depth = rec, depth[rec.path]
    if rec.kind != "pointer":
        out.reason = "exactly one current page owns this question"
        return out

    # A hub may point at the owner. It may not answer as the owner.
    target = (ledger.root / rec.points_to).resolve()
    hop = f"{rec.id} points to {rec.points_to}"
    out.kind, out.record = NOT_IN_CORPUS, None
    out.route = list(_route) + [hop]
    if not rec.points_to or not target.is_dir():
        out.reason = f"owner known ({rec.title}) but not reachable; the hub does not answer for it"
        return out
    if str(target) in visited or len(visited) >= MAX_HOPS:
        out.reason = "pointers loop; no owner reached"
        return out
    return answer(target, question, profile, _route=out.route, _visited=visited)


def _fan_out(out: Answer, ledger: Ledger, pointers: List[Record], question: str,
             profile: Profile, visited: List[str]) -> Answer:
    """No pointer declared the question, so ask each corpus the hub points at.

    Each corpus still decides for itself from its own declarations. Exactly
    one may answer. Two answering is ambiguity between corpora, and the hub
    names them and stops. It never merges, and it never answers itself.
    """
    if not pointers or len(visited) >= MAX_HOPS:
        return out
    subs: List[Tuple[Record, Answer]] = []
    for p in pointers:
        target = (ledger.root / p.points_to).resolve()
        if not p.points_to or not target.is_dir() or str(target) in visited:
            continue
        hop = f"{p.id} points to {p.points_to} (no pointer declared the question; each corpus was asked)"
        subs.append((p, answer(target, question, profile,
                               _route=list(out.route) + [hop], _visited=visited)))
    claims = [(p, a) for p, a in subs if a.kind in (RETURN, AMBIGUOUS)]
    if len(claims) == 1:
        return claims[0][1]
    if len(claims) > 1:
        out.kind = AMBIGUOUS
        out.candidates = [(p, a.known) for p, a in claims]
        out.reason = "more than one corpus claims this question; the hub does not merge them"
    return out


def render(a: Answer, why: bool = False) -> str:
    lines: List[str] = []
    if a.kind == RETURN and a.record:
        body = a.text.splitlines()
        if body and body[0].strip() == a.record.title.strip():
            body = body[1:]                 # the page's own heading
        lines += [a.record.title, ""]
        lines += ["  " + ln for ln in body]
        lines += ["", "  " + a.citation()]
    elif a.kind == AMBIGUOUS:
        lines += ["Ambiguous. " + a.reason[0].upper() + a.reason[1:] + ".",
                  "  Nothing is blended. Narrow the question to one of:", ""]
        for r, matched in a.candidates:
            lines += [f"  {r.id}  {r.title}", f"      scope: {r.scope}",
                      f"      declares: {', '.join(matched)}"]
    else:
        lines += ["Not in the corpus.", "  " + a.reason[0].upper() + a.reason[1:] + "."]
        if a.unknown:
            lines.append("  Not declared by any current page: " + ", ".join(a.unknown))
        lines.append("  Nothing is answered from outside the folder.")
    for r, d in a.withheld:
        limit = a.profile.max_depth
        lines.append(f"  withheld by profile {a.profile.name}: {r.id} is depth {d}, limit {limit}")
    for hop in a.route:
        lines.append("  route: " + hop)
    if a.quarantined:
        lines.append(f"  note: {a.quarantined} page(s) quarantined; run validate")
    if why:
        lines += ["", "  why:", f"    root        {a.root}", f"    profile     {a.profile.name} "
                  f"(max depth {a.profile.max_depth}, coverage {a.profile.min_coverage:.0%})",
                  f"    declared    {', '.join(a.known) or '-'}",
                  f"    undeclared  {', '.join(a.unknown) or '-'}",
                  f"    too common  {', '.join(a.common) or '-'}"]
    return "\n".join(lines)
