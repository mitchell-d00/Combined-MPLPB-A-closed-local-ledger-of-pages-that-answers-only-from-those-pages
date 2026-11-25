# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `deb2197ab32e58466f35e448c30b15e361cabaee` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `84e404030e2128fe7e3e81b8df17baee0b820c98cf4ecb57720d91abb4939e2b`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository before reading the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

It needs to read newest pr not always 97

### Implemented scope

- Discover the newest PR by creation time across all states for repo-link and Pages-link role commands. An explicit PR URL selects that PR.
- Remove the fixed report from the public manifest. Give web-only and browser API clients the live discovery URL.
- Read the selected PR detail and present its current head, report comparison and head-pinned handoff. Preserve the existing source archive catalog.

### Validation recorded

- Desktop HTTP and JavaScript contracts passed, including frozen CLI fixtures for newest PR, explicit override, stale report, fork handoff and empty listing.
- Both terminal paths read the live GitHub API and matched the newest PR and explicit historical override. Infrastructure and generated handoff checks are checked locally.

### Limitations and blocked checks

- The page-local API returns discovery metadata for an optional public GET. Terminal role commands perform the lookup themselves.
- Discovery uses creation time rather than comment or edit activity. Audit an unmatched report against HANDOFF.md at the actual PR head.

### Next steps

- Use the newest PR returned by the API before reading its Betty report. Supply a specific PR link to continue a different track.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
