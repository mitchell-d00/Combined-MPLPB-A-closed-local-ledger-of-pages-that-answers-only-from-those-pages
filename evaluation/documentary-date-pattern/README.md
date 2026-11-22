# Documentary date roles and report section discovery

Last reviewed: 2026-11-22.

The historical follow-ups separated two failures. Both Fort Sumter wordings
made the selected excerpts visible, and the paraphrase failed to reach the
existing date verifier. The ordinary Apollo 13 summary question missed its
reference passage under the default passage budget.

## Date proof rule

The reader accepts a second complete question form that requests separate
dates from a named page or record. Every item must map to a recognized date
role. “Opening fire” requires a source assertion about firing on the named
site or its matching site type. “Giving up the harbour” requires an
explicit statement that someone surrendered the named harbour. “Leaving it” must follow that surrender item and
requires the existing same-clause evacuation relationship. A date listed in
the catalogue retains its catalogue role. The original question remains the
input to the same ownership, source, counterevidence, and completion checks.

Independent phrasing about a fictional harbour failed before the change and
passes afterward. Controls keep extra obligations visible, including actual
telegram receipt and time restrictions. They also cover reported surrender,
a different target, missing evacuation, and an opening-fire date confused
with a bombardment date. [Before test log](baseline-focused.log) ·
[Paired results and typed evidence](paired-results.json)

On the unchanged original 22, all native answer contracts still match apart
from code hashes. There are 3 complete answers, 2 partials, 3 conflicts,
and 14 abstentions. On the 40 follow-ups, the Fort Sumter paraphrase is the
only changed answer. It moves from abstention to full native support with
all selected anchors. The paraphrase arm moves from **0/10 to 1/10**, and all
10 boundary cases still withhold full support. The repaired answer
distinguishes the firing, surrender, relative evacuation, and telegram
catalogue dates. It does not authenticate receipt or infer the missing years.

## Separate discovery experiment

For a request that explicitly names a report summary, first locate one
eligible record through the synonym graph. Then look for a unique numbered
summary heading followed by prose. Use the existing passage units, with a
bounded window around that section, as a second discovery result. A table
of contents and two competing summary headings cannot select a section.

In the Apollo 13 pair, ordinary discovery missed the target excerpt in
both wordings. The section probe surfaced the excerpt for the question
that names the summary. It left the other form without a section hint.
This probe runs separately from the answer engine. Its result establishes
a discovery improvement for the explicit-section case. It leaves the
causal proof question and any automatic use of the hints open.
[Section probe output](section-probe.json)

```sh
python -m test_tools.historical_patterns --output /tmp/date-pattern-40
python -m tools.article_study --output /tmp/date-pattern-22
python -m test_tools.report_section_probe --output /tmp/report-section-probe.json
python -m test_tools.historical_graph_study --historical-replay /tmp/date-pattern-40 \
  --output /tmp/date-pattern-graph
```

These are development fixtures and known original sources. Independent
historical semantic review remains outstanding.
