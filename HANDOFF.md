# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `9a4d2c09e9e31529867252779a2d15a7d998f985` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `100b079aaaa57271975df711579087596c69f33cf68e15bc68b87836157c93ed`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Do it

### Implemented scope

- Read Al note 0003 at a36cc00a52d28588e22a1e0faa5e6451451976fa and apply Heka-01 in disposable local Git fixtures. Reader, original controller and reservation code unchanged.

### Validation recorded

- Freeze 161d9100d preceded the baseline and bridge. The first Node/Python pipe capture preflight was retained; file-backed capture enabled actual runs.
- Pinned candidate 9a4d2c09e9e31529867252779a2d15a7d998f985. Disconnected baseline 10/11 exact phases and zero writes. Development 12/14; first fresh 13/13. Neither development diagnostic mismatch reached the writer.
- Competing CAS preserved the competing ref. Restart withheld known duplicates and preserved indeterminate post-Git completion. Controller and restart replay matched all frozen current grades.

### Limitations and blocked checks

- Same operator authored and scored. Keys are held locally in private workspace custody. Host identity, provenance and a cross-resource transaction are outside the lab evidence. Original unsupported or incomplete states remain in their recorded scopes.

### Next steps

- Keep the lab candidate held for the two frozen exact diagnostic discrepancies. The first-run traces and original keys are the reference for any separately authorized follow-up. No production dispatch.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
