# From Paraphrase Refusal to Bounded Field Access

## A Reproduction and Engineering Response to “Guarded Retrieval, Paraphrase Blindness, and Evidence-Grounded Answering”

**Mitchell D. McPhetridge**  
20 November 2026 — Research engineering report, version 1.0

## Abstract

The 19 November 2026 public evaluation identified a sharp difference between
canonical field requests and five alternative request structures in the pinned
Combined MPLPB strict pipeline [1]. We reproduced its public method-equivalent
script against the exact published source revision: 150 of 150 canonical requests
were supported, none of 750 paraphrases were supported, and all 200 negative
controls were refused. We localized the failure to exact-field question admission,
implemented bounded whole-question normalization in the existing parser, and
repeated the unchanged experiment from a frozen source archive. All 900 positive
requests were supported and their returned field/value text matched the supplied
synthetic key; all 200 negative controls remained refused. This is a repair of
measured request-form coverage, not evidence of general natural-language
understanding or historical truth. We additionally report regression tests,
unchanged historical outcomes, costs and a new sealed known-error stress generator.
Independent semantic review and genuinely unseen evaluation remain outstanding.

## 1. Accepting the measured criticism

Source-boundary discipline and access to supported source content are separate
obligations. A system that refuses a known documented field because a user changes
sentence structure has a usability and completeness defect. The original preprint
correctly limits its result to a strict local interface, isolated synthetic
records and a pinned revision. We reproduce that bounded result rather than
extending it to every MPLPB mode or every possible paraphrase [1–6].

This response is by the software's author and is a development measurement.
It is not an independent reassessment of the corrected candidate. The 750 questions
are correlated instances of five known surface forms, not 750 independent tests
of unconstrained language understanding. No hidden questions or human-reviewed
historical accuracy scores are claimed.

## Software, tests and evaluator attribution

Combined MPLPB and its pre-existing native testing/evaluation infrastructure are
Mitchell D. McPhetridge's software contribution. The separate B-Tests repository
also contains native-suite runners, authored benchmark generators and retained
reproducibility evidence. Its inspected native wrapper calls MPLPB's own unittest
suite and UI/transport/infrastructure/handoff tools; its randomized sorter driver
calls MPLPB's validator, sorter and candidate workspace [12]. These native tests
must not be relabelled as an OOCC implementation or credited as technology newly
introduced by the external evaluation.

The public reproduction script in the evaluated preprint imports
`mplpb_combined.ledger.write`, `mplpb_answers.pipeline.answer_query`, and
`mplpb_combined.reader.PROFILES`. Thus McPhetridge's implementation constructs,
seals and queries the native records and makes the support/refusal decisions.
The external evaluator supplies an additional benchmark: its fixture logic,
question formulations, execution and analysis. Running software through its own
APIs is legitimate evaluation; it does not transfer authorship of that software
or its pre-existing tests. The preprint already credits McPhetridge as MPLPB's
developer. This section makes the roles explicit rather than alleging an
unsupported authorship claim.

The supplied 60-file public package does not include an M6 implementation.
M6 was not shared in that package and was not available for inspection or
independent execution here. The published script does not import B-Tests, M6
or an OOCC implementation.
No execution records supplied here establish M6 as the original harness or OOCC
as the tested component. The running heading “OOCC strict retrieval evaluation”
should be read separately from the actual evaluated system, explicitly identified
in the methodology as Combined MPLPB. A clearer running heading would be
“Combined MPLPB strict retrieval evaluation.” This attribution clarification does
not invalidate the reproduced failure or remove the obligation to repair it.

| Role | Evidence-supported identification |
|---|---|
| Software and strict support/refusal implementation | Combined MPLPB, developed by McPhetridge |
| Pre-existing native test suite and tools | MPLPB repository; B-Tests supplies additional native wrappers and authored benchmarks |
| Public driver used for this reproduction | Unchanged `reproduce.py` from the publication ZIP |
| Original execution platform | Aggregate-results file reports observation on Amplify; that private execution was not independently audited here |
| M6 | Not included in the supplied public package; unavailable for inspection or execution here. No M6-specific interface or execution trace establishes its original role |
| OOCC | Appears in a running heading; no OOCC implementation is demonstrated as the component making these strict answers |

Even if additional records later establish M6 as an orchestrator, orchestration
must be credited separately from the MPLPB implementation it invokes. That would
not make M6 the author of MPLPB, its existing tests, or its strict support rules.
This is a conditional attribution principle, not a finding that M6 actually ran.


## 2. Materials, integrity and reproduction

