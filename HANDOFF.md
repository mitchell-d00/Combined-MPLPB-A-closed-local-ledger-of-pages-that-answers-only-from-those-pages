# Repository handoff

Last reviewed: 2026-11-18.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f030570aefd272a2fc0388d6f80b44232f0c8304` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `424c8796d00f46d7ab4dac63351e28cb1595e0383286efc4d17393e51e832801`.

## Latest user update instructions

Answer coverage: make a case-by-case table of what each question requires, what the sources establish, and where the checker stops. Add general, independently checked prose rules for the answerable parts. Unsupported parts must remain unresolved; 22/22 supported answers is not a valid target if some questions demand invented conclusions.
* Missed spans: give exploration a separate bounded retrieval budget, search question parts independently, and retain counterevidence. Keep that material out of strict proof slots so H05 does not regress again.
* Historical relationships: verify one explicit connection at a time, preserving attribution, date roles, conditions and negation. Stop at missing links. Similar wording can propose identity, but cannot establish it.
* Unknown accuracy: freeze outputs and create source-linked scoring packets. A fresh, blinded AI session can provide an AI assessment with cited reasons. Human-independent accuracy remains unmeasured until actual independent review occurs.
* Semantic tripwire: implement it as an optional flag-only sidecar, then measure useful flags, false flags, missed links and runtime. It gets no ledger write or promotion capability.
* Crash safety: use immutable staged ledger generations with an atomic publication pointer, or a durable transaction/recovery mechanism. Test process termination at every publication step. Ordinary rollback alone cannot establish crash safety.

## Implemented scope

- Implement and harden supplied five-part fixpack without pushing.
- Separate bounded discovery and conservative independently checked local-context partial evidence.
- Add optional strict-schema flag-only sidecar and process-interruption-tested POSIX generation publication.
- Freeze code, rerun unchanged22 questions, retain all failures and prepare blinded AI assessment.
- Repair reproduced exploration starvation by round-robin source traversal and existing wrapped-line context units.

## Validation recorded

- Baseline bbf6690:1267 extracted unittest tests passed;52 public controls passed.
- Baseline unchanged22:2 complete,1 partial,3 conflict,16 abstain;27/32 draft anchors.
- Focused new module tests passed; final archive full regression pending.
- Live Qwen0.5B pilot:6 rejected schemas; constrained rerun6 valid decisions,all abstentions,4 developer-expected flags missing. No demonstrated utility gain.
- New long-first-source and wrapped-context regressions failed before repair;32 router/discovery tests passed after repair. First frozen replay retained; final repair replay pending.

## Limitations and blocked checks

- Independent human semantic validation and unseen evaluation NOT RUN.
- No complete-answer gain established. New local context must remain partial when referent unresolved.
- Generation publishing is optional local POSIX process-interruption safety, not power-loss certification or global revocation of copied ledgers.
- Local branch only; do not push.

## Next steps

- Run frozen extracted full regression/public controls,unchanged22 direct replay and separate22 discovery.
- Retain comparison case table and fresh blinded AI assessment without answer keys or change log.
- Record final costs,negative results,remaining failures;update handoff and commit evidence.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
