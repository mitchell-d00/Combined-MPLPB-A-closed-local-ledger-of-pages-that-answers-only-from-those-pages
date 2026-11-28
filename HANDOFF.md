# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `e34d20cca4d5e96ed08e40d785c9a9e8eb707f06` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `36baecf1b30b699e198a8457e383ae40c355d184f73132c033534a60ebd31199`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Give her a few experiments what do you think we should push next and would our sets we have now work or should we extend Greek gods

### Implemented scope

- Al review step: publish note 0006 against main e34d20cc with three bounded proposed Greek experiments.
- Keep existing sets as consumed regression/preservation; propose Apollo receipt provenance, Ares cross-process revocation and Hestia damaged-record recovery, executed in that order.
- Advice and map/coordination metadata only. No implementation, key, scorer, runtime, source packet or workflow changes.

### Validation recorded

- Read PR 124, Hermes-02 results, the frozen restart-store contract, Work Coordination guide and preserved networked signature guide.
- The reviewed report records 9/9 phases in each Hermes-02 draw with two intended writes, two durable completions and seven no-writer phases; host/store limits remain explicit.
- No new reader, cryptographic, revocation or recovery experiment was executed by Al.

### Limitations and blocked checks

- New experiment families are proposed. Current evidence does not establish authenticated human identity, cross-resource atomicity, damaged-store recovery or actual power-loss/distributed guarantees.
- Existing draws are consumed evidence with repeated structures and same-operator scoring; independent evaluation remains unmeasured.
- Off-workspace custody is still unverified and requires an approved private destination plus retrieval verification.

### Next steps

- Betty acknowledges note 0006 and records applied/deferred/rejected scope.
- Freeze each set's baseline, contract, inputs/key digests and scorer before execution; run Apollo first, then Ares and Hestia.
- Preserve first results and original grades, push recoverable checkpoints, run affected preservation and applicable exact-head checks, and merge qualifying lab work under existing authorization without activating production dispatch.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