The supplied publication ZIP is retained unchanged. SHA-256:
`f4d1c8263dbb8dcf9f7ddbc9fc85be5d005864db4c74fce1a93cda1bb4865718`.
All 59 manifest-listed members verified. The ZIP contains a paper in Markdown,
PDF and DOCX, 50 HTML fixture projections, fixture and question CSVs, a public
reproduction script, reported aggregate results, provenance notes, README and
checksum manifest. A separate machine-readable inventory identifies every member,
its byte count and computed hash [7]. It contains 60 files including the manifest
itself; the manifest lists the other 59. All members are cited through that
inventory and retained archive, rather than substituted or rewritten copies.

The paper's private October archive audit was not repeated. Its reported hash,
row counts and count discrepancies remain attributed to that provenance account;
we neither authenticate the private material nor resolve its lineage [6].
No private records enter this public synthetic experiment.

The original published pin is
`bbf6690d69b32d16969cc10e5ce9d380427ead40`.
The immediately preceding development pin is
`3483b1afc7fca0998f0d6874b0c845a2ac94af03`.
Both produced the same 150-versus-750 native-support split. The public script was
read before execution and run unchanged with the selected source on PYTHONPATH.
The 900-query CSV contains only positive requests. Four negative controls per
record are generated separately by the script: total engine calls are 1,100.
This reconciles the apparent 900-versus-1,100 population difference.

## 3. Failure mechanism and bounded repair

`mplpb_answers/relation_graph.py::exact_request` recognized a full-match pattern
for “What is the FIELD for/of record/event/occurrence ID?”. Other questions still
located an explicit record identifier, but supplied no parsed field. On all 750
baseline CSV paraphrases the native pipeline ended at `exact_field_missing`.
The source field was present. The missing object was an admitted field request,
not a missing historical fact.

The repair adds general imperative, record-first, possessive and interrogative
structures with literal field and identifier slots. It does not branch on
benchmark identifiers, record values, file names or expected labels. The source
checker is unchanged. Two further whole-question classes, record-context field questions and
record-labelled imperatives, were subsequently exposed by the frozen stress
batch and tested with independent vocabulary before repair.
Additional independent-vocabulary examples use custody
locations rather than the publication's three field labels [8].

Whole-question matching is required. The parser must not remove “before the
revision,” attribution, negation, another record, or a second requested fact.
Unsupported clauses remain unresolved. The new route rejects contradictory
explicit selectors. It does not equate “current state” to “Current Status,” or
infer completed execution from any status value. Broader lexical semantics is a
separate unresolved problem.

The original question remains the gate's policy input. A separate
`question_normalization` object records the admitted identifier, literal field,
canonical request, implementation version, and `normalization_is_evidence: false`.
A recognized question is not proof. Currently eligible source-body fields,
provenance, exact quotation, conflicts, corrections, delivery profile, resource
budgets and final source-state checks remain necessary. The `mplpb_combined`
ownership, hash and reader core is unchanged [8–9].

## 4. Results on unchanged public questions

| Condition | Published pin | Before change | Corrected archive |
|---|---:|---:|---:|
| Canonical supported | 150/150 | 150/150 | 150/150 |
| Five paraphrase forms supported | 0/750 | 0/750 | 750/750 |
| Nonexistent identifier refused | 50/50 | 50/50 | 50/50 |
| Missing field refused | 50/50 | 50/50 | 50/50 |
| Machine-origin external-profile refusal | 50/50 | 50/50 | 50/50 |
| Unsupported identity inference refused | 50/50 | 50/50 | 50/50 |

All unchanged script runs exited 0; no positive-query exceptions were recorded.
A separate post-run scorer compared every accepted field/value text against the
public CSV key. The baseline matched 150/900 requests. The corrected archive
matched 900/900, with zero observed wrong supported field/value outputs. Expected
values were not provided to `answer_query`. Full individual contracts, exact
citations, questions and scores are retained in compressed JSONL [9].

Zero observed false support on these 200 negative controls is a bounded sample
observation. The four families and repeated records are not a basis for a universal
zero-error guarantee. Further adversarial testing is necessary.

## 5. Regression and historical preservation

The final frozen source revision is
`9b5ff0c220780875359a74918b3ad4dd50bf4d89`, ZIP SHA-256
`d11a24e93f1e471dd3b7ce09bed5a39c10b7127cc7b7f5178478473d678edc61`.
Its complete extracted Python suite passed **1,482 tests** (exit 0), followed by
**52 public-evidence controls** (exit 0), with zero observed supported bridges in
those controls. Native boundary checks, UI-script checking, JavaScript API parity,
browser transport and crawler checks passed. Three CLI checks accepted the new
literal-field form (exit 0) and refused an added past-time qualification and an
external-profile request (both expected exit 3). The kernel and source packages
remain unchanged after this tested pin; later additions are evidence/documentation.
An additional non-authoritative citation-readback script was run separately.

All 900 accepted public-fixture citations were reread against exact canonical
source text, matching source IDs/hashes/paths/offsets and fresh default-profile
eligibility at the recorded check time. This is quotation and policy readback,
not independent semantic or historical judgment. It does not certify perpetual
eligibility after future source changes.

