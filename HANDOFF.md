# Repository handoff

Last reviewed: 2026-11-18.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6350988a2f64d8e5fa53bd187d368f4397bf4f4c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `3247d75a4b661144d4113a6539d1afa40153c9301cef2da9c20515ff796f76f3`.

## Latest user update instructions

Add an optional Synonym Ranker and Candidate Relater to the offline sorter package. Start from the existing sorter and reuse its exact source spans, hashes, occurrence IDs, and review annotations. Preserve the current not-compared and compare outputs when the new options are off.

The Synonym Ranker should help users find relevant passages even when the wording differs. Start with a small, inspectable vocabulary and an optional user-supplied glossary. Keep exact matches and synonym matches visible as distinct ranking signals. For each hit, show the original phrase, the term it matched, the exact source span, and why it ranked. Preserve the original wording and keep contradictory passages visible.

The Candidate Relater should propose links such as possible references, possible duplicate appearances, conflicting versions, and possible corrections. Give each end of a link an exact source span and explain what prompted the proposal. Shared wording and synonym matches can suggest what to inspect. Leave identity, chronology, causation, or correction status unresolved when the sources do not establish it. For example, “planned to send,” “sent,” and “received” may be useful search neighbors, but retain their distinct meanings and qualifications.

In the CLI and any user-facing display, label the results “Sorter suggestions for review. MPLPB has not verified these links or answers.” Keep rank scores and candidate links non-authoritative in the machine-readable output as well. Users can follow suggestions back to eligible originals for strict checking. Preserve MPLPB’s current ownership, eligibility, correction, and proof rules.

Let the sorter-first retest already underway finish as configured. Then compare three runs on the same 22 questions, originals, reader revision, and budgets: sorter alone, sorter with the synonym ranker, and sorter with both additions. Report newly located relevant passages, false links, and changes in complete strict answers separately. Retain the exact passages behind each change. Include regression cases for ambiguous synonyms, negation, quoted headers, shared subjects, and missing links. Use the 22-question set for development and reserve unseen originals for independent evaluation.

## Implemented scope

- Complete frozen22-question direct versus unreserved sorter-first retest before introducing review additions; preserve measured H05 regression and preparation-only layout pilot.
- Add opt-in lexical neighbor ranking and candidate relation review beside the byte-unchanged core sorter; retain exact spans, qualifications and non-authority.
- Add fresh replay/perusal and bounded user glossary, source/pin guards and explicit ambiguous-sense signals.
- Prepare all22 questions for the subsequent three-arm study using one strict reader pin and a common discovery-reservation guard; do not alter original questions, sources, budgets or proof rules.

## Validation recorded

- Direct22 reproduced2 supported,1 partial,3 conflict,16 abstain; configured sorter-first completed22 with1 supported,2 partial,3 conflict,16 abstain. Draft span discovery27/32 to25/32.
- Original retest regression suite1225 tests passed356.255s; log retained.
- New focused sorter/adapter controls are executed separately; final three-arm/full regression results pending.
- 63 focused legacy sorter, new review-option and experiment adapter tests passed in1.445s, covering source pins, exact routes, current eligibility, qualification-preserving neighbors, ambiguity, embedded headers, shared subjects, missing targets, source replay and CLI perusal.

## Limitations and blocked checks

- Sorter-first retrieval can regress complete answers; H05 is retained as an actual failure.
- Source-faithful lexical suggestions are not established historical relationships.
- Default sorter statement/phrase caps leave incomplete extraction.
- Three-arm results pending; no independent human evaluation or genuinely unseen evaluation claimed.

## Next steps

- Freeze the optional-feature candidate; run all three arms under identical conditions and publish per-case changes, exact source witnesses, false/unresolved link assessment and costs.
- Run the full regression suite and extracted source checks; publish a focused PR without claiming deployment or independent validation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
