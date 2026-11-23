# Repository handoff

Last reviewed: 2026-11-23.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `06041b83a4b00a7c69230e4c31b7d6254b0627f6` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `0703af0a67cc1a403e46ca1a3369e454098c8bf788245e0efb84bb5f2eb4bf04`.

## Latest user update instructions

It needs a sub coordinator that can tag if we automate the repos processes into mplpb to detect errors and a coordinator to set and test rules a user could train like me

And run sprints on it as well testing vs 22 and any other benches Iv not tested in a while search repo

I’ll build this around WorkStore’s existing roles. The sub-coordinator will tag repeatable failures with evidence. The coordinator will turn those findings into a rule-testing sprint that a user can run and review. Let ai drive this too from the api

Self healing , evolving , fails gracefully then repairs all automated for user

## Implemented scope

- Add a sub-coordinator that tags repeated development misses with evidence and a coordinator that tests one named, user-authored D6 rule against frozen inputs.
- Expose replay, grading, filing and an automatic known-pattern sprint through the existing capability-gated WorkStore seat API.
- Retain selected, blocked and healthy sprint examples. Replay the original 22, frozen D20 seed 20 and a new Primary Book packet through fixed test tooling.

## Validation recorded

- The automatic elapsed-day fix recovered two development cases and one holdout while preserving both refusal controls. The wrong objective was blocked and the healthy rerun made no change.
- The 42 focused tests covered different roles, hidden grading labels, stale or altered artifacts, wrong counting rules, unchanged native evidence contracts, and same-baseline filing.
- The original 22 retained all native contracts. D20 recorded 2 supported, 15 withheld and 3 alias misses. All six Primary Book controls passed.

## Limitations and blocked checks

- Automatic repair covers the explicit year-count to Gregorian elapsed or inclusive day-count transformation. Unknown or failing repairs remain review-needed.
- WorkStore training receipts convey diagnostic history and carry no source-support or execution authority. The workflow does not install rules into the native engine or publish repository changes.

## Next steps

- Use fresh custodian-held evidence packets to validate another repeated rule failure before registering a second repair family.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
