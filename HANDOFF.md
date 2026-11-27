# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `99666618df1b2a2531d5010b9c8d1d14ec64c3f4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `80183a2e505e7ecf71132b130eb79f154aa3b209562e13f42ab5231abc9f253f`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

**Round 4 is now a released gain. Bastet has a useful baseline, with fresh evaluation still untouched.**

Bastet’s discovery found the passages, but selection and attribution remain unproved. The duplicate-writer status miss also matters: staying claim-free is only part of the required contract.

Betty’s next bounded task should be:

> Implement Bastet’s document-selection boundary using the consumed development packet.
>
> Require source-backed evidence of the printed writer. Apply the declared eligibility constraints, then determine whether exactly one document qualifies. Preserve the distinction between document writer and embedded reporter throughout interpretation, proof, and output.
>
> Test selection and attribution separately: selecting the right document must not authorize a statement attributed to the wrong reporter. For duplicate eligible documents, return the frozen ambiguity contract rather than choosing one.
>
> Retain every baseline result, including the duplicate-writer status miss. Do not revise the key to accommodate the implementation.
>
> Pin the candidate before opening the existing fresh packet. Preserve its first fresh score; any subsequent repair makes that packet development evidence.
>
> Run the applicable preservation and release checks, push and verify the recoverable evidence, then merge and verify deployment when requirements pass under existing authorization.

The target is precise: **prove which document qualifies, then independently prove who said what within it.** Report gains in those two responsibilities separately.

### Implemented scope

- Require an unqualified printed byline in a unique eligible original, then use the existing, independent report proof. Preserve all frozen packets, keys and baseline receipts.

### Validation recorded

- 41 focused tests passed. Direct development smoke selected eight documents and attributed six claims, with six abstentions. Isolated replay is pending.
- Pinned candidate 55bd3ff03eeea593be69fe3e21d9395de2b9b24a with scoped source ZIP SHA-256 d622665da100120ad94a635b66301fb37bb52db2bb816031479bc2e90c1d542d.
- The isolated development replay completed all 12. It verified eight source selections and six report attributions, including two selected-document reporter refusals. All six abstention contracts matched, including the duplicate-writer case.

### Limitations and blocked checks

- Only the two bounded named-document question forms apply. Fresh transfer and independent evaluation have not been run.

### Next steps

- Run the unchanged fresh packet once on the pinned native candidate and retain the first score. Verify the applicable preservation and release checks before merge and Pages readback.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
