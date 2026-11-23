# D6 evidence plans

Last reviewed: 2026-11-23.

D6 is an opt-in native experiment for compiling a step-by-step answer from a plan and declared ledger fields. The plan names each record and field. The strict reader checks the currently eligible body spans. The report shows each decision, the branch taken, unresolved steps, and exact source excerpts with their record, revision hash and body offsets.

| Step | What it does |
| --- | --- |
| `read` | Reads one verified body field from the specified record. |
| `match` | Checks a literal comparison. A field ending in `Date` requires valid full dates. A field ending in `Year` requires valid four-digit years. Other fields compare exact text. |
| `not_match` | Checks for a verified difference at the required precision. Missing or ambiguous values stay unresolved. |
| `year_difference` | Subtracts the left year number from the right. The fields must end in `Year` or `Date`. The result is a difference between calendar year numbers. |
| `if` | Runs the then branch on a verified true comparison and the else branch on a verified false comparison. An unresolved condition leaves both branches unrun. |
| `all` | Compiles required steps. A verified “no” can be part of a complete answer. Any unresolved required step leaves the group incomplete. |

The [fictional source](example-source.json) records October 28, 1872 as crisp, with mild weather in the prior autumn of 1871. The [example plan](example-plan.json) verifies the date, checks the weather contrast, and shows that 1872 is 98 year numbers after 1774 and one after 1871.

Run from the repository root. The setup creates a disposable ledger and prints its path.

```sh
ledger=$(python - <<'PY'
from html import escape
import json
from pathlib import Path
from tempfile import mkdtemp

from mplpb_combined.ledger import write

root = mkdtemp(prefix='mplpb-d6-example-')
source = json.loads(Path('evaluation/d6/example-source.json').read_bytes())
body = source.pop('body')
write(root, **source, body_html='<pre>' + escape(body) + '</pre>', when='2026-11-22')
print(root)
PY
)
python -m mplpb_answers.d6 "$ledger" evaluation/d6/example-plan.json
```

Add `--json` for the same result as a structured record.

## Calendar operations and discovery notes

D6 accepts elapsed and inclusive day counts, explicit month shifts, and role-pinned relative dates. See the [calendar, notes and thesaurus sprints](calendar-notes/README.md) for the new plan shapes and reproduction.

## Run corpus experiments

```sh
python -m test_tools.d6 --seed 6 --count 6 --output /tmp/d6-study.json
python -m test_tools.d6 --seed 12 --count 16 --output /tmp/d6-new-seeds.json
python -m test_tools.d6 --dice-bag-inputs /path/to/operator --output /tmp/d6-dice-bag.json
```

The [Dice Bag guide](../dice-bag/README.md) explains how to draw and seal a new operator packet. D6 reads the sealed operator packet and checks that its structured fields compile together. It adds a missing-duration control per record. This companion experiment has its own results and preserves the original Dice Bag question scores and custodian key.

For other D-series corpora, keep the source and existing judgments frozen. Add a separate plan where the corpus provides declared fields, record which comparisons and branches should resolve, and report D6 results alongside the existing suite. Cases that only offer ordinary prose remain useful for measuring passage discovery and extraction. D6 currently requires supplied selectors and declared source fields. It neither discovers them automatically from prose nor certifies external historical truth.

The [recorded first run](study-summary.json) covers 90 synthetic checks across six seeds and the 12-record frozen Dice Bag packet. These are structured-field development checks.
