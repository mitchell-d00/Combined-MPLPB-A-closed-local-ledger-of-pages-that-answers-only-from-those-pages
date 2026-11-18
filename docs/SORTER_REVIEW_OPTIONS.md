# Optional sorter review aids

Last reviewed: 2026-11-18.

The offline sorter has an opt-in Synonym Ranker and Candidate Relater. Their label is:

> Sorter suggestions for review. MPLPB has not verified these links or answers.

The existing `mplpb_work.sorter` implementation is unchanged. The adjacent `mplpb_work.sorter_suggestions` entry point delegates exactly to it when neither new option is enabled. Both legacy modes retain their source hashes, nodes, occurrence IDs, annotations and graph hashes. Optional results wrap the original graph rather than changing it.

```sh
python -m mplpb_work.sorter_suggestions sort RAW_DIRECTORY --mode compare --query 'Who received the report?' --synonym-ranker --output NEW_RANKED.json
python -m mplpb_work.sorter_suggestions sort RAW_DIRECTORY --mode compare --query 'Who received the report?' --synonym-ranker --candidate-relater --output NEW_REVIEW.json
python -m mplpb_work.sorter_suggestions peruse NEW_REVIEW.json --sources RAW_DIRECTORY --max-items 8
```

The small built-in vocabulary is inspectable in `mplpb_work/sorter_suggestions.py` and every optional result. Exact query terms and neighbor matches have separate signals. Every signal retains its original phrase, query term, vocabulary group, exact UTF-8 byte/character span and explanation. The rank gives two points per distinct exact query term and one per distinct neighbor-only query term. It is neither confidence nor source authority. All matching statements in the bounded core graph remain in the full results, including negation and qualified wording. Perusal reports omitted display items; extraction or comparison caps remain explicit.

A custom UTF-8 JSON glossary may be supplied with `--glossary glossary.json`:

```json
{"groups":[{"name":"example-search-neighbors","terms":["bank","shore"],"note":"Ambiguous vocabulary for inspection only."}]}
```

Glossaries are bounded to64KiB in the CLI,200 groups and16 literal terms per group. Terms are escaped literal words/phrases, not regular expressions. Multiple senses remain visible through distinct group IDs. A user group cannot replace a built-in group. The normalized glossary is pinned in the result. A neighbor group may include planned sending, dispatch and receipt as different search neighbors; their distinct source wording and qualifications remain intact.

The Candidate Relater reuses the core's exact identifiers, references, occurrence boundaries, source spans and existing review annotations. It can suggest possible references, duplicate appearances, conflicting versions and partial corrections; shared subjects remain shared-subject reviews. Missing/ambiguous targets have no invented endpoint. Shared query words and search neighbors rank inspection hits; they do not create a documentary relationship by themselves. Literal shared wording remains an explicitly textual review. Identity, chronology, causation, completed delivery and applied correction remain unverified. Each link has exact endpoint spans and a reason; contextual statement spans retain qualifications. Candidate identity, chronology, causation and correction remain unresolved. All support/truth flags stay false.

Fresh perusal replays source bytes, vocabulary, scores and links; source drift or forged rankings refuse. Snapshots remain subject to the existing retired export boundary. Neither rank scores, links nor the glossary activate a ledger page or alter ownership, eligibility, supersession, corrections or proof rules.

## Original-record experiment

The [configured sorter-first retest](../evaluation/sorter-first-originals/2026-11-18/REPORT.md) reproduced2 complete answers out of22 directly, then regressed to1/22 with unreserved sorter-first hints. Draft passage coverage fell27/32 to25/32. H02 remained complete; H05 became partial. All original results, questions, sources and exact failure passages are retained.

The first optional-feature experiment compared sorter alone, the ranker and both options under the same unchanged strict reader. Its experimental first-facet discovery reservation did not repair H05. That failed trial remains frozen. Later reader-owned witness admission is a separately versioned implementation experiment; its four arms use one common new reader pin and retain the original22 questions, originals and budgets. Discovery, false/unresolved suggestions and complete answers remain separate.

The22 questions are development data. Unseen originals are reserved for independent evaluation; independent human evaluation is NOT RUN. A quote replay, regression test or candidate similarity is not historical semantic accuracy.


The [first optional-feature trial](../evaluation/sorter-first-originals/2026-11-18-options/REPORT.md) completed66 executions but produced no new complete answer:1/22 in each arm, with draft discovery26/32,26/32 and24/32. Its995 neighbor-only links were too broad. All results and developer-reviewed misleading examples are preserved. Version2 removes neighbor-only relation edges and the experimental adapter stops traversing weak wording/subject reviews. It retains the ranker and explicit source-key/reference review links. The completed conservative v2 trial also retained1/22 complete answers in every arm. Original baseline2/22 and all failed trials remain unchanged.

Reader-owned admission now replaces the experimental first-discovery reservation. [Passage admission](PASSAGE_ADMISSION.md) documents classes, atomic proof witnesses, duplicate charging and counterevidence limits. The verifier remains unchanged; prior failed trials remain preserved. The [final same-reader four-arm rerun](../evaluation/sorter-first-originals/2026-11-18-witness-admission-final/REPORT.md) finishes all88 workers:2/22 complete and27/32 draft spans in every arm. Synonyms and the relater add no complete answer or additional draft anchor here. Candidate semantic precision/recall is not independently measured.
