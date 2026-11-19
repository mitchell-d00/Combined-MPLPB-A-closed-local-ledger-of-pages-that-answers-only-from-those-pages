# D% general-class fixes: full engineering findings

Recorded 2026-11-19. Tested implementation: **6e0de9e**. Developer-authored synthetic comparison; independent semantic assessment **NOT RUN**.

## Measured outcome

All **1,240 unchanged frozen D% cases** executed, with the same sources, questions, profiles, 12-passage/8,000-character budgets and private key. Complete checked answers increased **20 → 200 of 600**; detection **E: 3.33% → 33.33%**. There were **180 newly complete cases, zero lost complete cases and zero new false support** against this developer key. **640/640 expected refusals** were retained; observed **F = 0/640 = 0%**. No execution failures or unscored supported outputs occurred.

The 200 answers comprise **160 checked source assertions** and **40 textual locations**. The 160 assertions are 80 active writing statements, 40 passive writing statements and 40 explicitly source-stated causes. Source-assertion coverage alone increased **20 → 160**. Word-location questions prove that eligible source text contains requested words; they are not forty reconstructed historical relationships.

**400 answerable fictional cases remain incomplete:** 40 checked partial wording comparisons and 360 abstentions. The remaining ten answerable families each have 40 incomplete cases. The capability command with `--require-perfect` still exits **1**. The software regression suite passing does not make the capability benchmark a pass.

The unchanged real original-record replay remains **2 complete, 2 partial, 3 conflicts and 15 abstentions out of 22**. Every case retains its baseline native outcome category. Both question seals and import receipts match byte-for-byte. **No improvement in complete historical answers is demonstrated.** Independent semantic correctness of these outcomes was not reassessed here. See [paired historical results](final/historical-comparison.json) and [all historical cases](final/historical-cases.csv).

## Freeze, scope and reproducibility

* Baseline main: `6334e1b3a08db10984de637adbd5e5a6021b381c`; remote main was checked and still points there.
* Generator, worker and original generator tests: frozen at `0b2c5c834a87262b1cc4853a30f88e3f9252c6a5` and unchanged throughout engine fixes.
* Public packets/private-key commitments: `a58beb46bdf1e578dc320074204c43d521bb1e8f`, committed before baseline execution. [Original baseline](../2026-11-19/REPORT.md) is unchanged.
* Final tested engine/source archive: **6e0de9e**, containing documentary kernel v9 and source-unit index v3. Later PR documentation and evidence edits do not change runtime code.
* Private key SHA-256: `676699792759afb2a6cf7ff359a184cd6e04daf08007e0cf022c39e64334de8d`. Key/dice remain outside Git at `/tmp/dpercent-frozen-private`; operator custody archive: `/workspace/dpercent-private-custody-2026-11-19.tar.gz`.

D% has 31 stratified families, 40 cases per family: 15 expected-answer and 16 expected-refusal families. The conservative design comprises 1,674 structural cells, excluding extra name/date/layout/wrapping variants. Every percentile draw is retained and replayed. This is not an iid sample or an unseen independent historical evaluation. Early harness pilots were used during generator development and are retained separately. The separate-window requirement was waived; generator/fix authorship is not independent.

Each runtime mounts only three native packages and one read-only public case. No generator, scorer, key, dice record, host workspace or network is mounted. The host custodian is trusted, not isolated from its own key. All 1,240 cases preserve source bytes and post-setup ledgers; both sorter modes retain identical nodes/labels and non-authoritative relationships. The native `mplpb_combined` ownership, revision, authorization and hash-check code is unchanged from main. No ledger rewrite or candidate-to-fact promotion is added.

## Why these are class fixes

