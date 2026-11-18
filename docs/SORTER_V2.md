# Offline candidate sorter, rules v2

Last reviewed: 2026-11-18. Implemented addition; v1 (`mplpb_work.sorter`) is frozen and unchanged.

Rules v2 is a separate engine, `mplpb_work.sorter_v2`, with schema `offline-candidate-sorter-v2`. It keeps the v1 graph contract (sources, nodes, spans, edges, limits, replay, retired export) and every assessment flag stays false. v1 graphs, frozen studies and implementation pins are untouched; v1 and v2 refuse to verify each other's graphs. A v1 graph may be supplied to v2 as `--prior` (historical snapshot only).

```sh
python -m mplpb_work.sorter_v2 sort RAW --mode compare --output V2.json
python -m mplpb_work.sorter_v2 verify V2.json --sources RAW
python -m mplpb_work.sorter_v2 peruse V2.json --sources RAW --max-items 8
python -m unittest tests.test_sorter_v2 -q
```

## What changed

| Rule | Change |
|---|---|
| R1 | Identifiers and reference targets never end in `. : / -`. `Correction to SHIP-7.` now resolves. Internal punctuation (`REC-1850.7`) is kept. |
| R2 | Numbered designations (`Letter No. 41`, `Despatch No. 12`; a document-type word is required) are identifiers with canonical key `LETTER-NO-41`. A designation line in the file's leading header block declares the record. |
| R3 | A reference target must be an identifier, designation, `<message-id>` or URL. Ordinary words are never targets. Correction wording with no recognizable target becomes an `unrecognized_target_form` review. |
| R4 | Passive corrections are references with a direction: self (`hereby`, `by this notice`) links; a third-party agent (`by SHIP-9`) or no agent is review-only. |
| R5 | Every feature carries `local_scope`, judged within its clause. Statement `scope` keeps the exact v1 value. Reference resolution uses `local_scope`. |
| R6 | Negation must govern the correction cue (negator within the clause, before the cue, ≤5 words). Double negation (`not untrue`) is `negation_scope_unresolved`. |
| R7 | Reported speech (`said`, `claimed`, `according to`, …) in the same clause as the cue is `reported_speech_scope`. |
| R8 | "the earlier/previous/last note …" with a correction or error cue and no ID → `descriptive_reference_review` listing up to five candidate occurrences that share a four-word phrase, or ≥3 content words including one used by at most two occurrences. None is selected. |

On `tests/fixtures/sorter`, v1 and v2 propose the same 14 review edges.

## Limits

- Same-clause trailing reporting cues are conservatively qualified; arbitrary reported-speech scope is not understood.
- Descriptive pair checks share the comparison budget; exhaustion is explicit and never resolves a target.
- One numbered designation per file header block; multi-record files need `Message-ID`-style headers.
- Cue lists are English only and lexical; nothing here understands meaning.
- R8 candidates are lexical; their precision is unmeasured (see the evaluation plan).
