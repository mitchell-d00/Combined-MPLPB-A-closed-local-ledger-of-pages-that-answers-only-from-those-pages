# Event identity, co-reference D4

## Results at a glance

The paired study ran **4,096 cases per implementation across 95 question families**. The D4 candidate verified all **430** answerable identity and co-reference questions after **430** baseline misses. It preserved all **1,716** expected D4 refusals. All **1,950** inherited outcomes matched their paired baseline. The candidate also passed the separate 380-case mixed acceptance gate.

| Population | Matched before | Matched after | Correct refusals after | Positive misses after |
|---|---:|---:|---:|---:|
| Documentary event identity | 0 | 216 | 967 | 0 |
| Local co-reference | 0 | 214 | 749 | 0 |
| Inherited D% classes | 338 | 338 | 1352 | 260 |

The broad run recorded 0 structural graph obligation failures and 21 graph budget stops. The inherited misses are part of the published denominator. The focused gate includes established controls alongside the D4 classes.

## Research question

Can a closed ledger resolve documentary event identity and local co-reference
when the evidence supplies a checkable link? D4 asks the engine for a full
source-supported answer when a record contains that link. It also asks nearly
identical questions when the records supply only matching words, ambiguous
references, quoted examples, or inaccessible material. A conclusive “different
event” is an answer where the sources explicitly distinguish the events. A refusal
records that the evidence failed to establish the relationship.

## Study design

The broad mix contains 95 families. Twenty target event identity or co-reference.
The other 75 are the earlier D% known-weakness catalogue, including its known
positive misses and its structural sorter obligations. The generator assigns
four times as much sampling weight to each D4 class as to each inherited class.
Every case receives a single principal class before the schedule is shuffled.
Within each class the chart varies source order, query form, scaffolding,
document layout, or other applicable variables. Those choices are recorded in
custody. The gate mix exercises all twenty D4 classes and eighteen established
original D% controls.

This is a paired development experiment. The generator, question text, source
bytes, case order, expected propositions and required witnesses are committed
by the frozen seals. The first implementation is the merged Combined MPLPB
baseline. The second implements the named-source verification rules. Both run
the same packets through the unchanged D% worker. The worker mounts the
selected case and source packages, with the generator, expected outcomes and
scoring keys outside its filesystem. The broad comparisons preserve every
inherited case rather than replacing missed positives with easier examples.

The scorer requires a typed proposition with the expected polarity or referent,
and every required witness at the correct source, source hash and canonical
offset. It checks the citation by rereading the result's independently materialized
source receipt. An answer with a plausible label and missing, incorrect or
unlicensed citations earns no credit. Expected refusals are scored through the
native support flag. Diagnostics explain the engine's reason for stopping.
A graph that hits its own budget is recorded separately from graph authority
violations or failed structural obligations.

## Documentary proof rules

**Shared event keys.** The question names two ledger source IDs. Both records
must be current and eligible. Each must declare an exact registry name and
event key in its body. The checker reads both sources and takes four evidence
spans. A number reused under different registries cannot establish agreement.
The answer states that the sources declare the same key within that registry.

```text
Source LEAF-A
Event Registry: Maritime Inventory
Occurrence ID: COPY-A
Event ID: D-42

Source LEAF-B
Event Registry: Maritime Inventory
Occurrence ID: COPY-B
Event ID: D-42
```

**Explicit distinction.** Separate keys are compatible with multiple
possibilities, including independent label assignments or a revision. A
checkable distinction requires an explicit `Different Event From` declaration.
The target occurrence ID has to resolve uniquely within the registry, and the
two named occurrences must be distinct. A shared event key paired with an
explicit difference produces a conflict. Quoted and repeated label lines fail
the proof if their scope or authority is unresolved.

**Local co-reference.** The source must contain a complete explicit gloss
or a single direct speech turn with an explicitly named speaker. In
`“I checked the freight tags,” said Amélie Wells.`, the quoted “I” is bound to the
named speaker for that turn. The checked proposition concerns the attribution.
Independent confirmation of the attributed action is outside the proof. A source
may separately state `Pronoun "they" refers to Amélie Wells.` as a complete
gloss. Similar words, sentence adjacency and a plausible person's name do not
supply that binding by themselves.

**State and evidence budgets.** A proof cites all indispensable spans within
one shared passage and character budget. A hidden, retired, stale or restricted
copy cannot serve as a witness. The native pipeline rechecks source state
before delivering an answer. The independent mutation control changes a source
after verification and requires the complete proof to be discarded.

## A browser-path failure exposed by the study

