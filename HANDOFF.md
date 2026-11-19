# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5c0ce0a3f96396e67147dff383015843b9e9b06a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `776573c237a7f308f8100971c5d31a8c8730c7b46654ea77010c4cdd95aeb2e6`.

## Latest user update instructions

With about 440 failures, you can see patterns instead of individual cases, and class fixes become obvious.
D% records every dice roll, so you can cluster the failures by which structural feature was rolled: passive voice, a stated cause, quoted speech, negation, partial correction, and so on. That gives you each feature’s failure rate. Fix the class with the most failures and rerun the frozen set. Repeat until it’s fixed

## Implemented scope

- Preserve frozen baseline20/600 complete,640/640 refusals;580 incomplete answerable cases,including37 partials.
- Persist mandatory general-class/no benchmark-rigging rules in AGENTS.md.
- Reconstruct and verify exact sealed roll trace and packets;group failures by family and structural choices,not actor names.
- Implement correspondence boundaries,source-scoped request grammar,Unicode/passive actions and exact explicit-cause closure in existing independent kernel.

## Validation recorded

- 53 focused class/cohort and native documentary/admission tests passed,exit0.
- New general class tests fail before implementation;before log and intermediate invalid-budget/mistyped-module errors retained.
- All1240 baseline rolls and packets replay identically;generator/worker/tests/key remain unchanged.
- Paired historical baseline is running using archived pre-fix native packages;updated D%/originals and full archived regressions pending.

## Limitations and blocked checks

- This is developer-authored development,not independently judged historical accuracy.
- Scoring key remains outside Git and outside runtime;feature analyzer is custodian-only.
- No historical identity,quoted-speech execution,missing chain,partial-correction or model interpretation is promoted.
- Native rule candidate is not yet full-regression certified or merged.

## Next steps

- Freeze committed class-rule candidate;run updated1240 cases on identical packets with same unchanged key.
- Run exact archived full suite and52 public controls;retain all regression failures before repairing.
- Run paired unchanged22-question original-source direct arm and report losses as well as gains.
- Use descriptive feature failures to choose any next general fix;never change frozen questions or labels.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
