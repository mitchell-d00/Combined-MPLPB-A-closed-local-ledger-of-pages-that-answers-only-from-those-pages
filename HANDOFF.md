# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ee9975a9c6d3a6413a9295763e7cbea068195f17` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `c0903489717ee69526d73d3b6b09d4d1679f2e71a92f20d121ec564e14514f43`.

## Latest user update instructions

Continue improving MPLPB without weakening its existing protections.

First, investigate why 13 of the 23 historical reference passages are still missing and improve retrieval.

Second, help MPLPB recognize events, corrections, contradictions, and relationships in ordinary writing. Every connection must link back to the original evidence and remain a candidate until properly verified.

Third, test these improvements against unfamiliar historical documents. Measure correct relationships, incorrect relationships, missing information, processing costs, and justified refusals.

Preserve all existing results and run the full regression suite. Do not change the tests to make MPLPB appear more successful.

The goal is simple: MPLPB should not just store and retrieve information. It should help reconstruct what happened from the evidence, while knowing what it cannot prove. My main recommendation: Stop focusing on increasing the number of passing unit tests. Focus on proving that MPLPB can understand and connect information from real documents.

## Implemented scope

- Diagnose all 13 old missing draft spans without changing original inputs, scoring or earlier results.
- Reuse the gated passage index for source/subject query facets and preserve exact routes, restrictions and quote-only source authority.
- Add candidate actor/action/object, modality, scope, documentary bindings, date roles and typed textual connections; no semantic authority promotion.
- Freeze and compare prior/current on unfamiliar public originals, retain developer source-linked semantic assessments, mistakes and omissions, costs and justified refusals.

## Validation recorded

- Pre-change unfamiliar studies executed to terminal receipts before native replacement.
- All 19 focused existing/new reconstruction and source-protection controls passed in development checkout.
- Historical and unfamiliar updated executions and full post-change regressions pending; no score claimed yet.

## Limitations and blocked checks

- Finite deterministic candidate interpretation is fallible and not unrestricted semantic understanding.
- Independent human evaluation NOT RUN; developer judgments must be labeled and scoped.

## Next steps

- Run frozen primary/unfamiliar comparisons, inspect every scored interpretation against original sources, retain all failures.
- Run full regression and extracted-source checks before publishing final evidence.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
