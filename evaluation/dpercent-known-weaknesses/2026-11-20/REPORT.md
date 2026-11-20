# D% known-weakness study

Last reviewed: 2026-11-20.

The new study freezes4,096 developer-authored cases across75 executable classes,
54–55 cases per class. Fifteen additional known limitations are catalogued as
unmeasured rather than assigned artificial passing cases. This is not independent
semantic validation or a claim to cover every unknown failure.

Native code under test is2427d80e777b9cc76e071b2529e91a14b9bdb991.
No native implementation rule was changed while this batch executed. OldD%,
expanded stress,900-field and historical sources/questions/keys are unchanged.

## Protocol and execution history

Seed2026112003;16 shards of256 cases; original12-passage/8000-character proof
budgets,45-second worker wall and30-second CPU limits. The balanced schedule
and every unbiased D% draw are retained in disjoint custody, outside workers.
The frozen producer SHA-256 is
`718c0ebf0da56e08a3494c06d48528940c73bc0adfaf289d9887564c836889dc`.
`frozen-producer.py` retains those exact bytes for deterministic regeneration.
New source bytes total1,489,253. No acceptance-language filter is applied.

First sequential execution was terminated deliberately to switch to four bounded
parallel shards. Its completed outputs and interruption remain separate; they
are not counted twice. The parallel batch uses identical source packets and keys.
A scorer interoperability bug was found: three old structural-key schemas were
not understood by the new report's graph-obligation branch. The frozen producer
is retained; the repaired post-run scorer explicitly handles those observation
schemas and fails unknown schemas closed. No source, key, expected outcome or
native rule is changed by the repair. Scorer hashes remain separate from the
original producer hash. This is a harness failure, not an engine-answer failure.

The initial harness test also incorrectly expected zero edges in not-compared
mode. That mode retains textual containment edges and emits no comparison-only
edges. The test now checks that actual contract. Negated correction wording may
retain inspectable statements without generating an unresolved-reference edge;
the test requires absence of a correction link, not an arbitrary review format.
These corrections preceded source/key sealing.

## Scoring boundaries

Answer scoring retains detected complete answers, missed positives, correct
refusals, unsupported-positive errors and unscored supported semantics. Graph
obligations separately check primary versus embedded classification, cluster
membership counts, changed-body warnings, positive reference discovery and
forbidden links. Graph correctness does not establish historical identity.
The source audit rechecks UTF-8 byte/character spans, source hashes and all three
non-authority flags. Semantic relationship precision/recall and human-review time
remain null. Partial output counts are not independently scored partial accuracy.

## Reproduction

See [the usage contract](../../../docs/DPERCENT_KNOWN_WEAKNESSES.md).
Use the frozen producer for exact original generation; the current module has an
additive post-run scorer repair. The generation functions and charts are unchanged.
Use new output directories, preserve failed attempts and inspect every family
rather than treating a successful driver exit as perfect recall.

## Completed findings

All4,096 workers completed, with zero failed or unscored executions:

| Authored outcome | Count |
|---|---:|
| Complete source-key matches |657/1,262 answerable (E52.06%)|
| Missed complete answers |605/1,262 (47.94%)|
| Expected refusals retained |2,834/2,834|
| Incorrect supported negatives |0/2,834 (F0%)|
| Incorrect supported positives |0|
| Unscored supported outputs |0|
| Not run |0|

Every missed positive belongs to one of11 classes,55 cases each: partial
corrections, earliest-observed documentary dates, negated statements, wording
changes, complete-header location, compound fields, date-role inventories,
instruction arrangements, identical-wording comparisons, explicit multirecord
chains and reported statements. These are authored answerability keys, not
independently adjudicated historical conclusions. Similarity does not establish
identity or causation; no native rule was changed to fit these cases.

All1,026 new sorter cases satisfy their declared positive/negative structural
obligations and preserve the required answer refusal. All432 added alias controls
also match their authored outcomes. Across the entire study,37 graphs are
explicitly partial because of `repeated_phrase_group_budget`:11 editorial
competition,9 earliest-observed,9 explicit-chain and8 ambiguous-correction cases.
Those are disclosed completeness limits, not false historical relationships.
The score retains them instead of calling every graph complete.

The independent deterministic byte audit checked156,894 emitted node spans:
zero byte/character/hash errors and zero candidate authority-flag violations.
All isolated workers retained identical nodes/labels across modes, unchanged
original sources and no read-induced ledger changes. This is software evidence,
not independent semantic review or historical truth.

CPU466.730s; summed worker wall486.999s; maximum worker RSS30,031,872bytes.
Explicit original reads12,292, totaling1,489,253bytes. Summed wall excludes
orchestration and is not elapsed parallel-run latency. Complete internal ledger
read bytes and human-review costs remain null. Four concurrent shards were used.
The old single-shard attempt was terminated (exit143); the original parallel
orchestrator later exited1 because the expanded scorer assumed every feature
schema included `question_form` and `field`. Workers still completed; the fixed
post-run adapter rescored their original hash-pinned outputs (exit0). It also
honors partial runs when reporting E/F. The schema error and the earlier legacy
obligation error are retained, rather than described as engine-answer failures.