The initial 380-case gate passed, but an end-to-end Chromium check rejected a
valid imported speech turn. Native D% fixtures write the original body directly.
A browser import appends a capture manifest to protect the imported text, so the
initial whole-body speech parser treated provenance as part of the utterance.

The corrected checker uses MPLPB's existing capture boundary verification and
cites only the canonical captured text. A native import test reproduced the miss
before the fix. A second test exercises a forged manifest suffix and requires
the proof to remain unresolved. The corrected ZIP-built browser passed the
same three queries used during the initial check. They cover same-registry event
agreement, cross-registry refusal and imported speech attribution.

## Reading the question-class patterns

The most useful comparisons use the same question form across different
source conditions. Identical wording with identical registry keys and
identical wording across registries can look equally compelling during
retrieval. Only the shared-registry case licenses the scoped agreement.
Different keys accompanied by an explicit distinction yield a checked
negative relationship. Different keys without the declaration continue
to leave that relationship unanswered.

The three event requests vary “describe,” “refer to,” and “are the events
the same.” Co-reference requests vary direct “who,” an explicit “pronoun”
label, and “to whom.” The generic introductory and closing scaffolding
does not change the documentary obligation or supply a source hint.
Case counts should be inspected by class and by question form together.
Forms and source order are sampled features with overlapping cohorts,
so these comparisons do not estimate a causal effect or general linguistic
coverage.

For local reference, the contrast between a named speech turn and nearby names
matters more than proximity. The parser supports the direct turn's explicit
speaker even when spelling includes accents. A second antecedent, a conditional
form, an embedded quotation or an uncertain statement withholds support.
The ambiguous examples remain diagnostic successes when the expected refusal
is retained.

The inherited D% families provide a check for behavior away from the new
question parser. Exact field reading, bounded prose claims and literal
location keep their previous outcomes. Previously unanswered cases still
count as misses. The broad gate compares those case-level results and
structural outcomes with the paired baseline.

## Limits of the measurement

The study establishes synthetic behavior under the finite forms and licensed
evidence conditions. Register authentication, cross-document person identity,
narrative event matching and unconstrained pronoun resolution remain outside
the measured scope. The model of “same
event” is explicitly relative to the two selected source declarations and their
registry. The scoped difference proof is also a source attribution.

The cases are developer-authored and the frozen producer is public. Independent
semantic adjudication and a blind test on unfamiliar original records remain
unrun. The study reports inherited misses separately from D4 misses and keeps
read-only graph inspection separate from supported answer proofs.

## D4 class-by-class results

| Class | Case condition | Run count | Matched before | Matched after | Expected refusals held | Candidate diagnostic |
|---|---|---:|---:|---:|---:|---|
| `d4_event_shared_key` | The two eligible documents print one registry and event key. | 108 | 0 | 108 | 0 | `supported_documentary_assertion` 108 |
| `d4_event_declared_distinct` | A scoped distinction identifies a unique target occurrence. | 108 | 0 | 108 | 0 | `supported_documentary_assertion` 108 |
| `d4_event_cross_registry` | The same local key appears in different registries. | 108 | 0 | 0 | 108 | `event_identity_unresolved` 108 |
| `d4_event_different_keys` | Separate keys lack an explicit distinction. | 108 | 0 | 0 | 108 | `event_identity_unresolved` 108 |
| `d4_event_same_wording` | Two documentary appearances repeat their wording without keys. | 108 | 0 | 0 | 108 | `event_identity_unresolved` 108 |
| `d4_event_contradiction` | An explicit distinction conflicts with the shared event key. | 108 | 0 | 0 | 108 | `event_identity_conflict` 108 |
| `d4_event_quoted` | A necessary declaration occurs in a quotation or fenced example. | 107 | 0 | 0 | 107 | `event_identity_unresolved` 107 |
| `d4_event_withheld` | A necessary document cannot be served under the external profile. | 107 | 0 | 0 | 107 | `no_eligible_sources` 107 |
| `d4_event_budget` | The evidence budget is too small for the required witnesses. | 107 | 0 | 0 | 107 | `reader_budget_exceeded` 107 |
| `d4_event_ambiguous_occurrence` | The target occurrence ID has multiple appearances. | 107 | 0 | 0 | 107 | `event_identity_unresolved` 107 |
| `d4_event_late_conflict` | An additional late event declaration makes the source ambiguous. | 107 | 0 | 0 | 107 | `event_identity_unresolved` 107 |
| `d4_coref_explicit` | A complete gloss binds the exact requested pronoun. | 107 | 0 | 107 | 0 | `supported_documentary_assertion` 107 |
| `d4_coref_direct_speech` | One complete quoted turn identifies the first-person speaker. | 107 | 0 | 107 | 0 | `supported_documentary_assertion` 107 |
| `d4_coref_ambiguous` | Two explicit glosses offer competing referents. | 107 | 0 | 0 | 107 | `coreference_unresolved` 107 |
| `d4_coref_quoted` | The gloss occurs in sample material. | 107 | 0 | 0 | 107 | `coreference_unresolved` 107 |
| `d4_coref_reported` | Another source voice only reports or suspects the binding. | 107 | 0 | 0 | 107 | `coreference_unresolved` 107 |
| `d4_coref_conditional` | A condition governs the asserted binding. | 107 | 0 | 0 | 107 | `coreference_unresolved` 107 |
| `d4_coref_nearby_names` | Two nearby people leave the pronoun ambiguous. | 107 | 0 | 0 | 107 | `coreference_unresolved` 107 |
| `d4_coref_wrong_pronoun` | The stated gloss answers a different pronoun. | 107 | 0 | 0 | 107 | `coreference_unresolved` 107 |
| `d4_coref_withdrawn` | The named source is retired. | 107 | 0 | 0 | 107 | `no_eligible_sources` 107 |

