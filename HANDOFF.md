# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `a1021cc3403bd395049359e6d311993ebc25c16a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `3a94233da22378f4d9e7a7271dbc6966f8d591d661b1b758896f06d5850bcdd0`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Close the recovery attempt as INTERRUPTED / UNRECOVERED. Stop waiting for the retired session.

Preserve all published code, evidence, hashes and failure records. Mark the 17 private preservation checks incomplete and the 100 unavailable transfer cases NOT_RUN. Do not infer reader passes or failures from missing data.

Prepare a replacement verification plan using available, authorized sources. Distinguish exact reconstructions supported by retained bytes from newly authored replacement cases. Freeze new inputs and expectations before testing, and preserve the original missing checks as missing.

Record the interruption as a workflow/data-availability failure, with context-compaction involvement suspected but unconfirmed.

Continue public cleanup and organization. Keep the archive-publication incident separate; retiring the old session does not resolve its Git-history exposure.

Update HANDOFF with the next achievable step. Do not convert unavailable verification into a pass.

### Implemented scope

- Recovery checkpoint only. Verify live pins, public custody receipts, affected Git ancestry and Actions artifact metadata. Record the proposed cleanup in evaluation/cryptid/bunyip/round2/recovery-checkpoint.md and link it from the Test Index.
- Close the original recovery attempt as INTERRUPTED / UNRECOVERED. Document exact replay and new-case replacement criteria in the Round 2 recovery closure and link from the Test Index.

### Validation recorded

- Verified main 515a919df40996e9d1d521dd50474b832a1a599c and starting PR #106 head cc54c4276bb4895c33df46cc782e758f4c8e5a0b. Release follows the existing #107 deployment receipt. C3 reader, keys, acceptance and previous evidence remain unchanged.
- Both permitted replacement archives match their SHA-256 digests, lengths and recorded file-member counts. The cancelled source-ZIP run lists zero artifacts. Ancestry and Actions metadata checks are recorded separately from private payload review.
- Synthetic no-input Bubblewrap probes failed at namespace startup, before any reader invocation. No private or held case ran. PID 1, the supervisor and the original workspace were untouched.
- Reviewed the last three Betty reports (#105–#107) and recorded the interruption. Of 122 inspected heads, tags and #106 refs, only the Bunyip branch and #106 head and test-merge refs descend from the introducing commit.
- The a1021cc recovery and repository handoff workflows passed. This closure changes public coordination text only. No replacement, private or held reader case was run.

### Limitations and blocked checks

- The attached workspace does not contain the original Bunyip custody files or local publication-session receipt. Their availability elsewhere and integrity are unverified. Access and isolation are blocked; file loss is unverified.
- 832 public comparisons remain exact, one previous private probe failed execution and sixteen private cases remain NOT_RUN. Both held transfer packets remain unopened. No candidate transfer ZIP was frozen and no C3 release occurred.
- The incident archive paths are absent from the current tree and the prior history remains reachable. Private source-span inventory, artifact payload clearance and destructive history changes are pending. All independent and human NOT_RUN labels remain.
- First remote preservation run 45870399223 did not retain its raw outputs in Actions after EACCES. The full job log exists. Original private custody is unavailable to this session; permanent loss is unverified.
- Workflow and data-availability failure. Context-compaction involvement is suspected but unconfirmed. Permanent loss of original custody is unverified; no reader outcome is inferred.

### Next steps

- Inventory authorized public replay material against retained original source, question, expected contract or key, harness and budget pins. Mark receipt-only and unavailable cases explicitly.
- Prove required isolation on synthetic controls. Freeze newly authored replacement inputs and expectations separately. Keep the original 17 checks incomplete and original 100 transfer cases NOT_RUN. Freeze a committed candidate before opening newly authored transfer.
- Track the publication incident independently. Preserve evidence, present destructive changes concretely before executing them, and keep history exposure open until verified cleanup.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
