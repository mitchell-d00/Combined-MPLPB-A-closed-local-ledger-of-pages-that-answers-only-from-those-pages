# Repository handoff

Last reviewed: 2026-11-21.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6ba371ca07dd9269f28af762ed1971ad484fb6b5` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b18f47467f6933657ddc8543a6d66751eee8c61d1ca75697f60b505adab0a840`.

## Latest user update instructions

Put this in B Test and MPLPB under comparative tests test it first read it is it good etc then do repo

## Implemented scope

- Archive the supplied Executable Gates ZIP, Markdown, PDF, original probes and raw results under comparative tests.
- Add byte checksums, independent local replay receipts, a verifier and a review of the claimed fixture scope.
- Index the comparison in the MPLPB test and result guides and mirror the package in B-Tests.

## Validation recorded

- Replayed the seven paired MPLPB probes twice at 6ba371c using Python 3.12.14. All recorded probe fields matched the author's Python 3.13.18 results.
- Replayed the note-only and pre-receive Git fixtures using Git 2.56.1. Push results, server head changes and file contents matched the paper.
- Ran the packaged verifier successfully from both checkouts. All 48 focused MPLPB specialist-continuity tests and 130 B-Tests unit tests passed.
- The MPLPB documentation and infrastructure audits passed.

## Limitations and blocked checks

- The published comparison covers one fixture adapter, a single-page corpus, and disposable local Git repositories.
- P1 through P5 hold the seat grant fixed while computed permission changes. The archived author copy is preserved and the reproduction note records the distinction.
- Complete mediation, hosted branch rules and native OOCC behavior are outside this replay.

## Next steps

- Run the release gates for the MPLPB comparison package when submitting it for merge.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
