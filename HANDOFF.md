# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `b24238f2970f1e4c1573edf4c11dc47cbd3c9e66` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `fbf4e72297ea33681027a8c27e9363fa785be6847daf46b4e4e0b3e005946278`.

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
- The first frozen fresh replay matched all 12 I/O contracts. It verified eight selections and six attributions, with two selected-source reporter refusals, and no unsupported claims.
- The 832 preservation attempt stopped at the frozen harness checksum because new tests shared a frozen test file. The original test bytes are restored and new tests are in a separate file. This does not alter reader bytes, keys, or the first fresh result. The original attempt is retained.
- The isolated retry matched all 832 public contracts with unchanged native bytes. BB matched 900 positives, 900 citations and 200 withholds. The retained 96-case run reproduced 87 exact matches and the same nine bounded diagnostic changes. The original exact failure stands.

### Limitations and blocked checks

- The implementation covers the two frozen named-document forms and eligible anchored printed bylines. Fresh synthetic transfer has been run. Independent historical accuracy, outside scoring, independent adjudication, native OOCC and human evaluation are NOT_RUN. The historical incident remains open.

### Next steps

- Finish exact-head checks on PR #117, verify remote evidence bytes, then merge and verify the published runtime if all requirements pass. Keep the first fresh score and frozen original baseline unchanged.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
