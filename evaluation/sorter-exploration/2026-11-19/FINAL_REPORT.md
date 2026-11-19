# Sorter labels and unofficial research ideas — final engineering report

2026-11-19. Local branch only; nothing pushed or merged.

Baseline: `6174184edc1b47c7363a6369f7fe40ccb226601a`. Final tested runtime: `f85620548874d4daae608144c33c9c1d4286c622`. Tested source ZIP SHA256: `4d0409287caa42ea8202fc2bcccf57fa0b454d01f8f70190954caf610c0945e2`. The earlier [checkpoint](REPORT.md) and all failed runs remain preserved. Subsequent changes add only documentation, evidence and handoff state; implementation equality is audited.

## Working interface

`mplpb_work/sorter_explorer.py` adds an opt-in CLI/Python view beside the existing sorter and strict reader. It is not a new authority engine.

* Textual observations and exact spans are labeled as text fidelity, not semantic support.
* Possible connections, declared document identity, changed bodies, correction wording and missing links are review proposals. Document occurrences remain distinct.
* Entity resolution and event co-reference are explicitly **not established**. The view does not implement a verified entity/event resolver.
* Source-declared current/retired status remains provisional. Live native serving eligibility is a separate decision.
* Historical truth stays **not independently verified**.
* A native supported result is shown separately as **MPLPB source support checked — not independently verified historical truth**. Its original full contract/citations remain intact; native refusals/conflicts are never overwritten.
* Free-form unofficial questions may yield local-model hypotheses, unanswered research questions or exact source excerpts. Hypotheses require valid passage references and proposed missing evidence. Complete source quotations cannot drop a negation or qualification. The deterministic validator checks schema, IDs, bounded output and quotation fidelity, **not semantic correctness**. A misleading model interpretation can remain a labeled hypothesis; no positive support/identity/truth flag is awarded to it.

All exploration flags remain false. There is no ledger writer, ratification, automatic merging, source rewriting or candidate-to-proof promotion in this module. Existing full-question/profile gates and source-change invalidation apply to question exploration. External questions never read raw dumps. The standalone offline sort view has serving policy not evaluated and grants no delivery permission. Source context warnings, exact paths/hashes/coordinates, model status and missing evidence remain inspectable.

The v1/v2 sorter formats and all 62 pre-existing runtime files are byte unchanged. The new envelope contains a copy of the original replayable graph plus separate `node_labels`/`edge_labels`; it cannot be used as import approval. Neither this view nor generated prose is a ledger page.

## Reproduction

```bash
python -m mplpb_work.sorter_explorer sort SOURCE_DIRECTORY --mode not-compared
python -m mplpb_work.sorter_explorer sort SOURCE_DIRECTORY --mode compare --json
python -m mplpb_work.sorter_explorer ask 'What might connect these records?' --dump SOURCE_DIRECTORY
python -m mplpb_work.sorter_explorer ask 'What remains unresolved?' --ledger LEDGER --dump SOURCE_DIRECTORY --profile internal --json
# Explicitly optional local inference;default is source excerpts with no model.
MPLPB_NARRATOR_BACKEND=ollama MPLPB_NARRATOR_MODEL=phi3:mini MPLPB_NARRATOR_BASE_URL=http://127.0.0.1:11434 \
python -m mplpb_work.sorter_explorer ask 'What alternative explanations deserve investigation?' --dump SOURCE_DIRECTORY --model
```

Ollama, llama.cpp and local OpenAI-compatible servers reuse the existing `LocalBackend`. The existing strict narrator remains formatting-only. Missing/unreachable/invalid model output falls back to source inspection. No network inference is required by default; a generic loopback endpoint cannot attest that its operator disabled forwarding.

Bounds:64MiB labeled graph view;existing sorter input/comparison limits;separate8-passage/12000-character discovery display and2048-context/1,000,000-character index;24000-byte model prompt,1200 output tokens/16000 bytes,8 segments/1600 characters each. Source graphs are freshly replayed. Sorter truncation remains visible even when no passage matches; `search_complete` stays false. No historical absence is established by an empty bounded search. Exploration consumes zero strict proof slots.

## Actual checks and outcomes

| Check | Actual outcome |
|---|---|
| New boundary tests | 15 passed;mocked model proposals never gain support |
| Full extracted source unittest | **1379 passed**,527.963s unittest-reported,exit0 |
| Public evidence with required capabilities | **52/52 passed**,zero observed false-supported bridges in those fictional controls,exit0 |
| JS API/UI/transport/crawler | Final archive commands all exit0 |
| Actual pinned Pyodide/WebAssembly and collection policy | Final archive-built runtime passed,exit0 |
| Fresh Chromium native UI/IndexedDB workflow | Passed on first candidate HTML;final HTML byte-identical,with equivalence audit. New exploration is CLI/Python only. Deployed live site NOT RUN. |
| Installed wheel | Existing workspace and final unofficial CLI passed with isolated `-I` Python,exit0 |
| Historical H05 isolation | Native contract exactly identical before/during/after exploration;still4 citations/4070 characters;zero exploration strict slots |
| Previous sources/evaluations | All 5875 pre-existing evaluation files and 62 runtime files unchanged |

