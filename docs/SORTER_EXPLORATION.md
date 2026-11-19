# Sorter labels and unofficial idea exploration

Last reviewed: 2026-11-19.

The sorter supplies inspectable observations and possible connections. Its optional exploration view accepts free-form questions and can propose interpretations through a local model. Those interpretations are **not established facts, native MPLPB-supported answers or historical truth**. The strict reader, sorter v1/v2 formats and classing decisions remain unchanged.

## Sort with readable labels

```bash
python -m mplpb_work.sorter_explorer sort SOURCE_DIRECTORY --mode not-compared
python -m mplpb_work.sorter_explorer sort SOURCE_DIRECTORY --mode compare --json
```

Both modes use the existing v2 extraction. Their sources, nodes, exact character/byte spans, hashes, provisional assessments and node labels are identical. Compare may add review edges and their labels. An embedded source graph stays byte-for-byte replayable by `sorter_v2.verify_graph`; labels live in a separate `sorter-exploration-view-v1` envelope. The original graph is never rewritten. The derived view is bounded to64MiB and retains the sorter's completeness/limit report.

| Label | Meaning | What it does not establish |
|---|---|---|
| Textual observation | A keyed item or containment exists in the source text | An event happened |
| Exact source text checked | Local bytes and source span replay successfully | The source is truthful or the relationship is correct |
| Possible connection | Existing comparison suggests a reviewable link | A supported relationship |
| Possible document identity | Primary declared identifiers match; appearances stay separate | Same event, independent corroboration or resolved people |
| Entity mention / resolution not established | A name/header/identifier is observable | A resolved historical actor |
| Same historical event not established | No event co-reference proof has been awarded | An event merge |
| Possible correction | Wording may refer to a correction | Supersession, retirement or ledger write permission |
| Changed bodies | Matching identifiers have different body hashes | Which version is right |
| Missing or ambiguous link | Reference is unresolved and the chain stops | A guessed intermediate hop |
| Source says current/retired | Provisional source wording | Current ledger serving eligibility |
| Historical truth not independently verified | No independent truth finding is established | An accuracy score or an authenticity claim |

`node_labels` and `edge_labels` key back to original item IDs. Each includes separate source-integrity, quotation-fidelity, support-scope, serving-eligibility and false authority flags. Never flatten “exact source text checked” into “supported.” The full graph retains prior assessments; these are not authenticated independent reviews.

The offline `sort` command inspects explicitly selected local files, with serving policy **not evaluated**. It grants no delivery profile or import authority. Use the gated question path below to consult a ledger; do not export an offline inspection as externally eligible evidence.

## Ask an unofficial free-form question

```bash
# Offline/extractive: no model, no network calls.
python -m mplpb_work.sorter_explorer ask \
  'What possible connections and disagreements deserve investigation?' \
  --dump examples/fixpack_classing/demo_dump

# Consult currently eligible native material, retaining its separate strict decision.
python -m mplpb_work.sorter_explorer ask \
  'Could these accounts describe the same event, and what evidence is missing?' \
  --ledger LEDGER --dump SOURCE_DIRECTORY --profile internal --json

# Optional model-assisted hypotheses; reuse existing local backend configuration.
MPLPB_NARRATOR_BACKEND=ollama MPLPB_NARRATOR_MODEL=phi3:mini \
MPLPB_NARRATOR_BASE_URL=http://127.0.0.1:11434 \
python -m mplpb_work.sorter_explorer ask \
  'What might explain the different accounts?' --ledger LEDGER --model
```

Ollama, llama.cpp and local OpenAI-compatible servers reuse the existing bounded `LocalBackend`. See [local narrator configuration](LOCAL_NARRATOR.md). The strict narrator remains formatting-only; this explicitly separate research tool permits unverified hypotheses. It does not loosen the narrator or native proof rules. A local OpenAI-compatible endpoint cannot itself attest that its operator disabled remote forwarding.

Without `--model`, output is a source inspection packet, not generated reasoning. With `--model`, the only generated segment types are:

* **Hypothesis — model interpretation, not an established fact.** Requires valid passage references and proposed missing evidence. Entity matches, event co-reference, causes and corrections remain unverified.
* **Open research question — unanswered.** May lack citations, and therefore establishes nothing.
* **Source quotation — exact words, not verified meaning.** Must reproduce one complete cited passage; dropping a negation or qualification is rejected.

Every segment remains `answer_supported: false`, `source_support_established: false`, with identity and historical-truth flags false. The top-level exploration flags also remain false. The native result is kept separately in `native_mplpb.result`; only the existing strict checker can supply supported claims there. A native refusal or conflict is never replaced by an idea. A native supported answer is labeled source support checked, not historical truth verified. Checked partial native claims retain their original qualifications.

The prompt distinguishes document identity from event identity, document/event dates, conditions, attribution, reported instructions and completed execution. The validator checks schema, bounded output, reference IDs and complete quotations. **It does not establish the semantic accuracy of hypotheses**, even when their citations match. A model can propose a misleading interpretation; all such proposals remain labeled, with the original cited contexts and their warnings visible. Never display just a segment's text while hiding its label, citations, warnings or unresolved status. Proposed missing-evidence notes are also model interpretations.

## Eligibility, bounds and failure behavior

The original full question and profile gate apply to native and known classed source material. Restricted and question-excluded native bodies do not enter the model prompt. External delivery never reads raw dump files. Internal/lab withdrawn raw-source inspection retains the existing router warnings and cannot supply strict proof. Source/hash/policy changes during generation discard the result. There is no ledger writer, classing approval, support promotion, automatic event merge or model tool-call capability in this module.

Discovery has its own8-passage/12000-character display budget and the router's existing2048-context/1,000,000-character index bounds. It consumes zero strict proof slots. Sorter limits remain visible even when no passage matches, and `search_complete` remains false. Search limitations and incomplete contexts remain visible; absence from a bounded result does not prove absence from history. Model input is capped at24000 UTF-8 bytes, output at1200 tokens/16000 bytes,8 segments,1600 characters per segment,8 references and8 missing-evidence notes per segment. Backend timeout uses the existing bounded local configuration. Invalid responses, fabricated quotes/citations, promotion fields and endpoint failures fall back to complete source excerpts. No local model is required.

Tests:

```bash
python -m unittest -q tests.test_sorter_explorer
python -m unittest -q tests.test_sorter tests.test_sorter_v2 tests.test_answer_router_boundaries tests.test_local_narrator
```

These are software boundary tests, including mocked interpretations. They are not a live-model semantic evaluation, a historical truth test, or evidence of increased complete-answer coverage. Earlier frozen measurements remain unchanged. [Versioned execution record](../evaluation/sorter-exploration/2026-11-19/FINAL_REPORT.md) records the checks actually run for this update.

To reuse the original graph with existing tools, take `view["source_graph"]` and re-run `sorter_v2.verify_graph(graph, directory)`. The label envelope and any generated hypothesis are not ledger pages, accepted evidence, or import approval.
