# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `9f7ef1a9212152093ebeebacec68f7872cd3b4bf` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `2d4f8f71977c3fdc023072d7385cc1b033693623dbf9ab40d78d601e0c699417`.

## Latest user update instructions

Ok push everything and make it so the next Ai understand what outside agent let’s call it Al and inside ie the agent like you and it’s called Betty

And how to make ai take role ie if I tell a new ai it’s Betty it becomes repo archive editor and Al becomes strategist advisor

With just a link to my repo

Ie link you are al 2nd agent link you are Betty

And once it is set Betty and Al Betty makes reports to Al in pr and I past Al / my responses

## Implemented scope

- Define Al as the outside strategist and Betty as the inside repository and archive editor. Put both starters in the TeamBuilding guide and link them from the root README and AGENTS.md.
- Have Betty post the report to Al in each PR. Record the maintainer’s relay of Al’s response and their own direction back to Betty.

## Validation recorded

- The documentation inventory, repository infrastructure, generated handoff, and staged diff are checked locally.

## Limitations and blocked checks

- The documentation sets role responsibilities. Available tools and permissions come from each session. Browser release and Pole results have separate pins.

## Next steps

- For the browser track, read the TeamBuilding note on PR #93. It remains a draft with conflicts and its deployed smoke is pending.
- For the Pole track, read the TeamBuilding handoff on PR #95 and the FRUS-Presentation evidence at 2a0bc642fe21b164fd921758f56bb43f49e5a361. The three other FRUS cases remain open.
- Start a new strategy session with the repository link and “You are Al.” Start a separate repository session with the same link and “You are Betty.”
- Use the PR report to brief Al. Paste Al’s response and the maintainer’s direction back into Betty’s session.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
