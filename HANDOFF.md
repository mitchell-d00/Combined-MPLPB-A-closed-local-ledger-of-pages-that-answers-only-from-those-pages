# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3d694aafba1c81c0961c51f542d9cda9ff88de9f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `26dae512543f9fbb284651b03961962b6eb374e081019ea68e92a03ca1ab4457`.

## Latest user update instructions

With about 440 failures, you can see patterns instead of individual cases, and class fixes become obvious.
D% records every dice roll, so you can cluster the failures by which structural feature was rolled: passive voice, a stated cause, quoted speech, negation, partial correction, and so on. That gives you each feature’s failure rate. Fix the class with the most failures and rerun the frozen set. Repeat until it’s fixed

## Implemented scope

- Preserve frozen baseline20/600 complete,640/640 refusals;580 incomplete answerable cases,including37 partials.
- Persist mandatory general-class/no benchmark-rigging rules in AGENTS.md.
- Reconstruct and verify exact sealed roll trace and packets;group failures by family and structural choices,not actor names.
- Implement correspondence boundaries,source-scoped request grammar,Unicode/passive actions and exact explicit-cause closure in existing independent kernel.
- Iteration2:repair absolute source offsets,cover irregular passive counterevidence,and add literal-text location as a separate textual-only proof class.

## Validation recorded

- Iteration1:160/600 checked complete,E26.67%;640/640 expected refusals,F0%;440 incomplete answerable cases. All1240 executions completed.
- Iteration1 archived full suite:1408 tests,one failure,exit1;52 public controls passed. Two historical partials regressed to abstention. Candidate rejected as final;all outputs retained.
- New independent-vocabulary tests reveal named-attribution erasure and conflicting passive evidence in old main;written denial/hedge variants also require action-form handling.
- Iteration2 focused suite64 tests passed,exit0,including original appointment control,long-document coordinates,literal-only proof and forged-proposal refusal.
- Generator0b2c5c8,worker and official private key unchanged throughout;all original sources/questions/seals remain untouched.

## Limitations and blocked checks

- No independent semantic review or historical truth established.
- Literal location proves words only;do not count it as reconstructed historical relationships.
- Iteration2 full regression,D% and22-source replay pending;no final acceptance or merge claimed.

## Next steps

- Freeze iteration2,rerun same1240 packets and complete native regressions from extracted source.
- Rerun unchanged22-question direct arm;verify both checked partials are restored and complete answers do not regress.
- Compare roll cohorts and disclose remaining incomplete classes and any false support.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
