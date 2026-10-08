# Multi-domain evaluation

Run `python3 -m mplpb_combined.evaluate evaluation/manifest.json --out evaluation/results.json`.
This freezes 36 synthetic developer-authored probes across software operations,
library services, and office procedures. Corpus, question, and label authors are
all Codex. These fixtures are regression evidence, **not independent validation**.
No parameters or exclusions were adjusted after seeing their results.

The manifest embeds each corpus and pins probe bytes with SHA-256. Every return
label includes a verbatim evidence span; refusals include a rationale. This
checks label structure, not the truth or sufficiency of a human judgment.
Results include every probe, expected outcome, prediction, corpus hashes,
accuracy, return precision, and return rate. Read errors, missing files, and
changed probe hashes fail the run rather than silently changing the benchmark.

## Baselines

All methods share the ledger tokenizer (including its stopwords and stemmer).
Overlap returns the document sharing the most distinct query words. BM25 uses
term frequency, document length, and inverse document frequency with fixed
k1=1.2 and b=0.75. TF-IDF uses raw term frequency, smoothed IDF
`1 + log((N+1)/(df+1))`, and cosine similarity. Ties use path order. Baselines
refuse only zero overlap; no rejection threshold is tuned on the test set.

Each baseline runs on stripped prose, including retired pages, and separately
on valid current non-pointer pages. The latter isolates matching from metadata
filtering. The synthetic corpora contain no retired pages, so both pools match.
The existing pottery kill tests exercise the difference:

```
python3 -m mplpb_combined killtest examples/studio killtest/probes.json
python3 -m mplpb_combined killtest examples/studio killtest/probes_heldout.json
python3 -m mplpb_combined killtest examples/studio killtest/probes_adjacent.json
```

Their JSON now includes `lexical_baselines` and per-probe `lexical_rows`.
Historical results remain untouched. Top-one methods cannot express ambiguity;
report ambiguity separately and compare return and out-of-corpus questions
separately. Aggregate accuracy alone is insufficient. This is lexical retrieval,
not a semantic or neural baseline.

## Independent evaluation protocol

1. Freeze the code revision and ranking parameters before acquiring test queries.
2. Recruit corpus owners in at least three real domains. They provide local
   page corpora and consent to the evaluation. Record owner identities or stable
   pseudonyms and the corpus version. Keep sensitive corpora private.
3. Have a different group write realistic questions without seeing scope fields,
   exclusions, ranking results, or these fixtures. Include answerable, ambiguous,
   adjacent-topic, paraphrased, negated, and genuinely absent questions.
4. Have two reviewers label each question against page bodies, blinded to method
   output. Require evidence spans for returns and rationales for refusals;
   record disagreements and their adjudication. Include candidate IDs for
   ambiguity in the reviewer record. A third reviewer resolves disagreements.
5. Hash probes and corpora before execution. Register the manifest, commit,
   identities/roles, exclusions, domain sampling, and intended metrics. Separate
   development/calibration questions from untouched final-test questions.
6. Use the manifest format here. For real corpora, replace `pages` with a `root`
   path relative to the manifest. `probes` and `sha256` refer to the frozen
   question file. Record authors, reviewers, adjudicators, dates, and conflicts
   under `provenance`; declarations alone are not verified by this program.
7. Run once and publish all failures alongside per-domain and per-outcome
   counts, return precision, coverage, and paired uncertainty estimates. Obtain
   a separate review of code execution, provenance, and scoring. Changes after
   test inspection require a new untouched test set before another final claim.

External recruitment, labeling, and independent audit are pending. The runner
always reports `independence_verified: false`; a declaration in a manifest
cannot turn developer fixtures into independent evidence.

## Status authority change

Only successors with intact required fields, a unique ID, recognized origin,
numeric depth consistent with lineage, and an acyclic valid dependency graph
may retire a predecessor implicitly. References must pin the unique target's
actual hash. Invalid successors cannot determine another page's status.
Valid retired successors retain supersession authority, so withdrawal does
not resurrect old versions. An explicit predecessor status of `retired` stays
retired even if its successor is damaged; the reader does not undo withdrawals.

Unpinned legacy references do not provide implicit retirement authority until
`seal` pins them. Other validator findings remain visible; this patch does not
change every serving rule into a strict whole-corpus validation gate.
