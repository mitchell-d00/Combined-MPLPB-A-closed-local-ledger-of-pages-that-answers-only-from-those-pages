# Test Index for humans and AI

Last reviewed: 2026-11-25.

[Cryptid local programme](../evaluation/cryptid/README.md): sequential frozen shared-operation studies, retained failures and local-only review package. Current execution state is recorded separately from planned tests.

This is the starting point for running, interpreting, and extending Combined
MPLPB tests. Use the [test commands](TEST_TOOLS.md) to run a suite, the
[machine-readable inventory](results.json) to find the retained artifacts,
regression files, runners, and measurement scope for every indexed evaluation
family, and the [results guide](RESULTS_AND_TESTS.md) to read the reported results.

[Pole](../evaluation/pole/README.md) uses seeded difficulty levels and pinned documentary cases to measure general rule repairs.

[Current continuation](../evaluation/bubble-wrap/2026-11-25/README.md) passes **280/280** development/preservation after retaining the first16/24 transfer failure. **BW-BYLINE** adds [nine frozen metadata/governor controls](../tests/test_documentary_byline_units.py), [source seal](../evaluation/bubble-wrap/2026-11-25/continuation/byline-tests-freeze.json) and [before/after outcomes](../evaluation/bubble-wrap/2026-11-25/continuation/guard-summary.json):6/9→9/9, including one exposed false-supported conditional fragment now withheld. Origin PR103; protected operation is source-scoped metadata boundaries without pruning a governor. Reproduce with `python -m unittest tests.test_documentary_byline_units -v`. The expanded [280-case manifest](../evaluation/bubble-wrap/2026-11-25/continuation/development.json) and [unchanged-key seal](../evaluation/bubble-wrap/2026-11-25/continuation/freeze.json) link exact inputs and preserve the consumed first transfer separately. Fresh composition transfer passes **16/24 → 24/24**, twelve positive answers and twelve withholds, zero false support. [Once-only completion](../evaluation/bubble-wrap/2026-11-25/fresh-transfer/completion.json), [score](../evaluation/bubble-wrap/2026-11-25/fresh-transfer/candidate-score.json), [ZIP validation](../evaluation/bubble-wrap/2026-11-25/continuation/validation.json).

## Bubble and Wrap: failure → rule → protection → result

[Current cycle](../evaluation/bubble-wrap/2026-11-25/README.md) implements the
maintainer’s [frozen plan](../evaluation/bubble-wrap/2026-11-25/inputs-received/bubble-wrap-plan.json)
on PR #103. [Case registry](../evaluation/bubble-wrap/2026-11-25/registry.json)
and [native-test registry](../evaluation/bubble-wrap/2026-11-25/native-test-registry.json)
provide stable IDs and per-test origin PRs, mechanism, protected rule, frozen
input hashes, baseline pin, budgets, reproduction command and custody status.
Join those IDs to [immutable execution records](../evaluation/bubble-wrap/2026-11-25/runs),
[hash-linked run ledger](../evaluation/bubble-wrap/2026-11-25/run-ledger),
and separately appended score records for actual candidate pins, raw outputs
and measured outcomes. A registry entry marked PLANNED is not a passing test.

| Stable family | Protected distinction | Frozen inputs / actual results |
|---|---|---|
| BW-REPORT / BW-RPT-001…032 | Reporter/writer/actor; inner/outer denial; conditional report versus independent authorship | [32-case matrix](../evaluation/bubble-wrap/2026-11-25/wrap/matrix.json), [key](../evaluation/bubble-wrap/2026-11-25/wrap/matrix-key.json) |
| BW-INVENTORY / BW-INV-* | Reproduced old mechanisms and unaffected answer/partial/conflict contracts | [111 retained cases and overlap memberships](../evaluation/bubble-wrap/2026-11-25/registry.json) |
| BW-ATTRIBUTION / BW-ATTR-* | Signed instructions, speaker/recorder/writer and execution withholds | [96 consumed instruction cases](../evaluation/bubble-wrap/2026-11-25/registry.json) |
| BW-PE02 / BW-PE02-* | Historical checked partials, complete answers and unresolved attribution | [17 preservation descriptors](../evaluation/bubble-wrap/2026-11-25/registry.json); restricted originals/raw receipts stay in custody, public hashes/comparisons remain |
| BW-GUARDS / unittest ID | Source eligibility, qualified/quoted contexts, counterevidence, mutation and fixed budgets | [Guard tests](../tests/test_reported_content.py), [baseline failures](../evaluation/bubble-wrap/2026-11-25/baseline-native-guards/output.log) |
| BW-FOCUSED, BW-INTEGRITY | Permanent 56 controls and applicable older authority/integrity checks | [Native gate registry](../evaluation/bubble-wrap/2026-11-25/native-test-registry.json) |
| BW-ACCOUNTING, BW-ENV-* | Executed versus scored versus planned; fail-closed isolation | [Accounting tests](../tests/test_bubble_wrap_accounting.py), [required sandbox gate](../evaluation/bubble-wrap/2026-11-25/gates/BW-ENV-004/record.json) |

