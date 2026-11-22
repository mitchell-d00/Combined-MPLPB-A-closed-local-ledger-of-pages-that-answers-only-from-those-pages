# Historical synonym graph comparison

Last reviewed: 2026-11-22.

This test compares ordinary passage discovery and SQLite synonym graph-guided
discovery. It uses the [40 frozen historical follow-ups](../historical-patterns/README.md)
and adds 12 questions on three prepared starter records. All 52 graph queries
use curated record aliases. The graph preserves multiple record candidates.
The guided probe searches only the suggested records that pass the existing
eligibility check. Both probes use the same question, a 12-passage limit,
and an 8,000-character budget. With no eligible suggestion, the comparison
uses ordinary discovery for both sides.

The new records are compact factual summaries with source references.
They do not reproduce complete primary documents. The cases test commissioning
for USS America (CV-66), incorporation for Mount Airy, North Carolina, and the
South Riverside renaming in Corona, California. [Naval History and Heritage Command](https://www.history.navy.mil/our-collections/photography/us-navy-ships/alphabetical-listing/a/uss-america--cva-66-0.html) · [City of Mount Airy annual report](https://www.mountairy.org/DocumentCenter/View/1507/City-of-Mount-Airy-Comprehensive-Annual-Financial-Report---Year-Ended-June-30-2017) · [City of Corona Heritage Room](https://www.coronaca.gov/departments/library/heritage-room/history-of-corona)

## Results

| Measurement | 40 frozen follow-ups | 12 new-topic questions |
|---|---:|---:|
| Graph suggested every reference record | 27/40 | 12/12 |
| More than one eligible record suggested | 10/40 | 0/12 |
| Direct and paraphrase cases with every anchor visible, ordinary probe | 14/20 | 6/6 |
| Direct and paraphrase cases with every anchor visible, guided probe | 14/20 | 6/6 |
| Valid graph record-and-field pairs | 0 | 0 |

The Declaration paraphrase gained one of its two required excerpts.
The Darwin edition boundary question also gained a contextual excerpt.
No case lost a selected anchor. None of the imported pages declared a
literal field under the reader's field grammar. The graph selected documents
while proof still required interpreting prose.

The original strict results come from the retained replay, whose native file
hashes are checked against the current engine. The runner issued 12 new strict
queries for the prepared topics. It supported all three exact-quote locations
and withheld full support on all six ordinary questions and all three
boundary questions. All 13 boundary questions across both sets withheld full
support. The graph never changed the strict reader's input. Guided discovery
can exclude counterevidence, so the guided probe is for inspection. Authored
aliases and known-source questions do not establish blind transfer.

```sh
python -m test_tools.historical_graph_study --output /tmp/new-historical-graph
```

[Curated graph catalog](catalog.json) · [Starter records and questions](topics.json) ·
[Per-case comparison](report.json) · [New-topic strict outputs](new-topic-native.json)

## Original frozen 22

A separate replay uses all 22 original questions and the original reference
drafts. One question has no reference anchor and remains in the case report.
The graph produced an eligible record hint for **18/22** questions. Among 21
questions with drafted anchors, all anchors were visible in **4/21** ordinary
probes and **5/21** graph-guided probes. Two questions gained at least one
anchor and none lost one. The frozen native answer counts remain 3 full
supports, 2 partials, 3 conflicts and 14 abstentions.

```sh
python -m tools.article_study --output /tmp/historical-22-replay
python -m test_tools.historical_22_graph --original-replay /tmp/historical-22-replay \
  --output /tmp/historical-22-graph.json
```

[Original 22 case comparison](historical-22.json)
