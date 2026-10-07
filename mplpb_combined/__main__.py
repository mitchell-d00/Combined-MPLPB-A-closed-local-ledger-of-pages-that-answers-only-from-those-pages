"""Command line for Combined MPLPB.  python3 -m mplpb_combined --help"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, killtest, ledger as L, reader as R


def _profile(a) -> R.Profile:
    base = R.PROFILES[a.profile]
    depth = base.max_depth if a.max_depth is None else (None if a.max_depth < 0 else a.max_depth)
    prose = base.prose and not a.no_prose
    heed = not a.ignore_not_for
    if (depth, prose, heed) == (base.max_depth, base.prose, True):
        return base
    return R.Profile(f"{base.name}*", depth, prose, heed)


def _body(a) -> str:
    if getattr(a, "body_file", None):
        return Path(a.body_file).read_text(encoding="utf-8")
    return a.body or ""


def cmd_ask(a) -> int:
    ans = R.answer(a.root, a.question, _profile(a))
    print(json.dumps(ans.to_dict(), indent=2, ensure_ascii=False) if a.json
          else R.render(ans, why=a.why))
    return {R.RETURN: 0, R.AMBIGUOUS: 2, R.NOT_IN_CORPUS: 3}[ans.kind]


def cmd_validate(a) -> int:
    led = L.Ledger(a.root)
    found = led.findings()
    errors = [f for f in found if f.level == "error"]
    warnings = [f for f in found if f.level == "warning"]
    for f in found:
        print(f)
    pages = [r for r in led.records if r.kind != "index"]
    cur = sum(1 for r in pages if led.effective_status(r) == "current")
    print(f"{len(pages)} record(s) under {led.root}: {cur} current, {len(pages) - cur} retired; "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors or (a.strict and warnings) else 0


def cmd_list(a) -> int:
    led = L.Ledger(a.root)
    for r in led.records:
        if r.kind == "index":
            continue
        st = led.effective_status(r)
        if st != "current" and not a.all:
            continue
        flag = led.quarantine_reason(r)
        print(f"{r.id:16} {st:8} d{led.depth(r)} {r.origin:7} {r.path}"
              + (f"   QUARANTINED ({flag})" if flag else ""))
        print(f"{'':16} {r.scope}")
    return 0


def cmd_show(a) -> int:
    led = L.Ledger(a.root)
    recs = led.by_id.get(a.id, [])
    if not recs:
        print(f"no record {a.id}")
        return 3
    for r in recs:
        st = led.effective_status(r)
        print(r.title)
        print()
        for ln in r.text.splitlines():
            print("  " + ln)
        print()
        print("  " + R.cite(r, led.depth(r)))
        if st == "retired":
            by = ", ".join(s.id for s in led.superseded_by.get(r.id, [])) or "nothing (withdrawn)"
            print(f"  RETIRED. Superseded by: {by}. Act on the current page, not this one.")
        if r.derived_from:
            print("  derived from: " + ", ".join(x.id for x in r.derived_from))
    return 0


def cmd_history(a) -> int:
    led = L.Ledger(a.root)
    chain = led.history(a.id)
    if not chain:
        print(f"no record {a.id}")
        return 3
    for r in chain:
        print(f"{r.fields.get('updated', ''):18} {led.effective_status(r):8} {R.cite(r, led.depth(r))}")
    return 0


def _wrote(rec, root) -> int:
    led = L.Ledger(root)
    print(f"wrote {rec.id}  {rec.path}  depth {led.depth(rec)}  {rec.hash}")
    return 0


def cmd_write(a) -> int:
    return _wrote(L.write(a.root, title=a.title, scope=a.scope, when_to_use=a.when_to_use,
                          not_for=a.not_for, body=_body(a), prefix=a.prefix, directory=a.dir, origin=a.origin,
                          owner=a.owner, kind="pointer" if a.points_to else "page",
                          points_to=a.points_to), a.root)


def cmd_revise(a) -> int:
    body = _body(a) or None
    return _wrote(L.revise(a.root, a.id, title=a.title, scope=a.scope, when_to_use=a.when_to_use,
                           not_for=a.not_for, body=body, origin=a.origin, owner=a.owner,
                           ratified_by=a.ratified_by, note=a.note), a.root)


def cmd_derive(a) -> int:
    return _wrote(L.derive(a.root, a.parents, title=a.title, scope=a.scope,
                           when_to_use=a.when_to_use, not_for=a.not_for, body=_body(a), origin=a.origin,
                           prefix=a.prefix, directory=a.dir, owner=a.owner), a.root)


def cmd_ratify(a) -> int:
    return _wrote(L.ratify(a.root, a.id, a.who), a.root)


def cmd_withdraw(a) -> int:
    L.withdraw(a.root, a.id, note=a.note)
    print(f"retired {a.id}; the page stays in the folder")
    return 0


def cmd_seal(a) -> int:
    done = L.seal(a.root)
    for p in done:
        print("sealed " + p)
    print(f"{len(done)} page(s) sealed")
    return 0


def cmd_index(a) -> int:
    print("wrote " + str(L.build_index(a.root, a.title)))
    return 0


def cmd_killtest(a) -> int:
    res = killtest.run(a.root, a.probes, _profile(a))
    print(killtest.render(res))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.write_stripped:
        n = killtest.write_stripped(L.Ledger(a.root), Path(a.write_stripped))
        print(f"\nwrote {n} stripped page(s) to {a.write_stripped}")
    return 0 if res["probe_hash"] in ("OK", "no hash file") else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mplpb_combined",
        description="A closed local ledger of pages. Return, ambiguous, or not in corpus. Never blend.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd")

    def prof(s):
        s.add_argument("--profile", choices=sorted(R.PROFILES), default=R.DEFAULT_PROFILE)
        s.add_argument("--max-depth", type=int, default=None, help="override; -1 for no limit")
        s.add_argument("--no-prose", action="store_true",
                       help="scope only: never fall back to a page's prose")
        s.add_argument("--ignore-not-for", action="store_true",
                       help="for comparison only: read as if no page had a not-for field")

    def content(s, need=True):
        s.add_argument("--title", required=need)
        s.add_argument("--scope", required=need)
        s.add_argument("--when-to-use", default="" if need else None)
        s.add_argument("--not-for", default="" if need else None,
                       help="words for what this page does not cover")
        s.add_argument("--body", default="")
        s.add_argument("--body-file")
        s.add_argument("--owner", default="")

    s = sub.add_parser("ask", help="answer one question from the folder, or refuse")
    s.add_argument("root"); s.add_argument("question"); prof(s)
    s.add_argument("--why", action="store_true"); s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_ask)

    s = sub.add_parser("validate", help="check every page against the format; exit 1 on error")
    s.add_argument("root"); s.add_argument("--strict", action="store_true")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("list", help="list records"); s.add_argument("root")
    s.add_argument("--all", action="store_true", help="include retired"); s.set_defaults(fn=cmd_list)

    s = sub.add_parser("show", help="read one record by id, retired or not")
    s.add_argument("root"); s.add_argument("id"); s.set_defaults(fn=cmd_show)

    s = sub.add_parser("history", help="walk a supersession chain")
    s.add_argument("root"); s.add_argument("id"); s.set_defaults(fn=cmd_history)

    s = sub.add_parser("write", help="write a new page")
    s.add_argument("root"); content(s)
    s.add_argument("--prefix", default="DOC"); s.add_argument("--dir", default="")
    s.add_argument("--origin", choices=L.ORIGINS, default="human")
    s.add_argument("--points-to", default="", help="make this a hub pointer at another root")
    s.set_defaults(fn=cmd_write)

    s = sub.add_parser("revise", help="write a new page and retire the old one")
    s.add_argument("root"); s.add_argument("id"); content(s, need=False)
    s.add_argument("--origin", choices=L.ORIGINS, default="human")
    s.add_argument("--ratified-by", default=""); s.add_argument("--note", default="")
    s.set_defaults(fn=cmd_revise)

    s = sub.add_parser("derive", help="write a page derived from others; depth goes up by one")
    s.add_argument("root"); s.add_argument("--from", dest="parents", action="append", required=True)
    content(s); s.add_argument("--prefix", default="", help="default: the first parent's")
    s.add_argument("--dir", default="")
    s.add_argument("--origin", choices=L.ORIGINS, default="machine")
    s.set_defaults(fn=cmd_derive)

    s = sub.add_parser("ratify", help="a named person signs a page; depth returns to 0")
    s.add_argument("root"); s.add_argument("id"); s.add_argument("--who", required=True)
    s.set_defaults(fn=cmd_ratify)

    s = sub.add_parser("withdraw", help="retire a page with no successor")
    s.add_argument("root"); s.add_argument("id"); s.add_argument("--note", default="")
    s.set_defaults(fn=cmd_withdraw)

    s = sub.add_parser("seal", help="adopt hand-written or earlier-format pages: add hashes")
    s.add_argument("root"); s.set_defaults(fn=cmd_seal)

    s = sub.add_parser("index", help="rebuild index.html for people")
    s.add_argument("root"); s.add_argument("--title", default="Main Index"); s.set_defaults(fn=cmd_index)

    s = sub.add_parser("killtest", help="strip the declared fields and compare")
    s.add_argument("root"); s.add_argument("probes"); prof(s)
    s.add_argument("--out"); s.add_argument("--write-stripped")
    s.set_defaults(fn=cmd_killtest)
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    if not getattr(a, "fn", None):
        build_parser().print_help()
        return 0
    try:
        return a.fn(a)
    except (KeyError, ValueError, FileExistsError, FileNotFoundError, L.LedgerBusy) as e:
        print("refused: " + str(e).strip("'\""), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
