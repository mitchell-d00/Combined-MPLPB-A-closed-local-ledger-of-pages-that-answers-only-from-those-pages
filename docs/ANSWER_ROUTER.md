# Answer router

Last reviewed: 2026-11-18. The router wraps native strict answering and never awards support itself.

```sh
python -m mplpb_work.answer_router ask "Who sent SHIP-7?" --ledger LEDGER --dump RAW
python -m mplpb_work.answer_router ask "..." --ledger LEDGER --profile external --json
```

1. **Strict.** `mplpb_answers.pipeline.answer_query(ledger, question, profile)` with no hints. A `supported_answer` is returned as **OFFICIAL**.
2. **Explain.** The strict diagnostic category in plain words, plus facts from the ledger: the provenance gate's exclusion reasons for named records, field-scoped successors, withdrawn pages, which fields a record has and which are stacked (unreadable). The supported question forms are listed. A refusal is not evidence that the answer is absent.
3. **Rewrite.** Up to five `What is the <field> for record <ID>?` questions for fields the question names or hints at; a field-scoped successor is asked for the field it corrects. Each is run strictly. A hit is **OFFICIAL FOR A REFORMULATED QUESTION**, shown with both questions and a caution.
4. **Unofficial.** Ranked passages from eligible ledger pages and the raw dump (sorter v2), restricted to records the question names, with per-passage warnings (quoted, conditional, reported, negated, withdrawn) and correction candidates aimed at the same records. Labelled `UNOFFICIAL — not supported by MPLPB`. `answer_supported` is false.
5. **Classing help.** The next concrete step: which dump files are not in the ledger, which pages need re-classing, which decision would resolve a conflict.

`route(question, ledger, dump, profile, try_rewrites, reader)` returns the same structure as `--json`. `reader` is an optional callable `(question, passages) -> str` that may compose prose from the cited passages only; it is off by default and cannot change any support flag.

Limits: lexical ranking only; the extractive answer is one sentence or field line; rewrites cover the field route only.

## Additional admission safeguards

Native unofficial paragraphs use the full existing question/profile provenance gate, not only depth. Raw dumps have no sealed external-delivery policy and are not shown under the external profile. Known classed copies cannot bypass native exclusions through dump input. Withdrawn dump occurrences may be inspected explicitly under internal/lab with warnings; they never enter strict proof. Optional reader output must select one complete verbatim cited passage or the extractive fallback is kept. Dump evidence and native eligibility are rechecked after a reader hook; state changes stop output. Official results retain the strict claims and exact citations. No native CLI or browser default is changed.

Native unofficial indexing is capped at2048 paragraphs/1,000,000 canonical characters; displayed passages are separately bounded. Truncation is explicit, and never proves absence. Ledger citations include exact canonical body coordinates; raw dump citations retain source hashes and byte spans. These exploration bounds do not cap the existing native eligibility scan. Conditions, quotations, reported speech and negation retain warnings. This is source inspection, not general historical reconstruction.

Exploration now traverses eligible sources round-robin and reuses the native1200-character wrapped-line context units, preserving exact canonical slices and incomplete-context labels. This prevents an early long source from consuming the whole discovery index. It changes no strict proof slots or grammar.