`audit.json` retains original counts, resources, all37 graph limits and code/scorer pins.
`corrected-audit.json`, `corrected-summary.json` and `corrected-scoring.tar.gz`
retain the later accounting-consistent metrics; complete-study findings agree.
`summary.json` retains every family and feature cohort; raw executions and the
interrupted attempt are archived separately. `synthetic-packets.zip` includes
original public packets and separately sealed expected outcomes, plus the exact
producer and per-file hashes. These synthetic keys are intentionally public for
reproduction; original private study keys remain untouched.

A final progress regression also exposed unexecuted rows counted as executed
in partial summaries. The failing control reports2 instead of0; the repair keeps
not-run counts explicit and E/F null. Per-family field metrics and lower bounds
are now recomputed after literal-field matching rather than inherited from the
base proposition scorer. Both before/after logs and separate corrected-score
artifacts are retained; none of the4,096 native outputs or expected outcomes
changed. The aggregate complete/refusal/graph findings above remain identical.

Focused software checks:121 tests passed (exit0). Full final-head release checks
must run separately; the native freeze's seven CI checks succeeded. Independent
review: **NOT RUN**.


## All executable class outcomes

| Class | Executed | Complete matches | Missed positives | Expected refusals | Graph limits/failures |
|---|---:|---:|---:|---:|---:|
| absent_anchor |55|0|0|55|0|
| alias_adjective_date |54|0|0|54|0|
| alias_adjective_location |54|0|0|54|0|
| alias_adjective_time |54|0|0|54|0|
| alias_collision |54|0|0|54|0|
| alias_geographic_state |54|0|0|54|0|
| alias_role_date |54|54|0|0|0|
| alias_role_location |54|54|0|0|0|
| alias_role_time |54|54|0|0|0|
| ambiguous_correction |55|0|0|55|8|
| ambiguous_pronoun |55|0|0|55|0|
| chronology_causation |55|0|0|55|0|
| competing_accounts |55|0|0|55|0|
| conditional_execution |55|0|0|55|0|
| corrupted_source |55|0|0|55|0|
| date_roles |55|0|55|0|0|
| direct_action |55|55|0|0|0|
| earliest_observed |55|0|55|0|9|
| editorial_competition |55|55|0|0|11|
| embedded_identifier |55|0|0|55|0|
| exact_anchor |55|55|0|0|0|
| explicit_cause |55|55|0|0|0|
| explicit_chain |55|0|55|0|9|
| field_changed_body |55|55|0|0|0|
| field_compound |55|0|55|0|0|
| field_conflict |55|0|0|55|0|
| field_corrupted |55|0|0|55|0|
| field_literal |55|55|0|0|0|
| field_missing_bridge |55|0|0|55|0|
| field_missing_label |54|0|0|54|0|
| field_negation |55|0|0|55|0|
| field_past_scope |55|0|0|55|0|
| field_quoted_only |55|0|0|55|0|
| field_reported_only |55|0|0|55|0|
| field_restricted |55|0|0|55|0|
| field_same_subject |55|55|0|0|0|
| field_stacked |54|0|0|54|0|
| field_synonym |55|55|0|0|0|
| field_withdrawn |55|0|0|55|0|
| field_wrong_id |55|0|0|55|0|
| header_location |55|0|55|0|0|
| historical_priority |55|0|0|55|0|
| identical_wording |55|0|55|0|0|
| instruction_statement |55|0|55|0|0|
| intention_execution |55|0|0|55|0|
| missing_bridge |55|0|0|55|0|
| negated_execution |55|0|0|55|0|
| negated_statement |55|0|55|0|0|
| partial_correction |55|0|55|0|0|
| passive_action |55|55|0|0|0|
| reported_execution |55|0|0|55|0|
| reported_statement |55|0|55|0|0|
| restricted_source |55|0|0|55|0|
| sorter_ambiguous_target |54|0|0|54|0|
| sorter_changed_body |54|0|0|54|0|
| sorter_concatenated_records |54|0|0|54|0|
| sorter_conditional_correction |54|0|0|54|0|
| sorter_duplicate_appearance |54|0|0|54|0|
| sorter_fenced_example |54|0|0|54|0|
| sorter_forwarded_header |54|0|0|54|0|
| sorter_missing_target |54|0|0|54|0|
| sorter_negated_correction |54|0|0|54|0|
| sorter_numbered_reference |54|0|0|54|0|
| sorter_partial_correction |54|0|0|54|0|
| sorter_passive_correction |54|0|0|54|0|
| sorter_punctuated_reference |54|0|0|54|0|
| sorter_quoted_correction |54|0|0|54|0|
| sorter_quoted_header |54|0|0|54|0|
| sorter_reported_correction |54|0|0|54|0|
| sorter_same_body_different_ids |54|0|0|54|0|
| sorter_same_subject |54|0|0|54|0|
| sorter_unique_correction |54|0|0|54|0|
| subject_identity |55|0|0|55|0|
| withdrawn_source |55|0|0|55|0|
| wording_change |55|0|55|0|0|


## Next class-level work

Start with independently checked compound field obligations, then exact text
comparison and attributed denial/report questions. Each proposed rule needs its
own contrasting negative and mutation controls before replaying this frozen set.
Do not add identifiers, expected values or special cases to runtime rules.
The11 failing classes remain fully visible. Larger generations can sample more
variations, but repeated templates and54–55 examples per class do not establish
rare-error reliability or unseen semantic accuracy. The15 adapter/review gaps
remain unmeasured. This iteration changes test coverage, not the historical3/22
completion result or the finite proof boundary.
