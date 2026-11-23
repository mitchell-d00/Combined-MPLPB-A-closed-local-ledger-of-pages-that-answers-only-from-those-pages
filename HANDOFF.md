# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `a57d3b3fc92f96077503682ae73d04e5a3d4ec73` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b3efd29b707591c44fb8a820b0f9e5cfa8573416494ee8e6fffbf47c6966876d`.

## Latest user update instructions

Merge it to main I hope we made progress what do you think oh and update tool notes etc. and Readme

## Implemented scope

- Explain the user and AI rule-training coordinator, calendar operations, source notes and thesaurus discovery in the README.
- Update the app tool directory, test tool commands and WorkStore seat API notes with their relevant entry points.
- Carry the preceding D12 repairs and coordinator changes through the repository branch checks before merging.
- Synchronize the historical CI gate with the two recorded case transitions while preserving the baseline rows and checking every citation.

## Validation recorded

- Retained D12 work recovered five full and four cited partial answers on the frozen nine and moved the historical 22 from three full and two partial to four full and three partial.
- On the coordinator implementation, the registered repair recovered two development cases and a holdout while preserving two refusals. The full local implementation run completed 1642 tests with two skipped and no failures.
- The initial PR historical gate reported the recorded four full and three partial answers and passed all source guards. It failed only because its expectation still required three full and two partial answers.

## Limitations and blocked checks

- The measured improvements apply to the retained fixtures. Independent historical semantic accuracy and broader lexical transfer remain open.

## Next steps

- Assess further gains with a sealed human-graded historical panel while preserving refusal and conflict controls.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
