# Historical reconstruction engine

Last reviewed: 2026-11-17.

The reconstruction path extends the existing strict documentary checker and reversible prose investigation. It does not replace either engine. Source integrity, quotation fidelity, typed statement support, candidate interpretation, human review and historical truth remain separate states.

```sh
python -m mplpb_answers reconstruct LEDGER "Compare the wording in the two accounts."
python -m mplpb_answers reconstruct LEDGER "Why was the expedition delayed, and what resource supported its return?"
python -m mplpb_answers reconstruct LEDGER "When was the report published?" --profile external
python -m tools.reconstruct_original map --ledger LEDGER --question QUESTION --output NEW_REPORT
```

The JSON report includes the existing native answer, individually checked claims and unresolved obligations, reversible candidate propositions/graph, documentary units and layer hints. Existing Ask/API/browser routes retain the answer-contract-v1 behavior. New relationship rules remain partial unless the established complete-answer conditions are satisfied; a literal difference or causal assertion alone never resolves the whole historical question.

`PassageIndex.documentary_units` exposes canonical offsets, complete-boundary flags, source IDs/hashes and inferred documentary layers. Transcript, editorial, quotation, annotation, correspondence and site-chrome hints are derived inspection structure, not new source authority. Uppercase source labels can delimit units without supplying answer facts. Wrapped lines remain unchanged. Long/OCR fragments and exhausted limits remain visible. Original-byte mapping is resolved lazily with `tools.source_roundtrip.original_passage(CORPUS, IMPORT_RECEIPT, UNIT_OR_CITATION)`; null mapping fields do not mean original bytes were independently checked.

The existing kernel re-reads eligible sources and parses complete native units. New finite rules cover explicit because-of passive assertions, resource-provision statements, before/after statements with separate publication/revision/receipt roles, and explicit passive by-phrases. Arguments, negations and time expressions remain literal. They do not authenticate actors, normalize an uncertain date, establish actual execution, or independently prove a source's causal assertion true. Unsupported quotations, conditions and ambiguous prior context stop acceptance. In particular, damaged OCR quotation state can still block otherwise useful Apollo summary statements.

Exact comparisons use complete native paragraph units, including semicolon-separated originals. The checker computes token alignment independently from current source bytes. All equal/insert/delete/replace segments are retained in the structured proposition; the display previews the first twelve alignment segments. The comparison establishes differences between those two units only, not version order, source authenticity, historical correction, motive, responsible editor or absence elsewhere in an incompletely examined document.

The graph is a view of existing reversible proposition/connection mappings. Documentary appearances, actor mentions and event candidates have distinct nodes. Every edge retains source anchors, state dependencies and unresolved identity/link issues. Similar names, subjects, dates or text never merge event candidates. Candidate graph edges never receive strict support automatically. Date candidates preserve their existing roles and do not become a historical timeline by sorting.

For optional local model interpretation, pass `--reader-model INSTALLED_MODEL` and optionally `--reader-endpoint http://127.0.0.1:11434`. This reuses the existing bounded local-reader plan/read/review schema, model digest checks, exact-citation validation and loopback-only transport. Model-generated claims remain assisted output, never historical truth or independent evaluation. No weights are downloaded and no cloud service is required. Live-model efficacy remains unmeasured without an installed model.

Bounds include the caller's passage/character limits; four obligations and twelve proposals; 200,000 scan characters, 1,000 units and 64 action assertions; at most sixty local comparison candidates, two proposed comparisons (four for source-framed requests) and 600 tokens per alignment side; and 160 candidate graph nodes/edges. Full-context omissions and incomplete scans cannot establish historical absence or a complete answer. The source-unit API permits explicitly bounded larger scans; oversized sources bypass immutable caches. Canonical projections and structural parsing cache content only, at most four inputs of at most two million characters each. Current permissions, restrictions, revisions and source hashes are always re-read.

See [review and synthetic-truth rules](HISTORICAL_TRUTH_RULES.md), [crawler admission](../crawler/README.md), and [the versioned experiment](../evaluation/reconstruction-engine/2026-11-17/BASELINE.md). Independent review and unseen evaluation are NOT RUN. A 9/10 rating and the proposed 80%/95%/75%/95% targets require evidence that is not yet available.


## Completing literal source comparisons

Kernel v3 adds a separate completion proof for bounded opening-topic comparisons between a source-declared rough reconstruction and a transcription. It re-reads positive framing statements in canonical body prose, resolves a unique printed work reference and author reference within those declarations, selects the first relevant complete topic paragraph after each declaration, and independently computes both changed and shared wording. All four citations are required: two compared units and two role declarations. Source titles, filenames, ranking and model labels cannot substitute for these witnesses. An ambiguous/missing/qualified role, different work or author, additional factual obligation, incomplete display budget or changed source prevents completion.

The question parser accepts varied literal-comparison wording, not arbitrary historical reasoning. It explicitly rejects unsupported additional obligations rather than silently dropping question words or dates. Completion is scoped to the supplied source-declared appearances. It does not establish manuscript authenticity, that a transcription is the last-ever historical version, a real person's identity, revision motive or historical truth. Other question classes retain their existing support gates. A heading containing Draft may accompany a body-declared rough reconstruction for this text-comparison proof; it remains excluded from unconditional action/execution proofs. Plan, hypothetical and quotation scopes still block role declarations.

For plaintext transcriptions, physical blank paragraphs are used only when their canonical concatenation exactly reproduces the existing projection. Wrapped lines and offsets remain unchanged. Existing admission-manifest paragraphs are excluded from documentary wording/identity evidence. Complete arithmetic comparison does not depend on an exhaustive search for unrelated historical actions, and does not claim whole-document or historical absence. Every necessary selected-source/reference connection is checked separately.

## Accumulating a documentary history

The existing WorkStore can persist claims, evidence, challenges and review decisions with immutable prior revisions. Suggested graph links remain separate from checked source statements and human-reviewed interpretations. New or restricted sources must trigger dependency rechecks. The current derived graph is query-scoped; automatic corpus-wide graph maintenance as pages are imported is still an integration gap. Nothing in this implementation automatically turns a suggested or human-accepted relationship into historical truth.