## Patterns by question form

Query forms are indexed separately for the two tasks. Within each form,
the denominator includes its different source and delivery conditions.

| Task and request form | Positive obligations | Baseline matches | Candidate matches | Candidate refusals |
|---|---:|---:|---:|---:|
| event identity / Describe the same event | 77 | 0 | 77 | 314 |
| event identity / Are the events the same | 70 | 0 | 70 | 326 |
| event identity / Refer to the same event | 69 | 0 | 69 | 327 |
| coreference / Who does the quoted token refer to | 68 | 0 | 68 | 251 |
| coreference / Who does the pronoun refer to | 64 | 0 | 64 | 245 |
| coreference / To whom does the token refer | 82 | 0 | 82 | 253 |

## Inherited question classes

The following classes have matching paired outcomes and graph controls.
A zero in the matches column can represent a correct refusal or a missing
positive, as shown by the two separate columns.

| Class | Cases | Complete matches | Correct refusals | Positive misses |
|---|---:|---:|---:|---:|
| `absent_anchor` | 26 | 0 | 26 | 0 |
| `alias_adjective_date` | 26 | 0 | 26 | 0 |
| `alias_adjective_location` | 26 | 0 | 26 | 0 |
| `alias_adjective_time` | 26 | 0 | 26 | 0 |
| `alias_collision` | 26 | 0 | 26 | 0 |
| `alias_geographic_state` | 26 | 0 | 26 | 0 |
| `alias_role_date` | 26 | 26 | 0 | 0 |
| `alias_role_location` | 26 | 26 | 0 | 0 |
| `alias_role_time` | 26 | 26 | 0 | 0 |
| `ambiguous_correction` | 26 | 0 | 26 | 0 |
| `ambiguous_pronoun` | 26 | 0 | 26 | 0 |
| `chronology_causation` | 26 | 0 | 26 | 0 |
| `competing_accounts` | 26 | 0 | 26 | 0 |
| `conditional_execution` | 26 | 0 | 26 | 0 |
| `corrupted_source` | 26 | 0 | 26 | 0 |
| `date_roles` | 26 | 0 | 0 | 26 |
| `direct_action` | 26 | 26 | 0 | 0 |
| `earliest_observed` | 26 | 0 | 0 | 26 |
| `editorial_competition` | 26 | 26 | 0 | 0 |
| `embedded_identifier` | 26 | 0 | 26 | 0 |
| `exact_anchor` | 26 | 26 | 0 | 0 |
| `explicit_cause` | 26 | 26 | 0 | 0 |
| `explicit_chain` | 26 | 0 | 0 | 26 |
| `field_changed_body` | 26 | 26 | 0 | 0 |
| `field_compound` | 26 | 26 | 0 | 0 |
| `field_conflict` | 26 | 0 | 26 | 0 |
| `field_corrupted` | 26 | 0 | 26 | 0 |
| `field_literal` | 26 | 26 | 0 | 0 |
| `field_missing_bridge` | 26 | 0 | 26 | 0 |
| `field_missing_label` | 26 | 0 | 26 | 0 |
| `field_negation` | 26 | 0 | 26 | 0 |
| `field_past_scope` | 26 | 0 | 26 | 0 |
| `field_quoted_only` | 26 | 0 | 26 | 0 |
| `field_reported_only` | 26 | 0 | 26 | 0 |
| `field_restricted` | 26 | 0 | 26 | 0 |
| `field_same_subject` | 26 | 26 | 0 | 0 |
| `field_stacked` | 26 | 0 | 26 | 0 |
| `field_synonym` | 26 | 26 | 0 | 0 |
| `field_withdrawn` | 26 | 0 | 26 | 0 |
| `field_wrong_id` | 26 | 0 | 26 | 0 |
| `header_location` | 26 | 0 | 0 | 26 |
| `historical_priority` | 26 | 0 | 26 | 0 |
| `identical_wording` | 26 | 0 | 0 | 26 |
| `instruction_statement` | 26 | 0 | 0 | 26 |
| `intention_execution` | 26 | 0 | 26 | 0 |
| `missing_bridge` | 26 | 0 | 26 | 0 |
| `negated_execution` | 26 | 0 | 26 | 0 |
| `negated_statement` | 26 | 0 | 0 | 26 |
| `partial_correction` | 26 | 0 | 0 | 26 |
| `passive_action` | 26 | 26 | 0 | 0 |
| `reported_execution` | 26 | 0 | 26 | 0 |
| `reported_statement` | 26 | 0 | 0 | 26 |
| `restricted_source` | 26 | 0 | 26 | 0 |
| `sorter_ambiguous_target` | 26 | 0 | 26 | 0 |
| `sorter_changed_body` | 26 | 0 | 26 | 0 |
| `sorter_concatenated_records` | 26 | 0 | 26 | 0 |
| `sorter_conditional_correction` | 26 | 0 | 26 | 0 |
| `sorter_duplicate_appearance` | 26 | 0 | 26 | 0 |
| `sorter_fenced_example` | 26 | 0 | 26 | 0 |
| `sorter_forwarded_header` | 26 | 0 | 26 | 0 |
| `sorter_missing_target` | 26 | 0 | 26 | 0 |
| `sorter_negated_correction` | 26 | 0 | 26 | 0 |
| `sorter_numbered_reference` | 26 | 0 | 26 | 0 |
| `sorter_partial_correction` | 26 | 0 | 26 | 0 |
| `sorter_passive_correction` | 26 | 0 | 26 | 0 |
| `sorter_punctuated_reference` | 26 | 0 | 26 | 0 |
| `sorter_quoted_correction` | 26 | 0 | 26 | 0 |
| `sorter_quoted_header` | 26 | 0 | 26 | 0 |
| `sorter_reported_correction` | 26 | 0 | 26 | 0 |
| `sorter_same_body_different_ids` | 26 | 0 | 26 | 0 |
| `sorter_same_subject` | 26 | 0 | 26 | 0 |
| `sorter_unique_correction` | 26 | 0 | 26 | 0 |
| `subject_identity` | 26 | 0 | 26 | 0 |
| `withdrawn_source` | 26 | 0 | 26 | 0 |
| `wording_change` | 26 | 0 | 0 | 26 |

