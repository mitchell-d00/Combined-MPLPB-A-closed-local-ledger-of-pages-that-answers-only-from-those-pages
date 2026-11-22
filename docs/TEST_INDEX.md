# Test Index for humans and AI

Last reviewed: 2026-11-22.

This is the starting point for running, interpreting, and extending Combined
MPLPB tests. Use the [test commands](TEST_TOOLS.md) to run a suite, the
[machine-readable inventory](results.json) to find the retained artifacts,
regression files, runners, and measurement scope for every indexed evaluation
family, and the [results guide](RESULTS_AND_TESTS.md) to read the reported results.

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

The D-series names come from game dice. The current names are D4, D6, D20,
D% and D100. D100 and D% both draw on percentile dice and name separate
experiments. The unused names in a standard RPG dice set are D8, standalone
D10 and D12. Dice Bag draws live records. A die's name alone gives no case
count for a particular run.

| Suite | What it measures | Reproduce or inspect |
|---|---|---|
| **D4** | Event identity, local co-reference, documentary proof and controls | [Native runner and reproduction](D4_EVENT_IDENTITY_COREFERENCE.md) · [Retained case study](../evaluation/d4/2026-11-20/CASE_STUDY.md) |
| **D6** | Six declared-field operations for matches, contrasts, year arithmetic, branching and cited answer compilation | [Runner, worked example and Dice Bag corpus replay](../evaluation/d6/README.md) |
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
