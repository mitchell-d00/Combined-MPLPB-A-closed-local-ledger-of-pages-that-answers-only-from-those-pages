# FRUS-Presentation

Last reviewed: 2026-11-25.

This frozen replay compares the public baseline
`941511731b6b5af8d767110930aee7b92a1dcc5a` with the candidate on the same four
comparisons and five inherited controls. The added control asks the exact
PE-04 question with only the eligible advice record. The [freeze receipt](freeze.json)
binds all inputs, the private key digest and the [candidate rule](candidate-rule.md).

| Case | Native discovery before → after | Admitted propositions | Strict Ask before → after |
|---|---|---:|---|
| PE-01 | Both anchors → both anchors | 0 → 0 | Miss → miss. Assessment and forecast remain open. |
| PE-02 | Both anchors → both anchors | 0 → 0 | Miss → miss. Intent and delegation remain open. |
| PE-03 | Both anchors → both anchors | 0 → 0 | Miss → miss. The attributed account and conditional recommendation remain open. |
| PE-04 | Both anchors → both anchors | 1 → 2 | Checked partial → complete. Named advice and the quoted self-report are independently cited. |
| Five inherited controls | — | 0 → 0 | 5/5 expected withholds in each run. |
| Added presentation control | Advice record only | 1 → 1 | Presentation correctly withheld in both runs. The valid advice partial stays available. |

For the four positive cases, discovery stayed **4/4**, complete answers moved
**0/4 → 1/4**, partials moved **1 → 0**, and misses stayed **3**. Zero false
support or execution failures were observed across the ten cases.
[Decisions, citations and original source coordinates](results.json)

## What PE-04 establishes

The April 10 meeting record identifies the upcoming trip and reports that
Samuels suggested Stans stress “outwardness” rather than “inwardness” in trade
policy. The April 28 editorial account first names Maurice Stans as reporting to
President Nixon about a completed mission. It repeats Stans as the reporter,
then introduces his first-person wording with “He also reported”. The adjacent
memo citation names Secretary Stans and President Nixon and gives the same date.

> In my public speeches and meetings with the American and European business
> leaders, I expressed the basis of the Administration’s approach to
> international economic problems in terms of four economic freedoms expressed
> as ideals

The uninterrupted quotation lists freedom to trade, travel, invest and exchange
technology. The result preserves Stans's words as a self-report quoted within
the editorial account. The date check establishes the order of the records.
Event identity, implementation, outcome and independent truth remain unresolved.

The first candidate trial withheld presentation because the byline grammar did
not recognize the departmental title in “Secretary of Commerce Maurice Stans”.
Its readback is retained. The parser accepts departmental titles and checks
both full names and surnames, preserving the frozen rule and inputs. A
same-surname, different-first-name control also withholds in unit testing.

## Replay

Restore the two permission-reprinted pages into the
[operator packet](operator-packet.tar.gz) as directed by the
[public restore instructions](../focus-extend/README.md#replay). The scorer
needs the evaluator's separately held key. Readbacks omit permission-reprinted
body text and discovery excerpts. The worker was passed no custody path.
Local OS isolation was not used.

```sh
EVIDENCE=evaluation/pole/open-items/frus-presentation
(cd "$EVIDENCE" && sha256sum -c evidence.sha256)
python -m tools.pole_focus_extend run-prose --packet PACKETS/packet --implementation BASELINE --output before.json
python -m tools.pole_focus_extend run-prose --packet PACKETS/packet --implementation CHECKOUT --output after.json
python -m tools.pole_frus_presentation --packet PACKETS/packet --custody CUSTODY --freeze "$EVIDENCE/freeze.json" --rule "$EVIDENCE/candidate-rule.md" --before before.json --after after.json --output scored.json
```

[Native readbacks](native-readbacks.tar.gz)

Focus-12 and scan and phrase limits remain open. Outside-custodian scoring,
independent historical accuracy, independent semantic adjudication and
native OOCC remain **NOT_RUN**.

[Exact source archive validation](validation.json)
