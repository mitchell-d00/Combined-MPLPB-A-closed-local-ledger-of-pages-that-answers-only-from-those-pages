# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `e8e874ce8a8ae1d55c821da27b30d1dfe1bf1e45` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `530cdd61121c3ed19783fe3b0bed5ed4e4e545cb782f58443e46ce4aa2a69814`.

## Latest user update instructions

Continue the public MPLPB Pole training loop on pin 78f6a464212214a29a84f400a199be46a25db8bf.

Prior results (keep frozen):
- BT-Erratum: 0/1 → 1/1 complete. 5/5 withholds. Zero false-supported bridges.
- Polybius-Prose: 0/10 complete. 7/10 native anchors, one partial, nine misses, 10/10 withholds.
- Scan-Phrase: two eligible records retained. Literal and phrase-cap diagnostics reproduced (200k characters / 1,000 units).
- Komnene-Hold: 22/22 mappings verified. Outside scoring NOT_RUN.
- Retained: Tacitus 3/6, Douglass 6/12, Babbage caps, both DHS cases complete, zero false-supported bridges.

Goal: close or correctly diagnose the remaining ordinary-prose and original-focus gaps without inventing links or producing false-supported bridges. Freeze every new case set before scoring. Preserve the same public accounting (pinned commit, archive hash, before/after counts, explicit NOT_RUN labels). Do not claim independent historical accuracy or native OOCC.

Run these four named tests:

1. Focus-12 (original focus misses)
   - Isolate the 12 original focus cases (date roles, reported statements, partial corrections, wording changes, less explicit chains).
   - Apply any existing rules and measure whether any move to complete or correct withhold.
   - Keep negative controls. Report the exact reason for each remaining miss.

2. Polybius-Extend (ordinary-prose linking on unfamiliar originals)
   - Draw a fresh held-out authentic set where the relation is implied by ordinary prose but lacks an explicit volume/page/document-number citation.
   - Score discovery and Strict Ask separately.
   - Include negative controls that look similar but lack a verifiable chain.
   - Zero false-supported bridges allowed.

3. Cap-Diagnosis (scan and phrase limits)
   - Re-run the larger-corpus and multi-record cases under the existing 200k-character / 1,000-unit scan caps and phrase-token / phrase-group limits.
   - Record the exact budget that produces each partial or withhold.
   - Confirm the sorter still retains both records when both are eligible.
   - Do not raise the caps; diagnose only.

4. Komnene-Status (outside packet)
   - Confirm the existing 22-question / 44-arm package is still sealed and matches the concealed mapping.
   - Leave independent scoring marked NOT_RUN.
   - Confirm the delivery checksum.

After the tests:
- Write any new or refined rule that was added.
- Update the open-items README with before/after counts.
- Leave independent historical accuracy, outside-custodian scoring, independent semantic adjudication, and native OOCC marked NOT_RUN.
- Commit the frozen cases, results, and rules under a new public pin.

Return the four result tables, any new rule text, the updated open-item list, the new commit hash, and the archive SHA-256.

## Implemented scope

- Replay the exact 12 original Pole positive misses and 20 original controls.
- Freeze eight fresh FRUS originals, four comparisons and four controls with a separate reference key.
- Measure a source-layout projection with stable pins, then replay fixed limits and Komnene custody.

## Validation recorded

- Focus-12 reproduced every original outcome and diagnostic. Eight positives had complete discovery, two remained partial, ten abstained, and all 20 controls preserved non-support.
- Polybius-Extend native discovery moved from 0/4 to 4/4. Strict Ask remained at 0/4 with all four controls withheld and zero false-supported bridges.
- Character, unit, phrase-token and phrase-group diagnostics reproduced with both eligible records retained.
- Komnene reproduced all 22 concealed mappings across 44 arms and retained the existing delivery hash.
- BT-Erratum reproduced one complete proof and five withholds. Native proof modules are byte-identical to the baseline.
- The extracted source ZIP ran 1,727 Python tests with 2 skips and passed the 52 public evidence controls, installed wheel, JavaScript, Pyodide and Chromium checks.
- The extracted ZIP reproduced all four named tests and past supported decisions. Source-only workers independently replayed Focus-12 and both Polybius import arms with the same outcomes.

## Limitations and blocked checks

- The projection is experiment-only. All 12 original focus gaps and the new ordinary-prose proof gaps remain open.
- Two permission-reprinted pages have frozen public URLs and hashes. Their full archived bytes stay in the local acquisition.
- Case scoring is local development. Receipts record os_isolated false and a separate evaluator key.
- Independent historical accuracy, outside-custodian scoring, independent semantic adjudication and native OOCC remain NOT_RUN.

## Next steps

- Separate proof work on writing-date roles, reporter attribution, date-linked corrections and dispatches, and scoped wording comparisons.
- Test ordinary-prose composition with strong controls after anchors have been retrieved.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
