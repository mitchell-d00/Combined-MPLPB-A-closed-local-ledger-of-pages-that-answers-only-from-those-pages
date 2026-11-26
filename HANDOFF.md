# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `baa19f5b9d6d733735b4c570c74d7a643cd06e6e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `709d85bc10e96a7f282876f6694b7667c113a372997612826108275ac2914976`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty: First priority is getting the actual local work safely published—not only its description.

Recover the original workspace when available. Verify and push C3’s actual source changes and reviewed public test outputs to the branch, clearly marking unfinished verification. Preserve rejected candidates and original failures. Keep sealed inputs, held keys and private material in their designated custody.

If files remain inaccessible, list exactly which files are missing. Do not reconstruct them from summaries and call them recovered. Continue under my existing publication and merge authorization once required checks pass.

Then organize the existing repository around its three entry areas: MPLPB product; Experimental Lab; Testing apparatus and evidence. Extend the existing Test Index as the connecting map, preserving historical paths and frozen archive bytes. At future work boundaries push actual source and available public evidence with the working-state handoff; report publication, verification, merge and deployment separately.

### Implemented scope

- Actual C3 core recovered and included: seven changed mplpb_answers modules, new tests/test_bunyip_round2.py, existing-workflow assessor and development generator. Exact file hashes and archived byte comparison are in evaluation/cryptid/bunyip/round2/recovered-source-v1.json. This is an unfinished source checkpoint; no candidate ZIP freeze or transfer execution is implied.
- Canonical [Al](docs/TEAMBUILDING.md#al--review-evidence-and-propose-the-next-test), [Betty](docs/TEAMBUILDING.md#betty--implement-test-and-retain-the-result) and unchanged [Outside](docs/TEAMBUILDING.md#outside) definitions; [artifact and working-state recovery](docs/TEAMBUILDING.md#recover-artifact-state-and-working-state). Shared-rule and broader-coverage criteria remain in force.
- Complete recovery record: [Bunyip round2 checkpoint](docs/recovery/BUNYIP_ROUND2_CHECKPOINT.md). It records revision, task, criteria, decisions/reasons, rejected candidates, unresolved objections, custody, local archive hashes, infrastructure failures and authorized next actions. Prior released handoff/update retained under handoff/history/.

### Validation recorded

- GitHub main verified2622813aba9ee1f1880693eeb71ae015cb3da999/tree78ffea54e3ad0e35ac1dd27f6db16c32a8ec23dc; no open PR at discovery. Outside definition is unchanged from that exact revision. No reader code, frozen tests/keys or acceptance policy is modified in this remote checkpoint.
- Session-recorded local state: baseline21/78 primary positives and360/366 withholds; C1/C2 primary recovery rejected after2 and4 newly exposed unsupported completions respectively. C3 focused37 passed; broad C3 acceptance remains pending. See the checkpoint for disjoint suite counts and original failures. Offline access prevents re-verifying raw local receipts.
- Unique completed/resource-attempt evidence was byte-verified into persistent local archives before the outage. Archive locations/hashes are recorded; their payloads are not uploaded in this checkpoint. Held inputs/keys and private correspondence are excluded.
- Original workspace became reachable through a surviving shell despite process exhaustion. Actual source bytes were exported directly; nine files match the retained C3 archive exactly, and the development generator was retrieved directly with hash. No source reconstructed from summaries. Public evidence filtering/upload remains next.

### Limitations and blocked checks

- Observed host zombie-process exhaustion caused EAGAIN, then execution environment became unavailable. Local handoff build/check failed to launch. Initial checkpoint inventory may be stale until the dedicated recovery workflow rebuilds/checks it; retain the original failed checks and judge the latest exact head.
- 36 routing and64 cross-family transfer cases remain unopened/unrun under same-operator custody. Human onboarding, independent historical/semantic adjudication/preparation/blinding/outside-custodian scoring and native OOCC remain NOT_RUN.
- PID1 diagnostic was denied by automatic approval due supervisor disruption risk and was not executed. No sandbox/protection gate may be bypassed. No new round2 deployment verification has occurred.
- Core runtime source is now included; local UI/workflow/documentation changes and reviewed public output payloads are still being recovered. Previously published outage note is a historical snapshot. Local process creation remains EAGAIN; remote checks must evaluate this actual C3 head. Source publication is not acceptance/merge/deployment.

### Next steps

- Publish the actual recovered C3 core, then retrieve remaining original UI/docs/workflows and review public evidence member-by-member. Keep held packets/keys/private material excluded; preserve original rejected candidates and failures.
- Inspect/replay C3 execution failures and preservation including unchanged Bunyip BB; audit source support/polarity/citations/conflicts separately. Update authoritative Test Index/department map with actual outcomes. Freeze committed ZIP before either designated transfer packet is opened once.
- Run all required exact-head checks and acceptance/protection gates, then merge and verify deployment/live fingerprints under existing authorization. Existing coverage gaps may remain backlog; missing implementation or blocked gates are not passes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