Failures were retained: the original new-form regression failed, two later
record-context classes failed on four independently worded subcases, and a
post-run scorer mutation exposed missing citations passing a vacuous quotation
check. The parser fixes address complete syntax classes; the scorer now requires
citations for every accepted field claim. Initial and hardened scoring agree on
all actual baseline executions. A follow-up archive run at `2aca624` lost its
environment before completion; its partial logs have no final exit code and are
not counted as a pass. The later complete 9b5ff0c run supersedes that attempt.
Actual browser/WASM and deployed-site verification were not rerun locally.

The 22 unchanged original-record questions retain three native complete answers,
two partial answers, three conflicts and fourteen abstentions. This normalization
change demonstrates no new historical completion gain. Native article-assembly
preservation, unchanged source/ledger checks and existing truth disclaimers remain
separate from semantic correctness. The authentic sources and prior question keys
were not edited [10].

The original frozen 1,240-case D% suite was rerun at the first repaired field
candidate 044ac27: 200/600 key-matched complete answers and 640/640 expected
refusals, with zero observed false support or execution failures. Its 400 missed
positive cases remain failures. This is regression evidence, not validation of
new question forms absent from that original generator. That full population was
not rerun after the subsequent two context-form additions; the final 1,000-case
comparison below measures those additions directly.

## 6. Known-error structural expansion

The expanded D% tool retains the existing isolated worker and all old frozen
cases. It combines 31 original documentary-prose families with 17 new field-access
and boundary families. It varies question structure, field vocabulary, CRLF/LF,
Unicode, repeated and changed identifiers/bodies, quoted or reported headers,
conflicts, missing causal links, restrictions, withdrawal and corruption. It has
a conservative 1,440 field structural cells before further original-prose
variations. No acceptance-language filter discards difficult questions [11].

Synonyms and compound requests remain positive obligations even when unsupported
by the current checker. The scoring key and every d100 draw are sealed outside
the runtime. Public packets contain only sources, questions and execution budgets.
Both missed answers and false support are counted. Matching source words alone
cannot award historical relationship correctness. Semantic shapes without an
independent finite scoring rule remain unscored rather than receiving credit.

Both runs completed the same frozen 1,000 cases under identical source access
and execution/admission budgets: 420 expected-answer and 580 expected-refuse.
The first repaired candidate matched 156/420 complete answers (37.14%). After the
two additional whole-question classes, the final candidate matched 168/420 (40%).
Over-refusals fell from 264 to 252. All twelve changes were previously missed
literal-field obligations; no complete answer was lost. All 580 expected-refuse
cases remained refused in both runs (F=0/580). Execution failures and supported
outputs without scoring coverage were zero in both runs.

| Frozen stress metric | First repaired candidate | Context-form repair |
|---|---:|---:|
| Key-matched complete answers | 156/420 | 168/420 |
| Developer-key over-refusals | 264 | 252 |
| Expected-refuse cases refused | 580/580 | 580/580 |
| False-supported refusal cases | 0/580 | 0/580 |
| Execution failures | 0 | 0 |

The entire stress batch does not pass its completeness target. Twelve positive
families still miss all 21 cases each: synonyms, compound fields, date roles,
earliest observed chronology, explicit chains, complete-header location,
identical wording, instructions, negated statements, partial corrections,
reported statements and wording comparisons. These 252 cases remain visible,
with per-family and per-question-structure denominators. They are targets for
future general proof rules, not justification to relabel questions or weaken
support requirements.

This batch is developer-authored known-error stress testing. It is not hidden or
independent evaluation, and generated labels are not external historical judgments.
Further changes must target general failure classes, retain negative controls,
and rerun the unchanged sealed batch. A new generator revision needs a new seal;
old failures must remain inspectable.

## 7. Costs and reproducible commands

The final frozen-archive 900-positive CSV scoring run used Python 3.12.14 on
Linux x86-64. It took 6.572 seconds wall and 6.525 seconds CPU, with peak process
RSS 16,875,520 bytes. The before-change run took 4.338 seconds wall and 4.335 seconds
CPU, with 16,908,288 bytes peak RSS. These are shared-environment observations,
exclude fixture ingestion and are not a hardware-normalized speedup claim.
The environment reported Intel Xeon Platinum 8573C, five affinity CPUs, a four-CPU
cgroup quota and 16 GiB memory limit. Final full-suite process wall time was
556.469 seconds and CPU time 537.335 seconds. The archive runner's maximum child
RSS was 501,297,152 bytes, not aggregate process-tree memory.

