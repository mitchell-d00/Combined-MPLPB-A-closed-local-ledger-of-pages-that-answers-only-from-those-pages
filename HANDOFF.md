# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `273e5ba693142341eefc7a341b87f107544a7978` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `e141adf877bd71529149597ce62adaeda6fdab4d4375e826fa4e2cd433204153`.

## Latest user update instructions

Run the tests as you patch one pattern and it passes move to next expand the 9 I like your plan and it will work well with a run of error patterns / fix sprints

## Implemented scope

- Freeze the original nine coordinator questions, excerpt locators and strict results.
- Add bounded strict-reader coverage for recorded stage and open outcome, labeled item rows, permission qualifications, and explicit versus unsettled cause.
- Rerun the unchanged nine between sprints and retain 28 expanded positive and negative controls and their prepatch failures.

## Validation recorded

- Each sprint passed its new matched controls before the next. The final nine ended at five full answers and four cited partial answers, up from nine abstentions.
- All 28 matched controls and the two extra source-state and quoted-context checks passed. The focused deterministic regression run passed 102 tests.
- Three newly acquired National Archives transcript excerpts remained abstentions on both revisions. The separate passage probe located all three excerpts.

## Limitations and blocked checks

- New rules operate on small, complete source packets with explicitly supported source forms. The exploratory archival results show their present coverage limit.
- The direct source comparisons use supplied excerpts and authored controls. Independent historical truth review and the proposed human pilot remain pending.

## Next steps

- Use a sealed reviewer-graded historical corpus to test extraction of qualified clauses out of broader prose while preserving ambiguity and contradiction checks.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
