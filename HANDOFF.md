# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `246a1bdcb9cf80c5561bc7b761cb3fd58bed21bc` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `0ff04f685b5e4fa1096114fbccf4cc20ccd36009496b239bcb59f3da01806ac0`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

> Betty; finish the reconciliation, then run **Bunyip Round 3: cumulative reader assessment**. Push recoverable checkpoints throughout and merge completed work when applicable requirements pass.
>
> **1. Finish reconciliation.** Complete the remaining exact-head checks, merge the clean reconciliation PR, and verify the merged tree and remote evidence readback. Then close #106 unmerged as superseded, linking its clean successors. Keep the publication-history incident separately tracked. Preserve all incomplete and `NOT_RUN` labels.
>
> **2. Freeze Round 3 before running.** Pin current released main as the baseline. Include available pinned C3, Wampus and Thoth versions as historical comparators, clearly identifying their revisions. Use new case IDs.
>
> Examine retained misses and devise a small diagnostic packet covering:
>
> - Imperative and ordinary-language question forms.
> - Attribution, negation, and entity scope.
> - Conditions, modality, and conflicting evidence.
>
> Pair supported targets with contrasts that should withhold or return a checked partial. Freeze inputs, expected outcomes, scoring rules, and preservation requirements. Identify distinct questions separately from executions. Record preparation, key access, and scoring custody honestly.
>
> **3. Run the first comparison unchanged.** Preserve raw responses, citations, diagnostics, execution errors, and first scores. Report complete answers, checked partials, correct withholds, unsupported claims, and lost valid answers separately. Report coverage gains and rule consolidation separately.
>
> Use the findings to select one bounded repair if justified. Any packet that informs the repair becomes development evidence. Freeze a separately identified fresh packet before implementing the repair; do not inspect its scoring material during implementation. Disclose same-operator access wherever applicable.
>
> **4. Verify preservation.** Reuse old Bunyip and Wampus cases as consumed preservation. Run the applicable public-contract, BB positive/citation and withholding checks, plus the current release acceptance suite. Preserve original strict-score failures and approved diagnostic exceptions exactly as recorded. Do not replace missing historical keys with invented originals or reopen the original held packets.
>
> **5. Publish and finish.** Push specifications and checkpoints before long runs. Include publishable fixtures, generators, runtime pins, raw first results, scores, reproduction commands, and checksum inventories. Verify downloaded copies against local bytes.
>
> Update HANDOFF, CURRENT_STATUS, and the Test Index. Keep reader changes separate from the controller work.
>
> Existing authorization covers push, required checks, merge, and applicable deployment verification. Merge a qualifying candidate; otherwise publish the evidence checkpoint and state the exact blocker without weakening gates.
>
> Finish with reconciliation status, Round 3 results, preserved gains and remaining misses, tested and merged revisions, deployment status, and anything still unbacked.

### Implemented scope

- Finish clean PR #113 reconciliation and close #106 unmerged. Freeze Bunyip Round 3 against unchanged released main and exact C3, Wampus and Thoth packages.
- Retain and score the first four-reader comparison, replay the 832, BB and 96-case preservation cohorts, and publish exact archives and readback.

### Validation recorded

- PR #113 all 11 exact-head checks passed. Merged tree is identical to the checked tree. All 48 changed files matched remote readback. PR #106 is closed unmerged with its historical body intact. Round 3 pins and synthetic freeze verified without running a reader.
- All 48 diagnostic executions completed. Released main 5 complete, 1 checked partial and 5 withholds, with one attribution miss. All four arms had zero unsupported claim cases and zero errors. No valid outcomes were lost.
- BB 900 exact positives and citations, 200 exact withholds. All 832 public contracts exact. All 96 consumed cases executed, with the 87/96 exact comparison and nine unchanged diagnostic fingerprints separately retained.
- First evidence head failed the repository index audit because Round 3 was registered as a top-level family. Corrected its registration under Cryptid. The separate hosted isolation setup at that head stopped before tests on a Microsoft package feed HTTP 403. Both failures are retained. No study configuration, scoring or reader bytes changed.

### Limitations and blocked checks

- The independent and human labels remain NOT_RUN. The original 17 private checks remain incomplete and original 100 transfers remain NOT_RUN. Recovery is INTERRUPTED / UNRECOVERED. Publication incident OPEN. Round 3 preparation/scoring same-operator.
- D03-A retrieved both witnesses but attribution admission stopped in interpretation. Wrong-reporter control also stopped before proof. No repair or consolidation was measured.

### Next steps

- Run unchanged exact-head release and archive checks for the evidence PR, download and compare the pushed files, merge if qualified and verify Pages. A separate follow-up may distinguish generic and named-source attribution adjuncts with proof-stage contrasts.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
