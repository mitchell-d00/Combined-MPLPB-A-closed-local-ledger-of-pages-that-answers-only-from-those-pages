# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ddf16a11395964156ae206b2d2ca298c22c04cae` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5280862d09c8822936a9af53483f361600d2e7cd418e57318cefacf67a0485ed`.

## Latest user update instructions

Run synthetic people of varying educations and ages

## Implemented scope

- Add native whole-statement verification for bounded corrections, rescheduling, continuations, timed handoffs, log conflicts, scoped reference and cancellation cases.
- Preserve distinct support, partial support, conflict and unresolved outcomes with exact source spans.
- Cross four fictional adult age bands and four education labels with independent question styles and fresh synthetic cases. Run the same panel in the existing D4 workflow.

## Validation recorded

- Native reference, D4 generator, compound-field, historical verifier and new bounded-record tests passed locally.
- The paired 2,400-case synthetic panel matched 1,152 expected outcomes in the baseline and 2,400 in the candidate. A separate seed also matched 2,400 candidate outcomes.
- Existing UI, transport, JavaScript API and crawler fixture checks passed locally.
- The 380 public D4 packets produced identical baseline and candidate native answer decisions, claims and diagnostics in a direct comparison.
- The isolated 380-case D4 gate could not start its workers locally because this environment blocks Bubblewrap namespace setup.

## Limitations and blocked checks

- The new proofs cover finite, small packets under current source eligibility.
- The panel uses fictional reporting labels and authored fixtures. It provides no evidence about actual respondents or independent historical semantic accuracy.

## Next steps

- Run the exact-head archive-first checks and sealed D4 gate in GitHub Actions when a release candidate is submitted.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
