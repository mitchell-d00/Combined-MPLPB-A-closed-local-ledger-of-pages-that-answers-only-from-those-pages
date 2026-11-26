# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `89b1dc031ced2cc96f0e44f77fc9dcd230d992d0` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `a4e4c30f38b7eefb3a798b7958e5eb3ce2dea7c57896cfaa615f7b8eb36a81ac`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty: You have my explicit authorization to push, complete the required checks, merge to main and verify publication. Prioritize making the work recoverable before I leave; do not wait for another confirmation.

Push the current branch and open or update its PR as soon as the environment permits. Include the current implementation, retained evidence, TeamBuilding definitions and HANDOFF working state: exact revisions, decisions, objections, custody, blockers and next actions.

Run the required checks, using remote CI where supported if local execution remains blocked. Merge once those requirements pass. Document existing coverage misses as backlog unless they violate the agreed release criteria.

If verification is blocked, still push the recoverable checkpoint and clearly record the blocker. Do not label blocked checks as passed or bypass protected gates.

Keep sealed transfer inputs and held keys in their designated custody; exclude private correspondence. Preserve volatile evidence before any environment restart.

Finish by reporting the pushed commit, PR URL, main commit if merged, deployment status and anything still pending.

### Implemented scope

- Recovery checkpoint via GitHub connector, based on main2622813aba9ee1f1880693eeb71ae015cb3da999. Local branch local/bunyip-round2 held uncommitted C3 native changes; the environment is offline and their exact bytes cannot be uploaded now. This remote tree contains documentation/coordination only, not a C3 release.
- Canonical [Al](docs/TEAMBUILDING.md#al--review-evidence-and-propose-the-next-test), [Betty](docs/TEAMBUILDING.md#betty--implement-test-and-retain-the-result) and unchanged [Outside](docs/TEAMBUILDING.md#outside) definitions; [artifact and working-state recovery](docs/TEAMBUILDING.md#recover-artifact-state-and-working-state). Shared-rule and broader-coverage criteria remain in force.
- Complete recovery record: [Bunyip round2 checkpoint](docs/recovery/BUNYIP_ROUND2_CHECKPOINT.md). It records revision, task, criteria, decisions/reasons, rejected candidates, unresolved objections, custody, local archive hashes, infrastructure failures and authorized next actions. Prior released handoff/update retained under handoff/history/.

### Validation recorded

- GitHub main verified2622813aba9ee1f1880693eeb71ae015cb3da999/tree78ffea54e3ad0e35ac1dd27f6db16c32a8ec23dc; no open PR at discovery. Outside definition is unchanged from that exact revision. No reader code, frozen tests/keys or acceptance policy is modified in this remote checkpoint.
- Session-recorded local state: baseline21/78 primary positives and360/366 withholds; C1/C2 primary recovery rejected after2 and4 newly exposed unsupported completions respectively. C3 focused37 passed; broad C3 acceptance remains pending. See the checkpoint for disjoint suite counts and original failures. Offline access prevents re-verifying raw local receipts.
- Unique completed/resource-attempt evidence was byte-verified into persistent local archives before the outage. Archive locations/hashes are recorded; their payloads are not uploaded in this checkpoint. Held inputs/keys and private correspondence are excluded.

### Limitations and blocked checks

- Current native implementation and raw evidence are NOT in this pushed checkpoint: source access blocked by offline environment. Do not infer C3 software checks from remote documentation-tree checks.
- Observed host zombie-process exhaustion caused EAGAIN, then execution environment became unavailable. Local handoff build/check failed to launch. Initial checkpoint inventory may be stale until the dedicated recovery workflow rebuilds/checks it; retain the original failed checks and judge the latest exact head.
- 36 routing and64 cross-family transfer cases remain unopened/unrun under same-operator custody. Human onboarding, independent historical/semantic adjudication/preparation/blinding/outside-custodian scoring and native OOCC remain NOT_RUN.
- PID1 diagnostic was denied by automatic approval due supervisor disruption risk and was not executed. No sandbox/protection gate may be bypassed. No new round2 deployment verification has occurred.

### Next steps

- Restore the same workspace without discarding volatile evidence; verify archives, source/index, custody and recorded state. Upload actual implementation and reviewed public evidence, excluding held inputs/keys/private material; reconcile local and remote histories.
- Inspect/replay C3 execution failures and preservation including unchanged Bunyip BB; audit source support/polarity/citations/conflicts separately. Update authoritative Test Index/department map with actual outcomes. Freeze committed ZIP before either designated transfer packet is opened once.
- Run all required exact-head checks and acceptance/protection gates, then merge and verify deployment/live fingerprints under existing authorization. Existing coverage gaps may remain backlog; missing implementation or blocked gates are not passes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
