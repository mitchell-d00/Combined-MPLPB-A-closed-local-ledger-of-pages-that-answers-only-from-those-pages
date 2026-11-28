# FRUS Relationship 01 — consumed-case diagnosis

Last reviewed: 2026-11-28.

Reference main and PR #133 merge
`6942df4670196405797114cbe25317577c3118e1`. The original
[77-case baseline](../frus-correspondence-01/RESULTS.md) remains frozen.
[Source and runtime pins](freeze.json) bind extraction, corpus, protocol
and unchanged implementation. [Questions](questions.json) are the 11
consumed relationship cases and three earlier passing location controls
(LOC-03, LOC-09, LOC-14). [Exact target spans](consumed-anchors.json) are
only the selected consumed annotations. Fresh inputs, keys and generating
parameters have no role in either phase.

## Order and scoring

1. Run Strict Ask with the complete original question and no supplied hints,
   key or answer. Record its contract and independently inspect the native
   documentary planner, named-reference parser and relation frame. Explicit
   recognition requires a relation-specific obligation, and in a two-link
   case requires both edge obligations and a join. An unsupported return
   and empty plans indicate an interpretation stop even if the passage index
   is populated.
2. Keep separate original-question rank probes. Run native BM25 and
   documentary prose ranking independently at the same 12-passage and
   8,000-character budget. Strict's own emitted passages and citations
   remain separate. A ranked source is only a document visit. Count a
   target passage only where the exact frozen half-open span fits within a
   single eligible indexed, ranked or displayed passage. No score for
   matching names or nearby spans. Report rank-probe omission separately
   from actual Strict ranking never entered.
3. After retaining the full native trace, expose the selected consumed
   anchors to a separate evidence-supplied invocation. Re-read exact
   eligible originals under the same question and supply the complete
   native units enclosing each span to the existing documentary kernel.
   Probe its relationship and action statement verification. For the
   location controls also probe its existing literal-location certificate
   as a positive apparatus check. Keep original cause/qualification context
   and the 200,000-character, 1,000-unit, 64-assertion, 12-proposal limits.
   Neither a lexical match nor an unrelated certificate proves a requested
   link. A two-link result requires two actual eligible relation certificates
   and an explicit joining identity between them. An absent target,
   cross-reference or editorial identification alone does not prove
   underlying contents, agreement, delivery, or execution.

This is a same-operator public diagnostic. The native process receives
only the public corpus, questions, freeze and code. The second process
receives only consumed spans in addition. Local phase separation is
recorded without a new OS-isolation claim. No fresh, independent review,
human onboarding, older comparison or production dispatch in this study.
