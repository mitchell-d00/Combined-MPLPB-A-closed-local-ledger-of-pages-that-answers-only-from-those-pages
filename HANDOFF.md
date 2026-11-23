# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `a2abb278032c0d368d78378bf67bcbc6d8865326` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `72a19b5a79868e39835cd7882c4b406e8b7fc2bb5de071d9c28a82d84128a400`.

## Latest user update instructions

Run it until you fix the pass offs it is a break in logic in chain the unit is a whole strict mode is strict but keeping the rule one owner two should not be a skip it should be preventing boundries of both and none is refuse how it seems is refuse unless one owner

Develop D8 to solve it

Debug as well as test and fix as you find new breaks and errors

## Implemented scope

- Build eight D8 ownership handoff controls and repair missing competing witnesses, independent named record comparisons, and unsupported published-wording routing.

## Validation recorded

- Recorded the failing D8 baseline and passed all eight D8 controls and 85 focused tests on the candidate.

## Limitations and blocked checks

- Explicit multi-record field comparisons cover source-declared fields. Prose relationships still require a rule and witnesses that establish the relationship.

## Next steps

- Replay the frozen D12 and historical 22 against the committed candidate and preserve both outcomes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
