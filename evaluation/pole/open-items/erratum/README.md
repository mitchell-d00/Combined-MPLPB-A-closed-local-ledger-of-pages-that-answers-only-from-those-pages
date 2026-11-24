# BT-Erratum, Polybius-Prose, Scan-Phrase, and Komnene-Hold

Last reviewed: 2026-11-24.

Baseline `7b91951ec3aa2bf12f4c3fea34b91f1b2fae4d46`. Freeze the
[operator packets](frozen-operator-packets.tar.gz) and
[candidate rule](candidate-rule.md) before scoring. The comparison used identical
packets and budgets. Expected outcomes and the typed reference stayed outside the
worker. Raw receipts record `os_isolated: false` and no passed custody path.
The candidate readback identifies the in-progress engine by file hashes; its
checkout HEAD was still the baseline during the first comparison. All citations
use exact body-projection offsets and ledger path plus SHA-256. The operator
packets preserve original bytes and their SHA-256 identities.

## BT-Erratum

| Frozen measurement | Before | After |
|---|---:|---:|
| BT-01 discovery found all required anchors | 1/1 | 1/1 |
| BT-01 Strict Ask complete with typed proof | 0/1 | 1/1 |
| Expected withholds | 5/5 | 5/5 |
| False-supported bridges | 0 | 0 |
| Execution failures | 0 | 0 |

The erratum reports that it withdrew the attribution “McPhetridge's private M6”
and that benchmark scores did not change. The earlier version states
“The package does not establish that Gelhaus used McPhetridge's private M6.”
The two propositions have separate exact witnesses. The notice and version
1.2 document resolve by title and version under the same repository commit.
Private execution remains unresolved.
[Earlier version](https://github.com/mitchell-d00/B-Tests/blob/e3a544b2e8ac37f5a23323025b264c18a15678f7/docs/papers/archive/testing-oocc-v1.2/TESTING_OOCC.md) ·
[Erratum](https://github.com/mitchell-d00/B-Tests/blob/e3a544b2e8ac37f5a23323025b264c18a15678f7/docs/paper/TESTING_OOCC_ERRATA.md)

| Control | Candidate disposition |
|---|---|
| BT-03 | Withheld actual execution. Neither source certifies an execution. |
| BT-C01 | Withheld. No eligible earlier document matched the reported version. |
| BT-C02 | Withheld. No eligible erratum was available. |
| BT-C03 | Withheld. The captures did not belong to the named repository. |
| BT-C04 | Withheld the combined actual-execution and changed-score request. Its propositions lack evidence. |

The final rule shares the [frozen candidate’s](candidate-rule.md) scope.
Both captures must resolve within one GitHub revision by canonical title,
declared earlier version and a strictly later correction version. A positive
proof needs an unambiguous withdrawal, an explicit unchanged-scores sentence,
and a complete verification-limited sentence containing the exact disputed
wording. Quoted or qualified scope, duplicate matches, ineligible sources,
changed bytes, or a budget hit prevent completion. Repository capture
declarations bind the local proof; native support does not independently audit
the private execution or recompute scores. The prior frozen BT-01 projections
without capture manifests remain withheld on replay.

## Polybius-Prose

| Frozen cohort | Native discovery | Overlap discovery | Strict complete | Strict partial | Answerable misses | Expected withholds | False-supported |
|---|---:|---:|---:|---:|---:|---:|---:|
| Retained Scout, before → after | 3/6 → 3/6 | 2/6 → 2/6 | 0/6 → 0/6 | 1 → 1 | 5 → 5 | 6/6 → 6/6 | 0 → 0 |
| Added Solo, before → after | 4/4 → 4/4 | 2/4 → 2/4 | 0/4 → 0/4 | 0 → 0 | 4 → 4 | 4/4 → 4/4 | 0 → 0 |

The four added comparisons ask about a change across telegrams, a recommendation
reflected in a later message, contrasting descriptions of a leader, and a
reported omission paired with a separate activity. All four found the
authored anchors. Strict Ask returned `interpretation_unsupported` on each
before and after. These four are missed answerable cases. A shared date,
subject, or correspondent does not prove which proposition carries over.
The controls withheld final language, an operation, exact White Paper wording,
and deliveries without witnesses for those outcomes. This cycle added no rule
for ordinary-prose linking.

## Scan-Phrase

| Frozen test | Before → after | Limit reached |
|---|---|---|
| Authentic literal ladder, 2 and 24 pages | Complete → complete | None |
| Authentic literal ladder, 31, 34 and 38 pages | Partial → partial | 200,000 characters and 1,000 units |
| Authentic literal ladder, 42 pages | Partial → partial | 200,000 characters, with 456 units examined |
| 40-page controls, compact / long / many units | Complete / partial / partial, unchanged | None / character only / unit only |
| Babbage crowded witness control | Two distinct records in eight slots, unchanged | Witness slots filled |
| Babbage frozen chain | Incomplete → incomplete | Repeated phrase-group budget |
| Authentic USDA venue pair | Two records in 30 shared groups, incomplete in both runs | Phrase-token and repeated phrase-group budgets |
| Babbage proof eligibility and cap controls | One eligible proof, four withholds, unchanged | External denial, withdrawal, passage cap, reference scan cap |

Literal partials retained a local witness with corpus-wide completeness
unresolved. Sorter groups provide discovery only. No cap changed.

## Komnene-Hold

| Check | Before | After |
|---|---:|---:|
| Paired questions and anonymous arms | 22 / 44 | 22 / 44 |
| Public packet hashes matching concealed mapping | 22/22 | 22/22 |
| Keys in delivery | 0 | 0 |
| Independent scoring | NOT_RUN | NOT_RUN |

Delivery archive SHA-256
`af4f3c37b8f02c4f7a9cbe94db158e6a85b429d7d01202dfbceb90d7476076b1`.
The reproduced archive matched the existing delivery byte for byte.
[Custody verification](receipts/komnene-hold.json)

## Replay

Verify `sha256sum -c evaluation/pole/open-items/erratum/evidence.sha256` and
extract the frozen operator packets to a new directory. Use the worker without
the separate custody mount. Only the evaluator runs scoring with the sealed
local development key. The venue sorter replay uses the unchanged Douglass
packet from the [prose cycle](../prose/README.md).

```sh
python -I -B tools/pole_authentic.py run --packet PACKETS/bt-erratum --implementation CHECKOUT --output bt-native.json
python -m tools.pole_erratum_cycle score-erratum --packet PACKETS/bt-erratum --custody CUSTODY --receipt bt-native.json --output bt-scored.json
python -m tools.pole_remaining polybius --packet PACKETS/polybius-added --output prose-native.json
python -m tools.pole_remaining score-polybius --packet PACKETS/polybius-added --custody CUSTODY --receipt prose-native.json --output prose-scored.json
python -m tools.pole_remaining lovelace-limit --packet PACKETS/scan-phrase --output scan-phrase.json
python -m tools.pole_prose_cycle douglass-sorter --packet DOUGLASS --implementation CHECKOUT --output sorter.json
```

[Native readbacks](native-readbacks.tar.gz) · [Matched outcomes](receipts/matched-summary.json) ·
[Evidence checksums](evidence.sha256). The readbacks also retain the initial
candidate and a failing baseline regression with independently worded sources.
All previously complete Tacitus, Herodotus-DHS and Douglass cases retained
their claims and exact witnesses. Independent historical accuracy and native
OOCC remain **NOT_RUN**.
