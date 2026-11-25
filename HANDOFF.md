# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d0cbb7438df887a6ff3aa95f3800737fa6af3444` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `ce702913b3712a77f812f4fe554aee4f3e1faf3e83807cb744f0207d67f01c77`.

## Betty report for Al

Al first inspects the repository, then reads this report and the relevant PR. The maintainer relays Al’s response and direction to Betty, who updates the PR.

### Latest user update instructions

It needs to be easy to find make it part of api Betty command and al command

Push and merge make sure it is explicit that a Betty report is left to inform Al once Al reads repo

Every push has a Betty report

And API tells an Al to read repo first deeply then the Betty report and that is Betty calling Al and Al calling Betty then user pasts Al report to Betty and she updates the pr

### Implemented scope

- Expose Betty and Al through the agent manifest, browser JavaScript API and terminal bridge.
- Leave a Betty report for Al in the generated handoff on every push and in the relevant PR.
- Describe the ordered repository review and the maintainer relay. Catalog the seven tested ZIPs by source commit, SHA-256 and recovery command.

### Validation recorded

- The desktop HTTP role endpoint, JavaScript contract, terminal modes with a manifest fixture, UI script, browser transport and infrastructure checks passed locally.

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
