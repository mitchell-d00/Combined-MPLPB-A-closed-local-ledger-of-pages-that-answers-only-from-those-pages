# Archival inspection benchmark dashboard

Last reviewed: 2026-11-19.

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
