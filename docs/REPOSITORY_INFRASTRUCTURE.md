# Supporting-infrastructure synchronization gate

**Always check repository infrastructure when the engine, corpus, user-visible interface, API, packaging or documentation changes.** Changes are not ready for merge merely because their Python unit tests pass.

## What is the live interface?

The canonical public application is **[Combined MPLPB on GitHub Pages](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/)**. Its source is root `index.html`; `tools/build_browser_runtime.py` creates `dist/index.html` for Pages and the standalone WebAssembly HTML. There is **no separate `io.html` source file**, and this change deliberately does not invent one.

The API is the existing `window.MPLPB` in `index.html` (also in the built standalone UI), documented in `JAVASCRIPT-API.md`. The machine-derived [reference corpus](../reference_corpus/README.md) is optional, offline-generated, and **not automatically loaded into the deployed browser**. The default `internal` and `external` profiles do not authorize its unratified depth-two fact pages; use `lab` only for research. A page hash seals bytes, not source truth.

## Automated gate: required for every PR and main change

`python tools/check_repository_infrastructure.py` rejects missing/misaligned infrastructure: live URL references, root HTML/API anchors and research disclosure, docs index links, browser builder, packaging source list, unratified-corpus privacy boundary, release scripts and their workflow wiring. The separate `.github/workflows/infrastructure-audit.yml` runs this check on every PR and push to main, and **weekly on Monday**, plus a manual dispatch. Its weekly run checks the current deployed Pages application through actual Chromium using the existing `tools/browser_release_smoke.py`; a mere HTTP 200 is not counted as an application test.

Additionally, both `.github/workflows/pr-validation.yml` and the exact-head, extracted-ZIP `.github/workflows/zip-release-validation.yml` must run the same static check **before** the expensive tests. A successful checkout-only audit does not replace required Python, JavaScript, real Pyodide, browser, offline-persistence, archive checksum or postdeploy checks. `.github/workflows/pages.yml` already builds from `index.html` and uses postdeployment Chromium verification; retain that gate.

The required workflow check names should be enabled in the GitHub repository's branch protection/ruleset. Merely committing the automation does not enforce it against an administrator who bypasses branch protection.

## Checklist for each change

- Confirm root `index.html`, embedded JS/worker bridge, generated `dist/index.html`, UI text, live URL and public JavaScript API remain mutually compatible.
- Refresh `JAVASCRIPT-API.md`, `README.md`, `docs/README.md`, `CONTENTS`, operational docs and release/evaluation notes to distinguish **available now** from **experimental, unratified or optional**.
- Ensure release packages, ZIP-first extraction, Pages publishing, browser integration, data persistence, network permissions and offline imports are tested at the **same exact head revision**.
- Validate new corpus pages' hash/seal, narrow scope, non-overlap, exact grammar support, source citation and pinned lineage; report supported/refused/ambiguous/wrong counts and every refusal→support transition using frozen probes.
- Preserve older snapshots and their metrics. Revision, withdrawal and ratification must use the existing ledger operations; never overwrite past pages or rewrite frozen histories.
- Review CI failures and follow through to a green premerge exact-head result; after merge confirm Pages deployment and postdeploy Chromium. Never claim a prior live-site check proves the new commit is deployed.

## Reproduce

```sh
python tools/check_repository_infrastructure.py
python -m unittest tests.test_reference_corpus -v
python -m tools.build_reference_corpus --output /tmp/mplpb-reference-fresh
python tools/check_ui_script.py
node tests/javascript-api.cjs
node tools/check_browser_transport.cjs
```

Reference material is not automatically imported into a visitor's browser, nor does this automation silently approve source truth. Source audit and human ratification remain separate editorial gates.