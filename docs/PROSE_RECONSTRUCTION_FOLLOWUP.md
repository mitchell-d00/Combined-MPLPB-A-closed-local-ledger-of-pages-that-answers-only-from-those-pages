# Prose reconstruction follow-up

Last reviewed: 2026-11-16.

This iteration starts at `ee9975a9c6d3a6413a9295763e7cbea068195f17`. Earlier source bytes, questions, rules, reports, outputs and tests remain unchanged. The [13-span diagnosis](../evaluation/unprepared-originals/2026-11-16-followup/missing-13-diagnosis.json) identifies ranking, navigation and context-budget failures rather than failed imports. Some negative-control reference excerpts cannot establish absence or causality by themselves.

The optional prose path reuses the existing eligible passage index. Query facets separate document discovery from the requested subject; heading words guide routing only and never enter canonical answer evidence. Declared transcript sections retain separate source appearances, lexical expansions are explicit retrieval aids, and exact-field routes keep their unranked behavior. All paths remain bounded and search remains incomplete.

`mplpb_work/prose_relations.py` proposes source-linked actor/action/object structures, qualified requests, conditional versus asserted actions, date roles, textual scope, possible opposing statements, possible corrections and parallel wording. An explicit correspondence heading can propose first/second-person bindings within that appearance. Instructions to send are not completed delivery. Permission, intention and conditional failure are not observed events. Shared words cannot establish causality or event identity. Every proposition and connection remains `answer_supported=false` and `content_truth_verified=false`; faithful quotes do not certify semantic interpretation.

The new finite rules are fallible. Unresolved pronouns, passive agents, incomplete context and uncertain date roles remain visible. Similar wording can propose a textual comparison, not a verified correction. A possible correction never mutates native supersession or permission state. Existing `reconstruct` reloads the gate and checks hashes and quote coordinates.

The [dated follow-up directory](../evaluation/unprepared-originals/2026-11-16-followup) retains exploratory retrieval failures, the same frozen 14 historical questions, and separately frozen unfamiliar public government records. The unchanged prior implementation ran first on the unfamiliar sources. Questions/reference facets are developer-authored; no independent human blinding or review is claimed. Candidate quality must be assessed separately from retrieval coverage and quote fidelity. All processing costs, misses, refusals and incorrect candidates are retained.

```sh
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation REPAIR_CHECKOUT --mode updated --commit EXACT_SHA --seal freeze-v2.json --output NEW_OUTPUT_DIRECTORY
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-followup/unfamiliar --implementation REPAIR_CHECKOUT --mode updated --commit EXACT_SHA --output NEW_UNFAMILIAR_OUTPUT
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-followup/legal-transfer --implementation REPAIR_CHECKOUT --mode updated --commit EXACT_SHA --output NEW_LEGAL_OUTPUT
python -m unittest tests.test_prose_reconstruction tests.test_source_mapping tests.test_unprepared_prose -q
```

The existing frozen evaluator/importer and 180-second budget govern both compared implementations. Independent assessment remains NOT RUN. Unit controls validate boundaries; they do not establish historical understanding.


## Measured semantic failures and second revision

The first proposition prototype passed boundary regressions but developer inspection of all 80 unique unfamiliar-record proposals found 15 source-consistent, 38 incorrect, 17 unresolved and 10 irrelevant connections. These are developer/AI judgments, not independent human evaluation. All quotes, rationale and wrong outputs remain in the dated directory. The next revision rejects nominal/adjectival action matches, separates source-defined HTML paragraphs and site chrome, keeps uncertain agents unresolved, distinguishes reported speech from instructions, and proposes bounded same-paragraph antecedents and planned-action links with both source passages. It never silently substitutes a candidate antecedent as verified identity. New actual-source runs are required; those failures are not relabeled.
