# Expanded D% stress generator

Last reviewed: 2026-11-20.

This optional offline developer tool expands known-error testing without changing
MPLPB's answer rules. It reuses the existing D% worker, isolation and source gates.
There are 48 semantic families, 1,440+ field structural cells and further prose
variations. Names alone are not the test variation. No runtime acceptance filter
removes difficult cases. This is not independent historical validation.

## Generate, freeze, run and score

Run from a source checkout with Python and Linux bubblewrap available:

```sh
python -m tools.dpercent_expanded prepare --out /tmp/expanded-public --custodian /tmp/expanded-private --cases 1000
python -m tools.dpercent run --packets /tmp/expanded-public --implementation . --out /tmp/expanded-run
python -m tools.dpercent_expanded score --packets /tmp/expanded-public --custodian /tmp/expanded-private --run /tmp/expanded-run --output /tmp/expanded-score.json
python -m unittest tests.test_dpercent_expanded -q
```

Directories/files must be new. `--cases` accepts 1–4096; use `--seed` to replay a
chosen nonnegative 128-bit seed. Keep custody outside the repository and disjoint
from public packets. The public seal commits to the seed, exact keys/dice and all
source bytes. Keys are opened only by the post-run scorer. Do not edit generator,
keys or packets after sealing. Freeze a new batch for further generator changes.

The protocol states budgets. Existing worker network/CPU/memory isolation and
unchanged source, ledger, sorter-node and non-authority guards still apply.
Scoring emits both the base score and the expanded field-set score. A successful
scoring command means a report was written, not that all answerable cases passed.
Inspect E, F, execution failures, incorrect support and unscored outputs; retain
all failures. Never promote a matching quote into historical truth. Independent
semantic/human review remains NOT RUN. Feature counts have denominators and
outcomes; correlated feature cohorts are diagnostic, not causal explanations.

[Versioned experiment and frozen protocol](../evaluation/dpercent-expanded/2026-11-20/REPORT.md).
