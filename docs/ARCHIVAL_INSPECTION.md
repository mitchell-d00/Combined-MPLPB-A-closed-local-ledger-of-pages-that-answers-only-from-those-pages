# Archival document inspection: first use and proof boundaries

Last reviewed: 2026-11-19.

Archival document inspection is the current research focus. The first goal is
more complete, correctly supported answers from unchanged records, with false
support and unnecessary refusals measured separately. More interfaces or green
software tests do not establish historical understanding.

## Five-minute tutorial

Run these commands from a repository checkout; no model or package installation
is needed. The evaluation/tutorial tools are not installed by the minimal wheel.

```sh
python -m tools.archival_tutorial --output /tmp/my-first-archive
python -m mplpb_answers ask /tmp/my-first-archive/ledger "Who surveyed West Reach?" --json
python -m mplpb_answers ask /tmp/my-first-archive/ledger "Who wrote the berth ledger?" --json
python -m mplpb_answers ask /tmp/my-first-archive/ledger "Did surveying West Reach cause the bombardment of South Cove?" --json
```

The offline tutorial creates four fictional text documents, copies their exact
text into sealed ledger bodies, records source hashes, and runs read-only
questions. These prepared teaching examples are not historical evaluation.
The first answer identifies an explicitly stated surveyor. Two different writers
of the same ledger produce `clarify`, not a chosen winner. The causal question
abstains: neither vocabulary overlap nor chronology establishes its missing link.
The fourth walkthrough question demonstrates independently checked date roles.
`walkthrough.json` retains all outputs and original source files remain beside it.

**One owner returns; two stop; none refuses.** Page ownership selects material;
strict answering additionally requires eligible body evidence under finite rules.
The tutorial's source-attributed answers do not authenticate historical events.
Use the existing collection/import workflow for your own authentic records;
never insert hidden answer fields or event labels into them.

## Explicit event/date relationships

The new finite request form is:

```text
Distinguish the bombardment, surrender, evacuation and telegram dates in the South Cove record, without treating the webpage review date as an event date.
```

Names are literal source-body constraints, not special archive identifiers.
Supported roles include artillery firing/bombardment, surrender, evacuation,
departure, arrival, publication, revision, sending, receipt, and source-body
catalogue dates for telegrams, letters, reports, memoranda and dispatches.
Only complete supported predicate constructions qualify. A demand, plan,
conditional, denial, quotation or uncertain attribution is not execution.

The existing independent kernel reloads current eligible material. It derives
each date/predicate relationship and its exact source span, examines the selected
record for competing or unresolved dated predicates/corrections, and checks a
unique source owner before completion. Actor names, event co-reference and causal
links are not inferred. Repeated event dates and ambiguous owners stop completion.
An exact, complete catalogue line may be separate from nearby navigation in a
coarse sentence unit; the parent context remains cited. Titles, filenames and
ledger metadata never supply the date fact.

The proposition distinguishes `source_reported_action_date`,
`source_catalogue_document_date`, `explicit_same_clause_relative_date` and
`webpage_review`. Review mentions are textual annotations, not historical events.
A catalogue date is a statement printed in the source body; it does not establish
when a telegram was sent, delivered or received. Narrative clauses retain their
full literal wording. An unstated year stays null instead of inheriting the year
of a catalogue entry, title or webpage date.

“The following day” is linked only to its governing date in the same sentence.
Calendar display arithmetic uses an explicitly labelled proleptic Gregorian
convention, not an authenticated historical calendar. Unknown-year leap-day
ambiguity prevents completion. `normalized_event_time` and historical event
identity remain null. The answer is complete only for this finite source-date
inventory, not for an exhaustive historical timeline or all possible date forms.

The locator has separate explicit caps: 64 eligible records and 2 MiB of canonical
source text. A selected record must fit 16,000 characters and 256 native units.
Other proof paths retain their existing budgets. No candidate or sorter edge is
proof. All required citations must fit the caller's original passage budget, and
the standard final source-state gate still invalidates changed evidence.

## Benchmark dashboard and review

The [compact dashboard](benchmarks/dashboard.md) separates synthetic development,
authentic development and unseen independent evaluation. Its JSON retains sample
sizes, denominators, revisions, report hashes and null unknown metrics. Synthetic
precision is against a developer key; historical precision/recall and refusal
correctness are not inferred from native outcome counts. Exact citation fidelity
is not semantic correctness or a promise of future serving eligibility.

`tools.benchmark_dashboard` regenerates both formats from retained reports. The
[dated experiment](../evaluation/archival-inspection/2026-11-19/REPORT.md) supplies
the actual before/after commands and results, including failed attempts.

`tools.blind_archival_packets` exports anonymous paired answers, complete eligible
source projections, unchanged original bytes with source/import mappings, and
blank review templates. Original files preserve documentary layers for inspection;
their export is not new ledger authorization. It withholds implementation pins,
scores, change logs and draft reference answers. The private crosswalk must stay
outside the public packet directory and outside runtime. Every original case,
including refusals and partial answers, remains present. Familiar development
questions do not become an unseen evaluation by anonymizing their IDs.

Each anonymous collection is compatible with the existing human validator:

```sh
python -m tools.unprepared_challenge score COLLECTION REVIEWER1.json REVIEWER2.json --output /tmp/new-reviewed-score.json
```

Two real human submissions and bound adjudication for disagreements are required
by that validator. Declared identities and independence are not authenticated by
software. A fresh AI session can assess the same anonymous material with cited
reasons, but its output must be labelled **AI assessment**, not human review.
No model personas or downloaded historical articles count as reviewers.

The [independent protocol](../evaluation/archival-inspection/2026-11-19/independent-protocol.json)
keeps the 200-unseen-question milestone **NOT RUN** until independent questions
and actual review exist. Published institutional references found through search
are [reference notes](../evaluation/archival-inspection/2026-11-19/external-reference-notes.json),
not fresh judgments of MPLPB outputs. Shared wording may reflect shared source
dependence. None of those external pages enters the runtime ledger or closes an
answer. No independent historical accuracy target is claimed here.
