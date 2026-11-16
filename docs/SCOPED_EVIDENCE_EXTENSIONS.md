# Scoped evidence extensions

Last reviewed: 2026-11-16.

These extensions retain `answer-contract-v1`, the existing eligibility and lineage
checks, relation families, and work-event chain. An intact unique record, its
pinned ancestry, explicit origin/depth, delivery profile, not-for exclusions and
current serving view remain prerequisites. Source integrity does not certify
source truth. Assisted output and relation exploration keep
`answer_supported:false`. The existing deterministic strict-first proof path
remains available before an assisted fallback and labels its output mode `strict`.

## Exact source fields and diagnostics

```python
from mplpb_answers.pipeline import answer_query
result = answer_query(root, 'What is Owner for record CASE-1?')
result = answer_query(root, 'Inspect owner', record_id='SRC-1@sha256:...', field='Owner')
result = answer_query(root, 'Inspect owner', field='Owner',
    exact_value={'field':'Accession', 'value':'UNIQUE-7788'})
```

The bounded question form is `What is <field> for/of record/event/occurrence
<identifier>?`. Keyword selectors use the same pipeline. Exact record IDs and
pins, explicit body identity keys, and unique field/value selectors route only
after eligibility. Matching eligible pages skip ranking and diversity discounts.
A unique value also retains other appearances sharing its explicit identity key,
so selecting an accession cannot hide a competing owner statement.

Field evidence consists of complete `Label: value` lines in the initial source
body header block. A non-field line, Body, Example or Sample ends that block.
Labels normalize case, underscores and hyphens; values retain their exact source
text. Ledger metadata can route a request but cannot supply a body-field answer.
Repeated conflicting field lines, including later mentions outside the initial
header block, remain separate citations. Later mentions cannot grant field support;
conflicting values produce a conflict and other later context requires review. All competing eligible field passages are checked before any budget
selection. Conflicts never choose a winner. If the display budget cannot retain
all conflicting field passages, the conflict remains unsupported and records an
explicit omitted count.

| Diagnostic | Meaning |
| --- | --- |
| `exact_field_missing` | An exact route cannot establish the requested explicit body field. |
| `contradictory_passages_pruned` | The budget would omit known competing field passages; the selected subset cannot support an answer. Increase the budget to inspect them all. |
| `event_identity_unresolved` | The query needs an explicit event/occurrence identity that resemblance alone cannot establish. |
| `correction_scope_unclear` | A field-scoped correction needs the requested field stated explicitly. |

The existing `conflicting_or_multiple_owners`, `retrieval_ambiguous`, source-change,
eligibility, budget and reader diagnostics remain in use. Unique-value ambiguity
requires clarification. Source changes discard old claims, passages and explored
edges. CLI `ask` accepts `--record-id`, `--field` and `--as-of`.

## Distinct event and appearance identities

Source pages can declare sealed `event_id` / `occurrence_id` metadata through
`ledger.write`, or explicit `Event-ID:` / `Occurrence-ID:` source body headers.
`inspect_events` retains every appearance as its own `source-id@hash` occurrence,
along with any declared occurrence ID. An event has a distinct `event:` node ID
and its own false support/truth flags. Declared event IDs and generated shared-key
nodes occupy separate identity namespaces, even when their display labels match. A source declaration is not a historical
identity certification.

A new shared-key event candidate requires at least two appearances declaring the
same explicit `Event-Key:`. A repeated message ID, equal subject or equal date
alone does not create an event. Changed bodies under a common message key remain
visible for review. Original appearances are never merged or overwritten.

## Field and time-scoped corrections

```python
from mplpb_combined.ledger import write
correction = write(root, doc_id='SRC-2', title='Correction', scope='archive owner',
    supersedes=['SRC-1@sha256:...'], corrects_field='Owner',
    valid_from='2026-01-01', valid_until='2027-01-01',
    body='Record-ID: CASE-1\nOwner: Bob')
result = answer_query(root, 'What is Owner for record CASE-1?', as_of='2025-12-31')
```

