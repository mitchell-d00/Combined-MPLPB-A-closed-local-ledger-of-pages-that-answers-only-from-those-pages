# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3b1e517b1f48ae62aba4de0885ac0a6ead7f4948` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `30e42ce41a9de2c1736682e31426dd0ab2c3cc656c201c41a10fa341b0aab8bb`.

## Latest user update instructions

We need a rule constructer that builds as candidate for strict , how is the samantic logics set up ?
If it can apply strict organizational rules to raw data and sort by supported complete answers it should be able to  build rules for a corpus as it reads the raw data and only approved mplpb though once human approves but applies same rules to new data so it can ansewer as to available data
No human approves the ansewered and it’s path into MPLPB so if they upload a new data dump it sorts it and builds the database and rules and presents in strict as supported by available data but not approved like a MPLPB single page full artifact
We can call it spot

## Implemented scope

- Add D6 candidate construction, separate documentary recommendation proof drafts, and development-only field rule discovery.
- Add Spot to build an isolated ledger from labelled UTF-8 records and rank scoped rules by complete native evidence results. Label the report as an unapproved preview.

## Validation recorded

- Passed 78 focused native tests and the documentation audit.
- An elapsed-days candidate recovered two development cases and one holdout and preserved both refusal controls.
- Spot verified a closing date with an exact citation and withheld on a missing field and competing owners. A CLI Strict Ask against the new preview ledger also returned the cited closing date.

## Limitations and blocked checks

- Spot accepts explicit fields in labelled text. The prose draft records proof requirements for review, pending a native recommendation verifier.
- Spot creates a separate preview. Admitting an answer and its path to a main collection is outside the preview workflow.
- The full source archive requires about 2.1 GB uncompressed, exceeding available local space. The local archive check is scoped to the relevant source and tests.

## Next steps

- Develop and replay native recommendation comparison proof on independently worded positive and refusal cases.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
