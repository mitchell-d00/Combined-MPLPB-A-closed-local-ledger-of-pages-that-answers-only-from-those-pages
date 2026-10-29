# Documentation review — 2026-10-29

[Documentation index](README.md) · [Repository overview](../README.md)

Reviewed source baseline: `d2f92a89ad48206e884e514fbe221b4bfc5e9b0c`
(main after PR #18, the October 27 provenance-gated retrieval repair).
This is a documentation correction, not a new engine release, independent
accuracy study, or verified deployment of this candidate.

## Findings and changes

| Finding | Correction |
|---|---|
| README mixed supported answers with original lexical demonstrations and repeated feature updates. | Reorganized around runtime modes, four source-interface contracts, current examples, and guide links. |
| Root CONTENTS described the October 7 paper tree and 106 tests. | Replaced with a current source/runtime/release map without a permanent suite-count claim. |
| Latest retrieval behavior appeared mainly in the fix log/API table. | Added a dedicated page-retrieval guide covering authority, gate matching, failures, no pointer expansion, and no replacement owner. |
| Browser UI guide described only desktop Python and implied no browser rendering had ever been tested. | Documented desktop versus hosted/downloaded standalone, current controls, and the distinct real-browser release runbooks. |
| Storage instructions treated browser storage as only a desktop resume pointer. | Distinguished standalone IndexedDB data from server files, saved chats from free chat, and transcripts from full-ledger backups. |
| Discovery paths could resolve at the owner-site root. | Made manifest/public snapshot paths relative to the full GitHub Pages project URL. |
| Runtime size and compatibility documentation lagged the bundle. | Replaced the old approximate 20 MB claim with a dated byte measurement; corrected four allowlisted adapter revisions. |
| Earlier ruleset gap and earlier test counts read as current state. | Rechecked active rules, labeled dated observations, and linked current testing procedures. |
| Papers, supplied documents, and older implementation reports were difficult to distinguish from current manuals. | Added a documentation index and historical-context notes; preserved original papers, manifests, source captures, and frozen results. |
| Two README anchors no longer existed. | Replaced them with working current guide links. |

## Executed local checks

- `python -m unittest discover -s tests -q`: **674 tests passed**, 383.151 seconds, Python 3.12 in this environment. This is a checkout regression run, not the ZIP-first candidate gate.
- `python tools/check_ui_script.py`: passed element-stub/UI workflow checks; no rendered browser.
- `node tools/check_browser_transport.cjs`: passed serialization/save/error/embedded-hash checks; no actual IndexedDB/layout test.
- `node tests/javascript-api.cjs`: passed real Python bridge/API parity, session/import, profile, offline-default, and synthetic online-acquisition checks.
- `node crawler/test_worker.mjs`: passed bounded-crawler/security fixtures, not a deployed crawler test.
- `node --check tools/mplpb_agent_bridge.mjs` and its `--help`: passed.
- Documented version commands report supported CLI **2.0.0** / legacy core **1.0.0**. The supported-answer example returned the synthetic D&D assertion. The page-retrieval example returned `retrieved` with `answer_supported:false`; the separate-source gate example completed successfully.
- All three frozen kill-test probe checksum files passed verification. Supplied-paper and pre-gate archive manifests were checked separately for byte consistency.
- Active guide/index local links and Markdown anchors were checked; final diff whitespace checks passed. Documentation changes do not modify Python/JavaScript behavior, sealed pages, resource data, frozen evaluations, or original paper bytes.

## Live-site and settings observations

Fetched the [live project HTML](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/):

- Footer build: **`676a2ec4c670`**.
- HTML size: **37,547,269 bytes**, about 35.8 MiB.
- Embedded Pyodide version: **314.0.7**.
- All **378 bundled source-file payloads** matched their embedded digests and the baseline checkout; all **five runtime asset digests** matched their embedded bytes. The worker string matched `browser/worker.js`.

This checks the downloaded artifact, not execution of its Python engine, browser
permissions, UI interactions, network acquisition, or long-term storage. It also
does not imply this documentation candidate is already deployed. Hashes establish
byte consistency, not authenticated distribution or source truth.

Read-only inspection of active ruleset **Bear** (ID `24696697`) confirmed it targets
`refs/heads/main`, requires a PR and strict `archive-first` / `regression` checks,
and prevents deletion/non-fast-forward updates. Required approving reviews were
zero. No repository settings were changed or bypasses tested; settings can change
after this observation. See [release evidence](RELEASE_EVIDENCE.md).

## Checks left to the candidate workflows

No fresh real Chromium interaction or candidate WebAssembly build was run for
this documentation pass; Python Playwright and `/usr/bin/chromium` are unavailable
locally. The unchanged [ZIP-first workflow](ZIP_FIRST_RELEASE_TESTING.md) and PR
regression workflow must test the exact submitted commit, including package
extraction, runtime execution, live baseline, candidate browser/storage checks,
and evidence manifests. The separate Pages workflow verifies deployment after
merge. This local pass does not replace those required checks or independent
human/browser/security evaluation.
