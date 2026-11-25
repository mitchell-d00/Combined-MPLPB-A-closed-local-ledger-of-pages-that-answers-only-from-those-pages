# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `c1e2100169556070d61be88c9125c59e30179211` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `587778ccc32df91039bf0713a2470a43aa302f46e01a8082d566dd3445459941`.

## Latest user update instructions

Full report for external agent in txt

No it’s not a handoff you will do the work it helps me strategize as do you but I like outside checkers and controls

Note this pass-off method in the repo call it TeamBuilding

Once you are done push and merge and I’ll start new prompt

## Implemented scope

- Document TeamBuilding and link it from the README. Record role ownership, pinned evidence, and the distinction from Thespian.

## Validation recorded

- Documentation inventory and the staged diff are checked locally. Exact-head release checks run on the documentation pull request before merge.

## Limitations and blocked checks

- The repository change is documentation. The Pole result and browser PR retain their separate source pins. This update makes no new runtime or independent-evaluation claim.

## Next steps

- Use TeamBuilding to have an outside strategist review the public evidence and propose a focused test for the implementing agent.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
