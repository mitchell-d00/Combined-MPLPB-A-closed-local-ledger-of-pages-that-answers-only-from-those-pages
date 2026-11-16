# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `330779de18f5f3a28b2bc507dfca42d2a29b0580` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f92e5ca32a97d39d5750a7cbba4e1d48504bc5e10deb78177c6ceb00e650ae65`.

## Latest user update instructions

Can you do yiur suggestions and test them and once they pass tests push them and merge to main

MPLPB’s public original records

## Implemented scope

- Add a concrete original-record evaluation workflow using four unchanged public MPLPB originals: prepare, seal, run and score phases with pinned sources, question/gold separation, code/configuration receipts and non-overwriting output.
- Require complete source-cited review submissions, distinct reviewer IDs, explicit self-reported effort and adjudication for disagreement. Never claim that IDs or protocol tests prove independent human validation.
- Preserve existing 52-case suite, frozen reports, historical/vendor bytes and current source authority. Update affected operational guides and result/test index. Merge only after exact-head required checks pass.

## Validation recorded

- Ten final protocol tests passed, including private salted commitments, gold-free execution, code/source/question tamper rejection, citation validation and honest disagreement/independence reporting.
- The existing 52-case suite passed. The initial full local run passed 936 tests before the final salted-commitment refinement; the refined protocol passed its ten focused tests. Extracted protocol and JavaScript/API/transport/crawler checks passed. Exact final-head full/archive/browser CI remains required.

## Limitations and blocked checks

- No external reviewers or genuinely unseen questions have been supplied. Preparation deliberately emits no invented holdout questions or human judgments. Independent validation cannot be claimed from this work.
- This implements evaluation infrastructure; arbitrary semantic event inference, automatic historical correction, unrestricted as-of reasoning and externally attested READ/ACK transitions remain outside current capabilities. Reviewer time/identity are self-reported and unverified.

## Next steps

- Run protocol, 52-case, full Python and required archive/browser CI checks; merge the tested candidate under user authorization.
- Have separate external authors/reviewers supply unseen questions and judgments, then publish their permitted receipts and results after adjudication.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
