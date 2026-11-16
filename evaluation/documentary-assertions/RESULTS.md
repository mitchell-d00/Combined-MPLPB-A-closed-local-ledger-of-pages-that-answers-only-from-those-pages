# Checked documentary assertions: implementation and results

Last reviewed: 2026-11-16.

Implemented and built a finite source-assertion verifier, atomic question obligations, compound-answer composition and source-aware browser output. On unchanged development questions, checked partial answers increased from **0 to 2 of 22**. Complete supported answers remain **0 of 22**. This is a practical native-output improvement, not closure of the historical supported-answer gap or independently established semantic accuracy.

Baseline runtime revision: `c6f77bef76a90219ae6e2074f0302fa3d72ada19` (the following evidence commit `4e4db3ef80caab004abfb86bbfe651a09fe1dc9e` has identical runtime). Tested final source: **`6acf45a9f77213953f8236379236c96662442153`**, on `engineering/documentary-scope`. Source ZIP SHA-256: `017be798605dd0ca9d7e2d89b78bb9754e8b6c04df429a583a86e9b0d709bc7c`. Tests and build ran from its extracted contents. Subsequent commits retain evidence and documentation; implementation file pins in each run receipt identify the tested runtime. No push or deployment was performed.

## What actually improved

| Unchanged records | Completed before/after | Full supported before/after | Checked partial before/after | Draft spans before/after |
|---|---:|---:|---:|---:|
| Original correspondence and reports | 14 / 14 | 0 / 0 | 0 / 1 | 18/23 / 18/23 |
| Familiar government records, directory named unfamiliar | 8 / 8 | 0 / 0 | 0 / 1 | 9/9 / 9/9 |

Draft spans are incomplete developer retrieval references, not recall against exhaustive historical labels. No candidate count earns answer credit. The comparison validates matching frozen questions, seals, originals, importer and harness; uses the same updated execution mode and budgets for both implementations; reimports originals; independently reruns the software kernel against each accepted certificate; checks its meaning/evidence digest; and reverse maps every accepted citation to original bytes. This is a software contract audit, not an independent human semantic judgment. [Original comparison](original/comparison/comparison.json), [government comparison](unfamiliar/comparison/comparison.json), and [metrics](metrics.json) preserve every question, including refusals and conflicts.

**H02: a reported instruction becomes inspectable checked partial evidence.** The unchanged question asks who arranged Wallace's receipt of Darwin's book and which dated letter records it. The original letter heading is “CHARLES DARWIN TO A.R. WALLACE. Ilkley, November 13th, 1859.” Its opening says “I have told Murray to send you by post (if possible) a copy of my book” and states a hope about receipt. The result certifies that this documentary appearance reports the instruction, retains the condition, delivery method, hope and following N.B. note, and supplies both exact citations. It does not authenticate authorship, equate telling with a completed arrangement, certify dispatch/receipt, or turn the heading date into an event date. [Full native answer](original/after/H02.json) and [original-byte evidence](original/comparison/certificate-audit.json) retain hashes, canonical offsets and raw mappings.

**U01: an appointment assertion becomes checked partial evidence.** “Shortly after the conference ended, Roosevelt appointed Gen. Dwight David Eisenhower to that position.” The temporal qualification and unresolved “that position” remain literal. The system does not infer the role, merge person/event identities, or answer the question's comparison with a separate decision to proceed. [Full native answer](unfamiliar/after/U01.json) and [original-byte evidence](unfamiliar/comparison/certificate-audit.json) show the limits alongside support.

**Failures remain visible.** [H01](original/after/H01.json) still abstains; [H03](original/after/H03.json) retains a retrieval conflict rather than choosing an interpretation. All other government questions still abstain. Discovery and quotations alone cannot discharge their identity, role, chronology or multi-record relationship obligations. The complete output inventories and blank review sheets include these cases, rather than dropping them from denominators.

Controlled fictional tests and the real browser demonstrate complete composition of two independently checked explicit appointments. Adding an unsupported causal part produces a partial answer; opposed source assertions produce a conflict without declaring underlying event identity. These controls establish implemented behavior, not historical benchmark accuracy.

