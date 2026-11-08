# Results and their tests

Last reviewed: 2026-11-08.

Every retained evaluation family is listed below. The [machine-readable index](results.json)
is checked in CI for missing test files, reproduction tools and unindexed evaluation
directories. The [current status](CURRENT_STATUS_2026-11-08.md) separates published
measurements from this update's checks.

Tests protect behavior under their assertions. A file link does not certify a
historical score or supply missing independent human review. To reproduce an old
number exactly, use its report's source revision, corpus, profile, inputs and
runtime. Some old wiki observations remain unscorable because required capture
pins are missing. Original papers and their reported experiments remain archival;
modern application tests do not retrospectively validate those experiments.

| Family / retained artifacts | Regression tests | Reproduction tools | Scope / limits |
|---|---|---|---|
| [language-audit](../evaluation/language-audit) | [test_assertion_polarity.py](../tests/test_assertion_polarity.py); [test_relation_graph.py](../tests/test_relation_graph.py); [test_literal_evidence.py](../tests/test_literal_evidence.py); [test_answer_support.py](../tests/test_answer_support.py) | [evaluate_answer_reliability.py](../tools/evaluate_answer_reliability.py); [evaluate_language_audit.py](../tools/evaluate_language_audit.py); [trace_language_audit.py](../tools/trace_language_audit.py) | Inspected pottery labels and synthetic development data; document identity is not completeness. |
| [procedure-recovery](../evaluation/procedure-recovery) | [test_procedure_recovery.py](../tests/test_procedure_recovery.py); [test_procedure_constraints.py](../tests/test_procedure_constraints.py); [test_exploration_store.py](../tests/test_exploration_store.py) | [evaluate_procedure_recovery.py](../tools/evaluate_procedure_recovery.py); [browser_procedure_recovery.py](../tools/browser_procedure_recovery.py) | Authored linear procedures and synthetic recovery; not arbitrary prose or human execution validation. |
| [reference-corpus-reproduction](../evaluation/reference-corpus-reproduction) | [test_reference_corpus.py](../tests/test_reference_corpus.py); [test_reference_evidence.py](../tests/test_reference_evidence.py) | [build_reference_corpus.py](../tools/build_reference_corpus.py); [verify_reference_evidence.py](../tools/verify_reference_evidence.py) | 73 authored positives and 20 controls, four sealed corpus stages; lab-only unratified data, not learning. |
| [relation-graph](../evaluation/relation-graph) | [test_relation_graph.py](../tests/test_relation_graph.py); [test_relation_graph_generated.py](../tests/test_relation_graph_generated.py); [test_relation_graph_synthetic_users.py](../tests/test_relation_graph_synthetic_users.py) | [benchmark_relation_graph.py](../tools/benchmark_relation_graph.py); [simulate_relation_graph_users.py](../tools/simulate_relation_graph_users.py); [evaluate_relation_graph.py](../tools/evaluate_relation_graph.py) | Inspected pottery document-identity proxy and scripted synthetic users; original reports preserved. |
| [practical-coverage](../evaluation/practical-coverage) | [test_practical_evidence.py](../tests/test_practical_evidence.py); [test_operational_evidence.py](../tests/test_operational_evidence.py) | [evaluate_practical_coverage.py](../tools/evaluate_practical_coverage.py) | Historical intermediate reader coverage; use pinned revision for exact historical outcomes. |
| [reliability](../evaluation/reliability) | [test_answer_reliability.py](../tests/test_answer_reliability.py); [test_literal_evidence.py](../tests/test_literal_evidence.py); [test_answer_support.py](../tests/test_answer_support.py); [test_procedure_constraints.py](../tests/test_procedure_constraints.py) | [evaluate_answer_reliability.py](../tools/evaluate_answer_reliability.py); [evaluate_chat_modes.py](../tools/evaluate_chat_modes.py) | Historical strict-reader and chat-mode comparisons; synthetic free chat is not factual accuracy. |
| [ownership](../evaluation/ownership) | [test_ownership_adversarial.py](../tests/test_ownership_adversarial.py) | [evaluate_ownership.py](../tools/evaluate_ownership.py); [compare_ownership_predictions.py](../tools/compare_ownership_predictions.py) | Historical ownership comparison, bounded adversaries; later tests do not recertify old predictions. |
| [researcher-pilot](../evaluation/researcher-pilot) | [test_researcher_pilot.py](../tests/test_researcher_pilot.py) | [evaluate_researcher_pilot.py](../tools/evaluate_researcher_pilot.py); [browser_researcher_pilot.py](../tools/browser_researcher_pilot.py) | Six authored fictional workflows; no independent human usability validation. |
| [general-reader](../evaluation/general-reader) | [test_general_answers.py](../tests/test_general_answers.py); [test_general_evaluation.py](../tests/test_general_evaluation.py); [test_local_reader.py](../tests/test_local_reader.py); [test_release_answer_contract.py](../tests/test_release_answer_contract.py) | [evaluate_general_answers.py](../tools/evaluate_general_answers.py) | Evaluation machinery and protocol; no achieved live-model general-quality release claim. |
| [contextual](../evaluation/contextual) | [test_context_evaluation.py](../tests/test_context_evaluation.py); [test_grounded_chat.py](../tests/test_grounded_chat.py) | [evaluate_grounded_chat.py](../tools/evaluate_grounded_chat.py); [benchmark_grounded_chat.py](../tools/benchmark_grounded_chat.py) | Synthetic conversational context and historical metrics; contextual state is not source authority. |
| [conversation](../evaluation/conversation) | [test_conversation_router.py](../tests/test_conversation_router.py); [test_chat_matrix.py](../tests/test_chat_matrix.py) | [evaluate_conversation.py](../tools/evaluate_conversation.py); [evaluate_context_matrix.py](../tools/evaluate_context_matrix.py); [smoke_conversation_architecture.py](../tools/smoke_conversation_architecture.py) | Scripted finite conversation fixtures; exact old metrics require original revision/configuration. |
| [conversation-repairs](../evaluation/conversation-repairs) | [test_conversation_repairs.py](../tests/test_conversation_repairs.py) | [evaluate_conversation_repairs.py](../tools/evaluate_conversation_repairs.py) | Developer-authored conversation regression examples, not independent users. |
| [live-conversation](../evaluation/live-conversation) | [test_browser_bridge.py](../tests/test_browser_bridge.py); [test_live_acquisition.py](../tests/test_live_acquisition.py) | [live_conversation_wasm.mjs](../tools/live_conversation_wasm.mjs); [summarize_live_conversation.py](../tools/summarize_live_conversation.py) | Retained WebAssembly/live transport experiment; networking and deployed revision are run-specific. |
| [response-1000](../evaluation/response-1000) | [test_response_edge_smoke.py](../tests/test_response_edge_smoke.py) | [evaluate_response_1000.py](../tools/evaluate_response_1000.py) | Authored finite response edge smoke; not independent language accuracy. |
| [specialist-continuity](../evaluation/specialist-continuity) | [test_specialist_continuity.py](../tests/test_specialist_continuity.py) | [demo_specialist_continuity.py](../tools/demo_specialist_continuity.py) | Five-instance scripted interruption/recovery fixture; not distributed independent agents. |
| [user-collections](../evaluation/user-collections) | [test_policy_evidence.py](../tests/test_policy_evidence.py); [test_exploration_store.py](../tests/test_exploration_store.py) | [evaluate_user_collections.py](../tools/evaluate_user_collections.py); [browser_collection_policies.py](../tools/browser_collection_policies.py) | Synthetic unfamiliar collections, revisions and policy checks; independent builders outstanding. |
| [wiki](../evaluation/wiki) | [test_wiki_capture.py](../tests/test_wiki_capture.py) | [wiki_live_eval.py](../tools/wiki_live_eval.py) | Historical capture integrity checks; missing payload pins/raw-live mismatch prevent scoring the preserved snapshot. |
| [topics](../evaluation/topics) | [test_answer.py](../tests/test_answer.py) | [build_topic_examples.py](../tools/build_topic_examples.py); [test_topic_examples.py](../tools/test_topic_examples.py) | Authored topic-example source fixtures; no unseen-domain language accuracy claim. |
| [audit-2026-10-21](../evaluation/audit-2026-10-21) | [test_audit_20261021.py](../tests/test_audit_20261021.py) | [evaluate_audit_20261021.py](../tools/evaluate_audit_20261021.py); [browser_audit_20261021.py](../tools/browser_audit_20261021.py) | Dated system audit; live endpoint, browser and corpus configuration require original report context. |
| [documentation-audit](../evaluation/documentation-audit) | [test_documentation_audit.py](../tests/test_documentation_audit.py); [test_handoff.py](../tests/test_handoff.py); [test_self_knowledge.py](../tests/test_self_knowledge.py) | [audit_documentation.py](../tools/audit_documentation.py) | Current documentation inventory and evidence-link checks; structural coverage does not prove historical metrics. |
| [evaluation](../evaluation) | [test_evaluation.py](../tests/test_evaluation.py) | [evaluate.py](../mplpb_combined/evaluate.py) | Original frozen root benchmark results/probes; retain original labels and reader revision. |
| [killtest](../killtest) | [test_answer.py](../tests/test_answer.py); [test_canned_guard.py](../tests/test_canned_guard.py) | [killtest.py](../mplpb_combined/killtest.py) | Original adjudication inputs and outputs preserved; run original revision for exact historical reproduction. |
| [mcp-agent](../evaluation/mcp-agent) | [test_mcp_agent.py](../tests/test_mcp_agent.py) | [check_mcp_client.py](../tools/check_mcp_client.py) | Authored local protocol and recovery; official SDK client, not external AI obedience or human validation. |
| [free-browser-helper](../evaluation/free-browser-helper) | [Python assets](../tests/test_browser_ai_assets.py); [owner corpus](../tests/test_owner_corpus.py); [real-engine helper](../tests/browser-ai-helper.cjs); [loader state/DOM](../tests/browser-model-loader.cjs); [actual GPU negotiation](../tests/browser-webgpu-limits.cjs) | [Chromium](../tools/browser_free_helper.py); [asset builder](../tools/build_ai_assets.py); [corpus preparation](../tools/prepare_owner_corpus.py) | Source workflow and synthetic plans; no live neural/iPad/human validation. |

## Reproduce the currently claimed reference result

```sh
python -m unittest tests.test_reference_corpus tests.test_reference_evidence -v
python -m tools.verify_reference_evidence
python -m tools.build_reference_corpus --output NEW_EMPTY_DIRECTORY
```

The committed 372 rows, stage pages, checksums and original 73-positive/20-control
inputs are under `evaluation/reference-corpus-reproduction/`. Do not overwrite
those snapshots to report a later implementation run. The 73/73 result is authored
lab-profile source coverage; all 20 controls refuse in each stage.

## Check current documentation and release

```sh
python -m tools.audit_documentation --as-of 2026-11-02
python -m unittest tests.test_documentation_audit tests.test_handoff tests.test_self_knowledge -v
python tools/check_repository_infrastructure.py
python tools/build_handoff.py --check
```

Normal PR and extracted-ZIP workflows run the full Python suite, native/JavaScript
interfaces, actual WebAssembly and real Chromium paths. Pages runs a separate
postdeployment smoke. CI results are tied to their commit and run ID; a previous
828-test pass is not a claim that all future revisions have passed.
