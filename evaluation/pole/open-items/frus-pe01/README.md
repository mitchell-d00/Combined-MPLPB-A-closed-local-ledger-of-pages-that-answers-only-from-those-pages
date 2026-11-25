# FRUS-PE01

Last reviewed: 2026-11-25.

The [freeze receipt](freeze.json) binds the baseline
`2a0bc642fe21b164fd921758f56bb43f49e5a361`, the four comparison cases, six
inherited controls, one new same-form attribution control, the separate
evaluator key, and the [candidate rule](candidate-rule.md). The diagnostic
rereads the original sources through the existing native eligibility and
canonical projection. It leaves the Strict Ask implementation in place.

| Case | Native discovery before → after | Native propositions | Strict Ask before → after |
|---|---|---:|---|
| PE-01 | Both anchors → both anchors | 0 → 0 | Miss → miss. Canonical body lacks the required speaker and author declarations in the tested forms. |
| PE-02 | Both anchors → both anchors | 0 → 0 | Miss → miss. Intent and delegation remain open. |
| PE-03 | Both anchors → both anchors | 0 → 0 | Miss → miss. Attribution and conditional recommendation remain open. |
| PE-04 | Both anchors → both anchors | 2 → 2 | Complete → complete. Named advice and quoted presentation retain their citations. |
| Five inherited full-withhold controls | — | 0 → 0 | All five withheld in both runs. |
| Inherited missing-presentation control | — | 1 → 1 | Presentation withheld in both runs. Checked advice retained. |
| New Hoover attribution control | Both statements located by the probe | 0 → 0 | Expected withhold in both runs. Hoover is mentioned in the address. Neither publisher byline names him. |

Discovery remained **4/4** and complete Strict Ask remained **1/4**.
Three positives remained misses. Six controls fully withheld. The inherited
missing-presentation control retained its scoped partial. False-supported
bridges and execution failures were zero. [Exact results](results.json)

## Attribution boundary

The address contains an assessment about many old institutions. The article
contains a qualified forecast about the future US role. Exact proposition
anchors and their enclosing native units were found. Both publisher headings
name Richard M. Nixon. Their exact original byte and character coordinates and
hashes are recorded as diagnostic evidence. The current canonical projection
excludes those headings. Neither body supplied a matching declaration in the
tested forms. The same source pair supplied no Hoover attribution.

Each probe completed its native scan of **50,502 characters and 359 units**,
with no limit reached. The frozen rule withheld both target propositions at
the attribution prerequisite. It never converted a heading, loose mention,
or question premise into an answer certificate. The permission-reprinted
bodies are omitted from public receipts. The records allow reproduction
from pinned originals without republishing the full text.

## Replay

Extract the [sealed operator packet](operator-packet.tar.gz) and restore the
two permission-reprinted sources using the
[public restore instructions](../focus-extend/README.md#replay). Run the first
command with BASELINE and before.json, then with CANDIDATE and after.json.
Only the scorer needs the separately held evaluator key. The worker was
passed no key path. Local OS isolation was not used.

```sh
EVIDENCE=evaluation/pole/open-items/frus-pe01
(cd "$EVIDENCE" && sha256sum -c evidence.sha256)
python -m tools.pole_focus_extend run-prose --packet PACKETS/packet --implementation CHECKOUT --output native.json
python -m tools.pole_frus_pe01 --packet PACKETS/packet --custody CUSTODY --freeze "$EVIDENCE/freeze.json" --rule "$EVIDENCE/candidate-rule.md" --prior evaluation/pole/open-items/frus-presentation/results.json --before before.json --after after.json --output scored.json
```

[Native readbacks](native-readbacks.tar.gz)

PE-01 through PE-03, Focus-12, scan and phrase limits and broader held-out
proof remain open. Outside scoring, independent historical accuracy,
independent semantic adjudication and native OOCC remain **NOT_RUN**.
