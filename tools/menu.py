#!/usr/bin/env python3
"""One menu for the ledger, the parts, and the open-web clone.

Nothing here trains a model. Search is the folder you already have.
Networked MPLPB is the part under parts/networked: seeds, nodes, and hubs.
The clone formats alien pages. It does not decide that two sources are related.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ITEMS = [
    ("Ask this folder", "Search pages already on disk. One owner returns, two stop, none refuses.",
     [sys.executable, "-m", "mplpb_combined", "ask"]),
    ("Provenance gate", "Show separate sources. Co-presence is not a relationship.",
     [sys.executable, "-m", "mplpb_combined", "gate"]),
    ("Build web clone", "Format loose open-web files into an MPLPB tree.",
     [sys.executable, str(ROOT / "tools" / "open_clone.py")]),
    ("Wiki live match", "Load Simple English Wikipedia, match the live revision, then test.",
     [sys.executable, str(ROOT / "tools" / "wiki_live_eval.py"), "check"]),
    ("Seal an existing corpus", "Add hashes and pins. Change nothing else.",
     [sys.executable, "-m", "mplpb_combined", "seal"]),
    ("Validate a folder", "Report format errors. Exit 1 on error.",
     [sys.executable, "-m", "mplpb_combined", "validate"]),
    ("Kill test", "Run the frozen pottery probes. They are not the wiki test.",
     [sys.executable, "-m", "mplpb_combined", "killtest", "examples/studio", "killtest/probes.json"]),
    ("Parts", "Show the five carried implementations and how to run each.", None),
    ("Networked MPLPB", "Open the networked part: seeds, nodes, hubs. No model and no required server.",
     None),
    ("Local search tools", "Crawl or validate a local-mirror site. This is not training data.",
     None),
]

PARTS = [
    ("local-mirror", "Offline HTML site, crawl, search, validate.", "parts/local-mirror"),
    ("smart-local", "Retrieval-bounded reader, modes, teaching.", "parts/smart-local"),
    ("swarm", "Leases, origin depth, registry, profiles.", "parts/swarm"),
    ("networked", "Seeds, nodes, hubs, Ed25519 signatures.", "parts/networked"),
    ("image", "Signed image pages with evidence and attestation.", "parts/image"),
]


def _show_parts() -> None:
    print("Parts carried whole. Combined does not replace them.")
    for name, what, path in PARTS:
        print(f"  {name:<14} {what}")
        print(f"  {'':<14} {path}")
    print("Check all of them: python3 tools/check_parts.py")


def _networked() -> None:
    print("Networked MPLPB is parts/networked.")
    print("A seed is a corpus that can be copied. A node carries seeds. A hub lists nodes.")
    print("The hub does not answer. It only says where to look.")
    print("Read parts/networked/README.md before starting a node.")
    print("Example already in that part: mplpb-net ask node-a \"bisque firing schedule for a kiln\"")
    print("This menu does not open a port and does not train anything.")


def _local_search() -> None:
    print("Search uses the pages in a folder. There is no training set in this repo.")
    print("Combined: python3 -m mplpb_combined ask <folder> \"<question>\"")
    print("Local mirror crawl: python3 parts/local-mirror/tools/crawl.py")
    print("Local mirror validate: python3 parts/local-mirror/tools/validate.py")


def show() -> None:
    print("Combined MPLPB")
    print("Return, ambiguous, or not in corpus. Never blend.")
    print()
    for i, (title, about, _cmd) in enumerate(ITEMS, start=1):
        print(f"{i:>2}. {title}")
        print(f"    {about}")
    print()
    print("Choose a number. Extra words are passed to that command.")
    print("q quits.")


def run(choice: str, extra: list[str]) -> int:
    try:
        n = int(choice)
        title, _about, cmd = ITEMS[n - 1]
    except (ValueError, IndexError):
        print("no such choice")
        return 2
    if title == "Parts":
        _show_parts()
        return 0
    if title == "Networked MPLPB":
        _networked()
        return 0
    if title == "Local search tools":
        _local_search()
        return 0
    if not extra and title in {"Ask this folder", "Provenance gate", "Build web clone", "Seal an existing corpus", "Validate a folder"}:
        print(" ".join(cmd) + " <arguments>")
        print("Pass the arguments after the menu number.")
        return 0
    return subprocess.run(cmd + extra, cwd=ROOT).returncode


def main() -> int:
    if len(sys.argv) > 1:
        return run(sys.argv[1], sys.argv[2:])
    show()
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            print()
            return 0
        if not line or line.lower() in {"q", "quit", "exit"}:
            return 0
        bits = line.split()
        code = run(bits[0], bits[1:])
        if code:
            print(f"exit {code}")


if __name__ == "__main__":
    raise SystemExit(main())
