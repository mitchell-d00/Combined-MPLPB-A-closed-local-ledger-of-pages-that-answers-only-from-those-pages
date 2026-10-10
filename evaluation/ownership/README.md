# Adversarial semantic ownership evaluation

Run from the repository root:

```sh
python -m tools.evaluate_ownership
```

The frozen `rag-input.jsonl` contains **240 cases: 12 families × 20 entity
substitutions**. It is developer-authored synthetic material, not 240 independent
human questions. Only 12 failure patterns are represented. Each isolated corpus
contains one page, or two for conflicting sources; it does not measure large-corpus
ranking, latency or realistic traffic. Labels ask whether a page establishes the
requested fact, rather than whether it satisfies the implementation's word rule.
The input SHA-256 is recorded with the results. Do not edit labels after seeing
results to make a system pass. Review disputed labels separately and version changes.

Families: supported fact, missing attribute, wrong entity, stuffed scope, false
premise, wrong time, reversed relation, unsupported cause, scattered vocabulary,
synonym question, conflicting pages, and instruction decoy. The instruction case
measures false ownership, not execution of an injection. This suite does not cover
all integrity/profile/pointer attacks; retain the existing regression suite too.

## Measured result

| System | Wrong owner / all cases | Return precision | Return coverage |
|---|---:|---:|---:|
| MPLPB internal reader | 180/240 (75.0%) | 40/220 (18.2%) | 220/240 (91.7%) |
| BM25 top-one, current pages | 200/240 (83.3%) | 40/240 (16.7%) | 240/240 (100%) |
| TF-IDF top-one, current pages | 200/240 (83.3%) | 40/240 (16.7%) | 240/240 (100%) |

These are stress-test rates, not production accuracy estimates. The ledger correctly
refuses a unique answer for the 20 conflicting-page cases, but returns owners for
all nine unsupported families. Neither lexical baseline has an ambiguity policy
or a tuned abstention threshold. This is not a fair end-to-end RAG superiority claim.
The output contains every decision and family breakdown; failures are retained.

Wrong ownership means returning a page when no supported unique owner is labeled,
or returning the wrong page. Precision conditions on returns; coverage alone is
not success. Refusal on an answerable case is counted separately. No claims about
truth of generated answers, statistical independence, or calibrated confidence
follow from these measurements.

## Modern RAG comparison protocol — not yet measured

The measured baselines above are retrieval-only. No modern RAG model was run in
this release, and no RAG score is invented. A model runtime/endpoint and pinned
model revisions are required. Use at least these three configured arms:

1. BM25 + generator, with an explicit abstain/ambiguity output contract.
2. Dense retrieval + the same generator and token budget.
3. Hybrid retrieval + reranker + the same generator and token budget.

Pin embeddings, chunking, top-k, reranker, generation prompt, model revision,
decoding settings, corpus hash and software versions. Select thresholds on a
separate development set. Evaluate frozen test cases once, with no network lookup
or corpus expansion. Run both the same eligible corpus comparison and a separately
labeled ungated comparison; never conflate eligibility controls with retrieval quality.
For this tiny-corpus set, give every arm the full corpus as an additional oracle
context arm so reader support failures are not confused with retrieval failures.

Export JSON with `system`, `model_revision`, `retriever`, `prompt_sha256`,
`input_sha256`, and `predictions`. Each prediction has `id`, `kind` (`return`,
`ambiguous`, `not_in_corpus`), and `source_ids` (one id for a unique return, otherwise
empty). Keep generated text, full ranked ids, latency and token counts in a separate
trace. Missing/duplicate cases are errors, never dropped from denominators.

```sh
python -m tools.compare_ownership_predictions model-predictions.json
```

This scorer compares source decisions only. Independently score answer correctness,
claim support and citation precision with blinded human annotation; report judge
model configuration and disagreements if using an LLM judge. Also report Recall@k,
nDCG@k on a genuinely larger corpus, abstention/coverage curves, p50/p95 latency,
and per-query cost. Bootstrap by scenario family, not duplicated entity names.
Do not report significance from this 12-family diagnostic alone.

Next external evaluation: have separate authors contribute unfamiliar corpora and
questions, two annotators mark evidence spans and ambiguity, and an adjudicator
resolve disagreements. Freeze before tuning; disclose author overlap. No independent
human testers have been recruited or represented as having tested this release.

Method references (consulted 2026-10-10):
- [BEIR](https://github.com/beir-cellar/beir): retrieval evaluation across datasets;
  it does not by itself evaluate generated-answer support.
- [Ragas metrics](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/):
  separates context and generation metrics; automated scores need validation.
