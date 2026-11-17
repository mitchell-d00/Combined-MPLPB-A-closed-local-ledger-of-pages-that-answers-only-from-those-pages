# Historical reconstruction: completed engineering experiment

Last reviewed: 2026-11-17.

The final implementation produces **one complete source-supported comparison and two checked partial answers across 22 unchanged development questions**, versus zero complete and two checked partial answers before. All 22 worker executions completed. This is neither 22/22 correctness nor an independently validated historical accuracy result. The proposed 9/10 outcome and independent 80%/95%/75%/95% targets are **not established**.

The complete answer is H05: comparison of the opening truth wording in the supplied rough reconstruction and Declaration transcription. Completion now requires independently checked **body-text source-selection declarations, the opening topic in both records, the changed wording, the shared wording, all four citations, and current source eligibility**. It is not a Boolean relabelling of the prior two-citation candidate. Historical authenticity, finality, event identity and independently verified historical truth remain explicitly unverified.

## Exact implementation and experiment binding

Baseline: `4d0f4470adfa88e36b736d78f429ee86d003a925`. Final tested implementation: **`63cea982399280b4fa634893799e6642cbd19436`**, branch `engineering/reconstruction-engine`. Source ZIP SHA-256: `928a921e602704facca23a3188b452b8976974e96e6f727323c34d2f57862dc6`; 60,195,228 bytes. It was extracted before final testing. Browser build:38,524,313 bytes, SHA-256 `8700aba14f76a6630cbfa6f0aa0e79847674d05494de3c46ebe71bbdfd04380d`. Subsequent evidence/handoff edits preserve the tested runtime; receipts bind every implementation file. No push, merge or deployment of this iteration was performed.

The fresh before runs used an extracted archive of4d0f447 and the unchanged existing worker. Final after runs used the extracted63cea98 archive. Both use the same original documents, questions, frozen seals, importer, harness, profile and computational limits. Expected drafts remain outside runtime isolation. The old corpus, question, label and report files were not edited. The final preservation audit found all 2,246 pre-existing historical evaluation files, existing baseline test files and frozen harness/importer/mapper byte-identical. The prior phase's complete outputs, failures and measurements remain in [PHASE1_RESULTS.md](PHASE1_RESULTS.md); they were not overwritten when completion was added.

## Before, intermediate and final results

| Scope | Baseline complete / checked partial | First phase complete / checked partial | Final complete / checked partial | Draft retrieval spans |
|---|---:|---:|---:|---:|
|14 original questions |0 /1 |0 /2 |1 /1 |18/23 throughout |
|8 government-record questions |0 /1 |0 /1 |0 /1 |9/9 throughout |
|All 22 questions |0 /2 |0 /3 |1 /2 |Incomplete developer references |

These are native contract outcomes, not independent correctness labels. In particular, some questions deliberately request unsupported causality or priority claims. Their refusal is not automatically a defect. Source retrieval recall against an exhaustive reference, answerability-conditioned accuracy, semantic precision/recall, incorrect refusals, incorrect event merges, critical false-support rate and actual human times remain **null** in [completion-metrics.json](completion-metrics.json). Candidate count is never scored as success. Statistical target accounting is prepared, not populated with simulated reviewers.

The [original comparison](original/completion-comparison/comparison.json) and [government comparison](government/completion-comparison/comparison.json) verify matching frozen inputs and retain every case, not only favorable outputs. The postprocessor reimports originals, independently reruns the kernel from the exact updated implementation, matches evidence/meaning digests and reverse maps every accepted citation. **Seven accepted citations across three native findings passed these software checks**. This proves current source/quotation and finite-kernel compliance, not independent historical semantic accuracy.

## Source-linked successes and failures

**H05, now complete within a stated source-comparison scope.** The body of one page explicitly identifies a reconstruction of Jefferson's “original Rough draught” of the named work; the other explicitly identifies a transcription of the engraving of the parchment work. The checker does not use filenames, HTML titles, source ranking or a model to supply these roles. It resolves the printed work reference and author reference within those declarations, requires the first matching topic paragraph after each declaration, and computes both changed and shared tokens. The source wording includes “sacred & undeniable” versus “self-evident” and shared “We hold these truths to be”. It does not establish who caused revisions or authenticate an original manuscript. [Native output](original/completion-after/H05.json), [four-witness certificate and original bytes](original/completion-comparison/certificate-audit.json), [earlier partial output](original/after/H05.json).

