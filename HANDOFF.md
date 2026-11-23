# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `323492daf7b659c7718948e8b322f76d4c6a9247` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `cfab050bcecf2ab903bcf37b50bcc4dbe8f357f59298cfc782fbeec113dc9886`.

## Latest user update instructions

Improve supported language coverage: Concentrate on coreference, complex relationships, multi-document synthesis, and natural variations in question wording, without weakening proof requirements.
Produce a reproducible release demonstration: Provide one-command installation, a pinned evaluation dataset, baseline comparisons, performance numbers, and a concise limitations report.

## Implemented scope

- Verify one parcel delivery relationship across a catalog, dispatch, and receipt, including receipt-local pronouns and several ways to ask.
- Freeze a 40-case synthetic comparison and provide an offline command that installs and scores two archived native wheels.

## Validation recorded

- The pre-change focused run had four failures. The changed reader passed all six focused checks including mid-verification retirement and a tight citation budget.
- The checkout replay matched all 40 labels with 70 exact citation readbacks.

## Limitations and blocked checks

- The improvement applies to explicitly linked statements in a bounded packet. General historical language transfer and independent semantic accuracy remain unmeasured.

## Next steps

- Replay and retain exact installed-wheel comparison results.
- Evaluate transfer using independently authored prose packets and graded citation obligations.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