The [repository policy](../../../AGENTS.md#general-class-fixes-never-benchmark-specific-passing) now prohibits runtime branches on benchmark IDs, fixture names, generated actors, answer keys or expected outcomes. It requires general failure mechanisms, independent-vocabulary regressions, contrasting negatives, mutations, preserved failures and frozen before/after comparisons. No language acceptance filter discards hard generated cases.

The custodian-only [feature analyzer](../../../tools/dpercent_features.py) reproduces every source packet and every sealed draw before joining outcomes. Baseline answerable cohorts rolled as letters and mail each missed **147/147 complete answers**. That was a clue, not causal proof: some rolled layouts are overridden to preserve necessary documentary context. Inspection confirmed that headers/salutations were consumed as the first sentence's actor. See [baseline cohorts](baseline-feature-cohorts.json), [final cohorts](final/feature-cohorts.json) and [every before/after case](final/case-results.csv).

The implementation extends the existing parser and independent source checker:

1. **Correspondence structure.** Leading letter/mail headers and salutations supply boundaries only. The actor comes from the action sentence, never a nearby sender field. Unicode actor spelling is retained without resolving a real person.
2. **Question scope.** Finite polite request and non-factual safety instructions can be recognized without rewriting the original question or profile. Named speaker constraints, factual additions and conditions are preserved. Removing an arbitrary named attribution is now refused.
3. **Active/passive meaning.** Positive passive actions, including irregular written-by forms, enter the independently reread observation scan. Unparsed denials, hedging and pronouns still block completion. Active and passive counterevidence use the same finite action vocabulary.
4. **Explicit source-stated causes.** One independently derived because-of clause may close an exact source-scoped why question. Negation, relevant alternative appearances, unresolved refutations or incomplete scans stop closure. No historical event identity or causal truth is inferred.
5. **Textual occurrence.** Whole-request literal-location grammar verifies meaningful quoted words, exact code points, whitespace wrapping, original-source word boundaries and one eligible source owner. Blank/padded requests, clipped-word proposals, metadata-only matches, multiple owners and exhausted budgets cannot establish a complete answer. This proof type is explicitly `textual_occurrence`.
6. **Source coordinates and date roles.** Native sentence offsets remain absolute when retrieval starts later in a document. `Date written` and other layout labels are not action predicates; neutral subject headers are not additional event appearances. Values and original source locations are retained.
7. **Scope survives segmentation.** Plan/draft/reported headers, known structural example/quotation annotations, self-ascribed hypothetical layers, Markdown fences and uncertain quote continuations cannot turn into bare completed actions. A bounded original preformatted prefix checks folded fields, missing roles and unknown/over-budget headers. Literal locations remain available in these layers.
8. **Possible source refutations.** Unresolved self-referential denial/error wording is retained as alternative evidence. It can stop actor/cause closure but does not establish its target, independently verify a historical correction, retire a claim or change ledger state.

These are finite English rules. They do not solve general pronouns, historical entity identity, unfamiliar event co-reference, arbitrary reported speech, date normalization, partial-correction identity or multistep documentary composition.

## Source-linked gains and failures

[Examples](final/examples.json) contain original UTF-8 source text, raw and sealed hashes, canonical citations, propositions, missing obligations and complete native responses. The [full execution archive](final/raw-execution.tar.gz) retains every result and log.

One newly supported direct-writing case is **DP00001**. Its exact citation is “Nora Wells wrote the coastal dispatch.”, source `SOURCE-0001`, canonical `[55,93)`, hash `sha256:8b0877bca6cb4dd445d116ada7b5163b6999e020d2b883327174d1f23f48a51c`. The answer identifies a source-declared actor; event/person identity and historical truth remain unverified. The same source bytes were refused before the class fix.

The examples also include passive statements, explicit causes, literal locations, and still-unresolved date-role, reported-statement, partial-correction and request/dispatch/receipt-chain questions. Similarity is not used to invent missing connections. The remaining failures stay in the denominator and in the case table.

## Failed and interrupted attempts

* Pre-freeze generator tests and a 30-case pilot remain in the [baseline engineering record](../2026-11-19/engineering-attempts/index.json). Missing correspondent context and a missing earlier writing date were repaired **before** the official generator/key freeze.
* **3d694aa:** first class run reached 160/600, F=0, but its archived 1,408-test suite had **one failure**. Two historical partials disappeared. The cause was an absolute source position receiving the retrieval offset twice. The candidate was rejected; [raw results](raw-execution.tar.gz), [historical replay](paired-originals.tar.gz), [failed suite](software/report.json) and [status](iteration-one.json) remain unchanged.
* **35069e8:** reached 200/600 and restored both historical partials. Its archived **1,417 tests and 52 public controls passed**, but new adversarial controls outside D% exposed blank/padded word requests and clipped-word certification flaws. This iteration was not accepted as final. [Receipts](second-candidate/software/report.json) and [all results](second-candidate/score.json) are retained.
* **a71bfb7:** after word-boundary repairs, a new header-scope test exposed loss of plan/draft/report qualification. The candidate was deliberately stopped. **543 cases completed, 697 were unrun; primary E/F are null.** The superseded suite was terminated with exit **-15**, not reported as a software pass. [Interruption reason](interrupted-candidate/interruption.json), [partial score](interrupted-candidate/score.json), raw outputs, partial historical outputs, orphan checkpoints and software receipts are retained.
* Additional independent-vocabulary controls exposed named-attribution erasure, ignored opposing passive statements, irregular passive denials, date-label false counterevidence, structural quotation layers and unresolved source refutations. Their before-fix failures remain in [engineering logs](engineering). They are developer controls, not independent semantic validation.

The frozen D% negative set alone would miss several of these defects. Its observed F=0 must never be presented as universal zero-error reliability. No failed or interrupted case was relabeled or silently retried into a retained old run; corrected attempts use new directories and source revisions.

## Complete family results

| Family | Expected | Baseline complete | Updated complete | Still incomplete | False support |
|---|---|---:|---:|---:|---:|
| absent_anchor | refuse | 0 | 0 | 0 | 0 |
| ambiguous_correction | refuse | 0 | 0 | 0 | 0 |
| ambiguous_pronoun | refuse | 0 | 0 | 0 | 0 |
| chronology_causation | refuse | 0 | 0 | 0 | 0 |
| competing_accounts | refuse | 0 | 0 | 0 | 0 |
| conditional_execution | refuse | 0 | 0 | 0 | 0 |
| corrupted_source | refuse | 0 | 0 | 0 | 0 |
| date_roles | answer | 0 | 0 | 40 | 0 |
| direct_action | answer | 16 | 40 | 0 | 0 |
| earliest_observed | answer | 0 | 0 | 40 | 0 |
| editorial_competition | answer | 4 | 40 | 0 | 0 |
| embedded_identifier | refuse | 0 | 0 | 0 | 0 |
| exact_anchor | answer | 0 | 40 | 0 | 0 |
| explicit_cause | answer | 0 | 40 | 0 | 0 |
| explicit_chain | answer | 0 | 0 | 40 | 0 |
| header_location | answer | 0 | 0 | 40 | 0 |
| historical_priority | refuse | 0 | 0 | 0 | 0 |
| identical_wording | answer | 0 | 0 | 40 | 0 |
| instruction_statement | answer | 0 | 0 | 40 | 0 |
| intention_execution | refuse | 0 | 0 | 0 | 0 |
| missing_bridge | refuse | 0 | 0 | 0 | 0 |
| negated_execution | refuse | 0 | 0 | 0 | 0 |
| negated_statement | answer | 0 | 0 | 40 | 0 |
| partial_correction | answer | 0 | 0 | 40 | 0 |
| passive_action | answer | 0 | 40 | 0 | 0 |
| reported_execution | refuse | 0 | 0 | 0 | 0 |
| reported_statement | answer | 0 | 0 | 40 | 0 |
| restricted_source | refuse | 0 | 0 | 0 | 0 |
| subject_identity | refuse | 0 | 0 | 0 | 0 |
| withdrawn_source | refuse | 0 | 0 | 0 | 0 |
| wording_change | answer | 0 | 0 | 40 | 0 |

## Retrieval and resource measurements

Retrieval coverage did not improve: over the same 1,080 eligible-reference cases, native facets retain **89.85% source recall@10 / full-statement coverage**, versus **100%** for simple BM25 under the same budget. BM25 can fit all sources in these small packets. Recall@1 is 76.48% versus 77.61%; @5 is 89.57% versus 98.12%. These are developer reference-coverage metrics, not semantic precision. Five previously diagnosed historical draft spans were not established as recovered by this experiment.

| Measurement | Baseline | Updated |
|---|---:|---:|
| Post-import worker CPU, all cases | 147.676 s | 169.127 s |
| Post-import worker wall sum | 153.136 s | 176.142 s |
| Maximum individual worker RSS | 28,516,352 bytes | 29,175,808 bytes |
| Explicit original-ingest calls | 6,488 | 6,488 |
| Explicit original-ingest bytes | 795,751 | 795,751 |
| Total internal source-read bytes | null | null |
| Human review/correction time | null | null |

Updated summed parent per-case wall is **638.753 s**; baseline was 586.222 s. Worker timings include sealing, two retrieval methods, strict answering, both sorter modes and label checks, but exclude import/startup and parent orchestration. Source/ledger snapshot reads and internal repeated reads are not included in the explicit-ingest counter. Extra checks cost CPU; no speed improvement is claimed. Runs shared a Linux x86_64 container with concurrent regression/browser work: Xeon Platinum 8573C, five visible CPUs, four-CPU quota, 16 GiB cgroup limit and Python3.12.14. [Environment](../2026-11-19/environment.json) records details. RSS is not aggregate process-tree memory. The container init retained defunct sandbox helpers; long-running deployments need proper orphan reaping.

## Validation and exact commands

All final software checks ran from the archive of **6e0de9e**:

```sh
python -m tools.reproduce_boundaries --revision 6e0de9e --output /tmp/dpercent-scope-safe-software --suite full
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/dpercent-scope-safe-software/public-evidence.json
python -m tools.dpercent run --packets /tmp/dpercent-frozen-public --out /tmp/dpercent-scope-safe-run --implementation /workspace/mplpb
python -m tools.dpercent score --packets /tmp/dpercent-frozen-public --custodian /tmp/dpercent-frozen-private --run /tmp/dpercent-scope-safe-run --out /tmp/dpercent-scope-safe-score.json --require-perfect
python -m tools.dpercent_features --packets /tmp/dpercent-frozen-public --custodian /tmp/dpercent-frozen-private --score /tmp/dpercent-scope-safe-score.json --out /tmp/dpercent-scope-safe-features.json
python -m tools.sorter_first_study prepare /tmp/prose-scope-safe-originals
python -m tools.sorter_first_study run /tmp/prose-scope-safe-originals --arm direct
```

Results: **1,431 full Python tests, exit0; 52 public controls, exit0; native boundary subset, exit0; all1,240 D% executions, exit0; capability score, exit1; full roll replay, exit0; all22 historical workers completed, exit0.** The score exits1 because400 answerable cases remain incomplete, not because execution failed.

The archive also passed UI script, JavaScript API/rendering/model-loader/WebGPU-limit/transport checks, crawler checks and bridge syntax/help. Actual cached Pyodide execution passed, as did isolated headless Chromium collection-policy and free-helper journeys. [Interface commands and logs](final/interfaces/report.json) and [browser commands](final/browser/commands.json) give exact invocations, exits and timing. Models were mocked or absent; no live neural inference, physical-device test or deployed-site update is claimed. Initial default-sandbox JavaScript EPERM failures in the baseline were rerun with execution permission and retained. Frozen historical documentation and source artifacts remain untouched; generated extraction directories were removed only after their archived checks completed, retaining source ZIPs and receipts.

## Remaining failures and review status

The unresolved400 cases are ten families of40: header location; reported statements; explicit denials; stated instructions; document/event date roles; exact quantity/shared-wording comparisons; partial corrections; earliest observed writing date; explicit multistep chains; and identical documentary wording. Some have checked partials, but none is silently promoted. Next changes must solve these general proof classes and run the same frozen negative controls. New hidden batches are required for genuinely unseen assessment.

Historical entity/event identity, causal/correction relationship precision/recall, false candidate-link rates, historical truth and human intervention costs remain **null / NOT RUN**. No independent human review or fresh blinded AI assessment was performed in this task. Developer-authored synthetic scoring is not independent validation. Broad reconstruction, 80% historical answer coverage and a9/10 research-engineering rating are not established.

Scopes are intentionally conservative: folded/unmapped/over-budget headers, retrospective self-ascriptions, uncertain Markdown quote ends and unresolved refutations may withhold legitimate later prose in mixed records. Those over-refusal risks outside this distribution remain unmeasured. Finite name, verb, wrapper and word-location grammars do not cover all languages, OCR or historical prose. A valid source hash/quotation and a coherent current page do not authenticate testimony or independently establish history.

For a fresh **AI assessment**, provide only [frozen public packets](../2026-11-19/public-packets.tar.gz) and [final raw outputs](final/raw-execution.tar.gz), not the key, scores, family table or change log. Require cited reasons for each semantic judgment and retain its unedited response/hash before comparing scores. Label model review AI assessment, not human-independent accuracy. The key stays in operator custody. [Usage](../../../docs/DPERCENT.md), [rule boundaries](../../../docs/PROSE_RULE_CLASSES.md), AGENTS.md and the current handoff let another capable instance resume without the previous instance's private memory.
