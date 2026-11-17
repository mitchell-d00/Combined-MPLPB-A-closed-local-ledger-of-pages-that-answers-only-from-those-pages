# Solo recorded-arrangement milestone

Date: 2026-11-17. Development questions; source-linked **AI assessment**, not human
validation, outside-world authentication or independently unseen evaluation.

## Primary result on the same22 questions

| Fresh-context AI assessment | Before | After |
| --- | ---: | ---: |
| Complete correct answers |1 |2 |
| Correct refusals |4 |4 |
| Incorrect answers or over-refusals |17 |16 |

All44 blinded responses were assessed; none unassessed. This is a one-question
gain, not a solution to the other16 shortcomings. The source-bound completion
changed H02, the Darwin–Wallace arrangement question. H05's opening-wording
comparison remains complete. Correct-refusal judgments remained H10, H11, H12,
and U08. The assessor credits generic refusals on unsupported causal/authorization
demands, with stated uncertainty about their weak explanations. These judgments
are opinions from one fresh AI context, not independently verified historical facts.

The native finite checker also changes H02 from partial to complete source
support, giving2 complete,1 checked partial and19 abstentions/conflicts across22.
The other21 cases preserve native kind, claims, quotations and qualifications
(disregarding verification-version hashes). No new dispatch, receipt, delivery,
execution or historical-truth claim was accepted. The tool does not turn a model's
favorable assessment into runtime support.

## What the additional proof establishes

The current eligible source names CHARLES DARWIN and A.R. WALLACE in its heading,
prints November13th,1859, and states that the writer had told Murray to send a copy
of his book by post “if possible.” The checker now resolves the question's writer,
recipient and possessive object against those explicit local roles and examines
and cites the complete local letter. Its three witnesses are the printed heading,
complete opening instruction and complete letter. The exact original evidence is
retained in `certificate-audit.json` and the AI assessment packet.

This completes a question about the recorded arrangement request and printed
letter date. The printed date does not become the instruction, dispatch, receipt
or delivery date. The request does not establish execution, acceptance or delivery.
Source-declared authorship is not authentication. The complete local letter is
limited to4,000 canonical characters and its syntactic next-letter boundary;
there is no claim to have excluded every later correction in the historical record.
Missing ownership/date, ambiguous local roles, different objects, cancellation
wording, quoted/negated/planned instructions, extra delivery obligations and
insufficient citation budgets cannot close the question.

The original source bytes and frozen questions, seals, references, prior reports
and scoring artifacts were not edited. The change adds no answer-bearing metadata
to historical records. All22 workers completed under identical existing180s wall,
300s CPU and2GiB address-space limits, existing profile and display budgets.

## Frozen implementations and assessment separation

Baseline: `ec41332dbcfce5d6dfd5b9f5e75dd553507bbea2`.
Supporting-tools-only intermediate: `482e4987fec1d91c835a08198b140892bb0dc661`.
Frozen arrangement runtime: `d369346dfcdf4c6cd87866971b352be639506277`.
Test-adjusted release: `80a4b02d0a13ac0f986f83622514c4be5dddd844` (same runtime as d369346; prior H02 partial-only
regression updated to the explicitly requested source completion).

The AI session used fork_turns=none, original byte-pinned documents and randomized
opaque response IDs. It received no before/after labels, developer scores or
change log. `ai-assessment/method.json` records the procedure. Its shared-filesystem
access was constrained by instructions, not a cryptographic sandbox. The model
provider/version pin is unknown; no independent-model or human identity is claimed.
The engine runtime was already frozen before assessment. The assessor's output
is not imported into the ledger or used to add proof rules.

`score_ai_assessment.py` checks all108 supplied source anchors against exact raw
UTF-8 byte slices and pinned source hashes, verifies the corresponding output
hashes, then counts the opinions. It rejects a deliberately fabricated quotation.
Quote fidelity does not validate the assessor's interpretation. Independently,
the fresh deterministic kernel rechecked all3 native claims and8 citation spans,
and reverse mapping reproduced the corresponding original bytes. This certifies
finite-rule/source fidelity only; historical truth remains false/unverified.

## Supporting improvements, counted separately

`reconstruct --format text` presents question parts, linked evidence, exact source
IDs/hashes/offsets, qualifications, alternatives, missing obligations and separate
candidate counts. JSON remains the compatible default. The browser exposes the
same question-part links and canonical offsets. Local STORE observations can now
read and hash a bounded real artifact, with host-only read-only rechecks for changed
or missing bytes. These checks do not prove delivery, human reading or completion.

The immutable record parser cache retains at most8 exact text inputs of at most
2,000,000 characters, returning independent mutable Record objects. Files and
current policy are still reread. Same-size/same-mtime corruption, changed status,
changed restrictions and declared hashes cannot be hidden by the cache. It adds
only the standard-library functools module to the explicit core dependency list.

