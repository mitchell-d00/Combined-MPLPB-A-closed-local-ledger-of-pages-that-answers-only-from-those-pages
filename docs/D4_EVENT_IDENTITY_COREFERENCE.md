# Event identity, co-reference D4

Last reviewed: 2026-11-20.

MPLPB can answer a bounded event question about two explicitly named ledger
sources, or a bounded pronoun question about one named source. Both paths
cite current, eligible source bytes.

- A shared exact event key supports documentary agreement within one explicitly
  named event registry. For example, ask “Do sources LEAF-A and LEAF-B describe
  the same event?” Each source must supply the registry and event ID.
- A distinct-event proof requires an explicit `Different Event From` declaration
  and a unique target occurrence identifier in the same registry. Different keys
  and duplicate text alone leave the relationship unresolved.
- A selected source can bind a pronoun through a complete explicit gloss or
  bind “I” through one complete direct speech turn with a named speaker.
  Ask `Who does "I" refer to in source LEAF-A?` to check this form.
  The checker cites the complete turn. For a captured or imported source, the
  existing capture-manifest check verifies the captured text boundary.
  Competing names, embedded quotations and unresolved attribution withhold
  support.

The proof covers the printed records and their declared scope. Historical event
identity, cross-document person identity, free-form pronoun resolution and
independent source corroboration require further evidence and evaluation.

### Reading an event identity refusal

When the checker can identify a specific evidence gap, the CLI and browser
show the reason and a next step. The JSON diagnostic includes an optional
`evidence_gap` field. For example, a comparison can ask for verifiable event
declarations, explain that two verified declarations use different registries,
or flag that an occurrence target is ambiguous. A recognized but unsupported
unnamed comparison gets an example of the named-source question. That guidance
comes from the question form and expresses no finding about the source bodies.

The existing decision and diagnostic code still govern the result. Delivery
restrictions, source changes, and budget stops take precedence over these
explanations. A paired regression can compare both versions on the same inputs
and check that any new explanation leaves the decision, claims and citations
intact.

## Small documentary packets

The strict `ask` command also checks a bounded set of prose forms in a local
packet of up to eight eligible records. The verifier checks complete statements
and cites the original spans. It distinguishes `supported_answer`,
`partial_answer`, `conflict`, and `abstain` with an unresolved reason. This path
uses the same source eligibility and passage budget as other strict proofs.

- A matched room amendment can preserve the chair when the correction explicitly
  leaves the rest of the notice in force. Competing matching amendments retain
  both rooms and the unchanged chair.
- Explicit resumption under the same docket, body and printed dates can identify
  a continuation. An explicitly rescheduled proceeding can also be tied to its
  opening when the named proceeding, docket and adjusted date match.
- Competing logged times for the same numbered subject are displayed together.
  A bounded handoff chain can identify its immediate recipient while leaving a
  later returner unresolved. Signing a return log does not establish who returned
  the item.
- A local role description must identify a unique person. A case amendment used
  to bind a receipt signer needs the same case and role and explicit ISO dates for
  the applicable amendment and receipt.
- A canceled follow-up stays separate from the original inspection. Date-scoped
  depot names apply only to entries with the same declared log identifier.

Examples of admitted questions include “Which room and which chair should we
record?”, “Which September 10 meeting continued the September 3 session?”, and
“Which logging time do the records support?” The source grammar is finite.
The proof assumes a self-contained packet of eligible records. A loose match,
unsupported wording, extra unclassified records or an uncertain time scope can
leave the question unresolved.

## Run the fictional query panel

```sh
python -m tools.bounded_record_study --seed 91 --repeats 2 --require-pass
```

The panel runs 25 proof and boundary families using two seeded variations, three
wording styles, four fictional adult age bands and four education categories.
Each demographic group receives the same cases and the same mix of styles.
The age and education labels are reporting metadata. MPLPB receives the question
and source text. This design checks the wording variants and proof boundaries
under balanced labels. It provides no measurements about real people or their
language by age or education. The D4 acceptance workflow runs the panel alongside
the existing sealed mixed generator.

## Run the mixed generator

D4 offers a `gate` mix with the twenty identity and co-reference classes and
eighteen previously supported or safe-refusal D% controls. The `study` mix
includes all seventy-five known-weakness classes with additional sampling of
the twenty D4 classes. Old positive misses stay in the study denominator.
Fixtures vary question wording, source order, line endings, profile, speaker
spelling, quotation form and case family. The case schedule and choices are
seeded before execution without an engine-acceptance filter.

```sh
python -m tools.d4 prepare --public /tmp/d4-public --custody /tmp/d4-keys --mix gate --cases 380
python -m tools.d4 run --public /tmp/d4-public --output /tmp/d4-run --implementation . --workers 4
python -m tools.d4 score --public /tmp/d4-public --custody /tmp/d4-keys --run /tmp/d4-run --output /tmp/d4-score --require-pass
```

Use fresh paths. Bubblewrap runs the existing D% worker with a case packet and
the candidate implementation. The scorer opens custody only after execution.
For the broad study, prepare with `--mix study --cases 4096`, run the same
sealed packets against the baseline and candidate, then score the candidate
with `--baseline /path/to/baseline/summary.json --require-pass`. The study gate
requires all D4 cases to match and the mixed D% outcomes and graph controls to
match the baseline. Known legacy answer gaps remain visible in the report.

The [D4 acceptance workflow](../.github/workflows/d4-acceptance.yml) runs the
mixed gate and retains its per-case report. The
[D4 case study](../evaluation/d4/2026-11-20/CASE_STUDY.md) reports all 95
classes, the paired baseline, and the frozen producer. These fixtures are developer-authored synthetic data.
