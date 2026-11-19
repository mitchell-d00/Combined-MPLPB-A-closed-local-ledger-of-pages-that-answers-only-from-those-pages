# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f85620548874d4daae608144c33c9c1d4286c622` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `aee8d96d8edeaf627afa24af9cda45538a73361a471102df2cbe6ff281a18441`.

## Latest user update instructions

Sorter needs to label things in sorting as possible connections , supported etc and tags that make user aware   , entity resolution, event co-reference, historical truth, and an unofficial free-form question answering. That is not mplpb but a way to explore ideas that are not fact or presented as fact .

## Implemented scope

- Add a derived, replay-verified sorter view with explicit textual/candidate/identity/event/truth tags;preserve saved sorter formats.
- Add a separate free-form question-exploration CLI with optional local-model hypotheses/open questions;no ledger writer or promotion.
- Keep native strict results separate;reuse original-question/profile retrieval boundaries and recheck current sources after inference.
- Document labels,full-context citations,budgets,model limitations and exact commands.
- Retain partial-sorter budget diagnostics even when discovery returns no passages.

## Validation recorded

- Final runtimef85620548874d4daae608144c33c9c1d4286c622:1379 extracted unittest tests passed in527.963s;52/52 public controls passed with zero observed false-supported bridges in those fictional controls.
- 15 new tests cover identical nodes/labels across modes,exact UTF-8/CRLF spans,quoted identifiers,provisional retirement,empty-budget diagnostics,native isolation,false citations/quotes,promotion rejection,restrictions,source withdrawal,backend failure and CLI.
- Fixture demo:111 identical nodes and node labels;196 observation edges vs218 compare edges;22 extra proposals remain non-authoritative.Source hashes unchanged.
- One unchanged H05 original-record replay retains identical native contract before/during/after exploration:4 citations4070 characters;zero exploration strict slots.No22-question rerun or historical gain claim.
- Final installed wheel/new CLI and existing workspace passed with isolated Python.Native JS/crawler/API and actual pinned WebAssembly checks passed.Chromium passed on byte-identical native HTML;new UI is CLI/Python only.
- One cached local Qwen0.5B smoke returned a schema-valid open question that mostly repeats the original query.No useful semantic gain established;all exploration support/identity/truth flags false.Server stopped.
- Initial2 loopback fixture errors,empty-budget regression,ENOSPC full-run310 errors and repaired extraction failure preserved.Recovered run passed after cleanup of generated temporary archive copies only.
- Preservation audit:5875 pre-existing evaluation files and62 existing runtime files unchanged.Original sorters,native reader,kernel,router and narrator unchanged.

## Limitations and blocked checks

- Verified entity resolution,event co-reference and historical truth are not implemented by these labels;they remain explicitly unresolved/unverified.
- Model-generated hypotheses and missing-evidence notes can be wrong.Semantic correctness is not established by schema/citation checks.
- The tiny live model mostly echoed a question;no independent quality evaluation or answer-coverage gain is demonstrated.
- Interface is opt-in CLI/Python;no new browser UI or deployed-site claim.Offline sorting grants no serving profile or import approval.
- All prior historical limitations and null independent accuracy/human review metrics remain.Nothing pushed or merged.

## Next steps

- Read docs/SORTER_EXPLORATION.md and evaluation/sorter-exploration/2026-11-19/FINAL_REPORT.md before extending the interface.
- Keep labels visible alongside every excerpt/hypothesis;show native source support separately from historical truth.
- If adding a browser surface,retain original full-question/profile gates,source rechecks,budgets and non-promotion.
- Evaluate interpretation usefulness on frozen source-linked cases before claiming semantic improvement;human-independent historical accuracy remains unmeasured.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