The twenty proposal cases are memberships within the 111, not extra independent
samples. Per-input semantic hashes expose overlap. Compare actual claims,
qualifications, missing obligations and citations; answer totals cannot hide
false support. Approved intended recoveries are explicitly allowlisted.

Baseline [score](../evaluation/bubble-wrap/2026-11-25/baseline-score.json):
256 completed/scored; 230 expected decisions pass, 26 target misses, zero
false-supported claim cases. The ten old primary misses and sixteen new
source-scope targets are retained. This does not declare every preserved old
question answered: known non-target misses remain separate.

Development now passes **256/256** under the [versioned projection correction](../evaluation/bubble-wrap/2026-11-25/scorer-amendment-v3.json), with all ten primary targets, correct Wrap decisions, all earlier claims/contracts preserved and zero final false-supported claim cases. The [initial frozen-scorer rejection](../evaluation/bubble-wrap/2026-11-25/candidate-001-score-v1.json) remains failed; no key or reader edit followed that projection correction. See [joined scores and limits](../evaluation/bubble-wrap/2026-11-25/development-review.json). Twenty-eight non-target positive questions remain incomplete; preservation is not answer coverage. All 169 indexed native controls pass. That earlier development snapshot is preserved; the current continuation and ZIP results are linked above. Publication CI remains separate.

First committed transfer failed **16/24**, with eight positive misses and zero false support; [failed score](../evaluation/bubble-wrap/2026-11-25/transfer/candidate-score.json). It is now consumed development. The [fresh composition seal](../evaluation/bubble-wrap/2026-11-25/fresh-transfer-freeze/seal.json) precedes further native repair; the fresh result is separately24/24, with all failures retained and no native edits after opening.

The original [24-case transfer seal](../evaluation/current-failure-inventory/proposal/transfer-seal.json)
is preserved and unopened at harness freeze. Run only after a committed ZIP
candidate freeze; publish its result separately. Once it informs a repair it
becomes development material. Same-operator isolation is not independent
preparation, blinding or adjudication. Independent history/semantics,
outside-custodian scoring and native OOCC remain NOT_RUN.

Run `python tools/audit_bubble_wrap_delivery.py` to audit IDs, seals, run accounting,
links and omitted attempts. Frozen audit v1 remains retained; delivery v2 corrects
its misclassification of score rows as execution rows without changing worker,
adapter, scorer or frozen expectations. Every denied launch and publication/audit
failure stays visible in the ledger.

## How I train a deterministic AI

I use tests to train Combined MPLPB by changing the rules that govern its
decisions. The tests supply examples, counterexamples, and measurements. A
versioned code change is where the learning persists. Running a test alone
changes neither the reader nor a user's ledger. Synthetic facts stay in
disposable evaluation collections.

1. Freeze the source bytes, expected answers, controls, and engine revision.
2. Run the native path and record the answers, cited revisions, refusals, and
   diagnostic outcomes. Capture actual output before scoring.
3. Group misses by the decision they share. Trace intake and eligibility,
   retrieval and owner selection, and evidence verification separately.
4. Propose one bounded rule for a demonstrated class. Check independent wording,
   changed actors and values, missing evidence, competing owners, and source
   eligibility around that rule.
5. Replay the same fixtures. Keep the original miss, the changed result, and
   every still-unresolved case. Review changed cases individually before
   promoting the rule.
6. Check fresh structural variants and independently reviewed real records.
   Give any holdout that guided a fix a new role as a development regression.