## Technical decisions and safeguards

- `mplpb_answers/documentary.py` proposes opaque exact source spans, plans at most four obligations, composes independently checked statements and reports missing obligations. It retains the complete original question/profile throughout; shortened subqueries cannot lose exclusions. Every obligation, contrary-evidence check and display budget must pass for a complete answer.
- `mplpb_answers/documentary_verify.py` reloads current eligible source bytes, derives finite typed propositions itself, checks complete units and qualifier/quotation/heading context, and emits evidence/meaning digests. Extracted actor fields, citations, graph plausibility and model opinions cannot issue support certificates. Source assertion support, event identity, authenticated authorship and independently verified historical truth remain distinct.
- `mplpb_answers/pipeline.py` integrates the fallback after existing strict checks, preserves compatibility and clears documentary output on source-change invalidation. Corrections, revisions and restricted/profile evidence gates stay in force. Investigation remains read-only.
- `index.html` distinguishes supported source assertions from partial source evidence, displays missing obligations and supports exact source inspection. Existing ordinary answer modes keep their labels.
- Two Python test modules add 33 methods with varied positive/negative constructions and original-record round trips. Rendering, actual WebAssembly and CI controls cover composition without bundling the specialist-work package. `tools/compare_documentary_answers.py` audits certificates and prepares blank independent review/adjudication records; frozen harness and importer are unchanged.

Internal bounds: four obligations, 12 proposals, 200,000 characters, 1,000 source units, 64 parsed action assertions and caller display budgets. Frozen experiments retain 180-second worker wall, 300-second CPU and 2 GiB address-space caps, 12 discovery contexts/12,000 characters, and native answer display defaults. Exhausted or incomplete evidence cannot establish a complete answer.

## Regressions, build and failures

Final extracted source passed **1,068 Python tests in 377.064 seconds**, versus 1,035 at the preceding source baseline; **52/52 prepared public controls**, with zero observed false supported bridges in that suite; original-paper regression with four byte-verified originals, 31 documentary declarations, six traversed declared relations and 15 unresolved relations; infrastructure, documentation and handoff checks; UI, transport, JavaScript API/helper/loader/WebGPU and crawler checks; actual pinned WebAssembly; and five real Chromium UI checks. [Logs and receipts](validation/) retain the actual results. These are software checks, not independent historical review. The preservation audit found all 2,048 files across the pre-existing historical-experts, unprepared-originals and documentary-scope families byte-identical, with the frozen runner/importer and existing test files unchanged. Fifteen documentation/handoff/self-knowledge checks also passed after evidence assembly. Browser build: 38,462,635 bytes; SHA-256 `a151987fc14d19a18bc4273986d33fbee4d5f40fe451b2791cbb6c6eb66189f9`.

An earlier candidate `ba021f4` passed 1,068 tests but a later adversarial probe exposed a **false acceptance under a Plan heading**. The failing native output is retained in [intermediate/plan-scope-false-acceptance.json](intermediate/plan-scope-false-acceptance.json). Final `6acf45a` rejects plan/proposal/draft/scenario/forecast/hypothesis/intention heading scopes and bare plan labels; expanded negative controls and all final checks ran after that fix. A passing suite did not establish universal safety.

Other retained attempts exposed overly broad HTML navigation exclusion, possessive apostrophes mistaken for quotation and a correspondence boundary that dropped the following N.B. note. Final controls distinguish navigation ranges and lexical quotation delimiters and preserve complete safe notes; ambiguous correction notes stop acceptance. Environment interruption killed a first long suite and an incomplete original run without a terminal receipt. Those attempts are retained as interrupted, followed by complete runs in separate directories. Prior baseline sandbox/namespace failures remain in the preceding documentary-scope evidence. No failed attempt was scored as passed.

## Costs and unknowns

