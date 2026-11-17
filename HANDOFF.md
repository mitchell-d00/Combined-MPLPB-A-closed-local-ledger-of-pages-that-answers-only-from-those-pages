# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ccbb5804eb47f78c2338d57c142ad087b47be710` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `db2373a3222bb3c56a9db51eaaf1b3f75d3ba7cf5ea338afe431151d4ea8f5e8`.

## Latest user update instructions

Reproduce, diagnose, and fix false identity clustering in MPLPB’s offline sorter. Most important instruction is to fix occurrence classification, not just remove one cluster edge. A good fix distinguishes “this identifier appears in a document” from “this identifier is declared as the identity of this document.”

One of the main things we preserve the task state and verification rules so any capable AI instance can resume the work. demonstrating that the system doesn’t need its previous AI instance to keep functioning. While investigating how little continuity an individual AI instance actually needs.

## Implemented scope

- Reproduce the supplied probe on the native package and preserve original archive/source bytes. Add and run failing regression tests before implementation.
- Classify embedded versus primary headers before source-occurrence partitioning; preserve all observed quotations and forward/copy appearances.
- Gate primary cluster/reference/status/date consumers by structural role; add inspectable embedded-identifier review annotations. No reader/authority changes.
- Extend positive, adversarial, Unicode, budget, replay and native safety checks; preserve before/after exact evidence-node traces.
- Retain a resumable checkpoint with source/test/probe hashes, commands, results, verification contracts and remaining ambiguity independent of this conversation.

## Validation recorded

- Baselineccbb580 sorter suite27 tests passed0.891s. Two new regressions failed before changes:3-member cluster and3 instead of2 occurrence partitions. Exit1/log retained.
- Full native supplied probe reproduced baseline contamination (4 cluster members). After fix the original probe intentionally exits1 because its bug-presence assertion is now false; other invariants remain true.
- Final sorter42 tests passed1.005s; focused sorter/native99 tests passed1.989s, exit0. All12 requested classes covered with positive and negative controls.
- Minimal cluster3→2, supplied cluster4→3; source/node observations remain preserved and source bytes unchanged. Concatenated file partitions3→2.
- Fresh-process verification exists; fresh AI-instance resumption and minimum model context size remain NOT RUN/unknown. Frozen full regression/public-evidence runs pending.

## Limitations and blocked checks

- Finite layout recognition, not semantic authentication or general event identity resolution. Unmarked/OCR-damaged copied headers may remain ambiguous.
- Quoted/forwarded records remain inspectable but not primary declaration members; unclosed frames conservatively remain review-scoped.
- No supported answer or historical truth is granted. Existing reader authorization/serving/retirement gates remain unchanged.
- A deterministic fresh-process replay is not a measured proof of arbitrary AI-instance continuity or historical accuracy.

## Next steps

- Freeze implementation, run full Python/public-evidence suites and retained probe/fixture checks from an extracted committed archive.
- Record actual failures/successes and resource metrics in a separate evidence update, keeping the tested runtime unchanged.
- Successor: read checkpoint.json and REPORT.md in the header-scope evidence directory; preserve verification rules, never restore the probe’s defect merely to make its obsolete final assertion pass.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