The completion rule is tested with different names/works/wording, an alternative question form, wrapped plaintext, wrong authors, different work names, missing/ambiguous/qualified role declarations, quoted declarations, Plan scope, titles substituted for evidence, restricted sources, hidden display witnesses, extra motives/dates/questions and source mutation. The [actual-source sensitivity experiment](completion-validation/source-sensitivity.json) additionally revised only temporary imported copies: changing the body-declared author or referenced work removed completion despite unchanged comparison wording and routing titles. The original frozen bytes stayed unchanged. This is a developer sensitivity control, not an independent human judgment.

**H02 remains partial.** The Darwin letter reports telling Murray to send the addressee a copy, with delivery condition, hope and following note preserved. This does not establish completed arrangement, dispatch, receipt, authenticated authorship or the date of every action. [Output](original/completion-after/H02.json).

**U01 remains partial.** The source appointment statement retains the unresolved “that position” and relative temporal qualification. The system does not infer the missing role or silently connect appointment to a distinct decision to proceed. [Output](government/completion-after/U01.json).

**H08 remains unsupported by the strict path.** The report's summary contains useful causal/resource wording, but damaged earlier OCR quotation state prevents the current checker from establishing unambiguous attribution. The system does not repair original bytes or ignore that ambiguity to gain a score. Candidate inspection remains available. [Output](original/completion-after/H08.json).

**Unsupported bridges remain unsupported.** H10, H11, H12, H14 and U08 do not gain supported conclusions about cross-domain causality, personal authorization or historical priority. H06 also remains unresolved: local paragraph differences cannot establish an entire document's omission, motives or every responsible person. All outputs are retained under the final run directories. Independent appropriate-refusal accuracy has not been measured.

## What was implemented

- **Document units and retrieval:** `mplpb_answers/source_units.py` and `PassageIndex.documentary_units` expose derived layers, source/hash/canonical coordinates, completeness and lazy original-byte mapping. Complete-context expansion crosses existing passage boundaries. Physical plaintext paragraphs are accepted only when their canonical concatenation exactly reproduces the existing projection. Admission-manifest text cannot become documentary comparison evidence. The prose retriever records separate question obligations while keeping the complete original question/profile for every gate.
- **Independent checks and composition:** the existing `documentary_verify.py` kernel v3 re-reads eligible native bytes for explicit causal, temporal, resource and passive statements, exact paragraph alignment, checked ledger/content identity and source-framed comparison closure. The composer preserves partials and requires every supported obligation and witness to fit the budget. Only the literal-comparison contract closes H05; other relation types do not inherit completeness automatically. A Draft heading is permitted only for a body-declared rough reconstruction in a literal comparison, never as unconditional action/execution evidence. Conditions, plans and quotation scopes remain protected.
- **Research graph and interfaces:** existing reversible proposition/connection mappings produce distinct documentary occurrence, actor mention and event-candidate nodes. Edges retain anchors, state dependencies and unresolved links; similarity never merges events. `python -m mplpb_answers reconstruct` and the existing inspection tool return native evidence, candidate graph/layers, model-assisted output when explicitly configured, and missing obligations. Existing CLI/API/browser labels and citation inspection work with the richer result. This is a query-scoped graph, not an automatically maintained universal history.
- **Content caching:** immutable canonical projections and structure parsing use bounded content/version caches. Oversized inputs bypass them. No eligibility, profile, restriction or serving decision is permanently cached. Final source/policy checks still run. No material native performance improvement is established by the measured costs.
- **Crawler:** the existing Worker now accepts one or two explicit public HTTPS seeds, optionally hash-pinned, without a search API. Existing authentication, robots, redirect, byte/type/count/depth/time and failure rules remain. Async `sourceIdentity` independently rehashes both bounded raw captures, rejects forged/missing raw payloads, and distinguishes byte equality from a changed body at the same URL. Neither byte identity nor navigation establishes event identity, authorship or corroboration. PDF/OCR and live deployment remain unsupported/unperformed.
- **Historical review method:** `historical_review.py` extends existing WorkStore records and its closed API. Entries require current evidence, claim revisions, explicit visibility, authorized capability seat, identified review kind, decision, rationale, scope, attestation and uncertainties. The same typed rules apply to direct `put`, so the helper cannot be bypassed. Stale sources invalidate review status; reviews do not rewrite originals or grant strict factual support. Source integrity, quotations, source assertions, candidate interpretations, declared human reviews and historical truth remain distinct.
- **Synthetic truth test subject:** the [ordinary fictional source](validation/synthetic-synthetic-1.html), [separate pinned oracle](validation/synthetic-oracle.json) and [actual fixture review result](validation/synthetic-review-result.json) exercise two labelled software review seats. Wrong oracle values, stale claims/sources, duplicate seats and unauthorized or malformed entries are rejected by the corresponding controls. `synthetic_fixture_truth_matches:true` is limited to that declared fictional universe; real historical truth and real human independence remain false/unverified.
- **Evaluation infrastructure:** `tools.compare_documentary_answers` audits final certificates; `tools.historical_targets` runs after the existing two-human/adjudication validator, requires custody-pinned answerability annotations and reports denominators/uncertainty. The existing isolated framework supports frozen sources, sealed expectations and comparator runs. No200-question unseen study or human validation was invented.