### My spectrum of rules

On one end is a patch for a particular sentence. It can make a fixture pass
while leaving the same mechanism broken elsewhere. Repeating that pattern is
whack-a-mole. In the middle is a bounded rule for a demonstrated class, with
evidence defining when it applies and controls defining when it stops. On the
other end is a broad guess that treats similar wording as authority. MPLPB
targets the middle. A rule can recognize more forms while remaining narrow about
record identity, eligibility, attribution, and what the source actually says.

A shared diagnostic alone can group symptoms. To test a proposed mechanism,
change one factor while keeping the evidence fixed. In D20 the canonical
selector probe changes only the question. A recovered answer shows that those
same eligible bytes can support the owner through the known path. It narrows
the investigation to question interpretation or record identity lookup, while
code tracing and independent tests are needed to establish the exact rule.

The expanded D20 run used 64 seeds and 1,280 matched cases. The canonical
selector recovered 192 of 256 misses. The remaining 64 needed an additional
layout change: moving an intervening prose line below the owner field. This
distinguished alternate question grammar, explicit alias binding, and the
declared-field boundary. Those are candidate rule classes to test separately.
All 960 stop controls withheld a single owner, and only 64 of 320 competing
cases explicitly recognized the conflict. Keep that distinction when grading
a future repair.

