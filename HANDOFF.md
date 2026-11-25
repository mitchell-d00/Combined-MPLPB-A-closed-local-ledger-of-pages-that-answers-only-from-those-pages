# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `2a0bc642fe21b164fd921758f56bb43f49e5a361` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `2b0d705a1d0586955e798254fec2bc7ef8fc29c24212b4fc6243bdba96dd4365`.

## Latest user update instructions

My direction for Betty: Run FRUS-PE01 as proposed.
Use the prompt Al wrote on pin 2a0bc642fe21b164fd921758f56bb43f49e5a361. Freeze the cases and the new negative control before scoring. Preserve all previously closed results, zero false-supported bridges, existing budgets, and all NOT_RUN labels. Publish the result table, rule text, updated open-item list, new commit hash, and archive SHA-256 under a new public pin.

## Implemented scope

- Freeze FRUS-PE01 on the four inherited comparisons, six inherited controls and one Hoover attribution control.
- Record exact attribution misses without promoting HTML publisher headings into canonical evidence.

## Validation recorded

- Both PE-01 anchors located. Zero canonical body attribution matches under the frozen rule.
- Discovery stayed 4/4 and complete Strict Ask stayed 1/4. All inherited outcomes matched. The added negative withheld.
- No scan cap hit. Zero false-supported bridges or execution failures.

## Limitations and blocked checks

- The probe is an evaluation diagnostic. PE-01 through PE-03, Focus-12, and scan and phrase limits remain open.
- Outside scoring, independent historical accuracy, independent semantic adjudication and native OOCC remain NOT_RUN.

## Next steps

- Leave the pinned report for Al on the FRUS-PE01 PR. The maintainer can relay Al’s recommendation and authorized direction to Betty.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
