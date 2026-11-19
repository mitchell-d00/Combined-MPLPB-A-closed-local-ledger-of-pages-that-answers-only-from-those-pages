# Archival source/date completeness experiment

Last reviewed: 2026-11-19.

Baseline main: `bc6f25c053dfc1ceb3b0096cca56550041395105`. Existing sources,
questions, expected files and past runs remain unchanged. Scope: finite
source-attributed event/date relationships, an offline tutorial, retained-metric
dashboard and anonymous review preparation. No new model authority or historical
truth claim is added. Independent review is **NOT RUN**.

Before code edits, a sparse detached baseline worktree was created at the pinned
main revision. Full baseline D% completed all 1,240 cases: 200/600 matched complete
answers and 640/640 expected refusals; observed false support 0. The unchanged
original-record baseline has 2 complete, 2 partial, 3 conflicts and 15 abstentions.
The initial independent-vocabulary event/date regression failed 5 of 10 controls
with exit 1; its log is retained. The first implementation passed those controls
but the real record still withheld catalogue/review dates because coarse native
units overlapped unrelated navigation/footer regions. The correction locates the
complete catalogue field, retains parent context, and treats page-review mentions
as textual annotations only. No historical event claim is accepted from chrome.

The current working-tree H07 answer retains four separate links: source-reported
artillery firing on April 12, surrender on April 13 at 2:30 p.m., evacuation on
the following day (calendar display April 14, year unstated), and the source's
catalogue date April 18, 1861. The webpage review date May 10, 2022 is explicitly
not an event date. The source calendar and event identity are not authenticated;
the catalogue date does not prove transmission. No 1861 year is silently added
to narrative clauses. Runtime rules contain no case IDs or historical names.

These checks were pending at the initial source freeze. The complete results
and failed intermediate attempt are now retained below; the original source
archives preserve their earlier coordination state. The frozen D% scorer/generator/worker/key remain
unchanged; new unsupported semantic shapes do not get automatic credit.

## Rejected candidate and class repair

Candidate `ebe8a3d` is rejected. A new independently worded control showed three
false supports: an embedded reporting clause, “almost opened fire”, and a proposal
prefix. The actor regex had accepted arbitrary text before the main predicate.
The [failure](rejected-candidate/actor-before.log), partial D% run/score, complete
original-record attempt and interrupted software receipts are retained under
`rejected-candidate/`. D% execution was stopped; overall E/F are null. The full
suite child exited -15, not a pass. This is not hidden by its other green controls
or by its apparent H07 completion.

Kernel v11 constrains the entire main actor phrase: a literal capitalized name
or a small declared collective-noun grammar, with separate modality, reporting,
proposal and near-miss guards. It does not merely suppress the observed examples
at output time. The repaired focused suite passed 67 tests; new full-run results
remain pending at this corrected source freeze. No historical name or benchmark
case identifier appears in the runtime rule.

Commands:

```sh
python -m unittest tests.test_event_date_inventory tests.test_archival_onboarding -q
python -m tools.dpercent run --packets /tmp/dpercent-frozen-public --implementation IMPLEMENTATION --out NEW_RUN
python -m tools.dpercent score --packets /tmp/dpercent-frozen-public --custodian /tmp/dpercent-frozen-private --run NEW_RUN --out NEW_SCORE
python -m tools.article_study --output NEW_ORIGINAL_STUDY
python -m tools.blind_archival_packets --before BASELINE_STUDY --after UPDATED_STUDY --output PUBLIC_REVIEW --custody PRIVATE_CROSSWALK
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/new-archival-public.json
```

Human historical precision/recall, appropriate-refusal rate, candidate-link
accuracy and human intervention costs remain null. External institutional pages
were located for reference context only; they are not human review or independent
corroboration. The primary research use case is archival inspection, not arbitrary
historical narration. See [contract and first use](../../../docs/ARCHIVAL_INSPECTION.md).

## Accepted engineering candidate and measured results

The tested native implementation is **`ee85ab3b3fa501fbee71e102e4de6b7d1bbe48f3`**
(kernel v11), from a complete tracked-source ZIP. All native packages and tests
remain unchanged after that freeze. The tool-only follow-up
`eb5e4b9` adds raw-original context to review exports; its selected-path archive
and end-to-end export checks are separately recorded. Later edits concern
findings, documentation and the dashboard's complete-count display.

| Outcome | Baseline | Corrected |
|---|---:|---:|
| Original-record native complete answers | 2 | 3 |
| Original-record checked partials | 2 | 2 |
| Original-record conflicts | 3 | 3 |
| Original-record abstentions | 15 | 14 |
| D% key-matched complete answers / 600 | 200 | 200 |
| D% expected refusals preserved / 640 | 640 | 640 |
| D% observed false support | 0 | 0 |
| D% execution failures | 0 | 0 |

Only **H07** changes answer meaning. The other 21 native results, exact claim
meaning, source citations and unresolved content are preserved (implementation
versions/proof hashes naturally differ). The updated article assembler also
preserves every standalone contract at its own version. The source seals,
questions and import receipts are unchanged. This is a **native completion gain**,
not independently judged historical correctness or complete-answer recall.