| Records | Arm | CPU s | Worker wall s | Peak RSS bytes | Logical source HTML bytes read |
|---|---|---:|---:|---:|---:|
| Original | before | 875.295 | 916.862 | 50,634,752 | 9,452,711,906 |
| Original | after | 737.189 | 737.821 | 50,298,880 | 9,458,431,290 |
| Government | before | 63.532 | 84.581 | 21,237,760 | 188,246,268 |
| Government | after | 48.905 | 49.249 | 21,422,080 | 188,813,916 |

These are summed query-worker costs and maximum fresh-worker RSS, including imports. Logical reads include repeated HTML reads, not physical disk I/O. Jobs overlapped on a shared host; no speedup is established. Import receipts retain separate costs. Certificate auditing, build, test and human-review costs are outside query-worker totals; uninstrumented costs stay unknown. Prior identical-input BM25/keyword retrieval-only runs are preserved in [the baseline experiment](../documentary-scope/RESULTS.md); they are reused, not claimed as new runs or answer generators.

Both final runs completed all cases, with zero invalid citations and zero structurally detected unsupported conclusions. This does **not** establish zero semantic false positives or appropriate refusals. Source retrieval recall@k, exhaustive span coverage, event identity precision/recall, relationship precision/recall, false-positive relationship rate, false supported-answer rate, correction accuracy, temporal accuracy, appropriate/incorrect refusal rates and genuine human review/correction times remain **null**. Independent review, adjudication and genuinely unseen evaluation are **NOT RUN**.

Remaining limits include finite active-clause syntax, conservative qualification/quotation handling, unresolved aliases and pronouns, indirect role references, passive/compound actions, authentication, event identity, reported occurrence versus execution, correction composition and missing multi-record bridges. The next measurable goal is independently judged completion of these missing obligations on frozen questions, with separate source-assertion and historical relationship labels. Broad understanding and production readiness remain unproven.

## Reproduction and independent review

Run from an extracted committed implementation. Use fresh output directories; never edit original corpora/questions or overwrite runs.

```sh
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/mplpb-public-evidence.json
python -m tools.evaluate_historical_experts --output /tmp/new-experts.json
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation CHECKOUT --mode updated --commit SHA --seal freeze-v2.json --output NEW_ORIGINAL_RUN
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-followup/unfamiliar --implementation CHECKOUT --mode updated --commit SHA --output NEW_GOVERNMENT_RUN
python -m tools.compare_documentary_answers CORPUS BEFORE_RUN AFTER_RUN --output NEW_COMPARISON
python -m tools.unprepared_challenge packets CORPUS ONE_RUN --output NEW_PACKETS
python -m tools.unprepared_challenge score NEW_PACKETS HUMAN_REVIEW_1 HUMAN_REVIEW_2 --adjudication HUMAN_ADJUDICATION --output NEW_SCORES
node tests/documentary-render.cjs
python tools/build_browser_runtime.py --core-archive PINNED_CORE_ARCHIVE --output dist/index.html
node tools/check_browser_wasm.mjs EXTRACTED_CORE_DIRECTORY dist/index.html
```

The comparison must run from the exact updated implementation; it rejects mismatched runtime pins. The frozen worker uses real fail-closed Linux bubblewrap isolation and excludes draft answers from runtime access. The original uses `freeze-v2.json`; the government family uses `freeze.json`. For actual WebAssembly build commands and pinned Pyodide see [ZIP-first testing](../../docs/ZIP_FIRST_RELEASE_TESTING.md). The retained [browser driver](validation/browser_ui.py) uses system Chromium against the built output: `PYTHONPATH=. python evaluation/documentary-assertions/validation/browser_ui.py --dist dist --output NEW_BROWSER_JSON`.

Full packets under each family's `review-packets/` contain original projections, imports, unchanged questions, all native outputs and explicitly incomplete developer drafts. Two blank comparison reviewer sheets and an adjudication sheet accompany each comparison. The [prospective protocol](../../docs/DOCUMENTARY_SCOPE.md) requires a frozen new implementation, hash-pinned unseen originals, independently authored/sealed expectations, identical runtime access/budgets, two real independent human reviewers and adjudication. No reviewers were available; no scores or times were simulated. Development questions remain development material.
