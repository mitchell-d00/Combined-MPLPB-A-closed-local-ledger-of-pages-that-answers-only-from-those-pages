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
  For example, ask “Who does “I” refer to in source LEAF-A?”
  The checker cites the complete turn.
  Competing names, embedded quotations and unresolved attribution withhold
  support.

The proof covers the printed records and their declared scope. Historical event
identity, cross-document person identity, free-form pronoun resolution and
independent source corroboration require further evidence and evaluation.

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
[D4 study directory](../evaluation/d4/2026-11-20) retains the frozen producer
and study evidence. These fixtures are developer-authored synthetic data.
