# Candidate review workspace: source-linked development results — 2026-11-18

The opt-in native/CLI workspace makes processed documents explorable alongside eligible native originals without transferring approval. All22 standalone native results, exact citations and missing-information lists remain unchanged:2 complete,1 partial,3 conflict,16 abstain. H05 remains complete at12 strict passages/8000 characters, using4 witnesses4070 characters. This is preservation, not a new strict-answer coverage gain or22 correct-outcome validation.

Runtime: `e0ff22699a08f1878a1df98563ef1d19d40860fe`. Earlier source pins are `e75a6900eb4a9839aed20ed8bf7d552f32f2b542` (v1) and `7f95338dec32bc860a068f89bb3bc3e5e4ed4946` (v2). Original bytes, corpus/question/scoring seals and older historical studies remain unchanged. The native replay keeps the180-second wall/300-second CPU/2GiB per-question worker limits. The same five workspace executions (H02,H05,H05 tiny exploration,U01,U04), originals, processed graphs, profile and candidate budgets are compared across versions; tiny exploration is separately labeled and is not pooled into ordinary display totals. These questions are development data, not independently blinded questions.

## Workspace behavior

Every processed passage/conclusion is `candidate for review` and “Exploratory · outside MPLPB-approved evidence.” Original endpoints display eligibility under the selected profile with native revision/hash and exact byte/body coordinates. Exact copies do not inherit approval. The existing gate governs hash integrity, lineage, permissions, exclusion, depth, supersession and correction scope. The existing ownership algorithm is reused with an optional restrictive eligible-path intersection; default native callers are unchanged. One owner returns its page and independently checked strict evidence, multiple owners require disambiguation, and no owner retains labeled exploration without returning a supported answer through that route.

The workspace ownership panel and standalone multi-source evidence pipeline remain distinct. The actual H02 workspace asks for disambiguation, and H05 has no legacy single-page owner; these are reported honestly, not scored as loss of the still-complete standalone native answers. A requested owner-policy refusal must not be confused with a strict-proof budget regression.

Exploration has its own exact-span budget (ordinary24 spans/16000 characters), a bounded native original-discovery pool (at most64 passages/64000 characters),256 scanned processed hits by default,4096 pair checks and256 lexical tokens per four-word comparison. Both display and search truncation are visible. Native collection gating/index setup still examines its source collection; receipts measure that cost rather than calling it zero. No candidate or synonym uses a strict proof slot. Unmatched topics, qualified/quoted references and possible corrections retain unresolved status; chronology, identity, causation and correction applicability are not established.

## Measured candidate visibility

| Version | Exact-match review candidates | Wording-review candidates | Processed passages displayed |
|---|---|---|---|
| v1 | 15 | 164 | 28 |
| v2 | 15 | 0 | 44 |
| v3 | 15 | 49 | 39 |

V1's164 wording proposals used a broad three-word overlap rule. A disconnected-statements control reproduced an unwanted link. V2 removed those proposals but failed a new unique-phrase positive because it used the wrong core feature name and required repetition inside processed files. V3 reuses the bounded four-word tokenizer for unique processed/original phrase comparisons as well. It retains all15 exact matches and49 literal phrase reviews, while passing the disconnected-word negative. The28→39 displayed processed passages show increased inspectability under identical budgets, not verified historical reconstruction. V2's44 displayed passages are also retained; its missing phrase positives are not relabeled as success.

All original outputs, full source passages, candidates, unmatched records, qualifications, reviewer-unassessed statuses, costs and fresh-replay receipts are retained in sibling version directories. Literal wording fidelity is not semantic relationship accuracy. Global true/false relationship counts, precision/recall, appropriate-refusal accuracy and22-correct-outcome score are unknown; independent human/unseen-original evaluation is NOT RUN. No generated answer key or synthetic document enters the authentic corpus. Fictional regression fixtures remain separate tests.

## Resources actually measured

| Case | Build CPU seconds | Build wall seconds | Processed logical bytes read (build + replay) | Native-original logical bytes read (build + replay) | Process-lifetime peak RSS bytes |
|---|---|---|---|---|---|
| H02 | 8.138 | 8.160 | 16743612 | 18731236 | 165101568 |
| H05 | 7.316 | 7.341 | 16743612 | 18037852 | 165101568 |
| H05-tiny-exploration | 5.874 | 5.881 | 16743612 | 14339660 | 165101568 |
| U01 | 0.335 | 0.335 | 367572 | 812356 | 165101568 |
| U04 | 0.386 | 0.386 | 367572 | 924604 | 165101568 |

Full per-case receipts separate build from replay CPU/wall time and retain read-call counts. RSS is a process-lifetime high-water mark, not incremental memory attributable to one case. Logical reads include repeated integrity/eligibility checks and are not physical disk traffic. These local runs are not controlled efficiency comparisons. Model/API use was zero; compute price and real human labeling/review/correction/adjudication time remain unknown.

## Executed regression and packaging evidence

All1267 tests passed in389.724 seconds from the actual frozen source ZIP. Separate fictional finite-contract controls passed52/52. All five public workspace cases freshly replayed source bytes, eligibility, ownership and decisions; machine checks confirm exact-span budget charging and false candidate-authority flags. All22 native results are mechanically unchanged from the preserved baseline (`native-comparison.json`), with original-byte source mappings for every returned citation.


An actual installed v2 wheel failed because its byte mapper imported checkout-only `tools`. V3 moves the existing reversible projection into `mplpb_answers/source_projection.py` and preserves the old research-tool interface. The repaired wheel is built from the extracted frozen source and tested under isolated Python (`-I`) in a clean virtual environment; exact matching, strict eligible-source support, non-transfer of approval and fresh replay pass without importing checkout tools. The existing ZIP release workflow adds this installed-wheel gate. Wheel/archive hashes are in `full-regression.json`; no PyPI publication or deployed-site verification is claimed.

Existing legacy tests are not weakened. New controls cover all three owner outcomes, insufficient original body support, processed-only topics, processed contradictions, quoted/conditional corrections, unresolved references, Unicode/entities/negation, corrupt/withdrawn originals, resealed authority promotion, candidate budgets, exact/unique-phrase positives, disconnected-word negatives, CLI replay and unchanged H05 strict proof. Prior1265/1266-test passes and subsequently exposed failures remain retained.

## Reproduce

Use a clean checkout of the runtime revision and a fresh output directory:

```sh
python -m tools.sorter_first_study prepare evaluation/candidate-review-workspace/local-replay/native-replay
python -m tools.sorter_first_study run evaluation/candidate-review-workspace/local-replay/native-replay --arm direct
python tools/evaluate_candidate_workspace.py --implementation . --native-study evaluation/candidate-review-workspace/local-replay/native-replay --output evaluation/candidate-review-workspace/local-replay/public-originals
python -m tools.report_candidate_workspace evaluation/candidate-review-workspace/local-replay
python -m unittest discover -s tests -q
python -m pip wheel . --no-deps --wheel-dir /tmp/mplpb-workspace-wheel
python -m venv /tmp/mplpb-workspace-installed
/tmp/mplpb-workspace-installed/bin/python -m pip install --no-index /tmp/mplpb-workspace-wheel/*.whl
/tmp/mplpb-workspace-installed/bin/python -I tools/check_candidate_workspace_install.py
```

The native22 replay requires Linux Bubblewrap with permitted namespaces and has no unsandboxed fallback. The workspace itself is an opt-in offline native/CLI review surface; this update does not add a browser workspace. Existing original records, historical outcomes and independent-review limitations remain governing. Exact final publication-head ZIP/browser CI remains a separate premerge gate.