## Reproduction and evidence

- Baseline runtime `f40caa62253ba54a7ec6dac9b398e2eb1ba91b7d`.
- Candidate runtime `c17c482797946bbd3bcca95186529e9e468ece06`.
- Study manifest SHA-256 `79c828e0238160760cf8bca0fb58717b7fa6602adec10c6ac7ce58cb41ba97e3`.
- Candidate source ZIP SHA-256 `80e4d95d49a0ee7969ccdbe481a2d677ee87636c35a2ba63e422452a51ce22f5`.
- Native archive regression receipt. `Ran 1542 tests in 645.686s / OK (skipped=2)`.
- [Study manifest](study.json), [gate manifest](gate-study.json), [machine-readable patterns](patterns.json), and [per-case paired decisions](cases.jsonl.gz).
- [One reproducible example per class](examples.json), selected by lowest case ID with the generated sources and native claim spans.
- [Exact frozen producer](frozen-producer.py) and [pre-change focused failures](prechange-focused.log), and [browser import regression](capture-before.log).

From this checkout, run the frozen producer with the repository on the Python
module path to reproduce the matched study seal. Use fresh paths.

```sh
PYTHONPATH=. python evaluation/d4/2026-11-20/frozen-producer.py prepare --public /tmp/d4-public --custody /tmp/d4-custody --cases 4096 --seed 2026112004 --mix study
python -m tools.d4 run --public /tmp/d4-public --output /tmp/d4-before --implementation /path/to/baseline
python -m tools.d4 score --public /tmp/d4-public --custody /tmp/d4-custody --run /tmp/d4-before --output /tmp/d4-before-score
python -m tools.d4 run --public /tmp/d4-public --output /tmp/d4-after --implementation /path/to/candidate
python -m tools.d4 score --public /tmp/d4-public --custody /tmp/d4-custody --run /tmp/d4-after --output /tmp/d4-after-score --baseline /tmp/d4-before-score/summary.json --require-pass
```
