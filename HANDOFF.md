# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `8fb3eb82cde1781c1402d57986b63179b82ad4e5` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `21eec01b5c90e4a3f7aee865e11249fc911f1f56a84f83abce164078dd09b296`.

## Latest user update instructions

Read MPLPB, challenge reconstruction of complex relationships from original historical evidence, and fix the errors using the existing experts. Add an expert path that crawls relations while preserving MPLPB boundaries. Build public, inspectable tests and results without personal attribution or discussion of external commentary. Expand to 52 substantive tests; once all tests pass, push and merge to main. Update current operational documents with dated notes while preserving historical documents.

## Implemented scope

- Implement explicit capability-gated documentary, chronology and independent verification expert operations through WorkStore, bounded relation crawling, exact citations and source/profile rechecks. No expert receipt or candidate is a supported historical answer.
- Preserve preformatted source context and exact offsets; add documentary event candidates with separate occurrences/review flags and explicit uniquely scoped source corrections that retain predecessor and unaffected text.
- Publish a checksum-pinned, fully visible 52-case development suite, reproducible fictional fixtures, per-case results and measurements. Compare the same suite against an identified earlier source inventory. Do not claim hidden tests, human validation, or unavailable private-data reproduction.
- Add dated navigation/update notes to all current operational documents; preserve historical/vendor bytes, licenses, original papers, frozen corpora/probes/reports and source authority restrictions. User instruction is summarized to honor the explicit prohibition on personal attribution in public artifacts.
- Test a frozen extracted candidate, require successful exact-head checks, then merge to main under the user’s explicit authorization and observe postdeployment verification.
- Pin fixture record time and retain final per-case source hashes so public scenarios regenerate reproducible sealed bytes. Preserve human-effort measurements as unknown and separate unsupported capabilities from safety outcomes.
- Retain public per-case current/baseline results, implementation module hashes, fixture source hashes, resource measurements, and a version-bound comparison; preserve the tested implementation separately from evidence-only additions.

## Validation recorded

- Preliminary public development run passed all 52 cases with zero observed false supported bridges; a final frozen candidate replay is still required.
- Original-paper expert replay reached four hash-pinned originals, independently verified 31 documentary observations, traversed six declared relation edges and left 15 unresolved links visible; all three expert stages passed in the inspected run. These counts are documentary development controls, not historical truth or general semantic accuracy.
- Earlier focused extractor/verifier/crawler/passage tests passed before the final event/correction/public-suite integration. Full current regression, documentation, exact archive and browser checks remain to run.
- The first full candidate run completed 926 tests with one generated-guide synchronization failure; the generator has been updated to match the reviewed operational guide. Final candidate testing must confirm this correction.
- The generated-guide fix passed 13 focused system/documentation/public-suite tests, including the 52-case evaluator. The final corrected candidate still needs its extracted full regression and exact-head CI.
- The corrected frozen extracted implementation passed all 926 Python regression tests. Its strict 52-case suite and four-original-paper replay passed, as did extracted JavaScript/API/transport/crawler/infrastructure checks. The final fixed-timestamp/hash-receipt harness change passed eight focused tests including all 52 public requirements; exact final-head CI remains required.
- The clean published implementation 8fb3eb82cde1781c1402d57986b63179b82ad4e5 passed 52/52 public cases and the four-original-paper expert replay. Retained current/baseline per-case reports share manifest/evaluator hashes; baseline 257e54a records 10 passes and 42 capability gaps, with zero observed false supported bridges in both inspected runs. The comparison does not establish general historical accuracy.

## Limitations and blocked checks

- Only explicitly declared documentary fields and IDs/versions license relation traversal. Unknown or ambiguous targets, negation, conditions, restrictions, missing witnesses and budget limits cannot become guessed bridges.
- Event candidates are not confirmed historical events; source-stated dates are not inferred publication/invention dates. Scoped corrections require explicit authoring and do not provide unrestricted as-of or causal reconstruction.
- All 52 questions are public development tests, not blind holdouts. CPU/wall/Python allocation/source-text-read measurements are scoped; human labeling/correction effort remains unknown. Source integrity and source truth remain distinct.

## Next steps

- Run final 52-case acceptance, full regressions and all required checks; freeze and test extracted source, preserving code/manifest identity.
- Publish implementation, complete test fixtures/results, source/version pins and reproduction commands; merge only after exact-head archive-first and regression success, then observe deployment and actual live browser verification.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
