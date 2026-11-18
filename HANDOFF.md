# Repository handoff

Last reviewed: 2026-11-18.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `0c488a1ec93a6869df348755c31eb22be81d0d2c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `79bc165162c27f4e7f55eca5fdd3203842d02dc7d85960bffd78b8325d324f62`.

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
- Finish all66 v1 option executions before repair; retain1/22 complete in all arms, draft spans26/32,26/32,24/32, and all1033 unique proposed links.
- Conservatively separate vocabulary ranking from relationship generation: remove995 neighbor-only pair proposals, retain explicit source-key/reference/literal-wording reviews, and stop automatic traversal of weak wording/subject cues.

## Validation recorded

- Direct22 reproduced2 supported,1 partial,3 conflict,16 abstain; configured sorter-first completed22 with1 supported,2 partial,3 conflict,16 abstain. Draft span discovery27/32 to25/32.
- Original retest regression suite1225 tests passed356.255s; log retained.
- New focused sorter/adapter controls are executed separately; final three-arm/full regression results pending.
- 63 focused legacy sorter, new review-option and experiment adapter tests passed in1.445s, covering source pins, exact routes, current eligibility, qualification-preserving neighbors, ambiguity, embedded headers, shared subjects, missing targets, source replay and CLI perusal.
- V1 full suite1240 passed393.549s. All66 option workers completed with native reader files unchanged.
- Exploratory developer/AI short-passage sample16:4 useful textual reviews,4 false/misleading candidate links,8 irrelevant; not independent or representative. Remaining1017 unassessed.
- New unrelated-object neighbor-only control reproduced a failure under v1; v2 retains both search hits without proposing a relation. An unambiguous source-declared partial-correction positive control remains retained.
- 65 focused controls passed1.437s after conservative repair. Final v2 three-arm and full regression runs pending.

## Limitations and blocked checks

- Sorter-first retrieval can regress complete answers; H05 is retained as an actual failure.
- Source-faithful lexical suggestions are not established historical relationships.
- Default sorter statement/phrase caps leave incomplete extraction.
- Three-arm results pending; no independent human evaluation or genuinely unseen evaluation claimed.

## Next steps

- Freeze v2 and execute all three22-question arms with identical strict reader source pins and budgets; retain v1 failures and direct2/22 baseline.
- Publish source-linked discovery/complete-answer changes, sampled false/unresolved links, source/authority audits and costs; independent unseen/human evaluation remains NOT RUN.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
