# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `29584ff02e7b03494c393c47d95b64c3f7f20745` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f5d0e92e2028677b73187da33282b68aee74c33e9348c41c5d7e544b58e0e6cc`.

## Latest user update instructions

Do it run it until it’s fixed

## Implemented scope

- General whole-question literal field-request syntax in the existing exact parser; additive inspectable normalization; no core authority changes.
- Unchanged public reproduction preserved with baseline at published bbf6690 and pre-change 3483b1a; new tests and exact CSV scoring.
- Separate follow-up branch feature/field-question-normalization based on unmerged PR56; no merge performed.

## Validation recorded

- New regression failed before fix; 37 focused tests passed after syntax change; nine expanded controls pass.
- Public reproduction: baseline 150/150 canonical,0/750 paraphrases; updated150/150 and750/750. All200 negative controls refused. Script runs exit0.
- Full frozen-archive regression and public evidence pending; never infer pass from prior candidate.

## Limitations and blocked checks

- Literal field labels only; no semantic aliases or general historical reasoning.
- Public fixture now known development material; independent review NOT RUN.
- Browser/WASM/live-site and current historical/D% reruns not yet performed.

## Next steps

- Freeze commit/archive and run full regression/public controls; retain all logs and actual exit statuses.
- Record exact key-value CSV scoring and costs; update documentation and handoff after results.
- Do not merge without exact-head release checks and authorization.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
