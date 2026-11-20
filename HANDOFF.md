# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ef66c28fa2c7489f4e6a12ea2bb14f4427555729` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f6986537e3d07fea9456321244f502605af227fd358f556cb159bd906019f8b8`.

## Latest user update instructions

explain which link is missing when the evidence falls short.

## Implemented scope

- Expose a diagnostic and next step for specific event identity verification gaps.
- Offer an admitted named-source question when a narrowly recognized unnamed comparison falls outside the strict grammar.
- Keep the existing named-source proof rules and eligibility, recheck, and budget boundaries.

## Validation recorded

- Four new diagnostic controls failed on the baseline and passed on the candidate.
- A paired direct native comparison preserved the decisions, claims, citations, and diagnostic codes of 380 public D4/D% inputs. Sixty abstentions gained specific guidance.
- All 2,400 fictional query-panel outcomes matched expectations.
- The 43 focused Python tests, documentary rendering, UI script, documentation inventory, and infrastructure audit passed locally.

## Limitations and blocked checks

- This update covers selected event identity refusals. A formatting or selection explanation establishes no documentary fact.
- The paired direct replay checks native decision parity and is separate from the isolated CI gate.

## Next steps

- Apply paired tests to other refusal families after defining their distinct evidence obligations.
- Run the full exact-head release gates when a release candidate is submitted.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
