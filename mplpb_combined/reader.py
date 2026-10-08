"""The answer rule.

    A(q) = R               if exactly one current R owns q
           ambiguous       if two or more own q
           not in corpus   if none own q

Ownership is decided in two steps, and scope always goes first.

  1. Scope.  A page owns the question when its scope and when-to-use fields
             declare more than half of the question's content words.
  2. Prose.  Only if no page owns it by scope: a page owns the question when
             every content word appears somewhere on the page.

Before either step, a page is set aside if the question contains a word from
the page's own not-for field: the page has said this is not its question.

At either step, a page whose matched words strictly contain another owner's
is the more specific and the other drops out. One owner left: return it.
Two or more: ambiguous. There is no ranking, no score, and no fill from
outside the folder.
"""
from __future__ import annotations
from .delivery import external_restriction, authorship, clarification

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
long much many often
""".split())

MAX_HOPS = 4


_VOWEL = re.compile(r"[aeiouy]")


def stem(token: str) -> str:
    """A light suffix stripper, so that firing, fired and fire are one word.

    Plural s, then ing or ed, then a doubled final consonant, then a final e.
    A stem is kept only if it still has three letters and a vowel. It is
    crude, it is deterministic, and it has no word list.
    """
    t = token
    if t.isdigit() or len(t) <= 3:
        return t
    if t.endswith("ies"):
        t = t[:-3] + "y"
    elif t.endswith("s") and not t.endswith(("ss", "us", "is")):
        t = t[:-1]
    for suffix in ("ing", "ed"):
        if t.endswith(suffix) and not t.endswith("eed"):
            base = t[: -len(suffix)]
            if len(base) >= 3 and _VOWEL.search(base):
                if len(base) > 3 and base[-1] == base[-2] and base[-1] not in "aeioulsz":
                    base = base[:-1]
                t = base
            break
    if len(t) > 3 and t.endswith("e"):
        t = t[:-1]
    return t


def terms(text: str) -> Set[str]:
    words = re.findall(r"[a-z0-9]+", re.sub(r"['\u2019]s\b", "", (text or "").lower()))
    return {stem(t) for t in words if t not in STOPWORDS}


def declared_terms(r: Record) -> Set[str]:
    return terms(r.scope + " " + r.when_to_use)


def not_for_terms(r: Record) -> Set[str]:
    """Words a page says are not its business. A word the page also declares
    as its scope cannot be both, and scope wins."""
    return terms(r.not_for) - declared_terms(r)


def page_terms(r: Record) -> Set[str]:
    """Everything a page says: its declarations, its title and its prose."""
    return declared_terms(r) | terms(r.title + " " + r.text)


@dataclass(frozen=True)
class Profile:
    """What a deployment is willing to serve.

    max_depth  records deeper than this are withheld (None: no limit)
    prose      whether a question no page owns by scope may still be owned
               by the one page whose text contains every word of it
    """
    name: str
    max_depth: Optional[int]
    prose: bool = True
    not_for: bool = True        # honour the not-for field; off only for comparison


PROFILES: Dict[str, Profile] = {
    "lab": Profile("lab", 2, True),
    "internal": Profile("internal", 1, True),
    "external": Profile("external", 0, False),
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
    matched_on: str = ""            # "scope" or "prose"
    set_aside: List[Tuple[Record, List[str]]] = field(default_factory=list)
    withheld: List[Tuple[Record, int]] = field(default_factory=list)
    quarantined: int = 0
    route: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.record.text if (self.kind == RETURN and self.record) else ""

    def citation(self) -> str:
        if not self.record:
            return ""
        return cite(self.record, self.depth, by_prose=self.matched_on == "prose")

    def to_dict(self) -> dict:
        data = {
            "kind": self.kind, "question": self.question, "profile": self.profile.name,
            "root": self.root, "reason": self.reason,
            "id": self.record.id if self.record else None,
            "path": self.record.path if self.record else None,
            "hash": self.record.hash if self.record else None,
            "depth": self.depth if self.record else None,
            "text": self.text,
            "candidates": [{"id": r.id, "path": r.path, "scope": r.scope, "matched": m}
                           for r, m in self.candidates],
            "known": self.known, "unknown": self.unknown, "matched_on": self.matched_on,
            "withheld": [{"id": r.id, "depth": d} for r, d in self.withheld],
            "set_aside": [{"id": r.id, "not_for": w} for r, w in self.set_aside],
            "quarantined": self.quarantined, "route": self.route,
        }
        hint = clarification(terms(self.question), self.record)
        if hint:
            data["clarification"] = hint
        if self.record and authorship(self.record):
            data["source_authorship"] = authorship(self.record)
        return data


def cite(r: Record, depth: int, by_prose: bool = False) -> str:
    """Longer than anyone wants. There is no shorter form."""
    parts = [r.id, r.path, r.status or "?", f"origin {r.origin} d{depth}"]
    if r.ratified_by:
        parts.append(f"ratified by {r.ratified_by}")
    parts += [f"sha256:{r.short_hash()}", "local"]
    if by_prose:
        parts.append("matched on prose, not on declared scope")
    return "[" + " \u00b7 ".join(parts) + "]"


def owners(content: Set[str], sets: Dict[str, Set[str]], need_all: bool) -> List[str]:
    """Keys that own the question, with the less specific owners dropped."""
    found: Dict[str, Set[str]] = {}
    for key, have in sets.items():
        matched = content & have
        if (matched == content) if need_all else (2 * len(matched) > len(content)):
            found[key] = matched
    return [k for k in found if not any(found[k] < found[j] for j in found)]


def decide(content: Set[str], declared: Dict[str, Set[str]],
           full: Optional[Dict[str, Set[str]]] = None) -> Tuple[str, List[str], str]:
    """The rule itself, on bare sets. Shared by the reader and the kill test.

    Two fully named, non-subsumed declarations stop before majority can
    choose the longer one. Strict subsets retain the existing specificity rule.

    declared maps a key to the words that key declares; full maps it to every
    word on the page, or is None when prose may not be consulted. Returns the
    outcome, the keys involved, and which step decided it.
    """
    if not content:
        return NOT_IN_CORPUS, [], ""
    for step, sets, need_all in (("scope", declared, False), ("prose", full, True)):
        if sets is None:
            continue
        if not need_all:
            named = {k: have for k, have in sets.items() if have and have <= content}
            # Preserve the existing rule that strictly narrower matches lead.
            named = [k for k in named if not any(named[k] < named[j] for j in named)]
            if len(named) > 1:
                return AMBIGUOUS, named, step
        found = owners(content, sets, need_all)
        if len(found) == 1:
            return RETURN, found, step
        if len(found) > 1:
            return AMBIGUOUS, found, step
    return NOT_IN_CORPUS, [], ""


def answer(root, question: str, profile: Optional[Profile] = None,
           _route: Sequence[str] = (), _visited: Sequence[str] = ()) -> Answer:
    profile = profile or PROFILES[DEFAULT_PROFILE]
    ledger = Ledger(root)
    servable = ledger.servable()
    depth = {r.path: ledger.depth(r) for r in servable}
    within = [r for r in servable
              if profile.max_depth is None or depth[r.path] <= profile.max_depth]
    within = [r for r in within if not external_restriction(r, profile)]
    kept = {r.path for r in within}
    over = [r for r in servable if r.path not in kept]
    by_path = {r.path: r for r in within}
    declared = {r.path: declared_terms(r) for r in within}
    # A pointer routes. Its own prose is never a reason to land on it.
    full = ({r.path: (declared[r.path] if r.kind == "pointer" else page_terms(r))
             for r in within} if profile.prose else None)

    content = terms(question)
    barred: Dict[str, Set[str]] = {}
    if profile.not_for:
        for r in servable:
            hit = not_for_terms(r) & content
            if hit:
                barred[r.path] = hit
        declared = {k: v for k, v in declared.items() if k not in barred}
        if full is not None:
            full = {k: v for k, v in full.items() if k not in barred}
        over = [r for r in over if r.path not in barred]
    seen = set().union(*(full or declared).values()) if (full or declared) else set()
    said: Dict[str, str] = {}               # stem -> the word as it was asked
    for w in re.findall(r"[a-z0-9]+", re.sub(r"['\u2019]s\b", "", question.lower())):
        said.setdefault(stem(w), w)
    out = Answer(
        kind=NOT_IN_CORPUS, question=question, profile=profile, root=str(ledger.root),
        known=sorted(said.get(t, t) for t in content & seen),
        unknown=sorted(said.get(t, t) for t in content - seen),
        quarantined=len(ledger.quarantined()), route=list(_route),
    )
    out.set_aside = [(by_path[k], sorted(said.get(t, t) for t in hit))
                     for k, hit in barred.items() if k in by_path]
    # A page over the depth limit is reported only where it would have owned
    # the question had it been served.
    for r in over:
        alone_full = {r.path: page_terms(r)} if profile.prose else None
        if decide(content, {r.path: declared_terms(r)}, alone_full)[0] == RETURN:
            out.withheld.append((r, ledger.depth(r)))
    visited = list(_visited) + [str(ledger.root.resolve())]
    pointers = [r for r in within if r.kind == "pointer"]
    if not content:
        out.reason = "the question has no content words"
        return out

    kind, keys, step = decide(content, declared, full)
    out.kind, out.matched_on = kind, step
    sets = declared if step == "scope" else (full or declared)
    out.candidates = [(by_path[k], sorted(said.get(t, t) for t in sets[k] & content))
                      for k in keys]
    if kind == NOT_IN_CORPUS:
        out.reason = ("no current page declares most of this question" +
                      (", and no page contains every word of it" if profile.prose else
                       f"; profile {profile.name} does not consult prose"))
        return _fan_out(out, ledger, pointers, question, profile, visited)
    if kind == AMBIGUOUS:
        out.reason = ("two or more current pages own this question by declared scope"
                      if step == "scope" else
                      "no page owns this by scope, and two or more contain every word of it")
        return out

    rec = by_path[keys[0]]
    out.record, out.depth = rec, depth[rec.path]
    if rec.kind != "pointer":
        out.reason = ("exactly one current page owns this question by declared scope"
                      if step == "scope" else
                      "no page owns this by scope; exactly one contains every word of it")
        return out

    # A hub may point at the owner. It may not answer as the owner.
    target = (ledger.root / rec.points_to).resolve()
    hop = f"{rec.id} points to {rec.points_to}"
    out.kind, out.record, out.matched_on = NOT_IN_CORPUS, None, ""
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
                      f"      matched: {', '.join(matched)}"]
    else:
        lines += ["Not in the corpus.", "  " + a.reason[0].upper() + a.reason[1:] + "."]
        if a.unknown:
            where = "found on no current page" if a.profile.prose else "declared by no current page"
            lines.append(f"  Words {where}: " + ", ".join(a.unknown))
        lines.append("  Nothing is answered from outside the folder.")
    if a.kind != RETURN or why:
        for r, words in a.set_aside:
            lines.append(f"  set aside: {r.id} says it is not for: {', '.join(words)}")
    for r, d in a.withheld:
        limit = a.profile.max_depth
        restriction = external_restriction(r, a.profile)
        lines.append(f"  withheld by profile {a.profile.name}: {r.id}: {restriction}" if restriction
                     else f"  withheld by profile {a.profile.name}: {r.id} is depth {d}, limit {limit}")
    for hop in a.route:
        lines.append("  route: " + hop)
    if a.quarantined:
        lines.append(f"  note: {a.quarantined} page(s) quarantined; run validate")
    if why:
        lines += ["", "  why:", f"    root        {a.root}", f"    profile     {a.profile.name} "
                  f"(max depth {a.profile.max_depth}, prose {'on' if a.profile.prose else 'off'})",
                  f"    decided by  {a.matched_on or '-'}",
                  f"    on a page   {', '.join(a.known) or '-'}",
                  f"    on no page  {', '.join(a.unknown) or '-'}"]
    if a.record and authorship(a.record):
        lines.append("  " + authorship(a.record)["notice"])
    hint = clarification(terms(a.question), a.record)
    if hint:
        lines += ["", hint["prompt"]] + ["  - " + c for c in hint["choices"]] + [hint["notice"]]
    return "\n".join(lines)
