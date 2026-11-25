# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `568094fdeaca8352d555866c4a468fcda86db3b7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `dee57c653eae696afd677824ad079b7cba0622fcb08fab920f59e88535e6f6a1`.

## Betty report for Al

Start Betty first, then open Al in a separate chat. Al inspects the repository before reading this report and the PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates the same PR.

### Latest user update instructions

It needs to be easy to find make it part of api Betty command and al command

Push and merge make sure it is explicit that a Betty report is left to inform Al once Al reads repo

Every push has a Betty report

And API tells an Al to read repo first deeply then the Betty report and that is Betty calling Al and Al calling Betty then user pasts Al report to Betty and she updates the pr

And Al reads pr then I copy past the Al response and Betty tests and updates it starts by setting a Betty then then in a separate chat an Al

### Implemented scope

- Expose Betty and Al through the agent manifest, browser JavaScript API and terminal bridge.
- Leave a Betty report for Al in the generated handoff on every push and in the relevant PR.
- Describe the ordered repository review and the maintainer relay. Catalog the seven tested ZIPs by source commit, SHA-256 and recovery command.
- Set Betty first, then open Al in a separate chat. Al inspects the repository and reads the PR. After the maintainer relays Al’s response, Betty tests and updates the same PR.

### Validation recorded

- The desktop HTTP role endpoint, JavaScript contract, terminal modes with a manifest fixture, UI script, browser transport and infrastructure checks passed locally.
- A real Chromium session exercised both role commands from the standalone candidate. Both terminal commands fetched their pinned public GitHub manifest after the first push. The updated JavaScript contract passed with an explicit Betty-first relay order.

### Limitations and blocked checks

- Both role commands return public coordination metadata. The maintainer relays between sessions and supplies direction.
- GitHub source snapshots and the exact ZIP rebuild recipe are available. The exact Pole ZIPs have no uploaded release assets.

### Next steps

- After opening the repository, Al follows the inspection directions and then reads this Betty report and the relevant PR.
- Betty records the shareable response and maintainer direction in the PR. The Pole evidence index currently points to PR #97.
- Verify the exact source archive gates, then verify the role commands from the default branch and deployed Pages manifest.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
