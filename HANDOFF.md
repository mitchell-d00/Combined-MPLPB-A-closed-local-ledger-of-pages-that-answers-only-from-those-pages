# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ec41332dbcfce5d6dfd5b9f5e75dd553507bbea2` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b46cca3931794d2fb2d76a8c3f794301111d818830f14bff9899c95b0b82ff52`.

## Latest user update instructions

Do the parts we don’t need other humans for I’m solo and have no access to other people

## Implemented scope

- Cache immutable exact-content record parsing in eight bounded entries while rereading sources and retaining fresh policy/eligibility/hash checks.
- Link documentary question obligations to their actually displayed checked evidence; add readable reconstruction CLI and browser question-part view with canonical coordinates.
- Add native host-only bounded local storage byte inspection/recheck to existing receipt operation, without asserting delivery, human reading, completion or historical truth.
- Rerun unchanged original-record development questions with existing frozen seals and isolated workers, record CPU/wall/RSS/read costs and preserve all old results.

## Validation recorded

- Baselineec41332:74 focused source/reconstruction/provenance tests passed6.530s.
- Development88 focused tests passed5.809s and UI script check passed. Initial new test expectations for capitalization/retrieval-versus-display budget were corrected; no support rule changed.
- Final committed source ZIP validation and original-record before/after runs pending.

## Limitations and blocked checks

- Independent human semantic evaluation remains unavailable and is not required to use these software improvements; it will stay NOT RUN rather than blocking implementation.
- No new historical-answer proof rules or automatic event/identity resolution; full historical truth and authentic external delivery remain unverified.
- Local storage inspection proves byte equality at inspection time under a trusted host/OS, not durable storage, delivery, human reading or task completion.

## Next steps

- Freeze implementation and run extracted regression/public/JavaScript/WebAssembly/Chromium controls.
- Complete unchanged original-record before/after experiment, retain failures and report actual costs without independent accuracy claims.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
