# Optional local semantic triage

Last reviewed: 2026-11-18.

`mplpb_work.semantic_triage` consumes an explicit bounded allowlist of currently eligible native paragraph pairs. It does not choose relationships, author an answer, judge historical truth, admit proof or call a ledger writer. It is disabled by default. The only model outputs accepted are `AMBIGUOUS_LINK_CANDIDATE` and `POTENTIAL_CONTRADICTION`, or an empty flag list for each pair. Every result is quarantined with source-support and historical-truth fields false.

Pairs JSON is a list of `{left,right}` objects. Each endpoint contains exactly `source_id`, `path`, `hash`, `body_start`, `body_end`, `quote`. Quotes must match complete native paragraphs of at most2000 canonical characters; the complete original question/profile governs eligibility before and after inference. Unknown IDs, severed paragraphs, stale sources, extra model prose/fields, missing decisions, tools and attempts to set authority are rejected. Use the existing [local narrator backend configuration](LOCAL_NARRATOR.md); no model download occurs in the runtime.

```bash
python -m mplpb_work.semantic_triage pairs.json --corpus LEDGER --question 'Review archive passages' --output NEW_QUARANTINE.json
# Explicitly enable an already installed local backend:
python -m mplpb_work.semantic_triage pairs.json --corpus LEDGER --question 'Review archive passages' --model --output NEW_MODEL_QUARANTINE.json
```

At most16 pairs,24,000 pair-input UTF-8 bytes,28,000 message bytes,512 output tokens and8000 response-text bytes are accepted. Every skip is visible. The transport retains its bounded response read and socket timeout; it does not guarantee an absolute wall limit against a hostile trickle server. Use a trusted local service with remote forwarding disabled. Weight identity is not attested by a generic OpenAI-compatible endpoint.

A caller selects unresolved pairs from its inspection workflow. That selection does not prove relationships are absent elsewhere. No existing v1/v2 graph, workspace, strict reader or classing decision is automatically changed. The classing builder rejects injected decision records; a flag cannot authorize supersession, retirement or ratification. Quarantine output must be outside the ledger. Human review still does not establish historical truth automatically.

`python -m unittest tests.test_semantic_triage -q` checks admission, schema, optional operation, source changes, exact context and non-authority. `tools.evaluate_semantic_triage prepare NEW_DIRECTORY` freezes six fictional utility probes; `run` calls the configured local model before consulting developer expectations. Those expectations are not historical ground truth. Useful/unexpected/missed fixture flags, schema failures and runtime must be reported separately from independent semantic accuracy, which remains unestablished.