Full D% executed 1,240/1,240 unchanged cases with the same outer sandbox and
12-passage/8,000-character admission budgets. The fixed generator, worker,
scorer, key and sources are unchanged. All 1,240 input/ledger/mode/non-authority
checks passed. No previously complete synthetic answer was lost; no new support
flag appeared on an expected-refuse case. **400 answerable fictional cases remain
incomplete**. `--require-perfect` still exits **1**. The new date-inventory question
form is not represented in the frozen D% generator: D% is regression evidence,
not a precision evaluation of that new proof class. Its adversarial controls and
original-record result must be assessed separately.

**1,468 full Python tests passed**, no failures/skips, plus the native boundary
subset and **52 public-evidence controls**, all exit 0. The focused controls,
fictional tutorial, native/JavaScript API parity, UI script, transport and fixture
crawler also passed. No actual browser/WebAssembly or deployed-site rerun was
performed locally for this candidate; exact PR-head release CI remains separate.
No live model was used.

### Source evidence for H07

[Full typed answer and five original-byte mappings](final/H07-evidence.json)
retain every source ID, sealed hash, canonical interval, original raw-byte
interval and unmodified excerpt. The mappings verify literal round-trip fidelity,
not historical semantic correctness. The accepted source is `ORIGINAL-0006`,
from the unchanged `SUMTER-1861` archival page. The proof separates:

- artillery firing on April 12, as explicitly reported by the narrative;
- surrender on April 13 at 2:30 p.m.;
- evacuation on the following day, with April 14 shown as labelled calendar
  arithmetic and no inferred year;
- April 18, 1861 as the source-body **catalogue** date of the telegram, not proof
  of writing, dispatch, delivery or receipt;
- May 10, 2022 as a review-date text mention, never a historical event date.

The dated clauses and their qualifiers remain quoted. Catalogue/body-field
boundaries are independently located; nearby navigation is context, not proof.
The finite firing category does not resolve a historical event identity. The
original telegram's abbreviated/spelled date text is not silently normalized by
this rule. This is not an exhaustive interpretation of every date form.

The display budget is unchanged. The new rule introduces an explicit **2 MiB
source-owner locator** and **16,000-character/256-unit selected-record scan**,
with 64-source cap. These are separate from the older 200,000-character general
assertion scan; this is not a constant-internal-work ablation. All source access
remains closed-ledger. Costs below disclose the additional work; no efficiency
gain is claimed.

### Costs and reproducibility

The [software receipt](final/software/report.json) pins the full tested ZIP,
commands, CPU/wall times and peak-child memory scope. [Worker cost comparison](final/costs.json)
retains every measured aggregate; explicit ingest bytes are not total internal
source reads. [Original-record report](final/originals/report.json) includes
full runtime module pins and source seals; [comparison](final/comparison.json)
and [case CSV](final/originals/cases.csv) preserve all outcomes. Complete raw
baseline/updated D% executions and anonymous review packets are retained here.

| Measurement | Baseline | Updated |
|---|---:|---:|
| D% post-import worker CPU seconds | 163.545807648 | 168.41882735 |
| D% post-import worker wall sum seconds | 165.32140578910185 | 169.51221668287326 |
| Largest individual worker RSS bytes | 29188096 | 30134272 |
| Explicit original-ingest calls | 6488 | 6488 |
| Explicit original-ingest bytes | 795751 | 795751 |
| Total internal source-read bytes | null | null |
| Human review/correction time | null | null |

The complete updated original-record study took 169.354s wall, 169.057s CPU and 141,189,120 bytes peak process RSS. This includes imports, standalone comparisons and article assembly; it is not per-query latency. The environment is recorded in [environment.json](final/environment.json). Tests shared CPU; no speed gain or aggregate process-tree memory claim.

### Review readiness and remaining limits

The [anonymous packet archive](final/anonymous-review-packets.tar.gz) contains all
22 cases / 44 paired outputs, full eligible canonical projections, unchanged
original bytes, import/source mappings and blank review templates. No draft
reference answers, scores, change log or implementation pins are supplied.
A private crosswalk is kept outside Git/runtime/review packets; its custody
commitment is [recorded](final/review-custody.json). The existing human validator
accepts the collection format and correctly rejects unfilled forms; this control
is [retained](final/review-export-validation.json). It does not authenticate
reviewers or establish semantic agreement.

**Independent human review, fresh blinded AI assessment, unseen 200-question
assessment and adjudication are NOT RUN.** Familiar questions remain familiar
after anonymization. Published institutional reference material located through
search is context only: no author assessed MPLPB outputs, and institutional
separation does not prove independent testimony. None of these pages enters
runtime evidence. Actual independent accuracy, relationship precision/recall,
false-link rates, appropriate refusals and human costs remain null.

The [dashboard](../../../docs/benchmarks/dashboard.md) separates developer-key
rates from authentic native counts and unknown historical rates. The
[first-use guide](../../../docs/ARCHIVAL_INSPECTION.md) supplies an offline tutorial.
Raw material, original records, frozen questions, expected files and earlier
reports are preserved. Source profile/revision/integrity checks and candidate
non-authority remain unchanged. The system is not a general historical reasoner.
H08's OCR/qualification/composition limits and U07's legal modality still require
separate general proof rules and unchanged-input tests.

The five previously diagnosed missing draft-reference spans were not separately
rescored here; their recovery is not claimed. Native completion is distinct from
reference-span retrieval recall. The next source rules must preserve all existing
failures/refusals and be checked on independently authored unfamiliar material.
