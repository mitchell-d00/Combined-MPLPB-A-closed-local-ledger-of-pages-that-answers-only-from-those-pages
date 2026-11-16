# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `4e4db3ef80caab004abfb86bbfe651a09fe1dc9e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f9cb340405804fd12e4c5fa0c05b53daeaa7ee9eeeae2813b88ea2be24a27dc6`.

## Latest user update instructions

Codex Engineering Assignment: Evidence-Grounded Historical Reconstruction

Your task is to improve the actual repository and produce reproducible evidence of the improvement, not merely write an assessment, proposal, or favorable benchmark report.

Complete as much of the actual engineering work as the available environment permits.

Start by inspecting the repository and establishing the baseline.

Then implement the highest-impact improvements.

Do not stop at a plan. Do not merely add documentation or a benchmark that awards credit for candidate relationships.

Prioritize real, verifiable historical reconstruction and preserve the existing integrity-first design.

The final objective is a system whose capabilities can be established through independently reproducible original-source experiments, not through assertions about what it should be able to do.

How can we fix this The familiar-record replay still has no supported answers, and the broader reconstruction objective remains unproven.

How can we improve  close the supported-answer gap

We can do this The next implementation should target explicit documentary assertions and compound-question composition, then demonstrate gains on unchanged questions. Add it to the tests and build it

## Implemented scope

- Add a strict finite source-assertion proof checker and atomic obligation/composition path, distinct from candidate extraction and historical truth.
- Preserve full-question eligibility/profiles, current source rechecks, correction boundaries, complete qualifiers, directive/execution distinction, literal dates, and bounded partial output.
- Add original-record regressions, varied adversarial tests, citation rendering and real WebAssembly integration tests; prepare certificate-rechecking comparison tooling without changing frozen runners or questions.

## Validation recorded

- 33 new documentary/original-record tests passed in 9.917 seconds before source freeze; broader focused run passed 95 tests.
- Prototype native probes on unchanged H02/U01 returned checked partial assertions with execution, reference and comparison limits retained. These are not complete historical answers or independent accuracy scores.
- Prototype prepared public evidence controls passed 52/52; real WebAssembly source composition and UI rendering controls passed. Final extracted candidate checks and frozen complete replays are pending.

## Limitations and blocked checks

- Independent human semantic review and unseen evaluation NOT RUN.
- Finite native-source assertion support does not establish historical truth, authenticated authorship or person/event co-reference.
- Original-record complete-answer gains and final regression results pending at this freeze; do not infer success from candidate counts.
- Source parsing is conservative and fallible; unsupported syntax, scope, aliases, voices and corrections can remain unresolved.

## Next steps

- Freeze and test the extracted source candidate, replay unchanged original/familiar questions and independently recheck every accepted certificate and original-byte citation.
- Retain every failure/partial result, distinguish checked partials from full answers, and prepare real human reviews before accuracy claims.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
