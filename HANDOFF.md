# Repository handoff

Last reviewed: 2026-11-18.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `7c92db5caa39e90fca01fd8e3be5c8c8a2a11c4a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `42f7c4b9cfa110fcdad7bbe7009b77f67aa0cc5cb6d729fe8ca0a38b6b777ff9`.

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

- Baseline bbf6690:1267 extracted unittest tests passed;52 public controls passed;22 unchanged questions:2 complete,1 partial,3 conflict,16 abstain;27/32 draft anchors.
- Final tested runtime7c92db5caa39e90fca01fd8e3be5c8c8a2a11c4a:1364 extracted unittest passed in398.110s;52/52 public controls passed with zero observed false-supported bridges in those fictional controls.
- First freeze f030570:1362 full pytest passed in457.26s. Final changed router/discovery pytest:23 passed in0.69s;final full unittest includes both new tests.
- Final22 native workers completed exit0:2 complete,2 partial,3 conflict,15 abstain. U06 checked partial added without resolving the area. H05 exact4 citations4070 characters unchanged.
- Final22 separate isolated exploration workers completed exit0;combined draft anchors remain27/32;5 anchors not recovered. No expected keys mounted;zero strict slots consumed.
- Fresh no-history AI session assessed22 frozen outputs:2 complete_correct,2 partial_correct,5 appropriate_refusal,13 over_refusal.54 exact citations/coordinates and packet seal checked. Final native packet cases byte-identical. AI assessment only.
- Optional live Qwen0.5B:initial6 schema rejections retained;constrained frozen rerun6 valid abstentions,0 useful flags,0 unexpected flags,4 developer-expected flags missed. No semantic utility gain;temporary server stopped.
- All6 process-termination publication checkpoints passed. Local POSIX old/new generation pointer safety only,not physical power-loss certification.
- Final archive JS/crawler/API/actual WebAssembly/collection policy/Chromium candidate journey and isolated installed wheel checks passed. Deployed live site NOT RUN.
- Audit:5614 pre-existing tracked evaluation files and legacy sorter v1 unchanged. Prior reports and failed attempts retained in new versioned family.

## Limitations and blocked checks

- Complete answers remain2/22;5/32 draft anchors still unsurfaced.13 over-refusals identified by AI assessment,not independent human measurement.
- Unfamiliar event identity,chronology,causation and correction accuracy remain unproven;historical precision/recall and human intervention time null.
- Flag-only local model implementation is complete but the tested0.5B model demonstrated no utility on6 fictional pairs.
- Generation publishing is optional local POSIX process-interruption safety;pin a resolved generation for concurrent multi-read work. Old copied ledgers have no global revocation registry.
- Repeated native source reads remain high;updated native22 CPU268.751s,wall278.334s,9658683974 logical HTML bytes. No speed gain claimed.
- No independent human review or>=200 unseen question evaluation;no production or9/10 claim.
- Local branch only.Nothing pushed or merged.

## Next steps

- Read evaluation/fixpack/2026-11-18/FINAL_REPORT.md,CASE_ANALYSIS.md and AI_ASSESSMENT.json before adding proof rules.
- Target independently checked documentary quotation scope and full contrary-evidence scan for H08;preserve conditional/quoted negatives and original budgets.
- Recover5 full draft anchors through bounded context expansion/source-aware ranking;keep discovery outside strict proof slots.
- Use source-linked AI missed-answer evidence to design general grammar and composition rules,then replay unchanged questions.
- Keep semantic sidecar optional until a frozen model/probe experiment demonstrates utility without false flags;human-independent historical accuracy remains unmeasured.
- Retain process-fault controls and evaluate read pinning/power-loss durability separately;do not overstate optional publisher guarantees.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
