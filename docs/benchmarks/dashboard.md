# Archival inspection benchmark dashboard

Last reviewed: 2026-11-20.

Synthetic development, authentic development and unseen independent evaluation are separate. Percentages below are developer-key measurements; they are not historical accuracy. Citation fidelity concerns exact source anchoring at run time, not historical truth or permanent eligibility.

| Version / revision | Dataset | Cases | Complete count* | Supported precision | Complete recall | Correct refusal | Citation fidelity |
|---|---|---:|---:|---:|---:|---:|---:|
| initial / `6334e1b3a08d` | synthetic_development | 1240 | 20 | 100.0% | 3.33% | 100.0% | 100.0% |
| checked-prose / `6e0de9e6f14f` | synthetic_development | 1240 | 200 | 100.0% | 33.33% | 100.0% | 100.0% |
| archival-dates / `ee85ab3b3fa5` | synthetic_development | 1240 | 200 | 100.0% | 33.33% | 100.0% | 100.0% |
| archival-before / `bc6f25c053df` | authentic_development | 22 | 2 | unmeasured | unmeasured | unmeasured | unmeasured |
| archival-after / `ee85ab3b3fa5` | authentic_development | 22 | 3 | unmeasured | unmeasured | unmeasured | unmeasured |
| Unseen independent | NOT RUN | 0 | unmeasured | unmeasured | unmeasured | unmeasured | unmeasured |

*Synthetic counts are key-matched complete answers. Authentic counts are native support flags, not independently judged correctness. These counts do not establish historical recall.

For counts, denominators, source report hashes and limitations, inspect the adjacent JSON. Unknown is null, never zero. Incomplete executions do not get full-run rates. Unscored supported semantics prevents a precision claim. No independent human score has been supplied.


## Supplementary field-access and expanded stress measurements

These are separate known synthetic populations; do not combine their percentages
with the historical rows above. Exact field-key matches and developer-proposition
matches are not independent historical judgments.

| Population | Before | Updated | Expected refusals retained |
|---|---:|---:|---:|
| Public literal-field positives |150/900|900/900|200/200|
| Expanded frozen stress positives |156/420|168/420|580/580|
| Unchanged historical originals |3 native complete/22|3 native complete/22|Refusal correctness unmeasured|

[Field-access evidence](../../evaluation/field-question-normalization/2026-11-20/REPORT.md)
· [Expanded stress failures and costs](../../evaluation/dpercent-expanded/2026-11-20/REPORT.md)
· [Response paper](../research/field-question-normalization/README.md).
Full native regression:1482 tests and52 public controls passed at9b5ff0c.
The original dashboard generator covers the rows above; these supplemental dated
experiments are linked separately and pinned in dashboard.json.


## Bounded source-field aliases: native2427d80

This subsequent iteration preserves every prior table and population above.

| Population | Prior complete | Native2427d80 complete | Expected refusals |
|---|---:|---:|---:|
| Expanded unchanged1000 |168/420|189/420|580/580|
| Original unchanged1240 |200/600|200/600|640/640|
| Public field positives |900/900|900/900|200/200|
| Developer240 |16/64|50/64|176/176|
| Prospective150 after native freeze |10/40|33/40|110/110|
| Historical22 |3 native complete|3 native complete|Correctness unmeasured|

No incorrect support or execution failures were observed in these synthetic
replays. The prospective study caused no later native edits but remains
developer-authored. Independent semantic review is NOT RUN. Resource costs,
failed candidates, exact pins and a self-contained synthetic replication ZIP:
[field-alias report](../../evaluation/field-aliases/2026-11-20/REPORT.md).
The new [known-weakness sampling study](../DPERCENT_KNOWN_WEAKNESSES.md) has its
own source seals and per-class denominators; it does not replace these rows.
