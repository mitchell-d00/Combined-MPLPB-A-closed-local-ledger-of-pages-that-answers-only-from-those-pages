# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `bfd41a5a1392ccd5579b0e789be98690cffb6a1b` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `2829dc8202192a16f562249f3c0ec71e8cf4459211a3f4ad6f6479e64697a744`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty: First priority is getting the actual local work safely published—not only its description.

Recover the original workspace when available. Verify and push C3’s actual source changes and reviewed public test outputs to the branch, clearly marking unfinished verification. Preserve rejected candidates and original failures. Keep sealed inputs, held keys and private material in their designated custody.

If files remain inaccessible, list exactly which files are missing. Do not reconstruct them from summaries and call them recovered. Continue under my existing publication and merge authorization once required checks pass.

Then organize the existing repository around its three entry areas:

1. MPLPB product: runnable software, installation, ordinary-user instructions, releases and supported capabilities.
2. Experimental Lab: proposed changes, development trials, candidate implementations and unresolved questions.
3. Testing apparatus and evidence: reusable runners, test families, frozen protocols, results and retained failures.

Extend the existing Test Index into the connecting map. Each test family should identify:
- Stable ID and responsible area.
- Capability or boundary tested.
- Baseline and candidate revisions.
- Input/artifact checksums and retrievable evidence locations.
- Results, remaining misses and execution status.
- Development, consumed-transfer or unopened-transfer status.
- Related fixes and preservation checks.

Use links and manifests first. Preserve historical paths and frozen archive bytes. Store large public evidence in durable, versioned locations with checked links.

Make the path easy to follow:
product capability → implementation → test → result → retained evidence.

At future work boundaries, push actual source and available public evidence with the working-state handoff. Report separately what is published, verified, merged and deployed.

Clarification: The next milestone is getting those actual code files into a remote commit, then preserving the test evidence. Keep recovery ahead of reorganization and avoid publishing mixed archives blindly. A stalled command does not establish file loss.

### Implemented scope