[Full native command receipts](final-software/report.json),[final interface commands](final-interfaces/report.json),[wheel commands](installed-wheel/commands.json),[native H05 replay](H05-native-isolation.json) and [preservation audit](preservation-audit.json) retain exact scope. All prior22-question measurements remain unchanged;the whole22 was not rescored for this labels-only update and no historical coverage gain is claimed.

## Inspectable fixture output

The [reproducible demo helper](demo.py) uses the existing 8 fictional files at `examples/fixpack_classing/demo_dump`. Run it from the frozen extracted checkout:

```bash
python /PATH/TO/THIS/EVIDENCE/demo.py /tmp/NEW-sorter-exploration-demo
```

Both modes retain111 identical nodes and node labels. Not-compared has196 literal observation edges;compare has218 edges,adding22 review proposals. Those22 are **not22 proven historical relationships**. Four full source excerpts answer the example free-form discovery request unofficially. Separate synthetic ledger examples demonstrate a genuine native supported field answer alongside false exploration support flags,and a preserved native refusal.

[Compare view](demo/compare.json),[not-compared view](demo/not-compared.json),[readable labels](demo/compare.txt),[unofficial question output](demo/unofficial-question.txt) and [summary](demo/summary.json) are retained. Every original fixture byte/hash remains unchanged. This is developer-authored software evidence,not authentic historical accuracy.

Demo cost: 0.201392s CPU/0.201435s wall;peak process RSS 24469504bytes;1065 unique source bytes. Total repeated source bytes read is uninstrumented/null. Full regression cost: 511.262s child CPU/529.900s parent wall;maximum child RSS 303226880bytes,not aggregate process-tree memory. Linux x86_64,Python3.12.14,5 reported CPUs;test/interface/model jobs overlapped,so these are observations,not isolated speed claims. Human review/correction time and historical precision/recall remain null.

## Local model smoke — negative utility finding retained

One actual local request used cached hash-pinned Qwen2.5-0.5B-Instruct Q4_K_M with llama.cpp b12521/6f311d7ad,CPU2 threads,4096 context,no GPU,offline server at literal loopback. Weights SHA256:`74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`. This reused the [previously pinned download](../../fixpack/2026-11-18/downloads.json);no model weights/binaries are new repository dependencies.

The response passed structural/reference validation and produced **one open question**,essentially repeating the original question. Its proposed missing-evidence note was copied source wording,not an independently established gap. There was no new useful relationship inference demonstrated. All source-support,entity,event and historical-truth flags remained false. [Actual result](live-model/result.json) and [costs](live-model/summary.json) are preserved;semantic quality has no independent score.

Controller wall 12.523s/CPU 0.885s. Its peak RSS 515661824bytes includes a subsequent full weights-checksum read,so it is **not pure frontend memory cost**. Server lifetime CPU 24.890s/peak RSS 700129280bytes includes loading,idle and inference. The temporary server was stopped normally. A valid JSON response or citation is not proof of interpretation quality.

## Failed attempts and recovery

* Initial relevant-suite invocation:68 passed/2 existing narrator HTTP fixtures errored because the sandbox blocked loopback socket creation. The capability-enabled rerun passed all 70 then present tests. These were infrastructure errors,not silently excluded controls.
* The empty-result truncation regression failed before repair,then passed. The final 15-test module includes that repair.
* First full run367838c executed1378 tests but failed with 310 errors when `/tmp` filled. The repaired f856205 attempt then failed during source extraction with the same ENOSPC error,before its suite ran. [First failure](storage-failure-frozen/report.json) and [extraction failure](storage-failure-repaired/controller.log) remain retained. Neither run counts as passed.
* Cleanup removed only generated,reproducible old archive extractions/ZIP copies and the failed temporary extraction;committed code,original files,fixtures,logs,receipts and evaluation packets were preserved. Approximately9.25GB was available before the successful new-directory rerun. The recovered final run is a separate artifact with all 1379 tests and 52 public controls passing.
* A demo-helper invocation used the wrong working directory,and a subsequent cross-filesystem rename was rejected. The corrected helper run succeeded;generated extra helper files were removed from the frozen extraction. These did not alter any tracked implementation file or frozen input. Logs are retained.

No independent human semantic validation or unseen historical evaluation ran. Existing known historical limitations remain. The live small-model result does not establish general usefulness,entity/event resolution,truth verification or a better complete-answer score.

## Exact regression commands and pins

```bash
python -m tools.reproduce_boundaries --revision f85620548874d4daae608144c33c9c1d4286c622 --output /tmp/mplpb-sorter-exploration-recovery --suite full
# Runner commands execute from that extracted archive:
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/mplpb-sorter-exploration-recovery/public-evidence.json
python -m unittest -q tests.test_sorter_explorer
```

Use new output directories and keep failed runs. Handoff state records latest user wording,actual validation and remaining gaps so another AI instance can resume without this instance's private context. Implementation source is frozen at the revision above;the final evidence-only commit adds receipts and documentation without changing those tested bytes. Nothing has been pushed or merged.
