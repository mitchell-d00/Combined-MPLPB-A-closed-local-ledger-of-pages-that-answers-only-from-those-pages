# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d8d4cd5c4c4f3abd1ff1325868f0d16714b24eab` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `cdea345649559e5fdbbc1a7cb6c8474c3a3aa7c5e3fced1711699e6907fc732a`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Alongside Round 4, establish an Egyptian-series registry modeled on the Cryptid programme. Inventory existing families, retain their original results, and define the next Bast set around a specific uncovered responsibility.

Build deterministic generators, stable case IDs, frozen expectations, positive/negative pairs, and reproducible manifests. Distinguish development, consumed preservation, and fresh transfer.

Finish each family with end-to-end I/O checks: actual source inputs and questions must produce the expected answer status, supported fields, citations, unresolved fields, and diagnostics. Keep execution failures separate from reader misses.

Use Round 4’s attribution work as the first bounded implementation task. Freeze the wider programme now; execute it in small batches after each preceding result is recorded. Preserve failures and custody limits, then push and merge qualifying work under existing authorization.

**Round 4 produced a bounded gain:** one additional fresh complete answer, with prior valid outcomes preserved. The wrong-reporter controls now reaching proof is useful evidence; their earlier withholding alone did not establish that distinction worked.

For Bastet, my proposed rule is:

**The printed writer may select an eligible document; the embedded reporter determines attribution of the statement.**

Selecting Alice’s document must not turn Bob’s reported statement into Alice’s statement.

Betty should freeze matched cases covering:

- One eligible document with the requested printed writer.
- The same document with a different embedded reporter.
- Two eligible documents sharing that writer; uniqueness is unresolved.
- A writer’s name appearing only in quoted content.
- Missing or conflicting writer information.
- A correct document selection paired with an unsupported reporter attribution.

Record document selection and claim attribution separately. Require the full source-to-answer I/O contract, including citations and withholding reasons.

Finish #115’s checks, merge, and deployment verification first. Then pin that released reader as Bastet’s baseline. Preserve the named-source miss as a development case; use separately frozen cases for the fresh comparison.

The retained scorer errors and corrected coordinate readback should stay visible together. The original 87/96 result and its narrowly scoped diagnostic policy remain unchanged.

### Implemented scope

- After verifying PR #115 deployment, register the Egyptian programme, freeze Bastet development and fresh cases with separate keys, and retain Round 4 F05 as consumed development.

### Validation recorded

- PR #115 passed all 11 checks and the live Chromium, preview hash and native-module checks. Bastet baseline is the verified released merge. Generated and verified six matched pairs per draw with no execution yet.

### Limitations and blocked checks

- Bastet named selection and attribution remain unmeasured at the freeze. Fresh transfer and independent evaluation NOT_RUN. Original incomplete evidence and publication incident remain unchanged.

### Next steps

- Run only the frozen Bastet development arm and record selection, attribution and withhold reasons separately. Keep fresh reserved for a later committed candidate.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