## Verification and failures retained

Clean baseline: **1,068 tests in 376.449 s**,62 focused tests in 14.641 s and public52/52. First reconstruction archive: 1,106 tests in 387.305 s. Final completion archive: **1,124 tests in 394.726 s**; **52/52 public controls**, zero observed false bridges in those authored controls; existing original-paper software stages; JS/UI/transport/helper/loader/WebGPU/crawler controls; actual pinned WebAssembly; **nine real Chromium UI checks**; source sensitivity and original-byte certificate audits. The official MCP SDK client passed 45 protocol/workflow checks using installed **mcp 1.29.0**; this is not a claim that the repository's separately pinned1.26 CI environment was rerun here. [Actual receipts and logs](completion-validation/).

The initial abbreviation-tail regex caused severe long-document CPU behavior and those jobs were terminated, not counted as passes. A bounded tail fixed it. Review integration initially used the wrong existing state-field name. The first new Node control exposed a runtime crypto-property assumption. The crawler originally compared supplied digests without rehashing raw bytes; an adversarial forged-body test exposed that false identity and the fix rehashes both payloads. Initial comparison discovery could omit the relevant pair behind framing text; focused ranking, unit deduplication and bounded additional pairs repaired that refusal. Pasted plaintext and an existing Draft title also exposed differences from original HTML; exact paragraph mapping and the narrowly scoped document-role rule fixed the interface case without changing action-proof scope. These attempts are retained in intermediate/, with old reports and prior source freezes preserved.

The actual Library of Congress direct crawl was **blocked by robots policy**, accepted zero captures and was not bypassed: [live failure](validation/live-crawl.json). Crawler successes are fixture controls, not a deployed live-crawl certification. Optional live local-model efficacy and postdeployment checks are NOT RUN.

## Runtime, memory and read costs

| Records | Arm | CPU s | Worker wall s | Max fresh-worker RSS bytes | Logical source HTML bytes read |
|---|---|---:|---:|---:|---:|
|Original14 |before |775.746 |795.610 |52,420,608 |9,458,431,290 |
|Original14 |final |775.222 |776.457 |54,423,552 |9,469,870,058 |
|Government8 |before |53.009 |66.230 |21,417,984 |188,813,916 |
|Government8 |final |52.536 |52.803 |22,626,304 |188,813,916 |

Worker costs include the native answer, candidate discovery and specialist investigation, not just Ask latency. CPU/wall are sums, RSS is the largest fresh Linux worker including imports, and logical HTML reads include repeated verification reads rather than physical disk I/O. Import costs remain separate in receipts. Allocation tracing is disabled equally. Shared-host concurrent jobs do not establish a speedup; repeated authority reads remain expensive and memory increased modestly. Build/review/audit costs are outside these totals; uninstrumented costs and genuine human times stay unknown.

Environment: Linux6.18.57 x86_64, Python3.12.14, Node24.22.1, system Chromium156, AMD EPYC9V74,5 exposed logical CPUs on a shared host. Detailed environment and step wall times are retained. Existing budgets remain180s worker wall,300s CPU,2GiB address space; discovery12 contexts/12,000 characters and native display defaults. New finite limits include four obligations,12 proposals,32 eligible source records with leading6,000-character role declarations, at most60 local comparison units and four proposed pairs for framed requests,600 tokens per alignment side, and caller citation/display budgets. Exhaustion/unknown scope cannot invent a missing link.

