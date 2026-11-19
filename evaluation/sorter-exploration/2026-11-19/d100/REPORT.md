# B-Tests d100 local run and exploration companion

2026-11-19. Requested local d100 gate before merge. Native B-Tests and new exploration checks passed. This checkpoint does not claim main is merged;publication status is recorded separately after CI.

B-Tests revision: `64b646ee89ea819f59f39f0eecced71ee7ef24c8`. MPLPB revision: `c7dd333f06b4f0af739d36672b2f98727be5a5b9`. Fresh random seed: `13814892761879707678`. The upstream generator/harness/catalog were not edited. Their hashes and packet/key/dice commitments are in [freeze.json](freeze.json).

* Native run: **100/100 cases**,25/25 scripted users,100 exact workspace replays.25 supported,25 competing-owner,25 processed-only and25 insufficient-original cases. All expected results passed.
* Exploration companion: **100/100 cases**,25/25 users. Both v2 modes retained identical sources,nodes and node labels. Source replay,all false exploration support/identity/truth flags,native contract equality,current-profile boundaries,external raw withholding,budgets and unchanged ledgers/packets passed.
* External B-Tests harness regression: **123 tests passed**,exit0. Native and companion commands exited0.
* No model inference ran. This does not measure model quality,relationship semantic precision or historical truth. The100 web topics label fictional fixtures;Wikipedia supplied topic metadata,not evidentiary historical answers. Human-independent historical accuracy remains unmeasured.

The upstream runner targets the native v1 sorter/workspace,so passing it alone would not exercise the new explorer. The separately retained [companion checker](check_exploration.py) reads the same100 packet questions and built ledgers. It never reads `operator-key.json`. The upstream evaluator uses the operator key for scoring;the key is not passed to the MPLPB CLI. This is input separation,not a claim that the entire host filesystem was OS-isolated from runtime processes.

Reproduce from B-Tests at the pinned revision,with MPLPB at the clean pinned revision:

```bash
python -m unittest discover -s tests -q
python -m research_lab.sorter_random_batches prepare --out /tmp/NEW-d100 --seed 13814892761879707678 --revision c7dd333f06b4f0af739d36672b2f98727be5a5b9
python -m research_lab.sorter_random_batches run --out /tmp/NEW-d100 --mplpb-root /PATH/TO/MPLPB
python /PATH/TO/check_exploration.py --mplpb-root /PATH/TO/MPLPB --batch /tmp/NEW-d100 --out /tmp/NEW-d100-exploration
```

All generated packets,source files,questions,operator key,dice rolls,command receipts,native workspaces/source maps and companion outputs are in the two SHA-pinned ZIPs listed in [summary.json](summary.json). Outputs must be new directories. Neither suite changed MPLPB or its input packets.

Companion cost: 8.771005s CPU/8.800479s wall,peak process RSS 23404544bytes. The unchanged native upstream runner does not instrument CPU/wall totals,so those metrics remain null. Human review time,semantic precision/recall and historical accuracy remain null. No full historical22-question coverage gain is claimed.

Local test conditions are satisfied. Merge requires the repository's exact-head archived-source CI gates;these tests do not replace those gates.
