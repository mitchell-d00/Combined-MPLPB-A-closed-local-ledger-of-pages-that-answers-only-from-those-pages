# Dice Bag live-web blind test

Last reviewed: 2026-11-22.

Dice Bag draws historical earthquake records from the live USGS catalog. It
uses random historical windows from the existing open-data seed generator and
selects one unused event per draw by hashing the seed-dependent selection key
and the catalog event ID. It separately records unfilled draws. The loader
retains original JSON, request URLs, retrieval times, source hashes, event URLs,
and the pointers used to read magnitude and depth. The ledger fixtures are
field excerpts of that structured catalog data. [USGS reuse terms](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits)

The custodian receives the seed, raw captures, and answer key. The operator
receives source excerpts, a frozen field lexicon, shuffled questions without
category labels, and a hash commitment. Preparation, offline native execution,
and scoring are separate commands. The CLI uses separate input paths. Use a
separate OS account or mount for stronger custody if the operator is untrusted.
The field lexicon stays fixed across draws. Record aliases come from the
captured place labels and preserve collisions.

## Run a fresh bag

Use fresh paths for inputs, custody, and outputs. Run preparation with network
access. Run replay with just the operator packet and the local source checkout.
Keep the key with the scorer until the replay is complete.

```sh
python -m test_tools.dice_bag prepare --inputs /tmp/dice-bag-operator --custody /tmp/dice-bag-custody --count 12
python -m test_tools.dice_bag run --inputs /tmp/dice-bag-operator --output /tmp/dice-bag-run.json
python -m test_tools.dice_bag score --inputs /tmp/dice-bag-operator --run /tmp/dice-bag-run.json --key /tmp/dice-bag-custody/key.json --output /tmp/dice-bag-scores.json
```

Omit `--seed` for a new bag. A recorded seed reproduces the draw plan.
Retain the specific bytes and sealed packet for exact replay. The live catalog
can change. Keep unfilled draws when comparing batches.

The runner records the strict reader answer and synonym candidates separately.
Scoring verifies the frozen key hash and checks exact claims and citations.
After reveal, the scorer tests native proof with both selectors only on
reference-positive cases for which the index found the correct pair. This
measures what the reader can prove with a confirmed pair. Qualified, missing,
and ambiguous cases remain lookup-only for the index.

## First live run

All 12 draws filled. The test scored 72 questions. Source hashes and JSON
pointers were independently checked by reading the captured response files.
Two offline runs returned byte-identical JSON.

| Question family | Strict baseline | Synonym lookup | Native proof after revealed confirmation |
|---|---:|---:|---:|
| Direct field and explicit ID | 12/12 exact answers | 12/12 correct pairs | 12/12 exact answers |
| Natural wording using listed phrases | 0/12 exact answers | 12/12 correct pairs | 12/12 exact answers |
| Natural wording outside the lexicon | 0/12 exact answers | 12/12 incomplete | No pairs confirmed |
| Extra time condition | 12/12 withheld | 12/12 single candidate pairs | Lookup only |
| Competing place descriptions | 12/12 withheld | 12/12 ambiguous | Lookup only |
| Missing shaking duration | 12/12 withheld | 12/12 incomplete | Lookup only |

These are unseen live-source rows under authored question families. The
lexicon and listed-phrase questions were designed together, with a separate
unlisted wording control. The run measures catalog-field behavior on one
domain. It does not establish performance on independently authored
questions or unfamiliar prose. [Run receipt](first-live-receipt.json) ·
[Frozen lexicon](lexicon.json) · [Test Index](../../docs/TEST_INDEX.md)

For an opt-in graph replay, pass `--graph-db PATH` to `run`. The installed
[SQLite synonym graph](../../docs/SYNONYM_GRAPH.md) can also group the operator
questions for review. The published 72-case replay receipt preserves the
original comparison. [SQLite replay receipt](sqlite-graph-replay.json)
