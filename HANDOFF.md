# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0f07ac5a38863146ef92c8281ed52f60e8d72aa7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `a40011830d733224855ef41f6b4c12dbac47ed5c1bede875121b37a90b7b07cf`.

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
- Preserve eight original baseline executions and first score. Freeze the separate fresh arm and the bounded parser proposal before any reader change.
- Extend only the whole reporting-object pattern with the frozen generic terminal adjunct. Preserve the original authority question and all native proof gates.
- Publish the first fresh pair, unchanged diagnostic raw responses, versioned coordinate scoring, frozen runtime, and 832/BB/96 preservation.

### Validation recorded

- Remote main matches the verified released commit 39df3d14. Original Round 3 D03-A found both required passages and stopped before native attribution proof. Packet, key seal, runtime and runner verified without a new reader run.
- Baseline reached proof for bare attribution, bare wrong-reporter and opposed evidence. It missed generic and named positives before proof. The first score flagged two coordinate discrepancies. A separately versioned recheck of the unchanged raw outputs verified one valid complete answer, one cited conflict, four withholds and two misses.
- All 30 focused reported-content and ordinary-question tests passed on the scoped patch.
- Frozen native candidate 568b44c5fcba9fa65bb29e045a1e1080cfebb709, scoped ZIP SHA-256 f7aa5541e1114722fac62b09ba0323a1400b0d3af2eb7de61d33f17ae3a283b7.
- Eight diagnostic executions and 16 fresh paired executions completed on 14 distinct question strings. Fresh completes 1 to 2, cited conflicts 1 to 1, withholds 4 to 4, misses 2 to 1. Zero unsupported or lost valid outcomes, zero errors. The generic wrong reporter and competing objects withheld at attribution proof.
- All 832 public contracts match exactly. BB 900/900 positive plus eligible citations and 200/200 controls. All 96 retained cases executed, reproducing the historical 87/96 strict result and all nine pinned normalized diagnostic refusal fingerprints.

### Limitations and blocked checks

- Same-operator synthetic design and scoring. Independent and human evaluations remain NOT_RUN. Original 17 checks incomplete, 100 transfers NOT_RUN and publication incident open.
- Named-source requests have no verified named-source selector in this experiment. The correction to evaluator coordinates leaves frozen semantic expectations intact.
- The true named-source target still misses before proof. Neither the named negative nor the terminal generic gain verifies a named selector. Same-operator fresh authoring and scoring.

### Next steps

- Complete the unchanged exact-head CI, verify remote downloads, merge only after applicable checks, then verify Pages at the merged commit. Do not tune the first fresh packet.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
