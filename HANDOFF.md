# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `fe56551c752bd8df3f1728ac8b11e0cb256c5cdc` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `685f5460ee1f9829e5fb55a390900a79e2a9c4f49c508252d2d85c9c27604413`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Apply Al notes 0008 and 0009 to the newcomer evidence route. Keep the original onboarding protocol, and merge the separate documentation PR when verified.

### Implemented scope

- Read note 0008 at 97027f3f504de6e85f9e0d3e77af4fe504057ca7 and note 0009 at 5082c5d975ca41a2478ccb25576f3cfdf65b77f0. Separate documentation branch from verified Ares main.

### Validation recorded

- Chromium walked the supported demo to its exact source, refused a missing datum, then imported and reviewed synthetic pasted text and checked its citation and refusal. Managed Chromium HTTPS certificate setup failed first. The HTTPS-fetched bytes matched Ares Pages and passed from loopback.
- Reconciled PR #106, #112, #126 and #127 status and kept the incident open. F05 remains a pinned Round 4 miss with no later exact-case result verified. Bastet results stay separate.

### Limitations and blocked checks

- Software walkthrough only. Original twelve-person human onboarding remains NOT_RUN. Hestia and production dispatch are outside scope.

### Next steps

- Verify candidate files and exact-head checks. Merge the documentation-only update and verify publication. Use a separately versioned future newcomer study.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
