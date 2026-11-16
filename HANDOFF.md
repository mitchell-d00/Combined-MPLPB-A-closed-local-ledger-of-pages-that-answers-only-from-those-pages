# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `01f128bc6022ff64c2edf5c363f05f173ac95972` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `1096a328287330217a918811b6e3e7190030af1bad9d16fc3072fdeed2fea57c`.

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

## Validation recorded

- Final 01f128b completed all 14 original cases at 18/23 frozen draft-span coverage, native support 0/14.
- Developer semantic review, comparable deduplication: prototype 15 correct / 38 incorrect / 17 unresolved / 8 irrelevant; final 18 correct / 1 incorrect / 37 unresolved.
- Cold source acquired after code freeze: correct 3 retained; incorrect 14 to 0; unresolved 1 to 6. Not independent human review.
- Full final regression suite passed 1003 tests; public prepared 52/52; separate synthetic regression controls 24/24.
- All 727 rich proposal objects across historical and new studies passed source/policy/pin/quote integrity and non-authority checks.
- Native commit 01f128b passed all five CI workflow families, including exact archive and browser regressions.

## Limitations and blocked checks

- Finite deterministic candidate interpretation is fallible and not unrestricted semantic understanding.
- Independent human evaluation NOT RUN; developer judgments must be labeled and scoped.
- Developer semantic assessment is not independent human review and has incomplete historical reference scope.
- The intermediate launch metadata used a mistyped commit label; an explicit correction preserves original receipts and binds actual native SHA256 pins to commit 6499338f00377181a8ffc169b9977d4be31841e1.

## Next steps

- Recover missed distribution and called-off relationships with generic phrase/selection repairs; compare false proposals and retained useful relationships together.
- Keep earlier results and errors immutable; test further transfer records without authoring answer-bearing source fields.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
