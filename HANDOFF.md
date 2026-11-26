# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d4d5c192f6ff75c93a3f305c6b335378886c2a70` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `bb3eab996f06775a75838b38b9ed5d726df7aaeb57309d41ab8dffeb6f56edd9`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty: Continue the existing Bunyip reader work on PR #106. Main’s #107 documentation release is complete. Verify the current pins before proceeding.

Your first task is recovery and completion, not a new experiment.

1. Recover access to the original workspace. Verify the private preservation files, retained evidence and custody receipts. Preserve the old workspace until recovery is confirmed. Keep both held transfer packets unopened.

2. Establish a healthy, authorized isolated runner. Leave PID1 and the supervisor untouched. Run the 17 unchanged private preservation cases sequentially, retaining their actual outputs privately and publishing only permitted comparisons and receipts. Distinguish execution failures from reader decisions.

3. Privately inventory the restricted source text in the mistakenly published outputs. Prepare the exact history/artifact cleanup needed, preserving original evidence privately. Do not claim current-tree deletion erased history. Present any destructive history changes concretely before executing them.

4. When preservation and custody requirements are satisfied, freeze the designated committed candidate ZIP. Run the existing 36-case routing and 64-case cross-family packets once. Retain every result; any packet used to inform repairs becomes development material.

Keep coverage gains, consolidation, boundary correctness and infrastructure status separate. Preserve frozen keys, original failures and acceptance requirements.

Push recoverable source and permitted evidence at meaningful work boundaries. Update #106, HANDOFF and the Test Index so another session can continue.

My publication, merge and deployment authorization remains in force. Complete required checks, merge when applicable requirements pass, and verify deployment. No further confirmation is needed for already authorized work. If blocked, publish the precise checkpoint and continue unaffected work without weakening gates.

Follow-up: Note it as a inturptuion lost data and clean up check all the last few Betty notes to catch up

### Implemented scope

- Recovery checkpoint only. Verify live pins, public custody receipts, affected Git ancestry and Actions artifact metadata. Record the proposed cleanup in evaluation/cryptid/bunyip/round2/recovery-checkpoint.md and link it from the Test Index.

### Validation recorded

- Verified main 515a919df40996e9d1d521dd50474b832a1a599c and starting PR #106 head cc54c4276bb4895c33df46cc782e758f4c8e5a0b. Release follows the existing #107 deployment receipt. C3 reader, keys, acceptance and previous evidence remain unchanged.
- Both permitted replacement archives match their SHA-256 digests, lengths and recorded file-member counts. The cancelled source-ZIP run lists zero artifacts. Ancestry and Actions metadata checks are recorded separately from private payload review.
- Synthetic no-input Bubblewrap probes failed at namespace startup, before any reader invocation. No private or held case ran. PID 1, the supervisor and the original workspace were untouched.
- Reviewed the last three Betty reports (#105–#107) and recorded the interruption. Of 122 inspected heads, tags and #106 refs, only the Bunyip branch and #106 head and test-merge refs descend from the introducing commit.

### Limitations and blocked checks

- The attached workspace does not contain the original Bunyip custody files or local publication-session receipt. Their availability elsewhere and integrity are unverified. Access and isolation are blocked; file loss is unverified.
- 832 public comparisons remain exact, one previous private probe failed execution and sixteen private cases remain NOT_RUN. Both held transfer packets remain unopened. No candidate transfer ZIP was frozen and no C3 release occurred.
- The incident archive paths are absent from the current tree and the prior history remains reachable. Private source-span inventory, artifact payload clearance and destructive history changes are pending. All independent and human NOT_RUN labels remain.
- First remote preservation run 45870399223 did not retain its raw outputs in Actions after EACCES. The full job log exists. Original private custody is unavailable to this session; permanent loss is unverified.

### Next steps

- Recover the original custody mount and confirm the original receipts and hashes in a healthy authorized isolated runner. Run the seventeen unchanged cases sequentially; keep raw outputs private.
- Privately preserve and inventory the affected material. Present the exact ref and artifact mutations from the recovery plan before executing destructive cleanup.
- After preservation and custody gates, freeze the committed source ZIP, execute the 36 and 64 held cases once, retain results, complete applicable protected checks, then merge and verify deployment.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
