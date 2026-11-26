# Repository handoff

Last reviewed: 2026-11-26.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `dbf7e10efa0d1d2037186cb8848b312d0d179b1f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `c4d97e861ccc50b9caa184e03f5bcb5205592d47d494bc4013d02372ebb23496`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty: Finish the public replay inventory and prepare the next achievable verification plan for C3 on PR #106. The original recovery attempt is closed as INTERRUPTED / UNRECOVERED; do not wait for the retired session.

Classify each relevant case as:
- Exactly replayable from available inputs, initial state, runner, budgets and scoring contract.
- Receipts or outputs only.
- Unavailable.

Preserve original IDs, hashes, results and failures. Keep the original 17 preservation checks incomplete and the 100 original transfer cases NOT_RUN unless their exact required materials are recovered.

For missing coverage, propose separately identified replacement cases with explicit acceptance criteria. Freeze their inputs and expectations before execution. Do not count replacements as completion of the original missing tests or claim independent blinding.

Continue unaffected public replay and cleanup work. Keep the restricted-text publication incident separate; prepare precise remediation before any destructive history changes.

Update the Test Index, HANDOFF and PR report with what is available, what ran, what remains missing and the next executable step. Push recoverable checkpoints.

Existing publication, merge and deployment authorization remains in force when applicable requirements pass. No new language-test series or additional scope is needed.

### Implemented scope

- Complete the C3 per-case public replay inventory, retain a separate public rerun receipt, and record replacement preservation contrasts and acceptance before any new cases are authored or run. No reader change.

### Validation recorded

- Verified all 832 frozen authorized packet and retained result hashes, 65 frozen harness files and 104 distinct staged worker files across 35 cohorts. Hosted rerun at the existing C3 pin 3bf9657 passed four isolation controls and 832/832 full normalized contracts with zero execution failures.
- BB consumed regression reproduced 900/900 exact positives, 900/900 eligible citation readbacks and 200/200 negative withholds on 100 hash-matched fixture files. The 572 exposed D% cases have verified public inputs; their original scores stay receipt-only because the sealed custody key/dice bytes are unavailable.
- Current tree contains neither known restricted archive blob. Introducing ancestry remains reachable. The earlier publication incident and interrupted raw-output retention failure remain separately recorded.

### Limitations and blocked checks

- Original attempt remains INTERRUPTED / UNRECOVERED. The 17 original private checks remain incomplete and the 100 original held cases unavailable and NOT_RUN. No inferred reader decisions or replacement scores.
- No independent blinding or adjudication. No C3 merge, deployment, or gate substitution. Human onboarding, independent historical/semantic evaluation, outside-custodian scoring, and native OOCC stay NOT_RUN.

### Next steps

- Freeze the five named replacement preservation pairs and expectations in the recovery closure before executing any. Use the existing isolated runner and compare released 2622813 and C3 3bf9657 with unchanged budgets.
- Retain the original misses, withholds and incomplete checks. Any future separate replacement transfer requires its own frozen candidate ZIP and the documented preparation and exposure record.
- Handle publication remediation independently; preserve evidence and present exact destructive ref or artifact operations before execution.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
