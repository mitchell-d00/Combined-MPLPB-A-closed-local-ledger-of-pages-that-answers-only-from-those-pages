# Bounded documentary answers

Last reviewed: 2026-11-25.

The first transfer is retained with an explicit development-control overlap limit. A fresh packet was frozen before further edits and passed 24/24 once on source `7ed65a5`; its constructions differ from all inspected development examples, with generator templates still visible to the same operator. Both rounds remain separately reported.

The [shared attribution trial](../evaluation/attribution/2026-11-25/README.md) adds a bounded source-framed instruction path. A printed signature binds first-person letter voice; explicit bylines and instruction predicates keep recorders/reporters distinct from named speakers. Quoted speech supports what the source attributes to its speaker, with historical occurrence and execution unverified. Complete eligible witnesses, conservative competing-source checks and final source-state checks govern the claim. Development is **48/48** and the fresh once-only same-operator transfer is **24/24**, with 17 PE-02 contracts unchanged. Generator templates were visible and no independent preparation/blinding or adjudication is claimed. Full archive regression and exact-head CI are pending. [Permanent controls](../tests/test_source_attributed_instructions.py).

Ask for two explicit fields on one record, for example “What are the accession
date and shelf code for record FOLIO-71?” Each field uses the ordinary exact
checker and its own correction view under the original question and delivery
profile. An API-supplied as-of time applies to both views. The question must fit
the two-field grammar in full.

The browser and plain-text CLI display the decision for each field. The strict
JSON response exposes the same details under `question_parts`.
A missing field can leave a cited partial. A conflict remains a conflict. Two
complete field proofs must share a source record or have a direct, pinned
supersession between their sources. Both proofs share the same total citation
budget. Before output, the reader rechecks both serving views and all inspected
alias views. A source change discards the result. Fields inside HTML quotation
blocks remain contextual mentions.

The opt-in investigation output lists repeated explicit Message-ID declarations
under `event_candidates.communication_candidates`. Each occurrence keeps its
source pin, exact declaration and body digest. Quoted Message-ID lines are
excluded from grouping. A body collision flags the
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

## Selected-source inspections

Use `reconstruct` with one of these options and exact ledger source IDs.

```sh
python -m mplpb_answers reconstruct LEDGER "Inspect the archival records" --compare-wording LEAF-A LEAF-B --format text
python -m mplpb_answers reconstruct LEDGER "Inspect the archival records" --earliest-writing-date LEAF-A LEAF-B
python -m mplpb_answers reconstruct LEDGER "Inspect the archival records" --trace-sources LEAF-A LEAF-B LEAF-C
```

The wording inspection compares both complete canonical bodies, cites them, and
reports token changes and literal equality. The date inspection requires one
valid `Date Written: YYYY-MM-DD` body field on each selected source. It retains
ties and leaves the earliest date unresolved if either proof is missing.

Tracing requires three complete unqualified source bodies. The dispatch
statement must explicitly name the request source. The reported receipt must
explicitly name the dispatch source. The sender, object and destination must
agree literally. The returned prefix stops at the first unsupported step and
preserves the identity of the person reporting receipt. The operation reports
source observations and leaves event identity and historical truth unresolved.

These opt-in forms require explicit source selection. The unchanged strict
stress questions for chronology, wording and chains have their own grammar
coverage results. See the [documentary reconstruction guide](HISTORICAL_RECONSTRUCTION_ENGINE.md)
for the existing research workflows.