- Actual C3 core recovered and included: seven changed mplpb_answers modules, new tests/test_bunyip_round2.py, existing-workflow assessor and development generator. Exact file hashes and archived byte comparison are in evaluation/cryptid/bunyip/round2/recovered-source-v1.json. This is an unfinished source checkpoint; no candidate ZIP freeze or transfer execution is implied.
- Canonical [Al](docs/TEAMBUILDING.md#al--review-evidence-and-propose-the-next-test), [Betty](docs/TEAMBUILDING.md#betty--implement-test-and-retain-the-result) and unchanged [Outside](docs/TEAMBUILDING.md#outside) definitions; [artifact and working-state recovery](docs/TEAMBUILDING.md#recover-artifact-state-and-working-state). Shared-rule and broader-coverage criteria remain in force.
- Complete recovery record: [Bunyip round2 checkpoint](docs/recovery/BUNYIP_ROUND2_CHECKPOINT.md). It records revision, task, criteria, decisions/reasons, rejected candidates, unresolved objections, custody, local archive hashes, infrastructure failures and authorized next actions. Prior released handoff/update retained under handoff/history/.
- Original museum diagnostic-copy implementation, JavaScript tests/fixture and four workflow integrations now included. This UI work is separate from reader-language gains. Public evidence bundle, unchanged baseline archive and exact rejected C1/C2 source archives are included; see evaluation/cryptid/bunyip/round2/public-artifacts-v1.json.
- Existing optional source-metadata/read-only diagnostic worker adapter and public routing/polarity development packets are published unchanged. Remote workflow reuses D.run, sealed worker hashes, current limits and required Bubblewrap; it executes only public development on baseline/current source. Held keys remain local, so semantic scoring stays separate.
- Remote raw baseline/candidate ZIPs and unchanged strict/source-score files are durably versioned under round2. Candidate source-key development comparison572/572 passes; this is not unseen transfer, independent semantic adjudication or historical accuracy.
- Three existing entry areas now lead to product use, experimental development and evidence inspection. Existing Test Index/results.json connects66families/69family+subfamily IDs to responsibility, protected scope, implementation, tests, per-run pins/checksums, results/misses, execution/custody and preservation. Older multi-revision metadata explicitly refers to retained per-run receipts rather than inventing a single pin. Root README131lines. No physical paths moved.

### Validation recorded

- Current recovered source and public evidence are committed through46a0bb0 and generated handoff8a53b5f; main remains2622813. Actual source hashes and retained raw receipts supersede earlier outage-only status. Historical checkpoint statements remain in dated records.
- Public evidence selection includes4597 original files/27800118 uncompressed bytes; every bundled payload byte hash reverified. Keys, held transfer inputs and private material excluded. Rejected source snapshots retained byte-identically. Packaging first attempt failed a narrow allowlist before upload; inspected the public regression-test member and retained that attempt without changing reader or scoring.
- Recovered local C3 primary record:75/444 completed;75 source-key decisions correct, including14 positives;369 execution failures. Guards0/44 completed and44 execution failures. These are not369+44 reader refusals. At exact source commit baa19f5 remote regression passed1904tests with1skip plus JS/API/WASM/Chromium; later-head checks remain required.
- Matched remote development at483f35a:572 executions per revision, zero execution failures. Candidate128/128 supported positives+444/444 correct withholds;71 recovered positive executions across34 original question strings/71unique inputs.40executions/19strings are the matched-source wording diagnostic;31other source/proof recoveries separate.89question strings,524unique inputs,48repeated memberships per572.
- Source/citation audit:12 corrected baseline unsupported cases, zero lost valid support, no citation change to preserved support. Original main contract replay is exact for all560 earlier frozen baseline cases. All22 original strict-key output failures retained; all22 satisfy the prospective pre-implementation polarity contract and exact quotations.
- Navigation stage: stable IDs unique; Outside definition byte-unchanged; original documents preserved in reviewed versioned history snapshots. No frozen input/key/score or historical measurement was modified or rerun by navigation. Native1904(1skip) source test and572case comparison remain distinct from metadata/transport work.
- All849 retained released-reader contract outputs recovered directly; all recorded reader-code maps match the released main baseline. Reference archive SHA25671bd781c5a10041652a6b83d7d4b29ff30042f79006c00c7f5301b75fc1ae7a2; this validates reference identity, not C3 preservation. Interrupted C3 preservation retained separately.

### Limitations and blocked checks

- 36 routing and64 cross-family transfer cases remain unopened/unrun under same-operator custody. Human onboarding, independent historical/semantic adjudication/preparation/blinding/outside-custodian scoring and native OOCC remain NOT_RUN.
- PID1 diagnostic was denied by automatic approval due supervisor disruption risk and was not executed. No sandbox/protection gate may be bypassed. No new round2 deployment verification has occurred.
- Local Git working branch still has baseline ancestry2622813 and original uncommitted files; remote API commits are the current published state. Do not force-push/reset or deliver a local archive as current without reconciling. The key-bearing frozen-development-inputs.tar.xz was removed from the local index without changing its bytes, privately copied/verified, and explicitly ignored for publication. All held transfer/key material remains excluded.
- Local process exhaustion persists; actual source/evidence/navigation are published. Remote recovery workflow generated and checked the handoff; current exact-head gates and849C3 preservation are pending. Development passes do not erase22strict-key failures or rejected candidates. Both held packets remain unopened.

### Next steps

- Complete exact-head navigation/handoff/docs checks and the released quickstart software walkthrough; finish849contract preservation and unchanged BB accounting, then freeze the committed source ZIP before opening36+64held transfer once. Keep current PR report/source pins synchronized. Publication authorization persists.
- Inspect/replay C3 execution failures and preservation including unchanged Bunyip BB; audit source support/polarity/citations/conflicts separately. Update authoritative Test Index/department map with actual outcomes. Freeze committed ZIP before either designated transfer packet is opened once.
- Run all required exact-head checks and acceptance/protection gates, then merge and verify deployment/live fingerprints under existing authorization. Existing coverage gaps may remain backlog; missing implementation or blocked gates are not passes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
