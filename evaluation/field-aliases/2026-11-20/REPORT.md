# Source-grounded field-alias iteration

Last reviewed: 2026-11-20.

## Baseline and preserved populations

Current branch baseline isbe6a556, runtime identical to full-tested9b5ff0c.
Main isbc6f25c; the published external pin isbbf6690. These are distinct scopes.
The unchanged public900-positive field benchmark supports900/900 on the branch,
versus150/900 at the external pin;200/200 negative controls are refused. Original
frozen1240D% at044ac27 has200/600 complete matches and640/640 refusals. Expanded
1000-case9b5ff0c has168/420 complete matches,252 misses and580/580 refusals.
Historical9b5ff0c has3 complete,2 partial,3 conflict,14 abstain over22 unchanged
questions; main's retained2-complete result is not silently reconciled with it.
Baseline runtime parity and46 focused software tests passed before engine edits.
Exact pins and denominators:baseline.json. Original corpora, seals, keys, questions,
reports and paper formats are untouched.

## Diagnosis of all252 expanded misses

The table is a developer code/output diagnosis, not independent answerability
adjudication. Per-case diagnostics, stages, partial claims and retrieval coverage
are retained in failure-diagnosis.json. An unsupported request grammar does not
establish that the evidence is absent. Matching or overlapping spans do not by
themselves establish a requested relationship.

| Family | Cases | Actual primary stop | Explanation |
|---|---:|---|---|
| field_synonym | 21 | question interpretation | Literal field label mismatch; exact record reached; alias meaning not licensed. |
| field_compound | 21 | question interpretation / composition | No complete multi-field obligation parse; cannot compose independent field proofs. |
| date_roles | 21 | question interpretation / proof representation | Requested sending/writing date inventory does not match bounded date proof request. |
| earliest_observed | 21 | proof representation / composition | Relative minimum among documentary dates not admitted by finite question/proof grammar. |
| explicit_chain | 21 | proof representation / composition | No independently checked multi-record request-dispatch-receipt composition for this request. |
| header_location | 21 | question interpretation / evidence admission | Complete correspondence-header location request outside admitted grammar. |
| identical_wording | 21 | question interpretation | Text comparison routed into event identity refusal; identity is not requested. |
| instruction_statement | 21 | question interpretation / evidence admission | Arrangement request not admitted; source instructions must not prove delivery. |
| negated_statement | 21 | question interpretation / proof representation | Request to report denial outside admitted question grammar; negation must remain. |
| reported_statement | 21 | question interpretation / proof representation | Attribution-preserving report request not admitted; not independent execution. |
| partial_correction | 21 | question interpretation / scoped proof | No complete correction-target and retained-destination request/proof composition. |
| wording_change | 21 | proof verification / answer composition | Checked partial evidence exists but requested changed/identical argument composition unestablished. |

## One general improvement: source-declared field aliases

The existing exact-field checker remains the only authority for field answers.
The new bounded normalizer proposes source-field labels from a small declared
lexicon (phone/telephone number, postcode/postal code, current state to declared
current/present status) and role-preserving date/time/location-of reordering.
It never maps status into a geographic State declaration, changes receipt into
sending, or equates date/time roles. No model, rank, title, expected value or
benchmark identifier suggests a field. All original question text, identifiers,
qualification, negation, attribution and as-of selector remain unchanged.

Each candidate field is inspected under its own original serving/correction view.
Only currently eligible original body-header declarations can select a label.
Competing synonymous labels require clarification, even with identical values;
exact spelling cannot silently prune another eligible synonym. Explicit field
selectors retain their precise literal semantics. Quoted/report/conditional
contexts cannot supply a declaration. The existing checker independently rereads
source evidence, retains contrary mentions and obeys its unchanged witness budget.
Every inspected field view is revalidated at final output. Source or policy changes
discard claims and source-derived normalization anchors. Normalization is never
source support or historical truth.

Alias inspection caps:64 eligible sources,2MiB canonical bodies,256 declarations,
and at most four candidate/literal views under this version's finite rules.
The mandatory native ledger/eligibility reads still occur before these caps;
these are inspection caps, not a claim to bound total filesystem I/O. Aliases
add repeated eligibility reads; no speedup or content-addressed cache is claimed.
The main12-passage/8000-character proof budget is unchanged. Budget exhaustion
refuses rather than selecting the highest-ranked field.

## Failed attempts retained

The initial new11-test suite failed7 subcases before implementation (exit1).
An early exact-spelling-priority rule hid a competing synonymous declaration;
the collision control failed (exit1). It now clarifies instead of choosing.
The rejected rule is explicitly reconstructed and actually replayed in the retained
ZIP/log, not falsely presented as an earlier frozen commit. Source collisions,
identical values, restrictions, corrections, missing IDs, qualifiers, budget
exhaustion and state mutation are tested. The62 focused tests pass (exit0).

One old unit control expected refusal solely because “current state” was formerly
unsupported. Its exact question is preserved as a positive unit assertion for
the newly licensed capability; all genuine negative controls remain negative.
No frozen benchmark question, key or expected result was changed. The initial
legacy-unit failure is retained rather than hidden.

## New sealed development holdout

Before alias implementation, a240-case packet/key/dice seal was generated with
new field vocabulary and two previously untested request structures. Baseline:
16/64 complete positives,48 misses,176/176 refusals,zero execution failures or
unscored support. All cases, including unfamiliar syntax, remain in the denominator.
This is developer-authored and not context-blind. It is not independent/unseen
human validation. The source packets and key are disjoint and neither key nor
generator is mounted into the unchanged isolated execution worker. The final
replication bundle will include synthetic expected outcomes plus their seals so
another researcher needs no private developer records.

## Candidate status

Full archive regression, original900/1240/1000/22 replays and updated240-case
holdout are pending at this candidate freeze. No pass or completion gain is
inferred before execution. Independent semantic/human review remains NOT RUN.
The user authorizes merging dependent PRs once tests and release gates pass;
no merge has occurred for this iteration yet.

## Rejected100805f and typed-role repair

Candidate100805f passed1501 native software tests and52 public controls, and
measured189/420 expanded positives,50/64 new-holdout positives,with all580 and176
refusals preserved. The900 public fields and200 controls also passed; historical
completion stayed3/22. Those are intermediate results, not the final candidate.

A later developer counterexample exposed untyped modifier inversion: General
Location was selected for location of general; Due Date and Local Time had similar
problems. Three subcases failed (exit1). Citation fidelity did not establish that
the normalized field meant what the question requested. This candidate is rejected
for that criterion even though its software and frozen benchmark tests passed.
Actual frozen source100805f and raw execution/test evidence are retained under
rejected-100805f; no independent semantic judgment is fabricated.

Version2 restricts reordering to an explicit catalogue of documentary-role noun
heads, preserves every modifier, and declines arbitrary names or nonspecific
adjectives. Independent Deposit Date vocabulary remains answerable. The66 focused
controls pass (exit0); new full validation is pending. No frozen input/key/dice
was changed, and all prior runs remain available. The remaining lexical rules
and role catalogue are finite engineering assumptions, not general language
understanding or an independently certified ontology.
