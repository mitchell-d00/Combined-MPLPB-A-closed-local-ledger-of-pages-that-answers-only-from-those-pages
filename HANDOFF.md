# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3057a667a4421ac5298b9f599e8532bffc50740f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d3b5a9b50a2bee165a08352f8b4b7400a3799d09419f5dff94487d5739914e96`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository before reading the last Betty report on the live PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Make them realize it’s not a persona it’s just a pipeline

Make it run Al or run Betty  with repo Link

### Implemented scope

- Make Run Betty and Run Al with the repo link the primary TeamBuilding commands. Define both as pipeline steps.
- Give web-only readers a direct public manifest URL and ordinary repo and PR links for Al’s evidence review.
- Preserve the per-push Betty report, live PR resume contract, ZIP catalog and existing terminal and browser API methods.

### Validation recorded

- The JavaScript bridge contract confirms both starters, Al’s step type and the HTTP-only discovery path. Repository infrastructure and generated handoff are checked locally.

### Limitations and blocked checks

- The commands select a pipeline task. Each session uses its own tools and permissions. Mitchell relays the review and gives Betty direction.
- The current indexed Pole report remains PR #97. Release-asset status is recorded separately from the recoverable source commits.

### Next steps

- Use the short Run Betty and Run Al starters in separate chats. Both read the repository before the last Betty report.
- Al follows the public links and returns a review and next prompt. Betty updates the live PR after the maintainer’s direction.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
