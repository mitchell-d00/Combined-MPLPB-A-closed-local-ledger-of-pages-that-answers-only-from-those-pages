# Focus-12, Polybius-Extend, Cap-Diagnosis, and Komnene-Status

Last reviewed: 2026-11-24.

Baseline `78f6a464212214a29a84f400a199be46a25db8bf`. The original focus
packet supplied the 12 answerable misses and all 20 original negative
controls. The fresh Polybius set uses four authored source comparisons and
four matched controls on eight official FRUS pages from the 1969–1976
Foundations of Foreign Policy volume. These particular pages were absent
from the earlier Scout and Solo datasets. Local development keys were
committed by hashes and passed only to the evaluator. Worker receipts
record `os_isolated: false`.

## Focus-12

| Measure | Before | After |
|---|---:|---:|
| Native discovery found every required statement | 8/12 | 8/12 |
| Strict Ask complete | 0/12 | 0/12 |
| Checked partials / abstentions on answerable cases | 2 / 10 | 2 / 10 |
| Original controls with correct non-support decisions | 20/20 | 20/20 |
| False support / execution failures | 0 / 0 | 0 / 0 |

The 20 controls include 18 abstentions and two conflicts. The current
replay matched the older pinned focus outcomes and diagnostics on all 32
selected cases. The 12 positive outcomes retain their original labels.

| Case suffix | Family | Blocking condition |
|---|---|---|
| Medium 00004 | Date roles | Continuous source text. The question form and same-record writing role are outside the date inventory. |
| Medium 00005 | Reported statement | Indirect speech in a letter. The named-reporter question has no attribution goal. |
| Medium 00007 | Reported statement | Line-wrapped indirect speech. The authored anchors were found and the named-reporter question has no attribution goal. |
| Medium 00009 | Date roles | Two line-wrapped dates in one letter. The question form and writing role are outside the date inventory. |
| Medium 00011 | Reported statement | Direct quotation. The named-reporter question has no attribution goal and quoted authorship lacks a direct-action certificate. |
| Medium 00015 | Date roles | Both statements are line-wrapped. The question form and writing role are outside the date inventory. |
| Hard 00003 | Partial correction | Dated-letter reference and prose values. The current rule needs a named target and declared fields. Discovery missed one of two required source statements. |
| Hard 00006 | Request–dispatch–receipt | The receipt points back by request date. The current chain proof requires a link to a named dispatch. Discovery missed one of three required source statements. |
| Hard 00007 | Wording change | Exact local alignments were returned. The separate unchanged-destination goal stayed unresolved. |
| Hard 00010 | Wording change | Same unresolved destination goal. Local alignments remained a partial. |
| Hard 00011 | Request–dispatch–receipt | Line-wrapped date references with no named dispatch reference. Discovery missed one of three required source statements. |
| Hard 00012 | Partial correction | Transcript-form letter and date-based correction. The current proof requires a named target and declared fields. Discovery missed one of two required source statements. |

[Full IDs, native diagnostics and rule admission](receipts/focus-diagnostics.json)

## Polybius-Extend

| Measure | Raw layout | Rendered-layout projection |
|---|---:|---:|
| Native discovery found both anchors | 0/4 | 4/4 |
| Strict Ask complete | 0/4 | 0/4 |
| Strict Ask partials / answerable abstentions | 0 / 4 | 0 / 4 |
| Expected withholds | 4/4 | 4/4 |
| False-supported bridges | 0 | 0 |

