# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0526e026f77a888dd9db88750c477ea64a71d3c7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5dc4c9e0ab023285816b96643c644426bc0b422b1adff8804bcdf55fdb2bea50`.

## Latest user update instructions

Build a blind test that randomly builds blinds from live web and run it vs that call it Dice Bag

## Implemented scope

- Add Dice Bag live USGS acquisition, independently committed operator/custodian inputs, offline native execution, synonym lookup, and separate scoring.
- Index Dice Bag and retain the first live run's source references, result counts, and content hashes.

## Validation recorded

- Twelve live draws filled and yielded 72 questions. Independent readback verified the response hashes and all 12 selected records' source pointers.
- Two offline native outputs were byte-identical. The baseline answered 12 direct questions and withheld all 36 negative controls. The index found all 12 listed-phrase natural pairs and none of the 12 unlisted ones. The strict reader verified all 12 listed natural cases after revealed confirmation.
- Seven focused Dice Bag, synonym indexing, and persona transfer tests passed.

## Limitations and blocked checks

- The first study uses one structured source catalog and authored wording families. Listed phrases and the index share a lexicon, with unlisted forms as controls.
- The operator and scorer use separate paths and commands, but this local run did not place the custodian on a separate security principal. The confirmed proof arm is a post-reveal diagnostic.
- The default reader is unchanged. The capture files and scoring key stay in the separate workspace custody directory.

## Next steps

- Repeat against separately authored question wording and a second open catalog. Keep an independent custodian and report per-arm misses, ambiguity, and scope controls.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
