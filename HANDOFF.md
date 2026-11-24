# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `e3990bf98ac6fb2e3b991a2eb251347ca571e873` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `6a7cfb22d5e817b14fe15cb9dc9f0ee62f4d9a5144cc911c1964b55bfe22c133`.

## Latest user update instructions

Check the hiccups like time out and loose SQLite etc

## Implemented scope

- Close SQLite connections opened by four experience graph regression tests while preserving their transaction behavior.

## Validation recorded

- Reproduced all four unclosed database warnings under Python 3.13 and traced them to experience graph test fixtures.
- All 72 focused offline tests passed under Python 3.13 with ResourceWarning enabled. The log contained zero unclosed database warnings.
- The companion B-Tests run completed locally with 148 passes under a 45-second deadline.

## Limitations and blocked checks

- The external B-Tests transcript ends mid-test and contains neither a timeout report nor an exit status.
- Local source-archive checks are focused. Full source archive extraction exceeds local storage.

## Next steps

- Retain the external test process exit status and full output together on a future rerun.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
