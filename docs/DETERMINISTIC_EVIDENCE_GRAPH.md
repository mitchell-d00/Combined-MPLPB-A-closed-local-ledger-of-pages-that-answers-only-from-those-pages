# Deterministic source-evidence graph and synthetic users — proposed 2026-11-01

The original strict pottery **6/59 (10.2%)** is a dated historical result, retained unchanged in `evaluation/practical-coverage/after.json`. The previous deterministic graph candidate recorded **12/59 (20.3%)** on the already-inspected development question sets, as separately pinned in the evaluation report. This expanded cross-domain smoke-test candidate requires its own exact-head validation; new generated questions do not change that historical score or constitute independent language accuracy. All three pottery probe JSON files, SHA-256 sidecars, studio pages, old PDFs, and prior reports remain frozen.

## Why another graph?

MPLPB already has a **chat-command language graph** (`resources/chat_language_graph.json` / `tools/chat_language_graph.py`) and **user-declared conversation graph** (`tools/conversation_router.py`). Neither certifies source-body facts. The new `mplpb_answers.relation_graph` is a *separate* and deliberately bounded **question–predicate–entity–source statement–value–qualification** proof graph. It makes a return inspectable, instead of relying on a page's topical relevance.

A proof path is:

```text
question --asks--> typed relation --targets--> requested entity
source page (record ID + intact hash) --declares--> exact body statement
body statement --asserts_relation--> typed relation
body statement --asserts_subject--> requested entity
body statement --supplies_value--> extracted phrase
body statement --qualified_by--> retained exception, condition, or contrast
```

**The directed edges do not authorize reverse causality, cross-page completion, synonym guessing, medical guidance, or multi-hop inference.** Graph nodes are derived at query time, from *eligible* source bytes, and must not be stored as independently ratified ledger facts. Any statement on a retired, corrupt, excluded, not-for, withheld, or otherwise ineligible page is not an answer. Multiple matching eligible pages remain ambiguous even if their values agree.

## Fourteen generic relation families

| Question family | Permitted body assertion | Result |
| --- | --- | --- |
| What is (bag) code CODE for? | `Bag code CODE is for PURPOSE` or `NAME, CODE, is for PURPOSE` | Whole quotation; no code-ID lookup table |
| How much MATERIAL? | `Add NUMBER UNIT of MATERIAL …`, optionally after an exact stated condition | Entire sentence, including any conditions; never a stripped dosage |
| How long should I ACTION MATERIAL before NEXT-ACTION? | `Leave MATERIAL to ACTION for DURATION before NEXT-ACTION` | Exact entity, verb, next action and original quote |
| What causes SYMPTOM? | `SYMPTOM comes from CAUSE` / `is caused by CAUSE` | Source-declared cause; not independently verified diagnosis |
| ALTERNATIVE-A or ALTERNATIVE-B? | `A for CONTEXT-1, B for CONTEXT-2` | Verbatim comparison, without selecting an unsupported winner |
| How do I check ITEM with TOOL? | `ITEM should …: METHOD with TOOL to check` | Exact inspection sentence, including qualification |
| How long does SUBJECT need? | `SUBJECT needs DURATION[, not CONTRAST]` | Duration plus complete contrast |

Seven further relations use equally bounded source-declared evidence: storage instructions, named responsibilities, due dates, recorded statuses, locations, explicit contents, and scheduled dates. Their precise question and source grammars, positive/negative controls, and the Mitchell-Tech-style fixed-seed benchmark are documented in the [diverse-language smoke protocol](../evaluation/relation-graph/DIVERSE_SMOKE.md). These are **14 finite graph forms**, not all of English. Previous explicit *if-condition → outcome* and *separate items → containers* forms remain in `operational_evidence.py`. A source quote is a record of what a source declares, not evidence of real-world truth or an instruction that is safe for immediate execution. There is no unrestricted composition; answering "What caused X?" from merely co-occurring symptoms is still forbidden.