For the expanded batch, worker CPU sums were 102.452 then 100.350 seconds;
worker wall sums 103.009 then 101.053 seconds. Parent per-case wall sums, including
launch/isolation overhead, were 431.504 then 426.536 seconds. Worker timing starts
after module imports and includes the timed source ingestion/retrieval/sorter/answer
work. Both runs explicitly read 3,727 packet sources, 474,898 bytes. Those are
instrumented packet reads, not all internal engine I/O. Total internal source
bytes read and human review time remain null. No speedup is established by these
shared-environment observations [9,11].

Extract the retained public ZIP to PACKAGE. Use a new output directory per run.
From a source checkout at the selected revision:

```sh
PYTHONPATH=. python PACKAGE/reproduce.py --output /tmp/new-public-run
python -m tools.evaluate_field_questions --package PACKAGE --fixtures /tmp/new-public-run/fixtures --output /tmp/new-public-score
python -m unittest tests.test_field_question_forms tests.test_dpercent_expanded -q
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/new-public-controls.json
```

The original pin lacks the new CSV scorer; run the preserved scorer script with
that pin on PYTHONPATH, as documented in the experiment receipts. `git archive`
freezes tracked source. `tools.reproduce_boundaries` records its revision, ZIP
hash, per-command exits, logs and measured costs before any final report claims.
The D% generation, run and custody-separated scoring commands are documented in
`docs/DPERCENT_EXPANDED.md` and the retained protocols [9–11].

## 8. Remaining claims and non-claims

The measured request-form defect is repaired for the unchanged public test.
That does not establish arbitrary paraphrase coverage, reliable pronoun/entity
resolution, event co-reference, causal reconstruction, source independence,
correction accuracy across unfamiliar prose or general complete historical answers.
Source integrity, source-attributed support and historical truth remain distinct.
Independent human review, fresh blinded semantic assessment and a genuinely unseen
multi-domain study remain NOT RUN. The private archive audit also remains outside
this reproduction. M6 is not supplied by the public package; no M6 capability
comparison follows from these results. Neither the original preprint nor this response warrants a
universal reliability or production-readiness claim.

## References and evidence inventory

1. *Guarded Retrieval, Paraphrase Blindness, and Evidence-Grounded Answering*,
   19 November 2026 research preprint, supplied public package. The distributed
   Markdown does not supply a full author byline; no surname is invented here.
   Publication folder: https://drive.google.com/drive/folders/1i_n34wkDoHEky-5p7-pmu4Xs2IPblli0 .
   Preserved members: `paper.md`, `paper.pdf`, `paper.docx`.
2. Same package, `reproduce.py` and `README.md`: public method-equivalent script,
   pinned source, seed, isolated native fixture construction and execution.
3. Same package, `fixtures.csv` and all 50 `fixtures/REC-*.html`: synthetic values
   and logical fixture projections; individual hashes in reference 7.
4. Same package, `test_questions.csv`: all 900 positive requests, paired record,
   field and question-form labels.
5. Same package, `results/measured_results.json`: reported native-support and
   negative-control aggregates; reproduced here within their declared scope.
6. Same package, `SOURCE_PROVENANCE.md`: attributed private-archive provenance
   and unresolved row-count reconciliation, not independently repeated here.
7. Same package, `MANIFEST_SHA256.txt`; our complete member inventory:
   `evaluation/field-question-normalization/2026-11-20/external-file-inventory.json`.
   Every file in the public ZIP is retained, individually hashed and accounted for.
8. Combined MPLPB source: `mplpb_answers/relation_graph.py`,
   `mplpb_answers/pipeline.py`, `tests/test_field_question_forms.py`.
9. `evaluation/field-question-normalization/2026-11-20/REPORT.md`, public ZIP,
   baseline/updated/archived JSON/JSONL and software receipts;
   `tools/evaluate_field_questions.py`; `docs/FIELD_QUESTION_NORMALIZATION.md`.
10. Unchanged original-record replay receipts in reference 9; previous source/date
    experiment `evaluation/archival-inspection/2026-11-19/REPORT.md`.
11. `tools/dpercent.py`, `tools/dpercent_worker.py`,
    `tools/dpercent_expanded.py`, `tests/test_dpercent_expanded.py`,
    `evaluation/dpercent-expanded/2026-11-20/REPORT.md` and sealed protocols.

12. McPhetridge's B-Tests repository, inspected commit
    `7771497bb2aea6ae5f55fc9255798781bb45af22`:
    https://github.com/mitchell-d00/B-Tests/tree/7771497bb2aea6ae5f55fc9255798781bb45af22 .
    `research_lab/mplpb_native_suite.py`, `research_lab/sorter_random_batches.py`,
    `make_cases.py`, repository README and current acceptance workflow.
    Pinned source excerpts/hashes and import-role findings are retained in
    `evaluation/field-question-normalization/2026-11-20/attribution-evidence.json`.
    Inspection establishes code roles, not undocumented private harness use.

Repository: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages .
