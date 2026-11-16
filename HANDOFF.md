# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `38e273855e577cff038f704c63fe09b22ac6889a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `491ed9c98b1c93dcc0c01c22c225cf490a9909534e239fb519b6efc18d7f4092`.

## Latest user update instructions

Codex Engineering Assignment: Evidence-Grounded Historical Reconstruction

Your task is to improve the actual repository and produce reproducible evidence of the improvement, not merely write an assessment, proposal, or favorable benchmark report.

Complete as much of the actual engineering work as the available environment permits.

Start by inspecting the repository and establishing the baseline.

Then implement the highest-impact improvements.

Do not stop at a plan. Do not merely add documentation or a benchmark that awards credit for candidate relationships.

Prioritize real, verifiable historical reconstruction and preserve the existing integrity-first design.

The final objective is a system whose capabilities can be established through independently reproducible original-source experiments, not through assertions about what it should be able to do.

## Implemented scope

- Inspect current architecture, frozen reports and original mapping; preserve every prior artifact.
- Repair ordinary-prose shared scope, reporting/request complements, passive role candidates and date roles without authority promotion.
- Add adversarial controls and hash-checked original-record comparison with byte mappings and blank human reviews.

## Validation recorded

- Baseline at 38e273855e577cff038f704c63fe09b22ac6889a: public evidence run completed; full regression launched before edits, terminal result pending.
- 50 focused tests passed in 4.652 seconds, including 20 new adversarial controls.
- Initial frozen original/unfamiliar runs failed bubblewrap outer-sandbox NETLINK_ROUTE setup; retained, retry using unchanged bubblewrap runner outside outer sandbox.
- Unfamiliar baseline retry completed all eight cases; 9/9 incomplete draft spans, native support 0/8.

## Limitations and blocked checks

- Independent human review and genuinely unseen challenge NOT RUN.
- No native historical supported-answer gain demonstrated; finite fallible candidate interpretation only.
- Full candidate original-record replay, regression and archive checks pending at source freeze; evidence update will record actual results.

## Next steps

- Run frozen source candidate and exact extracted archive checks, retain all failures, compare costs and source-linked interpretation changes.
- Obtain independent question authors, reviewers and adjudicator for a new sealed evaluation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
