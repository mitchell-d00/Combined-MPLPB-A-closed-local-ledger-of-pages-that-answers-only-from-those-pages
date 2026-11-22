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
a future repair. [D20 class study](../evaluation/d20/README.md#large-study-and-class-level-probes)

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
| Historical studies and human review | Check attribution, missing evidence, completeness, and disagreement on unfamiliar originals with an independent key | [Archival inspection](../evaluation/archival-inspection/) · [Historical expert path](HISTORICAL_EXPERT_PATH.md) · [Researcher pilot archive](../evaluation/researcher-pilot/) |
| Conversation, optional models, MCP, and integrations | Verify interface behavior, session continuity, source policy, and authority boundaries across entry points | [Results and tests](RESULTS_AND_TESTS.md) · [MCP](MCP_AGENT.md) · [Specialist continuity](SPECIALIST_CONTINUITY.md) |
| Guarded work and comparative tests | Check named work, dispatch, and comparison behaviors through the documented routes | [Comparative tests](../evaluation/comparative-tests/) · [B-Tests](https://github.com/mitchell-d00/B-Tests) |
| Packaging, browser, crawler, and deployed-site tests | Verify the exact artifact and its runtime paths at the applicable local, candidate, or deployed stage | [ZIP-first release testing](ZIP_FIRST_RELEASE_TESTING.md) · [Browser checks](BROWSER_TESTING_FOR_AGENTS.md) |

For automation, each `families` entry in [results.json](results.json) names
`artifacts`, `tests`, `runners`, `scope`, and `measurement_status`. Use
`python -m tools.audit_documentation` to check archive coverage and paths.
Record the command, revision, serving policy, fixture digest, and per-case
output when adding evidence. Keep raw outputs separate from the grading key.
