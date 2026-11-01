# MT-style diverse-language smoke test for the deterministic evidence graph

**Scope:** Proposed developer-authored benchmark, not human fluency or real-world truth measurement. Historical pottery **6/59 (10.2%)** remains unchanged. The separately pinned graph candidate measured **12/59 (20.3%)** on already-inspected pottery development questions.

## Adaptation of Mitchell-Tech V120.2 testing

Mitchell-Tech's [testing contract](https://github.com/mitchell-d00/Mitchell-Tech-V120.2-A-self-teaching-scientific-and-graphing-calculator-/blob/main/TESTING.md) and [unique-benchmarks.cjs](https://github.com/mitchell-d00/Mitchell-Tech-V120.2-A-self-teaching-scientific-and-graphing-calculator-/blob/main/tests/unique-benchmarks.cjs) use a **fixed seed, global deduplication, stable IDs, expected-versus-actual reports, category failures and nonzero exit codes**. Its separate Chromium tests exercise delivery rather than confusing engine tests with browser verification.

For MPLPB, correctness additionally requires an **eligible source ID, intact hash, complete literal quotation and a licensed typed relation**. Refusals, contradictions and competing eligible owners have their own expectations. Generated tests are not independent users or a semantic accuracy certification.

## Expanded evidence graph

The seven existing graph families (code purpose, amounts, action duration, cause, required duration, alternatives, inspection) gain seven more cross-domain families. Each query has a bounded grammar, a licensed body sentence and refusal on missing or inconsistent evidence.

| Relationship | User questions | Required body declaration |
| --- | --- | --- |
| Storage | Where should we store X? Where do I keep X? Where should X be stored? | Store X in Y. / Keep X in Y. |
| Responsibility | Who is responsible for X? Who has responsibility for X? | PERSON is responsible for X. |
| Due date | When is X due? What date is X due? What is the due date for X? | The X is due on YYYY-MM-DD. / The due date for X is YYYY-MM-DD. |
| Recorded status | What is the status of X? What status is recorded for X? | Status of X is VALUE. / X has status VALUE. |
| Location | Where is X located? | The X is located in PLACE. |
| Contents | What does X contain? | The X contains EXPLICIT ITEMS. |
| Scheduled date | When is X scheduled? | The X is scheduled for YYYY-MM-DD. |

Dates must be real ISO calendar dates. Status means **status declared in the particular page**, not live status. Complete quotes preserve qualifications. This graph is neither a general synonym engine nor factual verification; it has no multi-hop inference or implied procedure execution.

## Fixed-seed, globally unique synthetic smoke test

[The seed fixture](diverse-smoke-seeds.json) has **12 fictional domains**: archive, library, software, orchard, freight rail, theater, museum, research, festival, animation studio, aquarium, and community services. Each domain has seven sealed body assertions, an invalid-date trap, positive variations and near-miss negatives.

The runner (tools/benchmark_relation_graph.py) uses seed **20261101**, globally deduplicates normalized questions, and records stable IDs beginning MPLPB-SM-000001. The generated plan contains **276 unique questions: 168 expected supported returns and 108 expected refusals**, plus **24 separately counted metamorphic checks** for changed source values and two-owner ambiguity. These figures describe the planned fixture, **not a passing result**; CI owns actual evaluated outcomes and failure rows.

Questions go through the real public strict supported_answer path on temporary sealed ledger corpora, not a substitute regex unit. A positive passes only if document ID, literal quote and graph contract match the separate authored oracle. Negative tests cover extra conditions, time modifiers, incorrect subjects, absent records, negated responsibilities and invalid calendar dates. Two eligible source pages remain ambiguous even if their contents agree. A source-value change must change the returned quote.

## Reproduce

Run from an exact checkout:

    python -m unittest tests.test_relation_graph_generated -v
    python -m tools.benchmark_relation_graph --output /tmp/mplpb-diverse-benchmark.json
    python -m unittest tests.test_relation_graph tests.test_relation_graph_synthetic_users -v
    python -m tools.simulate_relation_graph_users --output /tmp/mplpb-scripted-users.json
    python -m tools.evaluate_relation_graph --output /tmp/mplpb-frozen-retest.json

The PR CI uploads diverse-benchmark.json, synthetic-users.json and frozen-retest.json as a separate test artifact. Full Python, extracted-ZIP and actual browser/WebAssembly execution require their own final green checks. **Do not overwrite original results or claim that synthetic passing numbers demonstrate human-language accuracy.**

Related: [source graph architecture](../../docs/DETERMINISTIC_EVIDENCE_GRAPH.md), [frozen pottery development retest](README.md) and [historical 6/59](../practical-coverage/README.md).
