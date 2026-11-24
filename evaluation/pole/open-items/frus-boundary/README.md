# FRUS-Boundary

Last reviewed: 2026-11-24.

FRUS-Boundary binds the four Polybius-Extend comparisons and their four
existing controls to baseline `16a1f9f883bd5c1d6e366cb139272a997a41765a`.
The [freeze receipt](freeze.json) pins the original packet, prior result,
separately held scoring key and the [candidate rule](candidate-rule.md).
Questions, originals, publisher-layout projection, order and budgets
match the preceding run. The scorer receives the key after Strict Ask
has run. Worker receipts record `os_isolated: false`.

| Frozen case | Native discovery before → after | Strict Ask before → after | Boundary reason |
|---|---|---|---|
| PE-01 | 2/2 → 2/2 | Abstain → withhold, answerable miss | The checker does not certify the address's institutional assessment and the article's prospective limit on the U.S. role as separately attributed assertions. |
| PE-01-CONTROL | — | Withhold → correct withhold | The packet supplies neither an abolition witness nor a causal link to the address. |
| PE-02 | 2/2 → 2/2 | Abstain → withhold, answerable miss | No native certificate binds Nixon's intended transition in the letter to Laird and his instructions in the separate letter to Smith. The modality of each assertion matters. |
| PE-02-CONTROL | — | Withhold → correct withhold | A concluded agreement and its proposed cause have no witness in the two letters. |
| PE-03 | 2/2 → 2/2 | Abstain → withhold, answerable miss | No native certificate composes Buchanan's attributed account of Nixon's pre-trip view with Nixon's direct recommendation at the council. |
| PE-03-CONTROL | — | Withhold → correct withhold | The records show a reported need and a proposal. The packet leaves creation of an actual body and its cause unresolved. |
| PE-04 | 2/2 → 2/2 | Abstain → withhold, answerable miss | No native certificate combines Samuels's advice with Stans's reported presentation while preserving the two speakers and roles. |
| PE-04-CONTROL | — | Withhold → correct withhold | Advice, reported messaging and reactions leave actual removal of specific trade barriers and the proposed link unresolved. |

Strict Ask complete stayed **0/4 → 0/4** and partials stayed **0 → 0**.
All four controls withheld in both runs. There were zero false-supported
bridges. The four comparison results retain their answerable reference
labels. Each still returns `interpretation_unsupported` with zero native
claims. Neither the named-reference grammar nor the documentary planner
admitted any of the four full questions.

The audit matched all eight discovery anchors to unique projected spans
in the intended eligible appearances and checked raw SHA-256 and byte and
character coordinates. Each positive returned 12 passages and between
2,874 and 6,451 characters under the fixed 8,000-character output budget.
The retrieval search reported incomplete coverage. The exact referenced
witnesses were nevertheless present. The reader refused at proof
admission, with no binding budget diagnostic on the four positives.
The witness audit measured the sealed packet; native binding of the
question's document and speaker roles remains unverified.
[Exact witness coordinates and reader decisions](boundary.json)

The rule withholds cross-record support until each proposition has a
native certificate tied to the proper original and attribution. A
comparison of two source statements requires those two certificates.
An asserted causal, temporal or implementation link needs its own
witness. This cycle records the boundary over the existing native checker.

## Replay

Extract [the operator packet](operator-packet.tar.gz) into a fresh directory.
Restore the two permission-reprinted originals using their pinned
publisher URLs and hashes as described in the [previous replay](../focus-extend/README.md#replay).
The [public native readback](native-readbacks.tar.gz) retains the complete
local receipt's hash and omits the two reprinted sources' full projections
and discovery excerpts.

```sh
EVIDENCE=evaluation/pole/open-items/frus-boundary
sha256sum -c "$EVIDENCE/evidence.sha256"
python -m tools.pole_focus_extend run-prose --packet PACKETS/prose --implementation CHECKOUT --output native.json
python -m tools.pole_frus_boundary --packet PACKETS/prose --custody PROSE_CUSTODY --rule "$EVIDENCE/candidate-rule.md" --freeze "$EVIDENCE/freeze.json" --previous evaluation/pole/open-items/focus-extend/receipts/prose-rendered.json --receipt native.json --output boundary.json
```

The open Focus-12 items and scan and phrase limits keep their previous
accounting. Outside-custodian scoring, independent historical accuracy,
independent semantic adjudication, and native OOCC remain **NOT_RUN**.
