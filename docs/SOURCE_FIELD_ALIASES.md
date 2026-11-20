# Source-grounded field aliases

Last reviewed: 2026-11-20.

The strict question pipeline can map bounded alternative field expressions to
currently eligible source-body declarations. For example, “date of inspection”
may select an actual `Inspection Date:` header. The original question remains
the policy input. The output quotes the original label and value, with normal
source IDs, hashes and offsets. `question_normalization` is explicitly not evidence.

Only small finite lexical rules and date/time/location-of reordering with a
declared documentary-role noun head are licensed. Arbitrary names and adjective
inversions (for example General Location into location of general) are declined.
No model chooses fields, no semantic score awards support, and no dates, actions
or identities are invented. Two matching labels require clarification even when
values agree. Use the existing explicit `--field` selector to inspect a particular
literal label; this still passes every source and delivery gate.

Alias candidates use their own field-scoped correction views and the original
as-of selector. All inspected source/policy states are rechecked before output.
A mutation discards old claims and normalization anchors. Body quotation, examples
and conditions do not become primary declarations. Missing or ambiguous mappings
remain unresolved; unrelated record IDs cannot supply a field.

Inspection is capped at64 eligible sources,2MiB canonical text,256 declarations
and at most four field views. Native authority reads are additional; total I/O
is not established by these caps. The existing answer budget is unchanged.
Unsupported syntax, unrestricted synonyms, compound questions and general
historical understanding are not claimed.

[Versioned technical report](../evaluation/field-aliases/2026-11-20/REPORT.md)
contains before/after commands and failure records. New holdout generation:

```sh
python -m tools.field_alias_challenge --out /tmp/alias-public --custodian /tmp/alias-keys --cases 240
python -m tools.dpercent run --packets /tmp/alias-public --implementation . --out /tmp/alias-run
python -m tools.dpercent_expanded score --packets /tmp/alias-public --custodian /tmp/alias-keys --run /tmp/alias-run --output /tmp/alias-score.json
```

Use new directories; never overwrite old seals/runs. Synthetic keys remain outside
engine execution. Developer-authored holdouts do not establish independent semantic
accuracy. Published expected outcomes will be hash-pinned for third-party replay.
