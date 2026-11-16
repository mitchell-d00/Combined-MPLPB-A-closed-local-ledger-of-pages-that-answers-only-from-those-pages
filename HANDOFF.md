# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f82d9548af31e00e4b3335c9d09b1ceae884002e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `6e08c391fd1fedd351610ea32135b5b41e2c53ce46e73d954479c218073dd3a3`.

## Latest user update instructions

Can you do yiur suggestions and test them and once they pass tests push them and merge to main

MPLPB’s public original records

Can we sandbox the execution operator.

## Implemented scope

- Add a concrete original-record evaluation workflow using four unchanged public MPLPB originals: prepare, seal, run and score phases with pinned sources, question/gold separation, code/configuration receipts and non-overwriting output.
- Require complete source-cited review submissions, distinct reviewer IDs, explicit self-reported effort and adjudication for disagreement. Never claim that IDs or protocol tests prove independent human validation.
- Preserve existing 52-case suite, frozen reports, historical/vendor bytes and current source authority. Update affected operational guides and result/test index. Merge only after exact-head required checks pass.
- Add opt-in Linux bubblewrap worker isolation with read-only inputs/code, excluded gold and host credentials, private scratch, isolated network, cleared environment, dropped capabilities, resource limits, run-bound receipts and required real-isolation CI. Fail closed without direct fallback.

## Validation recorded

- All fifteen final protocol/isolation tests pass, including actual Linux namespace file/network/environment probes, gold-free execution, tamper rejection and stale sandbox-receipt rejection. Required-isolation mode ran with no skips.
- The unchanged strict public suite passes 52/52 with zero observed false supported bridges. Documentation audit passes for 234 documents and 27 evaluation families. Full regression, exact-head archive/browser CI and dedicated required-isolation CI remain to complete.

## Limitations and blocked checks

- No external reviewers or genuinely unseen questions have been supplied. Preparation deliberately emits no invented holdout questions or human judgments. Independent validation cannot be claimed from this work.
- This implements evaluation infrastructure; arbitrary semantic event inference, automatic historical correction, unrestricted as-of reasoning and externally attested READ/ACK transitions remain outside current capabilities. Reviewer time/identity are self-reported and unverified.
- Sandbox isolates the execution worker, not its human operator, trusted host custodian, administrator or kernel. Limits are per process/file except wall timeout and scratch size; aggregate process-tree resource containment is not claimed.

## Next steps

- Complete final protocol/isolation and full regression checks, publish this candidate and require all exact-head checks including actual sandbox isolation before merging; then observe postdeployment verification.
- Have separate external authors/reviewers supply unseen questions and judgments, then publish their permitted receipts and results after adjudication.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
