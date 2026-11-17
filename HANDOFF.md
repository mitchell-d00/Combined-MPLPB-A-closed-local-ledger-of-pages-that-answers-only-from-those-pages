# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `26ca2b5be17281684551ca2649ff62e7c0aa250f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `50fe15a1b91a2c7da7f06de66374cbbbfe64431d8d8d3b9f0b1f249efbd2fdb7`.

## Latest user update instructions

Push it to main merge and update all documentation write me a new paper by Mitchell d Mcphetridge in txt pdf and md A Dual-Mode Sorter for MPLPB: Turning Unformatted Material into Inspectable Candidates; Source-Anchored Candidate Extraction for Closed Local Ledgers

## Implemented scope

- Publish authorized offline sorter and native export work to main through a PR with exact-head required checks.
- Write a new dated technical paper by Mitchell D. McPhetridge with requested title/subtitle in Markdown, text and PDF; retain source/format hashes and honest measurement boundaries.
- Refresh relevant operational documentation, installation/pipeline guidance, repository map, fix log and past-documentation navigation, preserving frozen originals and earlier reports.
- Extend existing paper renderer with explicit source and metadata parameters, optional invariant PDF metadata; runtime remains standard-library only.

## Validation recorded

- Inherited measured sorter runtime30f0d89:1184 tests and52 public controls; current publication head is separate and not yet checked.
- New nine-page paper renders with requested PDF author/title metadata. Sample pages visually inspected; initial orphan final line removed, rerendered to nine pages.
- New renderer tests2/2 passed0.109s; custom-source text rendering leaves original paper bytes unchanged, invariant PDF builds repeat exactly under ReportLab4.4.9.
- Remote main is3df2c6e and branch is four commits ahead with no divergence at initial fetch. Active Bear ruleset requires PR plus archive-first/regression on exact up-to-date head; no reviewer approval required.

## Limitations and blocked checks

- Sorter output remains non-authoritative; no historical reconstruction, truth or supported-answer completion gain claimed.
- All semantic accuracy/human review measurements remain null/NOT RUN. Retained paper results are developer-authored controls, not publication-head or deployment evidence.
- Original historical corpora, questions, reports, original papers and vendor bytes remain untouched.

## Next steps

- Freeze and ZIP-test publication candidate, push branch and create PR.
- Wait for exact-head archive-first/regression and other checks, merge to main without bypassing branch rules.
- Verify Pages build/deploy and actual live-browser checks; report exact merge/deployment receipts.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