## Resource measurements

| Arm | Worker CPU s | Worker wall s | Maximum worker RSS bytes | Logical source HTML bytes read |
| --- | ---: | ---: | ---: | ---: |
| Original14 before |801.053 |807.468 |54,362,112 |9,469,870,058 |
| Original14 after |230.350 |230.671 |47,665,152 |9,469,870,058 |
| Government8 before |51.621 |52.838 |22,568,960 |188,813,916 |
| Government8 after |11.934 |11.975 |22,945,792 |188,813,916 |

Combined CPU is852.674→242.284s, about3.5 times less in this run. The intermediate
supporting-only experiment also preserves all22 outcomes and takes234.702+13.679s
CPU, isolating most of this change to parsing reuse rather than the new proof.
Reads include repeated logical read_text calls; no reduced physical disk I/O is
claimed. Same shared Linux x86_64 host, Python3.12.14,5 exposed CPUs; some checks
ran concurrently. These are single-run development measurements, not latency
percentiles, independent measurements or a general performance guarantee. Genuine
human effort, AI inference compute/charges and independent semantic accuracy stay
null when unmeasured. Costs include native answering, discovery and specialist
investigation, not just Ask latency.

## Reproduce

Use separate new output directories and the documented existing frozen harness:

```sh
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation BASELINE_EXTRACT --mode updated --commit ec41332dbcfce5d6dfd5b9f5e75dd553507bbea2 --seal freeze-v2.json --output NEW_BEFORE
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation AFTER_EXTRACT --mode updated --commit d369346dfcdf4c6cd87866971b352be639506277 --seal freeze-v2.json --output NEW_AFTER
```

Repeat for `evaluation/unprepared-originals/2026-11-16-followup/unfamiliar` with
`--seal freeze.json`. Both use mode updated so candidate/expert work is identical.
Place the run directories under `RUNS/{original,government}/{before,after}`.
The existing isolated workers do not mount reference answers or AI assessments.

```sh
python evaluation/solo-milestone/2026-11-17/compare_runs.py RUNS --output NEW_COMPARISON.json
python evaluation/solo-milestone/2026-11-17/certificate_audit.py --runs RUNS --output NEW_CERTIFICATES.json
python evaluation/solo-milestone/2026-11-17/score_ai_assessment.py --packet evaluation/solo-milestone/2026-11-17/ai-assessment --runs evaluation/solo-milestone/2026-11-17 --output NEW_AI_COUNTS.json
python -m tools.reproduce_boundaries --revision 80a4b02 --output NEW_VALIDATION_DIRECTORY
```

Run the certificate audit under the pinned runtime: it checks implementation-file
hashes. The AI score command reproduces counts for the retained frozen outputs;
it does not rerun AI inference. The executed blind packet builder is retained as
`prepare_blind_executed.py`; its /tmp paths document this actual experiment.
For a new AI experiment create new packets and a new response key, keep labels and
keys outside the assessor's supplied directory, and preserve all judgments.

## Failures and limitations retained

The supporting-only full run482e498 ran1148 tests and failed the core dependency
allowlist because functools had not yet been explicitly permitted. The declaration
was updated for this standard-library cache helper; prohibited network/model
imports remain prohibited. The first arrangement full run d369346 ran1157 tests
and failed a prior regression that required H02 to remain partial. That expectation
was updated for the new capability while retaining all party/date/condition,
no-delivery and original-byte checks and requiring the third source witness.
Both complete failed logs and all intermediate historical runs are retained.
Initial new fixture expectations about capitalization and retrieval-versus-display
budget were corrected. No frozen question or historical expected-result file was
changed to obtain a pass.

The Apollo summary remains an over-refusal: its relevant assertions are found,
but OCR quotation state from earlier source material prevents existing certification.
This update does not silently weaken that quotation safeguard. Broader historical
identity, chronology, correction, full-document absence and causal reconstruction
remain incomplete. The16 remaining AI-assessed errors/over-refusals are retained
case by case. This is a small original-source completion gain, not22/22 success,
a9/10 rating,200 unseen questions or general historical understanding.

## Final software validation

The extracted80a4b02 release passed **1157 tests in337.950s** and public **52/52**.
The report retains actual process CPU/wall and maximum child RSS separately.
JavaScript API, browser transport, crawler fixtures and actual pinned WebAssembly
checks passed. Actual Chromium passed11 documentary UI checks, including the prior
nine checks, visible question-part/canonical-offset inspection, three-witness
arrangement completion and refusal to inherit completion for a delivery question.
The release-generated HTML is byte-identical to that browser-tested candidate.
Documentation, handoff and infrastructure audit results are recorded at final
packaging; neither commits nor candidate checks imply a deployed-site release.
