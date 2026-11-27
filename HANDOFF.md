# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `39df3d14ebf4bb01c056e8b04b8da65c7303fa61` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `230a2ebc037c4480b96d6d272e7c2d4f9573989de8cd9c1a5834d854c3145eb0`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

> Betty; start **Bunyip Round 4: attribution interpretation and proof**, using released main as the baseline.
>
> Investigate Round 3’s remaining attribution miss. Trace where the question stopped: parsing, source selection, attribution proof, or final admission. Preserve the original miss and first result.
>
> **Freeze a small diagnostic set before execution**, distinguishing:
>
> - A generic source adjunct, such as “according to the record.”
> - A named-source constraint, such as “according to Reporter A.”
> - A wrong-reporter contrast where the requested attribution is unsupported.
>
> Include supported answers, relevant conflicts, and cases that must withhold. Require citations and correct attribution. A wrong-reporter case that stops at interpretation does not demonstrate working attribution proof.
>
> Pin inputs, expected contracts, scorer, runtime, and case IDs. Record distinct questions separately from executions and disclose preparation and scoring custody.
>
> Run the unchanged baseline first. If the evidence justifies a repair, freeze a separate fresh comparison before implementation and make one bounded change. Preserve specialized proof requirements. Measure wording coverage separately from any reduction in duplicated logic.
>
> After freezing the candidate, run the fresh comparison once and preserve its first score. Do not repair against those results while continuing to call them fresh.
>
> Verify the affected focused tests, retained Bunyip/Wampus/Thoth contracts, 832 public contracts, BB positives/citations and withholds, and applicable release checks. Keep existing diagnostic exceptions within their authorized scope.
>
> Push recoverable checkpoints before long runs. Include publishable fixtures, generators, runtime pins, raw results, failures, scoring records, and checksum inventories. Verify remote byte readback and update HANDOFF, CURRENT_STATUS, and the Test Index.
>
> Existing authorization covers push, merge after applicable checks pass, and deployment verification. If no justified repair emerges, publish and merge the assessment as evidence without changing the reader.
>
> Keep the effect-controller lab unchanged during this sprint. Finish with the diagnosed cause, measured gains, preservation results, remaining misses, PR and commit links, and merge/deployment status.

### Implemented scope

- Verify released main and freeze Round 4 attribution diagnosis under eight new IDs. Keep Round 3 results and the controller lab unchanged.

### Validation recorded

- Remote main matches the verified released commit 39df3d14. Original Round 3 D03-A found both required passages and stopped before native attribution proof. Packet, key seal, runtime and runner verified without a new reader run.

### Limitations and blocked checks

- Same-operator synthetic design and scoring. Independent and human evaluations remain NOT_RUN. Original 17 checks incomplete, 100 transfers NOT_RUN and publication incident open.

### Next steps

- Run the unchanged diagnostic first. Freeze a separate fresh comparison and one bounded repair only if the stage and control evidence warrant it.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
