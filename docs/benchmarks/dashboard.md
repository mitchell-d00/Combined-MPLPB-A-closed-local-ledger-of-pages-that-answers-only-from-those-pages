# Archival inspection benchmark dashboard

Last reviewed: 2026-11-19.

Synthetic development, authentic development and unseen independent evaluation are separate. Percentages below are developer-key measurements; they are not historical accuracy. Citation fidelity concerns exact source anchoring at run time, not historical truth or permanent eligibility.

| Version / revision | Dataset | Cases | Supported precision | Complete recall | Correct refusal | Citation fidelity |
|---|---|---:|---:|---:|---:|---:|
| initial / `6334e1b3a08d` | synthetic_development | 1240 | 100.0% | 3.33% | 100.0% | 100.0% |
| prose / `6e0de9e6f14f` | synthetic_development | 1240 | 100.0% | 33.33% | 100.0% | 100.0% |
| archival-baseline / `bc6f25c053df` | synthetic_development | 1240 | 100.0% | 33.33% | 100.0% | 100.0% |
| original-baseline / `bc6f25c053df` | authentic_development | 22 | unmeasured | unmeasured | unmeasured | unmeasured |
| Unseen independent | NOT RUN | 0 | unmeasured | unmeasured | unmeasured | unmeasured |

For counts, denominators, source report hashes and limitations, inspect the adjacent JSON. Unknown is null, never zero. Incomplete executions do not get full-run rates. Unscored supported semantics prevents a precision claim. No independent human score has been supplied.