The first bounded repair recognized alternate owner wording and reused the
existing exact owner-field proof. On the same fixtures, supported answers
rose from 64 to 128 and explicit conflicts rose from 64 to 128. All 960
stop controls still withheld a single owner. Keep the later alias and layout
rules separate so each can be evaluated against its own evidence and failure
conditions. [D20 class study](../evaluation/d20/README.md#large-study-and-class-level-probes)

## D-series tests named after game dice

The D-series names come from game dice. The current names are D4, D6, D8, D10,
D12, D20, D%, and D100. D100 and D% both draw on percentile dice and name
separate experiments. Dice Bag draws live records.

| Suite | What it measures | Reproduce or inspect |
|---|---|---|
| **D4** | Event identity, local co-reference, documentary proof and controls | [Native runner and reproduction](D4_EVENT_IDENTITY_COREFERENCE.md) · [Retained case study](../evaluation/d4/2026-11-20/CASE_STUDY.md) |
| **D6** | Six declared-field operations for matches, contrasts, year arithmetic, branching and cited answer compilation | [Runner, worked example and Dice Bag corpus replay](../evaluation/d6/README.md) · [Calendar, notes and lexical discovery](../evaluation/d6/calendar-notes/README.md) |
| **D8** | Eight controls for the handoff from owner lookup to strict proof and a complete or partial answer | [Ownership handoffs and reproduction](../evaluation/d8/README.md) |
| **D10** | Ten topic draws for a selected D% class, frozen source sampling, and matched quotation controls for the implemented exact-anchor suite | [Index, captures, and replay](../evaluation/d10/README.md) |
| **D12** | Matched relation and evidence-path perturbations, frozen historical trace, and citation readback | [Generator and historical replay](../evaluation/d12/README.md) · [Proposed human pilot](../evaluation/d12/HUMAN_PILOT.md) · [Pattern fix sprints](../evaluation/d12/pattern-sprints/README.md) · [Rule-training coordinator and API](../evaluation/d12/coordinator/README.md) · [Candidate rule construction](ADVANCED_MPLPB.md#semantic-rules-and-candidate-construction) |
| **D20** | Matched owner and alias cases, including competition, missing fields and retired evidence | [Seeded replay and rule-class study](../evaluation/d20/README.md) |
| **Dice Bag** | Randomized live-web catalog records, blind replay, strict evidence and synonym lookup | [Custody, replay and first results](../evaluation/dice-bag/README.md) |
| **D100** | Randomized sorter/workspace cases across separate ledgers, with source isolation and exact workspace replay | [External B-Tests runner and five-batch replay](https://github.com/mitchell-d00/B-Tests#repeatable-d100-test-with-100-web-sourced-topics) · [Local companion replay](../evaluation/sorter-exploration/2026-11-19/d100/REPORT.md) |
| **D%** | Stratified randomized prose and refusal cases, with a separate custodian key | [Original study](DPERCENT.md) · [Expanded generator](DPERCENT_EXPANDED.md) · [Known-weakness sampling](DPERCENT_KNOWN_WEAKNESSES.md) |

### External harness

**B-Tests is an external test harness in its own repository.** It runs pinned
versions of MPLPB from outside the MPLPB checkout and retains its own source
packets, scoring keys, commands, and results. Its MPLPB coverage includes
mixed-dump and D100 sorter/workspace replays, public-paper reader probes,
native work and dispatch controls, and comparative studies. Cite the B-Tests
revision and the MPLPB revision when reporting a replay. External execution
and independent human review describe separate kinds of evidence.
[B-Tests harness and full experiment catalog](https://github.com/mitchell-d00/B-Tests)

## Choose the test that answers your question

| Test type | What it contributes to training or verification | Start here |
|---|---|---|
| Native unit and regression tests | Keep corrected behavior and previously enforced invariants during code changes | [Run Python tests](TEST_TOOLS.md) · [Test files](../tests/) |
| Synthetic D% and D4 | Find recurring gaps across controlled source and language structures, with explicit denominators | [D%](DPERCENT_KNOWN_WEAKNESSES.md) · [D4](D4_EVENT_IDENTITY_COREFERENCE.md) |
| D20 owner and alias replay | Compare matched ownership, competition, missing-field, and retired-source cases, then group repeatable misses | [D20 fixtures, study, and results](../evaluation/d20/README.md) |
| Frozen repairs and adversarial replays | Check bounded fixes and verify that provenance, one-owner stops, and refusal decisions survive the change | [Field-question normalization](FIELD_QUESTION_NORMALIZATION.md) · [Ownership evidence](../evaluation/ownership/) · [Kill tests](../killtest/) |
| Public evidence and lab reference sets | Reproduce declared capabilities and negative controls with sealed inputs | [Public evidence](PUBLIC_EVIDENCE_TESTS.md) · [Reference corpus](../reference_corpus/README.md) |
| Raw originals, sorter, and candidate workspace | Locate extraction, mapping, or review issues before testing answer coverage | [Sorter](PREPROCESSING_SORTER.md) · [Candidate workspace](CANDIDATE_REVIEW_WORKSPACE.md) · [Original-document results](RESULTS_AND_TESTS.md#unprepared-original-conversion-study--2026-11-16) |
| Primary books and fresh open records | Draw new source material and test citations or authored questions on material outside the synthetic generator | [Primary Book Test](TEST_TOOLS.md#primary-book-test) · [Fresh open-data batch](TEST_TOOLS.md#collect-a-fresh-real-world-test-batch) |
| Cross-domain persona and corpus transfer | Compare matched field lookups, natural record descriptions, and scope controls across eight domains | [Persona transfer panel](../evaluation/persona-corpus-transfer/README.md) · [Synonym index experiment](../evaluation/persona-corpus-transfer/README.md#experimental-synonym-index) |
| Historical studies and human review | Check attribution, missing evidence, completeness, and disagreement on unfamiliar originals with an independent key | [Archival inspection](../evaluation/archival-inspection/) · [Historical expert path](HISTORICAL_EXPERT_PATH.md) · [Researcher pilot archive](../evaluation/researcher-pilot/) |
| D12 solo post-freeze pilot | Draw and seal fresh historical source packets, then compare passage discovery and proof with a precommitted source key | [24-question FRUS run](../evaluation/d12/solo-post-freeze/README.md) |
| Live graph flag sync | Check that read/write passes reuse eligible candidates and that a strict presentation withholds on a flag mismatch | [Graph controls](../tests/test_experience_graph.py) · [Advanced graph commands](ADVANCED_MPLPB.md#live-experience-graph-and-strict-flag-matching) |
| J/Opass | Check the Observer and Judge warnings on historical and authored cases, then test model layout choices | [Presentation and live model results](../evaluation/d12/j-opass/README.md) |
| Scout | Measure interpretation, discovery, and cross-document proof on newly drawn historical sources after an engine freeze | [Scout protocol, results, and replay](../evaluation/d12/scout/README.md) |
| 4score20 historical prose | Trace question interpretation, relevant passage discovery, and proof in context on the same frozen cases | [4score20](../evaluation/d12/4score20/README.md) |
| Historical 22 pattern expansion | Compare quote discovery, matched direct/paraphrased questions, and scope controls on the same originals | [Run and results](../evaluation/historical-patterns/README.md) |
| Historical synonym graph comparison | Compare graph-guided passage discovery on frozen and new history topics | [Study and new source records](../evaluation/historical-synonym-graph/README.md) |
| Documentary date wording and report sections | Check a bounded date paraphrase rule and separate named-section passage discovery | [Pattern study and replay](../evaluation/documentary-date-pattern/README.md) |
| Conversation, optional models, MCP, and integrations | Verify interface behavior, session continuity, source policy, and authority boundaries across entry points | [Results and tests](RESULTS_AND_TESTS.md) · [MCP](MCP_AGENT.md) · [Specialist continuity](SPECIALIST_CONTINUITY.md) |
| Guarded work and comparative tests | Check named work, dispatch, and comparison behaviors through the documented routes | [Comparative tests](../evaluation/comparative-tests/) · [B-Tests](https://github.com/mitchell-d00/B-Tests) |
| Packaging, browser, crawler, and deployed-site tests | Verify the exact artifact and its runtime paths at the applicable local, candidate, or deployed stage | [ZIP-first release testing](ZIP_FIRST_RELEASE_TESTING.md) · [Browser checks](BROWSER_TESTING_FOR_AGENTS.md) |

For automation, each `families` entry in [results.json](results.json) names
`artifacts`, `tests`, `runners`, `scope`, and `measurement_status`. Use
`python -m tools.audit_documentation` to check archive coverage and paths.
Record the command, revision, serving policy, fixture digest, and per-case
output when adding evidence. Keep raw outputs separate from the grading key.

## Next authorized trials

[Source-linked tag comparison](../evaluation/bubble-wrap/2026-11-25/next-source-tags-proposal.json) is proposed, NOT_RUN: identical raw documents versus source-linked proposals, exact eligible witnesses and tampered-tag rejection.

[ONBOARD-12 protocol proposal](../evaluation/bubble-wrap/2026-11-25/next-onboarding-proposal.json) is NOT_RUN. Mitchell will recruit twelve first-time participants and return uncoached results. Software journeys cannot count as human observations. Freeze engine, collection, both documentation versions, tasks and rubric before human execution.

**BW-BOUNDED-TRANSITION:** [21original positive witness keys and raw readback](../evaluation/bubble-wrap/2026-11-25/bounded-transition/README.md), [versioned host audit](../tools/verify_bounded_reported_content.py), [tampering controls](../tests/test_bounded_report_audit.py). Origin PR103; source-scoped reporting versus independent authorship. Original v1 failure retained; full rerun pending.

## Source-linked proposals: ST-D / ST-T

Responsible department: [Testing and Evaluation](departments/testing-evaluation.md), protecting [Reader](departments/reader.md) and [Intake and Research](departments/intake-research.md). [Frozen source-tag trial](../evaluation/source-tags/2026-11-25/README.md) retains72development inputs and baseline plus a sealed24-case future packet. Baseline tag checks are NOT_RUN; prototype validation adds no answer coverage. No committed/fresh candidate acceptance is claimed at this preparation snapshot.

## Department ownership

[Testing and Evaluation](departments/testing-evaluation.md) maintains frozen inputs, keys, custody, run records and scoring. Every family in [results.json](results.json) names its responsible department and protected implementation departments. Reader owns answer/proof behavior; Ledger owns record/eligibility behavior; Intake and Research owns proposals/discovery; Work Coordination owns permissions/dispatch; Applications owns interfaces; Delivery and Project Operations owns release and handoff gates. The [component routing map](departments/components.json) preserves every existing path. `python tools/audit_departments.py` checks path coverage and entry sections; it does not test semantic accuracy.

**ST-GUARD:** [15native source-tag controls](../tests/test_source_tags.py), including stale/withdrawn/corrupt/missing sources, role/original containment, eligible conflict, budget stops, source mutation and host-policy withholds. [Schema and limits](../evaluation/source-tags/2026-11-25/SCHEMA.md).

**ONBOARD-12:** [Frozen protocol/materials](../evaluation/onboarding/2026-11-25/README.md) and [null actual results](../evaluation/onboarding/2026-11-25/results.json). Responsible: Testing and Evaluation; protected Applications/Delivery. Software parity and scoring arithmetic tests are separate from12unrun human observations.