The [pinned development retest](../evaluation/relation-graph/README.md) reports 12/59 correct-document returns on the inspected pottery questions, versus the preserved historical 6/59, without changing the original JSON or question files. Both the bounded 36-turn synthetic result and the exact returned source statements are recorded there; semantic accuracy outside these reviewed development examples remains unmeasured.

## Synthetic users and measurement boundaries

`evaluation/relation-graph/synthetic-users.json` defines **six authored personas and 36 scripted queries** across a pottery apprentice, archivist, laboratory assistant, warehouse clerk, plant operator and duplicate-source reviewer. Each starts with an isolated, newly sealed local corpus; turns ask both answerable and absent/negated near-misses. The reviewer asks about two identical but independently eligible pages: the expected result is **ambiguous**, not a top-ranked success. Synthetic users are **software regression agents, not actual people or independent participants**.

The separate [12-domain generated benchmark](../evaluation/relation-graph/DIVERSE_SMOKE.md) is derived from fictional, authored seed data, with globally unique questions, stable IDs, mutant source rechecks and duplicate-source ambiguity. It is not independent testing or a replacement for the six scripted users.

`tools.simulate_relation_graph_users` runs all turns through the same public `supported_answer` path as real users, reports exact returned text and record pins, distinguishes wrong returns, false refusals and ambiguities, and records both fixture and code SHA-256 pins. Its oracle is authored and literal; a passing 36-turn run is not semantic accuracy validation.

`tools.evaluate_relation_graph` independently **replays the unchanged historical question files** using the current code and compares them with the October 31 snapshot. It reports every changed result and both per-set metrics, without modifying the old report. Existing tests also query unchanged studio pages for bag-code use, additive amount, crawling cause and sculpture drying duration, plus both operational relations. Document identity is only a correctness proxy: review every newly returned complete statement against the actual question before announcing a new score.

## Reproduce (branch checkout)

```sh
python -m unittest tests.test_relation_graph tests.test_relation_graph_synthetic_users tests.test_operational_evidence -v
python -m tools.simulate_relation_graph_users --output /tmp/mplpb-synthetic-users.json
python -m unittest tests.test_relation_graph_generated -v
python -m tools.benchmark_relation_graph --output /tmp/mplpb-diverse-benchmark.json
python -m tools.evaluate_relation_graph --output /tmp/mplpb-graph-retest.json
python -m unittest discover -s tests -t . -q
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
```

Required PR checks include the extracted-ZIP, actual WebAssembly and real browser workflows. These are separate from a post-merge deployed site check. Do not merge a failed candidate, overwrite `evaluation/practical-coverage/after.json`, claim new independent human measurements, or silently replace historical text. No test has been declared successful here until the exact-head GitHub run finishes.

## What still needs new language and relation engineering?

A deterministic graph can improve *inspectability and bounded recall*, but most of the original answerable cases are not instantly solved by adding a node type. The frozen probe labels are page-ownership proxies, and some questions are too underspecified for source-supported factual answers (e.g., kiln-room ambient temperature versus firing temperature; warm gloves without measured temperature; a yesterday-specific recycle decision without time-qualified source text). Other cases require reviewed alias rules, evidence-aware anaphora, scoped processes, comparative queries, situation-to-recommendation semantics, cross-sentence qualification propagation, source truth adjudication, or a distinct model-assisted channel. **Never reduce these to loose lexical overlap.**

The product progression should be: (1) single-sentence proof paths; (2) testable phrase variants tied to explicit predicates, not uncontrolled synonyms; (3) document-local anaphora with retained ambiguity when multiple antecedents are possible; (4) explicit machine-readable procedure graphs with prerequisites/conditions; (5) carefully reviewed temporal and causal edges; and (6) independently authored, human-scored cross-domain evaluation and calibration before calling it general-quality.

Related: [operational-relation error classes](OPERATIONAL_EVIDENCE.md), [existing chat graph](CHAT_LANGUAGE_GRAPH.md), [conversation router](CONVERSATION_ARCHITECTURE.md), [policy relations](USER_BUILT_COLLECTIONS.md), [evaluation protocol](../evaluation/README.md), [historical pottery coverage](../evaluation/practical-coverage/README.md).
