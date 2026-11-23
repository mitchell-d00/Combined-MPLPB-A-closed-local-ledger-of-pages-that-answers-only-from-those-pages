# D6 calendar arithmetic, source notes, and thesaurus sprints

Last reviewed: 2026-11-23.

The three features use independent interfaces. D6 verifies declared source fields and performs arithmetic. WorkStore notes order source inspection and suggest which existing rule family to inspect. The thesaurus provides lexical discovery alongside the reviewed synonym graph. Strict answer support still comes from the deterministic reader.

## Calendar arithmetic

D6 plans select `proleptic_gregorian` explicitly for each new operation. Dates must be complete and in years 1–9999. Results are stated under the chosen calendar convention.

| Operation | Inputs and result |
| --- | --- |
| `day_difference` | Two Date fields, with signed `elapsed` days or chronological `inclusive` endpoint counting. A same-day inclusive interval returns one. |
| `add_months` | A Date field, signed integer month count, and `clamp` or `reject` for absent month-end days. |
| `relative_date` | A Date field and same-record Relative Date field with the same role prefix. Supports “the next day,” “the following day,” and “the previous day.” |

Calendar operations report the calculation and cite the operands. A relative expression bound to `Opening Date` remains unresolved with `Publication Date` as its anchor. The plan gives the endpoints their source labels and leaves event identity, causal claims, business-day calendars, and historical calendar conversion outside its conclusions.

Create a disposable ledger from the [example source](calendar-source.json) and run the plan.

```sh
ledger=$(python - <<'PY'
from html import escape
import json
from pathlib import Path
from tempfile import mkdtemp
from mplpb_combined.ledger import write

root = mkdtemp(prefix='d6-calendar-demo-')
source = json.loads(Path('evaluation/d6/calendar-notes/calendar-source.json').read_bytes())
body = source.pop('body')
write(root, **source, body_html='<pre>' + escape(body) + '</pre>', when='2026-11-23')
print(root)
PY
)
python -m mplpb_answers.d6 "$ledger" evaluation/d6/calendar-notes/calendar-plan.json
```

The [example plan](calendar-plan.json) produces a leap-day relative date, elapsed and inclusive counts, and a clamped month shift.

## Read and write source notes

Use a WorkStore seat with the needed task scope and `create:source_note`, `revise:source_note`, or `search:source_note` rights. Register the ledger as a work corpus, create a task, and write an evidence record with the eligible source ID, revision hash, and exact quote. The note anchors that quote at a zero-based character position in MPLPB’s canonical body text. The work log retains changes and withdrawals.

An example `put` request for a note. Set the source offset, evidence revision, visibility and view head from the actual task. Only grant visibility already available on the evidence.

```json
{
  "op": "put", "id": "N1", "kind": "source_note",
  "payload": {
    "task": "T1", "body_start": 0, "rule": "date_roles",
    "keywords": ["opening date", "receipt"], "comment": "Check which date belongs to the action.",
    "state": "active"
  },
  "dependencies": {"E1": 1}, "visibility": ["reviewer"],
  "expected_revision": 0, "expected_head": "<current seat view head>"
}
```

Read the current authorization-scoped rank with this request. Submit JSON with `python -m mplpb_work request /path/to/work --credential-file /path/to/seat.json --input search.json`. The local seat RPC also accepts this operation.

```json
{
  "op": "source_note_search", "task": "T1", "corpus": "archive",
  "question": "Which date does the receipt record?",
  "max_passages": 4, "max_chars": 2000
}
```

The six rule labels are `date_roles`, `conditions`, `corrections`, `recorded_stage`, `causal_scope`, and `literal_values`. Search scores unique query terms against note keywords and gives each exact span at most one vote. The report includes the note revision, evidence revision, source span, note snapshot, and serving policy fingerprint. Free-text note comments remain in the WorkStore and are excluded from ranking output. Missing or changed sources drop from discovery. A source change during the read clears the results.

## Build and inspect the thesaurus graph

Use the Princeton WordNet 3.0 archive and the pinned 62b916d mirror of Grady Ward’s Moby Thesaurus. WordNet supplies same-sense lemmas and typed broader, narrower, instance, part, member and substance links. Moby entries are shown as separate associations because they mix synonyms and related terms. The database preserves the WordNet license text. [WordNet license](https://wordnet.princeton.edu/license-and-commercial-use) · [WordNet archive](https://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz) · [Moby publication](https://www.gutenberg.org/ebooks/3202) · [Pinned Moby input](https://github.com/words/moby/blob/62b916d83a13324094c16c0e7a0fe9c6c8caeb61/words.txt)

```sh
python -m mplpb_work.thesaurus build /tmp/thesaurus.sqlite /path/to/WordNet-3.0.tar.gz --moby /path/to/mthesaur.txt
python -m mplpb_work.thesaurus lookup /tmp/thesaurus.sqlite canal
python -m mplpb_work.thesaurus probe /tmp/thesaurus.sqlite /path/to/ledger \
  "What happened to the canal?" canal --sense n:02947212 --relation broader
```

The probe requires an explicit sense and one edge type. It shows the ordinary search, a small expanded query, and exact spans containing the selected edge terms. Each is a discovery view with its own budget. Keep the [reviewed synonym graph](../../../docs/TEST_INDEX.md) for corpus-specific phrase-to-record and field suggestions. Lexical results can guide what phrases to review for that graph.

## Sprint results

| Check | Result |
| --- | --- |
| Calendar operations | 48/48 matched controls over six century years, with invalid inputs and source boundaries checked separately |
| Notes discovery at one passage | 0/12 ordinary hits, 12/12 with authored notes on the same collections |
| Strict answer contracts | All 12 exploratory questions and one supported exact-field control stayed identical after note creation |
| Real lexical relations | All six selected WordNet edges existed and Moby associations remained separate |
| Lexical discovery at one passage | 0/6 ordinary hits, 2/6 with expanded terms, 6/6 from the separate exact-edge span search |
| Lexical strict controls | All six strict contracts stayed identical |

These discovery measurements use authored passages and deliberately placed distractors. The lexical datasets are real. Historical transfer remains a separate evaluation.

```sh
python -m test_tools.calendar_notes_study --thesaurus /tmp/thesaurus.sqlite --output /tmp/calendar-notes-study.json
python -m unittest tests.test_d6_calendar tests.test_source_notes tests.test_thesaurus_graph -v
```

[Final case rows](study.json) · [Earlier lexical ranking](before-lexical-span-ranking.json) · [Lexical dataset pins and counts](thesaurus-build.json)
