#!/usr/bin/env python3
"""Run every vendored part's own checks, then adopt each part's example site
into the combined format and validate it.

    python3 tools/check_parts.py

This is a tool, not part of the package: it starts subprocesses, which the
package itself never does.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PARTS = HERE / "parts"
sys.path.insert(0, str(HERE))

from mplpb_combined import ledger as L  # noqa: E402

SUITES = [
    ("combined (this repo)", HERE, ["-m", "unittest", "discover", "-s", "tests", "-t", "."]),
    ("smart-local", PARTS / "smart-local", ["-m", "unittest", "discover", "-s", "tests", "-t", "."]),
    ("swarm", PARTS / "swarm", ["-m", "unittest", "discover", "-s", "tests"]),
    ("networked", PARTS / "networked", ["-m", "unittest", "discover", "-s", "Tests", "-t", "."]),
    ("image", PARTS / "image", ["-m", "unittest", "discover", "-s", "tests"]),
]
SITES = [
    ("local-mirror", PARTS / "local-mirror" / "site"),
    ("smart-local", PARTS / "smart-local" / "site"),
    ("swarm corpus-a", PARTS / "swarm" / "site" / "corpus-a"),
    ("swarm corpus-b", PARTS / "swarm" / "site" / "corpus-b"),
    ("networked seed", PARTS / "networked" / "Seed"),
]


def main() -> int:
    bad = 0
    print("test suites")
    for name, cwd, args in SUITES:
        if not cwd.is_dir():
            print(f"  {name:22} missing"); bad += 1; continue
        p = subprocess.run([sys.executable] + args, cwd=str(cwd), capture_output=True, text=True)
        tail = (p.stderr or p.stdout).strip().splitlines()
        ran = next((ln for ln in reversed(tail) if ln.startswith("Ran ")), "no tests ran")
        m = re.search(r"Ran (\d+) tests?", ran)
        verdict = "OK" if p.returncode == 0 else "FAILED"
        print(f"  {name:22} {m.group(1) if m else '?':>4} tests  {verdict}")
        bad += p.returncode != 0

    mirror = PARTS / "local-mirror"
    if mirror.is_dir():
        p = subprocess.run([sys.executable, "tools/validate.py", "site"], cwd=str(mirror),
                           capture_output=True, text=True)
        print(f"  {'local-mirror':22} its own validate.py exits {p.returncode}")
        bad += p.returncode != 0

    print("\nadoption: copy each part's example site, seal it, validate it in the combined format")
    for name, site in SITES:
        if not site.is_dir():
            print(f"  {name:22} missing"); bad += 1; continue
        tmp = Path(tempfile.mkdtemp(prefix="mplpb-adopt-"))
        try:
            root = tmp / "site"
            shutil.copytree(site, root)
            sealed = L.seal(root)
            led = L.Ledger(root)
            errs = [f for f in led.findings() if f.level == "error"]
            pages = [r for r in led.records if r.kind != "index"]
            cur = sum(1 for r in pages if led.effective_status(r) == "current")
            print(f"  {name:22} {len(sealed)} sealed, {cur} current, {len(pages) - cur} retired, "
                  f"{len(errs)} error(s)")
            bad += bool(errs)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
