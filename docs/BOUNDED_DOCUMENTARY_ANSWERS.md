# Bounded documentary answers

Last reviewed: 2026-11-20.

Ask for two explicit fields on one record, for example “What are the accession
date and shelf code for record FOLIO-71?” Each field uses the ordinary exact
checker and its own correction view under the original question and delivery
profile. An API-supplied as-of time applies to both views. The question must fit
the two-field grammar in full.

The strict response includes a decision for each field under `question_parts`.
A missing field can leave a cited partial. A conflict remains a conflict. Two
complete field proofs must share a source record or have a direct, pinned
supersession between their sources. Both proofs share the same total citation
budget. Before output, the reader rechecks both serving views and all inspected
alias views. A source change discards the result.

The opt-in investigation output lists repeated explicit Message-ID declarations
under `event_candidates.communication_candidates`. Each occurrence keeps its
source pin, exact declaration and body digest. A body collision flags the
candidate for review. Matching wording and candidate membership leave event
identity and co-reference unresolved.

## Automated acceptance

The [bounded acceptance workflow](../.github/workflows/bounded-documentary-acceptance.yml)
runs the focused controls and public evidence suite, then replays the frozen
expanded batch with the existing isolated D% worker. After execution, the
[acceptance verifier](../tools/verify_bounded_repair.py) compares earlier verified
answers with their retained native outputs, requires all 580 refusals to hold,
and checks each new compound answer against the two literal field lines in its
frozen source. The private key stays outside the runner. The workflow also
replays the 22 historical development questions and publishes its run reports.
These runs measure source support under the declared rules. Independent
semantic review remains open.

A chronology, wording comparison, attributed statement or explicit chain still
requires its own bounded proof and acceptance cases. The
[documentary reconstruction guide](HISTORICAL_RECONSTRUCTION_ENGINE.md)
describes the existing opt-in investigation and its evidence limits.
