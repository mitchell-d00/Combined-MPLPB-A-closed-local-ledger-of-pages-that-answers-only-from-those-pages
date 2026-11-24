# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `1ab0e1158e9d730b2ff27c95fbe1540b6a215c65` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d3f52c2d9611b7821d6c9df8dffe5287936dc9c9b0811b05cedf095aa120ef3d`.

## Latest user update instructions

Continue the public MPLPB Pole training loop on pin 7b91951ec3aa2bf12f4c3fea34b91f1b2fae4d46.

Prior results (keep frozen):
- Herodotus-DHS: FR-10 and FR-11 moved to complete. BT-01 remains a miss.
- Polybius: 0/6 complete (relations without explicit publication references unchanged).
- Lovelace-Limit: scan caps and phrase-group limits still produce partials at larger sizes; sorter retains both records.
- Komnene-Ship: package delivery-ready; independent scoring NOT_RUN.
- Retained: Tacitus 3/6, Douglass 6/12, Babbage caps, zero false-supported bridges.

Goal: close or correctly diagnose the remaining open cases without inventing links or producing false-supported bridges. Freeze every new case set before scoring. Preserve the same public accounting (pinned commit, archive hash, before/after counts, explicit NOT_RUN labels). Do not claim independent historical accuracy or native OOCC.

Run these four named tests:

1. BT-Erratum (B-Tests attribution)
   - Isolate BT-01.
   - Write and freeze a candidate erratum rule that preserves both the reported withdrawal and the earlier verification-limited statement.
   - Score discovery and Strict Ask separately. Keep negative controls.
   - Report complete, partial, or correct withhold, and the exact reason for any remaining withhold.

2. Polybius-Prose (ordinary-prose relations)
   - Re-draw or extend the authentic set where the relation is implied by ordinary prose (dates, docket language, sequential amendments, agency action) but lacks an explicit volume/page/document-number citation.
   - Measure whether a supported bridge can be formed or is correctly withheld.
   - Include negative controls that look similar but lack a verifiable chain.
   - Zero false-supported bridges allowed.

3. Scan-Phrase (budget diagnosis)
   - Re-run the multi-record and larger-corpus cases under the existing 200k-character / 1,000-unit scan caps and the phrase-token / phrase-group limits.
   - Record exactly which budget causes the drop from complete to partial or withhold.
   - Confirm the sorter still retains both records when both are eligible.
   - Do not raise the caps in this run; diagnose only.

4. Komnene-Hold (outside packet status)
   - Confirm the existing 22-question / 44-arm Komnene-Ship package is still sealed and matches the concealed mapping.
   - Leave independent scoring marked NOT_RUN.
   - Produce or confirm the delivery checksum.

After the tests:
- Write any new or refined rule that was added.
- Update the open-items README with before/after counts.
- Leave independent historical accuracy and native OOCC marked NOT_RUN.
- Commit the frozen cases, results, and rules under a new public pin.

Return the four result tables, any new rule text, the updated open-item list, the new commit hash, and the archive SHA-256.

## Implemented scope

- Freeze and score BT-Erratum and the expanded Polybius-Prose development draws with separate reference custody.
- Resolve the reported erratum by repository revision, title, and version, then verify the withdrawal, unchanged scores and distinct earlier verification limit.
- Replay the unchanged literal and sorter caps and verify the existing Komnene delivery checksum and concealed mapping.

## Validation recorded

- BT-Erratum recovered 1/1 complete without a discovery change. All five controls withheld and no false-supported bridge occurred.
- The first candidate incorrectly supported two authored Markdown scope controls. The accepted candidate withholds on those controls and the Setext variant and preserves the frozen authentic results.
- Polybius-Prose preserved 0/10 complete, one partial, nine misses, 7/10 native discovery anchor coverage, and 10/10 expected withholds.
- Scan-Phrase retained two records at the eight-slot cap and reproduced the character, unit, phrase-token and phrase-group diagnostics.
- Komnene-Hold matched all 22 packet hashes across 44 anonymous arms. The delivery archive was byte-identical.
- Frozen Herodotus-DHS, Tacitus, Douglass and Babbage replays preserved all previously complete claims and control support decisions.
- The exact extracted source ZIP ran 1,725 Python tests with 2 skips and passed all 52 public controls, the installed wheel, the native Pole replay, Pyodide and local Chromium.
- Six source-only worker replays matched their original scores with separately passed evaluator keys and a Python file-read allowlist. The OS isolation flag remains false.
- Fresh downloads matched both commit-pinned B-Tests originals. All seven verified witnesses mapped uniquely to exact original byte and character spans.

## Limitations and blocked checks

- All 12 original synthetic misses and the general ordinary-prose join problem remain open.
- The new erratum rule requires commit-pinned captures. Legacy projections without those manifests withhold.
- The baseline and candidate had no passed custody path and were not OS-isolated.
- Independent historical accuracy, outside scoring and native OOCC remain NOT_RUN.

## Next steps

- Measure proposition attachment on additional held-out ordinary-prose records with distractor controls.
- Keep completeness bounds visible on larger mixed corpora.
- Keep Komnene ready for separately authorized delivery and independent assessment.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