## Remaining gaps and target assessment

Independent answerable-question accuracy≥80%, checked relationship precision≥95%, exhaustive annotated recall≥75%, correct refusals≥95% and≥200 unseen questions are **unmeasured**, not achieved. Seven development citation checks passed; that does not establish the independent100% citation target for future accepted claims. No critical historical false-support rate can be inferred from unreviewed outputs or software tests.

General entity/pronoun resolution, authentic event co-reference, missing intermediate records, multi-document causal composition, partial-correction authority, full-document absence, OCR quotation recovery and reliable event/document timelines remain incomplete. The source-unit index can exhaust its global budget before later sources; it must not be mistaken for exhaustive relevant-layer coverage. The local-model path reuses existing assisted schemas but has no newly measured live-model accuracy. Automatic accumulation and maintenance of a corpus-wide history as pages are imported remains a separate integration step; current WorkStore claims/reviews persist, while the derived reconstruction graph is query-scoped. Human acceptance alone does not make a link independently true.

The next complete-answer work should discharge these missing obligations individually with inspectable witnesses, not force all22 questions to be affirmative. A9/10 historical research-engineering claim is not warranted by this development experiment.

## Reproduction and external review

Use clean archives/worktrees at the exact revisions and new output paths. Do not modify frozen questions, originals or expected files.

```sh
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/mplpb-public-evidence.json
python -m tools.evaluate_historical_experts --output NEW_EXPERTS_JSON
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation CHECKOUT --mode updated --commit SHA --seal freeze-v2.json --output NEW_ORIGINAL_RUN
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-followup/unfamiliar --implementation CHECKOUT --mode updated --commit SHA --output NEW_GOVERNMENT_RUN
python -m tools.compare_documentary_answers CORPUS BEFORE_RUN AFTER_RUN --output NEW_COMPARISON
python -m tools.unprepared_challenge packets CORPUS ONE_RUN --output NEW_PACKETS
python -m tools.unprepared_challenge score NEW_PACKETS HUMAN_REVIEW_1 HUMAN_REVIEW_2 --adjudication HUMAN_ADJUDICATION --output NEW_SCORES
python -m tools.historical_targets --output NEW_PROTOCOL_JSON
python -m tools.demo_historical_review --output NEW_SYNTHETIC_DIRECTORY
python -m mplpb_answers reconstruct LEDGER QUESTION
node crawler/test_worker.mjs
node crawler/test_historical.mjs
python tools/check_mcp_client.py --output NEW_MCP_JSON
python tools/build_browser_runtime.py --core-archive PINNED_CORE_ARCHIVE --output dist/index.html
node tools/check_browser_wasm.mjs EXTRACTED_CORE_DIRECTORY dist/index.html
PYTHONPATH=. python evaluation/reconstruction-engine/2026-11-17/completion-validation/browser_ui.py --dist dist --output NEW_BROWSER_JSON
PYTHONPATH=. python evaluation/reconstruction-engine/2026-11-17/completion-validation/source_sensitivity.py --corpus evaluation/unprepared-originals/2026-11-16 --output NEW_SENSITIVITY_JSON
```

The comparison must run from the exact updated implementation and rejects mismatched runtime pins. The existing runner requires actual fail-closed Linux bubblewrap isolation. BM25/keyword retrieval-only comparison records are retained in the preceding documentary-scope experiment, not claimed as newly executed answer generators. Full final packets under each family's completion-review-packets/ contain every output, original projections, imports and explicitly incomplete developer drafts. Two blank reviewer sheets and adjudication accompany each completion-comparison/. The [independent protocol](independent-protocol.json) and [review rules](../../../docs/HISTORICAL_TRUTH_RULES.md) specify source/implementation freeze, separately authored unseen questions, sealed private expectations, equal runtime access/budgets, two real reviewers, adjudication and measured effort. This requires an independent custodian; software cannot authenticate human independence or turn inspected development questions into unseen material. Independent review and genuinely unseen evaluation remain **NOT RUN**.
