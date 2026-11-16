# Documentary scope and original-record experiment

Last reviewed: 2026-11-16.

The v6 prose interpreter preserves shared conditional/negative scope across coordinated predicates, records literal reporting and request complements, and exposes explicit passive by-phrases as role candidates. A by-phrase does not authenticate or resolve the named person. Calendar deadlines are excluded. Date cues after publication, receipt and revision predicates retain those candidate roles; no date becomes normalized event time. Copulas in earlier clauses no longer automatically erase an active actor.

The strict answer pipeline and source gate are unchanged. Every prose finding remains unsupported, carries its full source sentence and existing hash/canonical offset/state pins, and can be reconstructed through the existing inverse mapper. `kind` on the reconstruction report is `candidate_interpretation` or `abstain`; the existing strict pipeline continues to own supported/partial/conflict/clarification decisions. Candidate conflicts are not verified conflicts. Read-only investigation never changes correction or supersession state.

This is a bounded interpretation repair, not a general historical solver. It does not infer missing records, merge events, verify passive identities, or promote a graph to source support. Reported speech without the finite complement grammar, nested quotations, OCR damage, indirect requests and long-distance scope can remain unresolved or incorrectly proposed. Existing retrieval, segmentation and event identity limitations remain. The evaluation must include these omissions and false candidates.

The [experiment](../evaluation/documentary-scope/BASELINE.md) retains baseline and updated runs in new directories. Reproduce using the original frozen runner, identical mode/budgets and exact implementation revisions:

```sh
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation CHECKOUT --mode updated --commit SHA --seal freeze-v2.json --output NEW_ORIGINAL_RUN
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-followup/unfamiliar --implementation CHECKOUT --mode updated --commit SHA --output NEW_UNFAMILIAR_RUN
python -m tools.compare_documentary_scope CORPUS BEFORE_RUN AFTER_RUN --output NEW_COMPARISON
```

The comparison verifies frozen input equality and run hashes, exports all changed interpretations, maps every new rich finding to original bytes, and prepares two blank review sheets plus adjudication. It never assigns correctness from pattern matches or citations. Full run outputs must accompany delta sheets so reviewers can count retained errors and omissions. Semantic metrics and human times remain null. Use existing `tools.unprepared_challenge packets` separately for each run (both have arm `updated`), then its two-human `score` workflow for full semantic assessment; the lightweight delta sheets are inspection aids, not scoring submissions. Source links, hashes and raw byte offsets are in original-mapping-audit.json.

For a genuinely unseen evaluation, an independent custodian must first freeze a clean implementation revision/archive and budget, then acquire new hash-pinned originals and obtain independently authored questions and complete expected event/relationship graphs. Keep expected answers in a separate sealed directory inaccessible to workers; commit only their digest before running. A custodian other than the implementation author executes identical inputs/budgets against the frozen baseline, updated, BM25 and keyword arms using the existing isolated worker. Preserve every failed/partial/timed-out case and the full run receipt. An inaccessible worker sandbox is a failed run, not authorization to drop isolation.

Randomize arm labels for two separate human reviewers, supply complete original records and exact citations, and record positive/negative opportunities, reference completeness, all false relationships, wrong support and answerable refusals. A third human resolves disagreements with source-linked rationale and pinned review submissions. Record actual review/correction time; unknowns stay null. Unseal only after outputs are frozen. The current developer corpora and questions cannot become unseen by renaming them. This prospective experiment and independent human review are **NOT RUN**.

The [terminal experiment record](../evaluation/documentary-scope/RESULTS.md) binds the final temporal repair to `c6f77bef76a90219ae6e2074f0302fa3d72ada19`. The source-linked receipt-date regression is preserved alongside its fix. Native supported-answer counts did not improve. See the [14-case refusal analysis](../evaluation/documentary-scope/REFUSAL_ANALYSIS.md) for the verification/composition work still required.
