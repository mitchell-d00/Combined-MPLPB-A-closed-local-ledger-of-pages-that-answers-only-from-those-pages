# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f12540c73d15ee81248e9eb4fe07f5b12242a312` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `acf8ed32aae8ef02094edbcd764480c585768081d011e570044dfb80fa567d86`.

## Latest user update instructions

Continue improving MPLPB without weakening its existing protections.

First, investigate why 13 of the 23 historical reference passages are still missing and improve retrieval.

Second, help MPLPB recognize events, corrections, contradictions, and relationships in ordinary writing. Every connection must link back to the original evidence and remain a candidate until properly verified.

Third, test these improvements against unfamiliar historical documents. Measure correct relationships, incorrect relationships, missing information, processing costs, and justified refusals.

Preserve all existing results and run the full regression suite. Do not change the tests to make MPLPB appear more successful.

The goal is simple: MPLPB should not just store and retrieve information. It should help reconstruct what happened from the evidence, while knowing what it cannot prove. My main recommendation: Stop focusing on increasing the number of passing unit tests. Focus on proving that MPLPB can understand and connect information from real documents.

The most important engineering objective now is reducing false relationships while retaining useful correct ones.

The next challenge is demonstrating that MPLPB can consistently recover the important relationships it currently misses, without reintroducing false ones.

## Implemented scope

- Diagnose all 13 old missing draft spans without changing original inputs, scoring or earlier results.
- Reuse the gated passage index for source/subject query facets and preserve exact routes, restrictions and quote-only source authority.
- Add candidate actor/action/object, modality, scope, documentary bindings, date roles and typed textual connections; no semantic authority promotion.
- Freeze and compare prior/current on unfamiliar public originals, retain developer source-linked semantic assessments, mistakes and omissions, costs and justified refusals.
- Use actual unfamiliar-record semantic failures to correct noun/adjective event errors, compound speakers, passive roles, quote boundaries and irrelevant website comparisons; retain bounded candidate pronoun/planned-action connections.
- Recover the demonstrated distribution omission by counting only valid predicates against extraction limits; recognize generic called-off/cancelled phrasing with negation and conditional scope.
- Reject prepositional names as grammatical actors; expose same-clause coordinated actor proposals conservatively, without upgrading semantic truth.
- A stricter frozen-context test found distribution recovery inconsistent at 1/4. Replace the per-context cap with the existing global 48-proposition bound; preserve all earlier results and evaluate retention/false proposals again.
- Recognize cancellation phrases across preserved physical line breaks without rewriting original text.
- Reject ambiguous modal may and non-calendar march/marching as date cues; keep calendar-context bare months, explicit dates and relative-time phrases without normalized-event-time claims.
- Allow the existing CLI inverse mapper to select rich propositions, connections and qualification nodes while retaining source rechecks and non-authoritative output.
- Publish complete baseline/final recovery results, all intermediate failures, per-case resource measurements, source-linked semantic labels and blank independent review/adjudication packets in a new immutable dated report.

## Validation recorded

- Final 01f128b completed all 14 original cases at 18/23 frozen draft-span coverage, native support 0/14.
- Developer semantic review, comparable deduplication: prototype 15 correct / 38 incorrect / 17 unresolved / 8 irrelevant; final 18 correct / 1 incorrect / 37 unresolved.
- Cold source acquired after code freeze: correct 3 retained; incorrect 14 to 0; unresolved 1 to 6. Not independent human review.
- Full final regression suite passed 1003 tests; public prepared 52/52; separate synthetic regression controls 24/24.
- All 727 rich proposal objects across historical and new studies passed source/policy/pin/quote integrity and non-authority checks.
- Native commit 01f128b passed all five CI workflow families, including exact archive and browser regressions.
- Recovery focused controls: 26 passed in 1.683 seconds after fixing a conditional actor-clause error. The premature passing statement in cbee135 is explicitly corrected in recovery/validation-correction.json.
- Allocation revision: 28 focused controls passed in 3.928 seconds, including all four existing complete-evidence distribution opportunities and multiline conditional cancellation.
- Previous a259 whole historical run reached terminal state before allocation code replacement; its consistency failure remains immutable.
- 30 focused reconstruction/source controls passed in 4.484 seconds in the isolated worktree; current main benchmark was not modified.
- Final native f12540c full Python suite: 1011 tests passed in 486.615 seconds; complete log/hash retained.
- Final public prepared evidence suite: 52/52; final separate released synthetic controls: 24/24. Neither establishes historical semantic accuracy.
- All 21 previous useful reviewed associations retained; three source-consistent candidates added. Final reviewed actor/action/text associations: 24 correct, zero labeled incorrect, 51 unresolved across 75; developer/AI source review, not independent humans.
- Final distribution recovery is 4/4 complete-evidence context opportunities; cancellation is 3/3. These are two target relations, not seven independent historical events. The unsuccessful 1/4 intermediate run is preserved.
- Final date-cue source review retains all 16 genuine cues and removes all 12 false cues; actor/action quality remains separately reported.
- All five native f12540c CI workflows passed, including archive/browser, worker isolation, infrastructure, conventional regression and handoff.
- Actual extracted f12540c source archive: handoff/documentation checks passed, 30 focused controls passed in 4.440 seconds, UI/transport/JavaScript API/crawler checks passed.
- All 491 tracked original-study and frozen import/evaluation files remain byte-identical to ee9975a; all 105 existing test files unchanged.
- Final f12540c original 14-question run completed under the frozen 180-second budget: 18/23 incomplete draft spans retrieved; native supported answers remain 0/14. No source, question, score or authority requirement was changed.
- All 850 final rich mapping objects across five authentic studies passed exact quote, canonical offset, digest, native pin, current source/policy and non-authority checks; each case exercised a fresh inverse reconstruction. Mechanical fidelity is not semantic correctness. Complete final blank human review packets are prepared; independent review NOT RUN.

## Limitations and blocked checks

- Finite deterministic candidate interpretation is fallible and not unrestricted semantic understanding.
- Independent human evaluation NOT RUN; developer judgments must be labeled and scoped.
- Developer semantic assessment is not independent human review and has incomplete historical reference scope.
- The intermediate launch metadata used a mistyped commit label; an explicit correction preserves original receipts and binds actual native SHA256 pins to commit 6499338f00377181a8ffc169b9977d4be31841e1.
- Two additional historical records still produce five unresolved proposed associations and miss important intent/publication/signing/ceasefire/revision links. Broad consistent historical reconstruction is not demonstrated.
- Zero incorrect labels in the limited actor/action assessment is not a global historical false-positive rate; date roles and unresolved candidates remain uncertain.
- Later allocation/date revisions reused the post-a259-code-freeze transfer records; final implementation is not independently unseen.
- Human labeling, correction, review and adjudication time, engineering/model-assistance cost and compute pricing are unknown. No efficiency or deployment claim.

## Next steps

- Use genuinely independent authors/reviewers for a new sealed challenge; prepared human review and adjudication are NOT RUN.
- Address unresolved transfer semantics in a future frozen experiment, preserving current failures and source authority.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
