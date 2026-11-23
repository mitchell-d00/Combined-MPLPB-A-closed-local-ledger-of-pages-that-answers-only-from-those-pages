# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ee3f039ce4913e832937339101152f55447ffd76` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `8a16bd5561023272e5fdd60393e11f2611f3b78ee82a049b668aada9d83ad772`.

## Latest user update instructions

Do it test it run sprints on both features until they are concrete

If we build a thesaurus graph that goes with synonym graph that may help,as well we could use open source thesaurus to build it and a open source synonym reference and test relies and relations as we go

## Implemented scope

- Add explicitly selected Gregorian D6 day-count, month-shift, and same-role relative-date operations with exact source citations.
- Add revisioned source notes and live WorkStore discovery under the existing capability, task, visibility and source gates.
- Build a separate sense-aware SQLite graph using Princeton WordNet and Moby as an independent association reference. Keep the reviewed synonym graph and strict reader paths unchanged.
- Retain the earlier lexical ranking misses, the subsequent exact edge-span search, and a reproducible example.

## Validation recorded

- All 48 calendar controls passed. The six-year sprint includes Gregorian century boundaries and wrong-role anchoring.
- At a one-passage budget the 12 independently authored notes located all 12 intended excerpts, versus zero in the ordinary probe. The strict contracts for the twelve exploratory cases and one positive exact-field control remained identical.
- The full WordNet and Moby import succeeded. All six selected lexical edge choices matched, ordinary discovery found zero, expanded-query discovery found two, and exact edge-span discovery found all six without changing any strict contract.
- Focused regressions cover stale sources, withdrawn notes, wrong offsets, rights and visibility, exact date operands, and distinct lexical senses and edge directions.
- On four frozen historical questions the lexical variants recovered no additional complete drafted anchor. All original 22 native contracts matched the preceding revision except code fingerprints.

## Limitations and blocked checks

- Calendar arithmetic assumes the declared proleptic Gregorian convention and verifies supplied date roles. It does not establish historical calendar conventions.
- The note and lexical discovery runs use authored passages and deliberate distractors. Independently reviewed historical transfer has not been measured.

## Next steps

- Exercise reviewer notes and lexical discovery on fresh source packets before using either to select a proposed documentary rule change.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
