# Independent contextual-answer evaluation protocol

Status: protocol and execution tooling prepared; independent recruitment, annotation,
execution and audit **not performed**. The bundled 54 probes and all current results
are assistant/developer-authored development evidence. No score here demonstrates
production readiness or independent validation.

## Primary question

Does topic-bound chat refuse unsupported questions despite shared vocabulary,
while answering a useful fraction of questions the selected page does support?
A page's lexical ownership is not evidence that it answers the question. Provenance
pins establish byte consistency, not factual truth, authorship or semantic entailment.

## Freeze and independence

An independent coordinator recruits at least six corpus owners across distinct real
workflows (for example workshop procedures, library services, office operations,
software operations, public science education, and transport information). Obtain
permission to use each corpus. Use stable pseudonyms where identity is confidential.
The coordinator records funding, conflicts, prior involvement, roles and dates.
The code authors must not author, label, adjudicate or inspect the final questions
before results are locked. A tool cannot certify these relationships.

Freeze a code commit, exact engine hashes, full corpus file hashes, question JSON,
annotation rubric, metrics, sampling procedure, seeds and decision thresholds in a
signed or timestamped registration held by the coordinator. Public hashes can cover
private material; do not publish sensitive source bodies or user transcripts.
Separate development and final-test corpora by source organization and question
author, not just random questions from the same templates. No holdout tuning.

## Sample and labels

Proposed final sample: 100 supported and 100 unsupported questions per domain,
1,200 total. Register final counts and strata before collection. Include naturally
occurring user questions as well as deliberately adversarial questions, reporting
those strata separately. Log exclusions before running; retain excluded IDs and reasons.

Unsupported strata include permission versus procedure, same vocabulary/different
entity, missing attributes, changed conditions, negation, conflicting statements,
hypotheticals, wrong units, stale/withheld sources, and attempted instruction
injection. Supported strata include pronouns, natural paraphrases, multi-turn
follow-ups, source selection, and retrieval after restart. Include ordinary questions
the finite recognizer cannot parse: these must count as missed coverage, not be removed.

Two reviewers independently inspect page bodies and the selected-topic/question
history without seeing system outputs, gold labels, scope fields or exclusions.
They label supported, unsupported, ambiguous or invalid, cite exact evidence spans,
provide a rationale, and record confidence. Evaluate permission questions against
explicit permission evidence, never against vocabulary overlap. A third independent
reviewer adjudicates disagreement before predictions are exposed. Preserve both
initial labels, agreement/confusion counts, and the adjudication record. Treat
ambiguous questions as requiring a non-answer in the binary runner and retain their
original category for separate reporting. Invalid cases are excluded before scoring.

`prepare_chat_review.py` emits a blinded packet, but the supplied practice packet
is still developer-authored. External annotators need independently collected material.
An annotation row should preserve: case ID, reviewer pseudonym, original label,
verbatim evidence, rationale, confidence, time spent, adjudicator, final label and date.
Do not overwrite the initial review with the adjudicated label.

## Running and scoring

Use `evaluate_grounded_chat.py`. External manifests use `root` and `corpus_sha256`
(an exact map of relative files to SHA-256), instead of inline `pages`. The runner
requires the independently registered manifest SHA-256 and fails on changed bytes.
Keep session sources writable only in a separate temporary directory. No remote
search is authorized by a probe; mock/deny network at execution and record that policy.
Do not use unsolicited production queries or send private corpora to external models.

Primary measures, with denominators and per-domain counts:

- Unsupported false acceptance = answered unsupported / all unsupported.
- Answer precision = supported, evidence-correct answers / all answers.
- Answerable coverage = evidence-correct answers / all supported.
- Unnecessary refusal = non-answers on supported / all supported.
- Wrong answers on supported questions, conflicts, clarifications and source offers.

Publish all predictions, quotations, source pins, traces and failures. For protected
corpora publish redacted rows and an auditor-access procedure. The runner checks exact
span agreement only; reviewers must separately judge answer relevance, sufficiency,
qualifier retention and misleading extra text. Gold-span inclusion alone is not proof
of correctness. Compare the prior lexical page-return behavior on the same cases;
that baseline is retrieval, not a semantic answer engine. A refuse-all baseline has
zero unsupported acceptance but zero coverage and undefined answer precision.

Wilson 95% intervals in the runner are descriptive. For final inference, cluster
resampling by organization/source and question author is required because probes
are correlated; publish the resampling implementation and seed with the independent
analysis. Report paired changes and macro/per-domain results, not only pooled accuracy.

Proposed research progression criterion to register *before* collection: pooled
unsupported false-acceptance upper 95% bound <= 1%, per-domain <= 5%, answer-precision
lower bound >= 95%, and coverage >= 60% in every domain. These are research targets,
not a critical-use safety standard. Hazard-specific thresholds and an independent
risk review are necessary before any critical deployment. Failing any criterion
means report the failure, not change the cutoff. A new release needs a new untouched
holdout after tuning on failures.

## Operational experiments and authoring burden

Run repeatable scale tests at registered corpus sizes and realistic page lengths,
with cold/warm caches, concurrent clients, browser memory and persistence quotas.
Report median, p95/p99, throughput, errors, timeout rate, hardware/runtime and raw
samples. `benchmark_grounded_chat.py` currently measures only short synthetic pages,
one process, five repetitions: it is a diagnostic, not an SLA or stress certification.

Security review must independently examine HTML/URL injection, source instructions,
SSRF/crawler redirects, large inputs, regex/parser resource exhaustion, changed pins,
profile isolation, save corruption, concurrency, interrupted writes and recovery.
The repository's automated boundary tests cover examples, not a penetration test.

Run a consented pilot with corpus owners and users. Record question success,
unsupported-answer incidents, refusal comprehension, source-offer behavior, confusion
between quotes and truth, accessibility, and recovery after restart. Measure human
minutes per authored page, exclusions per page, collisions, revision effort and
maintenance at increasing corpus sizes. This release needs no new attribute metadata
for recognized prose, but carefully authored source content is still required.

## Release claims

The runner always emits `independence_verified: false`; coordinator declarations
are recorded, never promoted into proof. An independently signed report can provide
additional evidence outside that flag. Until then describe this as a deterministic,
source-bound research prototype with developer regression evidence. Do not call the
54-probe experiment an independent benchmark, semantic reasoning proof, or safety
validation. Do not claim that no observed failures means zero risk.