The pairs cover policy institutions, a move toward negotiation and delegation
instructions, allied consultation, and a comparison of proposed and reported
trade-policy messaging. The controls ask for institutional abolition,
a concluded agreement, the creation of a consultation body, or the removal
of trade barriers. All four answerable questions still return
`interpretation_unsupported` after discovery recovers both anchors.
[Anchor readback](receipts/prose-anchor-coverage.json) ·
[Official FRUS volume](https://history.state.gov/historicaldocuments/frus1969-76v01)

The [frozen projection rule](projection-rule.md) is confined to the evaluation
importer. It folds delivery whitespace inside ordinary HTML text nodes.
The complete publisher document div, its structural boundaries, and
the original byte and character anchor coordinates provide the same
scoring obligations. Strict Ask's proof rules and numerical limits were
unchanged.

## Cap-Diagnosis

| Frozen test | Before → after | Limiting condition |
|---|---|---|
| Literal lookup, 2 or 24 pages | Complete → complete | No limit reached |
| Literal lookup, 31, 34 or 38 pages | Partial → partial | 200,000 characters and 1,000 units |
| Literal lookup, 42 pages | Partial → partial | 200,000 characters, with 456 units examined |
| 40-page compact, long, and many-unit controls | Complete, partial, partial in both arms | None, 200,000 characters only, 1,000 units only |
| Crowded multi-record test | Two eligible records retained in eight witness slots in both arms | Witness slots filled |
| Frozen phrase chain | Incomplete in both arms | 32 repeated groups |
| Authentic USDA venue sorter | Two records and 30 shared groups in both arms | 256 tokens per unit and 32 repeated groups |
| Named proof eligibility and budget controls | One eligible proof and four withholds in both arms | External denial, withdrawal, passage budget, reference scan budget |

The direct ordinary-prose question abstained at every corpus size with
`interpretation_unsupported`. The literal partials retained evidence and
reported incomplete scan coverage. [Caps receipt](receipts/caps-after.json) ·
[Phrase receipt](receipts/phrase-after.json)

## Komnene-Status

| Check | Before | After |
|---|---:|---:|
| Paired questions / anonymous arms | 22 / 44 | 22 / 44 |
| Question hashes matching concealed mapping | 22/22 | 22/22 |
| Keys in delivery | 0 | 0 |
| Outside scoring | NOT_RUN | NOT_RUN |

The byte-identical delivery SHA-256 is
`af4f3c37b8f02c4f7a9cbe94db158e6a85b429d7d01202dfbceb90d7476076b1`.
Independent historical accuracy, outside-custodian scoring, independent
semantic adjudication, and native OOCC remain **NOT_RUN**.
[Komnene verification](receipts/komnene.json)

## Replay

Check `sha256sum -c evaluation/pole/open-items/focus-extend/evidence.sha256`
from the repository root. Extract the [frozen operator packets](frozen-operator-packets.tar.gz)
into a fresh directory. The two permission-reprinted pages are represented
by pinned publisher URLs and hashes in the public bundle. Restore them
from matching originals before replay. The runner rejects a changed
file or an incomplete packet. The public native readbacks retain hashes
of the complete local receipts for those pages and omit their full
projected bodies and discovery excerpts.

```sh
curl -fsSL https://history.state.gov/historicaldocuments/frus1969-76v01/d2 -o PACKETS/prose/sources/FRUS-D2.html
curl -fsSL https://history.state.gov/historicaldocuments/frus1969-76v01/d3 -o PACKETS/prose/sources/FRUS-D3.html
python -m tools.pole run --packets PACKETS/focus --out FOCUS_RUN --implementation CHECKOUT
python -m tools.pole score --packets PACKETS/focus --custody FOCUS_CUSTODY --run FOCUS_RUN --out focus-score.json
python -m tools.pole_focus_extend run-prose --raw-layout --packet PACKETS/prose --implementation CHECKOUT --output prose-before.json
python -m tools.pole_focus_extend run-prose --packet PACKETS/prose --implementation CHECKOUT --output prose-after.json
python -m tools.pole_authentic score --packet PACKETS/prose --custody PROSE_CUSTODY --receipt prose-after.json --output prose-score.json
python -m tools.pole_remaining lovelace-limit --packet PACKETS/caps --output caps.json
```

[Native readbacks](native-readbacks.tar.gz) · [Evidence checksums](evidence.sha256)
