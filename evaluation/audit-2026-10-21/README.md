# October 21 independent retest evidence

Start with [the audit report](../../docs/SYSTEM_AUDIT_2026-10-21.md) and [PR #17](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/17). No automatic merge or deployment is performed.

`baseline/` contains observations against main commit `c3af6ef3bdf66d987adde092ce3594f529b70bf6`. `candidate/` contains both failed intermediate attempts and repaired results. Filenames ending in `before`, the first `python-full.log`, and the incomplete live-run record are deliberately retained failures; do not aggregate every log as one successful run. Later code-pinned JSON and exact-head CI identify the tested revisions.

`cases.json` contains 24 new synthetic development controls. They were authored during this audit and then used to repair defects. They are separate from untouched historical and held-out fixtures, and are not independent reliability scores after repair. Additional tests in `tests/test_audit_20261021.py` cover lineage, source isolation, exact attribution and compatible negative statements.

## Evidence map

| Evidence | Purpose |
|---|---|
| `environment.json`, `environment-pip.txt` | Baseline SHA/date, local runtime/dependency snapshot |
| `baseline/commands.jsonl` | Exact initial command lines, timings and exit codes |
| `baseline/parts.log` | Full combined and vendored suite counts |
| `baseline/audit-probes.json`, `candidate/adversarial-final.json` | Before/after new language controls with code hashes |
| `baseline/ownership-600.json`, `candidate/ownership-600.json` | 600-case development ownership evaluation |
| `baseline/reliability.json`, `candidate/reliability.json` | Preserved frozen pottery and prior adversarial results |
| `candidate/literal-final.json` | Corrected 20-question SQuAD development regression |
| `baseline/grounded-chat-before.json`, `candidate/grounded-chat-fixed.json` | Mislabeled evaluator arm and explicit legacy-reader correction |
| `candidate/response-1000.json`, `candidate/conversation-repairs.json` | Offline synthetic 1,000-case matrix and 240 repair scenarios; distinct from live WebAssembly replay |
| `candidate/replay-observation.json` | Equal generated response, distinct fresh session/hash metadata |
| `candidate/installed-contract.log`, `candidate/wheel-*.log` | Wheel installation and query outside checkout |
| `ci-first-regression.log`, `ci-second-failure.txt` | Preserved CI failures and their repairs |
| `candidate/incomplete-live-run.json`, `candidate/partial-log-rejected.log` | Incomplete artifact detected and rejected |
| `live-final/summary.json`, `live-final/manifest.json`, `live-final/raw-replay.tar.gz` | Complete 1,000-turn real WebAssembly replay, code/input pins and raw HTTP/session evidence |
| `ci-third-browser/` | Real Chromium JSON observations and before/after mobile screenshots; baseline defects are separated from candidate checks |
| `source-integrity.json`, `protected-sha256.json` | Protected source/fixture hashes and intentional README-only discrepancy |
| `repository-rules-2026-10-21.json` | Read-only snapshot of main's active required-check rules |
| `live-browser-observations.json`, `chromium-install-final.log` | Independent deployed UI observations and local browser-install blocker |

CI uploads Chromium screenshots, browser/version observations, and an exact source ZIP with commit/tree/content digests. A successful ZIP run additionally includes `release-evidence.json`; verify it using `tools/release_evidence.py verify --archive-dir ... --expected-commit ...`. A failed workflow artifact is not successful release evidence. GitHub artifact retention is finite; retain the final tested archive before expiration.

The documentation separates local/CI, baseline/candidate, synthetic/held-out, Node WebAssembly/Chromium, and desktop viewport/iPad Safari. Precision is undefined where no supported answers were returned. Historical failures remain visible.