`corrects-field`, `valid-from` and `valid-until` are sealed optional fields. Old
pages retain their hashes because absent optional fields do not enter their
hashes. `supersedes` pins must resolve exactly. Dates mean midnight UTC;
timestamps require an explicit timezone. The lower bound is inclusive and the
upper bound exclusive. Invalid or reversed windows are rejected. The default
view uses current UTC time. Queries outside a declared correction window see the
pinned predecessor, subject to all its original eligibility checks. Queries for
other fields also use the predecessor. Field-scoped correction sources require an explicit matching field selector at
the provenance gate; generic source reads cannot bypass this restriction. No page
bytes or status lines are rewritten by a read. Query contexts are isolated and reset after success or failure.

Withdrawing a correction never restores its predecessor, including in an as-of
query. A valid standalone withdrawal in its successor chain remains an eligibility
barrier. Restoration still requires a new explicit revision. Query views do not
authorize edits to old nonterminal heads. This is declared-window serving, not
arbitrary reconstruction of the entire ledger at a historical time.

`correct_claim` and CLI `correct-claim` also accept `corrects_field`, `valid_from`
and `valid_until` (`--corrects-field`, `--valid-from`, `--valid-until`). A field
correction must name the complete unique field line and preserve its label. The
predecessor and unaffected text remain inspectable. Unrelated claim text is not
automatically corrected or inferred.

## Evidence-gated relation exploration

`answer_query(..., relation_hops=[...])` accepts one or two explicit hop objects:
`question`, `source_id`, `hash`, `quote`. Each question must fit a current
relation-graph family. Each edge independently reloads eligible source evidence
and verifies its full source quote and pin. Consecutive subject/value keys must
match. A missing quote, restricted/changed source, unsupported question or missing
link produces a candidate edge. Causal chains and reverse causal inference are
not licensed. Three or more hops are rejected.

The `exploration` result records each edge, family, direction, quotation and
verification status. Even fully quoted edges remain an inspection graph;
exploration never composes a supported answer. Existing deterministic direct
answering remains available by omitting this optional mode.

## Independent receipts and operator effort

Completion receipts retain false answer/truth flags. Host-only
`WorkStore.record_external_receipt` records READ/ACK observations tied to an
existing execution receipt in the work-event stream. These are host declarations,
not independent external-world verification. They cannot become claim evidence,
change a source pin, or promote a claim. Existing dispatch fencing, reconciliation
and recheck-on-source-change rules remain in force. Work source checks always use
the present serving view: a historical query context cannot authorize work from
a source that is retired today. The seat RPC does not expose
this host operation. Handoffs always retain `answer_supported:false` and
`content_truth_verified:false`.

`WorkStore.put(..., operator_seconds=2.5)` attaches optional self-reported effort
to that work event. Trusted host adapters may return `operator_seconds` and
`operator_seconds_basis` (`measured` or `self_reported`). No execution duration is
automatically labelled human effort. Values must be finite nonnegative numbers;
booleans are rejected. Effort never affects eligibility, assessment or answer
support. Handoffs expose only visible, readable event measurements and their sum;
unknown effort is `null`, not zero. Private effort does not leak through another
seat's view.

Study reviewers can optionally supply `operator_seconds` per case. Scoring reports
their total separately from `work_event_operator_seconds` captured by the engine.
Missing measurements stay `null`; reviewer measurements and identities remain
unattested. This adds instrumentation, not a completed operator-burden study or
independent human validation.

## Reproduction

Run `python -m unittest tests.test_scoped_extensions tests.test_historical_study -v`.
Existing supersession, record, coordinator, relation-graph and public 52-case tests
remain compatibility gates. These are public development controls, not held-out
historical accuracy measurements. See [result/test index](RESULTS_AND_TESTS.md)
and [original-record study](ORIGINAL_RECORD_STUDY.md).
