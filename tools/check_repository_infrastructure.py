"""Fail-closed synchronization checks for public Pages, docs, JS API and corpus.

This is a static repository consistency check. Runtime functionality is tested
separately by the existing exact-head ZIP/Pyodide/Chromium workflows.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = "https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/"
REQUIRED = (
    "index.html", "browser/client.js", "browser/worker.js",
    "tools/build_browser_runtime.py", "tools/check_browser_wasm.mjs",
    "tools/check_ui_script.py", "tools/check_browser_transport.cjs",
    "tools/browser_release_smoke.py", "tests/javascript-api.cjs",
    "JAVASCRIPT-API.md", "README.md", "CONTENTS", "docs/README.md",
    "docs/REPOSITORY_INFRASTRUCTURE.md", "reference_corpus/README.md",
    "reference_corpus/catalog.v1.json", "reference_corpus/probes.v1.json",
    "tools/build_reference_corpus.py", "tests/test_reference_corpus.py",
    ".github/workflows/pages.yml", ".github/workflows/pr-validation.yml",
    ".github/workflows/zip-release-validation.yml",
    ".github/workflows/infrastructure-audit.yml",
)


def audit(root=ROOT):
    root = Path(root)
    problems = []
    for item in REQUIRED:
        if not (root / item).is_file():
            problems.append("Missing supporting infrastructure: "+item)
    if problems:
        return problems
    html = (root / "index.html").read_text()
    js_doc = (root / "JAVASCRIPT-API.md").read_text()
    readme = (root / "README.md").read_text()
    docs = (root / "docs/README.md").read_text()
    infra = (root / "docs/REPOSITORY_INFRASTRUCTURE.md").read_text()
    builder = (root / "tools/build_browser_runtime.py").read_text()
    pages = (root / ".github/workflows/pages.yml").read_text()
    pr = (root / ".github/workflows/pr-validation.yml").read_text()
    zip_flow = (root / ".github/workflows/zip-release-validation.yml").read_text()
    auto = (root / ".github/workflows/infrastructure-audit.yml").read_text()
    if (root / "io.html").exists():
        problems.append("Do not create a second io.html application: published Pages is generated from index.html")
    if "<title>MPLPB" not in html or "BEGIN MPLPB PUBLIC API" not in html:
        problems.append("Desktop HTML missing application title or public JavaScript API")
    if "reference_corpus/README.md" not in html or "JAVASCRIPT-API.md" not in html:
        problems.append("Public UI footer must disclose optional reference corpus and JS API")
    if "not loaded" not in html:
        problems.append("UI must not imply unratified machine corpus is available by default")
    if PAGES not in readme or PAGES not in docs or PAGES not in infra:
        problems.append("Published URL is missing from canonical docs")
    if "unratified" not in js_doc or "profile:'lab'" not in js_doc:
        problems.append("JavaScript API docs must disclose machine draft and lab-only boundary")
    if "reference_corpus/" in re.search(r"folders\s*=\s*\((.*?)\)",builder,re.S).group(1):
        problems.append("Reference draft corpus must not be silently bundled into live browser")
    if "'index.html'" not in builder or "'browser/client.js'" not in builder:
        problems.append("Browser builder missing source HTML or embedded worker bridge")
    for text, pattern, name in (
        (pages, "dist/index.html", "Pages output"),
        (pages, "tools/browser_release_smoke.py", "postdeploy live Chromium"),
        (pr, "tools/check_repository_infrastructure.py", "PR validation"),
        (zip_flow, "tools/check_repository_infrastructure.py", "ZIP-first validation"),
        (auto, "schedule:", "weekly scheduled automation"),
        (auto, "tools/check_repository_infrastructure.py", "scheduled static audit"),
        (auto, "tools/browser_release_smoke.py", "scheduled real-browser live audit"),
        (js_doc, "window.MPLPB", "JS API documented client"),
        (readme, "reference_corpus/README.md", "README corpus reference"),
        (docs, "REPOSITORY_INFRASTRUCTURE.md", "documentation index infra guide"),
    ):
        if pattern not in text:
            problems.append("Missing linkage in "+name+": "+pattern)
    if re.search(r"^\|\s*Supported answers.*\|\|",docs,re.M):
        problems.append("Malformed documentation index row (merged table cells)")
    return problems


def main():
    problems = audit()
    if problems:
        print("FAIL infrastructure synchronization:\n- "+"\n- ".join(problems))
        return 1
    print("PASS infrastructure synchronization: desktop index.html, generated Pages runtime, JavaScript API, corpus staging, docs and workflows are linked")
    print("NOTE static linkage is not runtime/deployment evidence; exact archive, Pyodide and real Chromium tests remain required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
