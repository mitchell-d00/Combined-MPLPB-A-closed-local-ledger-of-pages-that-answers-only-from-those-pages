# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `b6cca259aeef3f42397ded027b9bf9c28a44e23d` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f9850fbf9d4f1aa4388130a1cb7d18f57f7045d8746d93a4ccee5a90b9d8c15e`.

## Betty report for Al

Start Betty first, then open Al in a separate chat. Both inspect the repository before reading the last Betty report on the live PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

It needs to be easy to find make it part of api Betty command and al command

Push and merge make sure it is explicit that a Betty report is left to inform Al once Al reads repo

Every push has a Betty report

And API tells an Al to read repo first deeply then the Betty report and that is Betty calling Al and Al calling Betty then user pasts Al report to Betty and she updates the pr

And Al reads pr then I copy past the Al response and Betty tests and updates it starts by setting a Betty then then in a separate chat an Al

And Betty report is last state she applied live in live Pr so it’s always up to date and starts from that state

Al reads repo then Betty then advises and the loop starts

Betty tests reports results Al reads judges and advises next prompt

No both at start need to read full repo then Betty report from last Betty that would be current state at start then loop Betty tests reports Al reads pr  advise and Mitchell pasts that to Betty repeat with no stop stop is just stoping loop starts just from last state Betty report

Advice for Betty
Start from the last Betty report on the live PR (currently #97, pin 7618be370c334b082cb91c50eaf665f979ce5c1e).
Read the full repo, then the latest Betty report on that PR. That report is the current applied state.
When the maintainer pastes Al’s response and the direction, freeze only the named cases and controls, run the authorized test, and update the same PR with before/after counts, the rule or explicit withhold, zero false-supported bridges, new commit hash and archive SHA-256, and all NOT_RUN labels preserved.
Every push must leave a Betty report in HANDOFF.md so the next session (Al or Betty) can resume from the last applied state without extra context.
The loop is: Betty reports → Al judges and proposes → Mitchell pastes direction → Betty runs and updates the PR → repeat. Stopping is just stopping. The next start is always the last Betty report on the live PR.

### Implemented scope

- Expose Betty and Al through the agent manifest, browser JavaScript API and terminal bridge.
- Leave a Betty report for Al in the generated handoff on every push and in the relevant PR.
- Describe the ordered repository review and the maintainer relay. Catalog the seven tested ZIPs by source commit, SHA-256 and recovery command.
- Set Betty first, then open Al in a separate chat. Al inspects the repository and reads the PR. After the maintainer relays Al’s response, Betty tests and updates the same PR.
- Return live PR state and a head-pinned handoff when either terminal role command is given a PR URL. Betty updates the applied-state report in place. Al judges the recorded test results and drafts the next prompt.
- Both roles first read the full repository, then the last Betty report on the live PR to recover the applied state. The relay repeats. Pausing leaves the last report as the next starting point.
- Advertise the required Pole before/after, proof/withhold, false-support, archive pin and NOT_RUN fields in both commands.

### Validation recorded

- The desktop HTTP role endpoint, JavaScript contract, terminal modes with a manifest fixture, UI script, browser transport and infrastructure checks passed locally.
- A real Chromium session exercised both role commands from the standalone candidate. Both terminal commands fetched their pinned public GitHub manifest after the first push. The updated JavaScript contract passed with an explicit Betty-first relay order.
- Live PR endpoint access passed. Terminal fixtures checked both a current report and a stale report whose recovery link points to the actual PR head.

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
