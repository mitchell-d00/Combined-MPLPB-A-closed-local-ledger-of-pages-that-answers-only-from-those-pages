# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6174184edc1b47c7363a6369f7fe40ccb226601a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `da5348e19ff786619fa43e773dcdbb10d6a3315a772a8506a694c1b6b1789812`.

## Latest user update instructions

Sorter needs to label things in sorting as possible connections , supported etc and tags that make user aware   , entity resolution, event co-reference, historical truth, and an unofficial free-form question answering. That is not mplpb but a way to explore ideas that are not fact or presented as fact .

## Implemented scope

- Add a derived, replay-verified sorter view with explicit textual/candidate/identity/event/truth tags;preserve saved sorter formats.
- Add a separate free-form question-exploration CLI with optional local-model hypotheses/open questions;no ledger writer or promotion.
- Keep native strict results separate;reuse original-question/profile retrieval boundaries and recheck current sources after inference.
- Document labels,full-context citations,budgets,model limitations and exact commands.

## Validation recorded

- 14 new focused tests passed;baseline and prior historical evaluations retained unchanged.
- Broader test invocation encountered2 existing narrator HTTP socket PermissionErrors in sandbox;capability-enabled rerun recorded separately.
- Extracted frozen full regression/public/interface checks pending.

## Limitations and blocked checks

- Model hypotheses are semantically unverified;matching citations do not prove them.
- New labels do not implement verified entity resolution,event identity or historical truth.
- Live local-model interpretation quality and independent historical accuracy NOT RUN;no coverage gain claimed.
- CLI/Python inspection view only;existing browser default unchanged.Nothing pushed.

## Next steps

- Freeze and archive committed source;run full Python/public controls and applicable interface checks from extraction.
- Retain actual demo outputs,source replay checks,all errors and final measured costs.
- Update evidence-only final report,handoff and docs without altering tested implementation bytes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
