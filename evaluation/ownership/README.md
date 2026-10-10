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

## Before/after measured result

The original frozen 240 cases remain unchanged. `baseline-results.json` preserves
pre-fix output; `results.json` adds the gated `supported_reader` arm. The old
`ledger` arm is intentionally retained and still fails; it is lexical retrieval.

| Original 240 cases | Wrong owner | Supported returns | Wrong refusals |
|---|---:|---:|---:|
| Legacy lexical reader | 180 | 40 | 0 |
| New supported-answer path | 0 | 40 | 0 |

Run the expanded, frozen **600-case / 48-family** diagnostic:

```sh
python -m tools.evaluate_ownership --input evaluation/ownership/expanded-input.jsonl --out evaluation/ownership/expanded-results.json
```

| Expanded 600 cases | Wrong owner | Return precision | Answerable cases answered |
|---|---:|---:|---:|
| Legacy lexical reader | 430 (71.7%) | 150/580 (25.9%) | 150/150 |
| New supported-answer path | 0 | 150/150 (100%) | 150/150 (100%) |

The v2 path answers all **150 answerable cases**, with zero false refusals in
this set. Return coverage over *all* cases is 150/600 (25%). The previous v1
path refused 50 answerable cases across five paraphrase families. The fix adds
explicit opening-date, ownership, length, chosen-color, and closure-cause
statement grammars; it does not loosen source eligibility or use scope as evidence.
Negative regression cases check reversed relations, wrong entities, quotations,
instructions, and conflicting values. Imported headings are excluded before
sentence matching so they cannot contaminate the first body sentence.

These cases informed development, including the paraphrase fixes, heading-only
evidence, negated/positive conflicts and invalid port values. This is a development
stress set, not an untouched held-out or independently authored evaluation.
Substitutions within each family are correlated. Unknown grammar still abstains.

The expanded cases include different objects, owners, colors, measurements,
temporal qualifiers, hypothetical/quoted/instructional text, missing attributes,
within-page conflicts, and answerable paraphrases. Neither this suite nor zero
observed false returns establishes safety on arbitrary language or large corpora.
The existing eligibility/hash/profile regression tests remain necessary.

`tools.answer_support` consumes only a selected eligible page's affirmative body
statements under a finite grammar. It excludes the generated heading, requires
an exact requested subject, rejects uncertainty/negation, checks numeric port
bounds and refuses conflicting values. Supported output contains matched spans,
not the whole page. Source truth is still not authenticated. Unknown grammar
abstains. Bare topic lookup remains inspection, explicitly `candidate_only`.

The browser/server query endpoint uses this gate. Use `python -m tools.supported_query
CORPUS "What is ...?"` for the same path in a source checkout. The existing
`mplpb_combined.reader.answer` and installed `mplpb-combined ask` retain their legacy
candidate-retrieval contract; they are **not** semantic-answer APIs. This preserves
sealed archive engine pins and reproducibility of previous evaluations. Do not
use those legacy paths as proof of answer support.

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
