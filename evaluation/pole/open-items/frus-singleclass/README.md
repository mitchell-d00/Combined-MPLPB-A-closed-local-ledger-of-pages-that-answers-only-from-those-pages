# FRUS-SingleClass

Last reviewed: 2026-11-25.

The baseline is `1b963aea9ce14d207ec2f6b645912c3a7c98cdd9`. The
[freeze receipt](freeze.json) binds the original four FRUS comparisons,
their existing controls, one additional wrong-speaker control, the
evaluator key digest and the [candidate rule](candidate-rule.md).
Publisher-layout projection and the budgets are stable across both runs.

| Case | Discovery before → after | Native proposition admission | Strict Ask before → after |
|---|---|---|---|
| PE-01 | 2/2 → 2/2 | 0 → 0 | Miss → miss. Institutional assessment and forecast remain outside the admitted class. |
| PE-02 | 2/2 → 2/2 | 0 → 0 | Miss → miss. The intent and delegation obligations remain open. |
| PE-03 | 2/2 → 2/2 | 0 → 0 | Miss → miss. Reporter attachment and the conditional recommendation remain open. |
| PE-04 | 2/2 → 2/2 | 0 → 1 | Miss → checked partial. Named advice is cited. The separately reported presentation remains unresolved. |
| Existing controls | — | 0 → 0 | 4/4 → 4/4 expected withholds. |
| Added wrong-speaker control | — | 0 → 0 | Expected withhold → expected withhold. The question asks for Buchanan’s advice. The witness names Samuels. |

Complete answers stayed **0/4 → 0/4**. Partials moved **0 → 1** and
misses moved **4 → 3**. All five controls withheld with no claims.
There were no false-supported bridges or execution failures.
[Exact counts and checked citations](results.json)

## Admitted proposition

The eligible meeting record provides both exact witnesses.

> The focus of the discussion was Secretary Stans’ upcoming trip to Europe.

> Mr. Samuels suggested that Secretary Stans stress “outwardness” rather than “inwardness” in trade policy.

The native rule accepts a finite two-obligation question where the first
part asks about named advice before a specified trip. It matches adviser,
recipient and subject to a complete source sentence and checks the adjacent
discussion’s upcoming-trip witness. It rereads eligible originals, checks
source state and scopes chronology to the recorded discussion. Ambiguity,
negation, uncertain quotation, missing trip context, an ineligible source or
a budget hit prevents the partial. The second obligation remains unresolved.
The rule carries the reported-advice modality and exact emphasis in its typed
proposition. No general discourse composition or execution claim follows.

The initial candidate missed the surname-final possessive “Stans’.” That
readback is retained. The revised parser accepts possessive forms for names
ending in S and preserves the original rule, packet, labels and budgets.
The independent wording regression was tested on both sides. The public
readbacks omit full projections and retrieval excerpts for the two
permission-reprinted pages.

## Replay

Extract [the operator packet](operator-packet.tar.gz) and restore the two
permission-reprinted originals from the existing pinned captures or
[public restore instructions](../focus-extend/README.md#replay). The
evaluator keeps its key separate from the worker.

```sh
EVIDENCE=evaluation/pole/open-items/frus-singleclass
sha256sum -c "$EVIDENCE/evidence.sha256"
python -m tools.pole_focus_extend run-prose --packet PACKETS/packet --implementation CHECKOUT --output after.json
python -m tools.pole_frus_singleclass --packet PACKETS/packet --custody CUSTODY --freeze "$EVIDENCE/freeze.json" --rule "$EVIDENCE/candidate-rule.md" --before before.json --after after.json --output scored.json
```

Generate the before receipt with the same worker and packet on the exact
baseline checkout. [Native readbacks](native-readbacks.tar.gz)

Focus-12 and scan and phrase limits remain open. Outside-custodian scoring,
independent historical accuracy, independent semantic adjudication and
native OOCC remain **NOT_RUN**.
