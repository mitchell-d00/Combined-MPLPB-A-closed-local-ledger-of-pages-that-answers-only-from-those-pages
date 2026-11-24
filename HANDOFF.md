# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `623f3c4abb38499020df193b037d303d3a329a7f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4f792a365465beae4afe60ffd6d990bc7c09f544b1a77cb802188f3498d46347`.

## Latest user update instructions

Continue the public MPLPB Pole training loop on pin 623f3c4abb38499020df193b037d303d3a329a7f.

Prior results (keep frozen):
- FRUS-Boundary: four fresh FRUS cases. Both anchors 4/4. Strict Ask 0/4 complete. Partials 0. Controls 4/4 withheld. Zero false-supported bridges. Native checker admitted no proposition-level proof. Blocker traced to native proposition and attribution admission.
- BT-Erratum 1/1 complete. Both tested DHS relations complete. Focus-12 still 0/12. Scan/phrase caps and Komnene mapping checks unchanged. Independent historical accuracy, outside scoring, and native OOCC remain NOT_RUN.

Goal: force a decision on the proposition/attribution admission gap for the same four frozen FRUS cases. Do not add new cases. Do not raise scan or phrase caps. Preserve all previously closed results. Do not claim independent historical accuracy or native OOCC.

Run one named test:

1. FRUS-Proposition
   - Use the same four frozen FRUS cases (and their existing negative controls) from FRUS-Boundary.
   - Write and freeze one candidate rule that either:
     (a) admits a proposition-level proof by binding the required attributions and relations to exact witnesses already present in the eligible originals, with unique resolution, chronological order where applicable, and existing budget checks, or
     (b) correctly withholds because proposition or attribution admission cannot be established under the current native rules.
   - Score discovery and Strict Ask separately.
   - Zero false-supported bridges allowed.
   - Report complete, partial, or correct withhold for each case, and the exact reason for any remaining withhold.

After the test:
- Write the rule that was added (or the explicit withhold condition).
- Update the open-items README with before/after counts for these four cases only.
- Leave the original 12 focus cases, the scan/phrase limits, outside scoring, independent historical accuracy, and native OOCC marked NOT_RUN or open as they currently stand.
- Commit the frozen cases, results, and rule under a new public pin.

Return the result table for FRUS-Proposition, the rule text, the updated open-item list, the new commit hash, and the archive SHA-256.

## Implemented scope

- Refreeze the four FRUS comparisons and original controls on the requested public pin.
- Run Strict Ask on the unchanged inputs and independently probe native action and relationship admission on their exact full source units.

## Validation recorded

- Discovery stayed at 4/4 pairs. Strict Ask remained at 0/4 complete with four answerable misses, zero partials, and all four controls correctly withheld.
- All 16 exact-unit proposals were rejected by the current checker. Four source rereads completed without a cap hit. Existing extraction emitted no letter-instruction proposal for PE-02.
- The initial assessor invocation misspelled the existing propose entry point and failed before scoring. The corrected invocation completed with the same frozen inputs and rule.
- The native runtime and prior named evidence files match the pin. No false-supported bridge occurred.

## Limitations and blocked checks

- The test supplies evaluator-verified source coordinates to the kernel after the unchanged worker run. This diagnostic is separate from Strict Ask.
- The four positive comparisons remain answerable misses. The classifier introduces no native proof grammar.
- Outside scoring, independent historical accuracy, independent semantic adjudication and native OOCC remain NOT_RUN.

## Next steps

- Native admission for attributed evaluations, forecasts, intent, advice and nested reports remains open.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
