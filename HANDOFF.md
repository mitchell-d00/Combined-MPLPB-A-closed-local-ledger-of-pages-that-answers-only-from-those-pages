# Repository handoff

Last reviewed: 2026-11-21.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `7afa6af987c6973639935ac06e3c16f669e1fc88` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `6e8f39a1dbc5d7589e80d3dbe14a5b039f062c395c57547e42bfdda04bf54bd2`.

## Latest user update instructions

Fix the bugs you founds test for more bugs fix them as a pattern if possible then push to main and merge

Make a small generator than generates seeds to cause an ai to search and copy random real world Ope source data to test vs each time a new set of random world data

Let’s seprate test harness from MPLPB tools in two files test tools and mplpb tools

## Implemented scope

- Validate selector types and require explicit field and record selectors to agree with canonical and normalized field questions.
- Reject competing record and exact-value routes and report invalid requests cleanly from the CLI.
- Provide a seeded open-data collection prompt in the test tools package and two focused guides for testing and MPLPB application workflows.

## Validation recorded

- Independently worded regressions reproduced selector overrides, silently discarded exact-value selectors and inconsistent input errors.
- 86 focused tests passed, including selector, source-policy, passage-budget and seed controls.
- The frozen field-question generator reproduced 900 supported positives and 200 expected refusals with equal before and after counts and sample outcomes. All 52 public evidence cases passed.
- A live draw retrieved Wikidata entity Q53451 and USGS event us7000dk88 from the generated official catalog URLs.

## Limitations and blocked checks

- The generator emits a collection plan and evaluation instructions. It leaves acquisition, license confirmation and answer-key review to the collector and custodian.
- A seed replays the draw plan. Reproduction of live data also needs retained response bytes and revision information.
- Arbitrary natural-language requests are still subject to the bounded proof grammar.

## Next steps

- Run the archive-first and PR checks for the submitted commit, then verify the deployed browser after merging.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
