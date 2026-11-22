# D20 owner and alias stress test

Last reviewed: 2026-11-22.

D20 runs 20 synthetic cases per seed. Five request or alias formats each receive
four matched conditions. The question within each group stays fixed.

| Condition | Expected source decision |
|---|---|
| Unique owner | Give the recorded owner and cite eligible evidence |
| Competing owners | Withhold a single owner and preserve the conflict where the reader detects it |
| Missing owner | Withhold the missing field |
| Retired source | Withhold the owner given only by the withdrawn page |

The strict arm uses native ledger writes and withdrawal in a fresh temporary
ledger per case. The raw arm feeds the same starting text to the offline sorter
and records the candidate graph digest, candidate counts, and exclusions. Raw
files do not carry the ledger's withdrawal decision. This arm measures candidate
preprocessing only. It does not score a raw-intake answer or measure human
review time.

## Run D20

From the full source checkout, use a new output directory and record the engine
revision. Share the fixtures with the operator and keep the key with the scorer.

```sh
git rev-parse HEAD
python -m test_tools.d20 generate --seed 20 --output /tmp/d20-seed20
python -m test_tools.d20 run --fixtures /tmp/d20-seed20/fixtures.json --output /tmp/d20-seed20/native.json
python -m test_tools.d20 score --run /tmp/d20-seed20/native.json --key /tmp/d20-seed20/answer-key.json --output /tmp/d20-seed20/score.json
```

Use a different integer seed and directory for another draw. Seeds change the
record identifiers and owners across the same five public structures. The
challenge split holds back whole structures from the development split, and both
are visible in this repository. Arrange a separate, custodian-held batch with
independently written structures for blind evaluation. When a case informs a
repair, retain it as development and regression evidence.

The scorer reports positive misses without failing the command. It exits 1 for
unsupported answers or incorrect support among these fixture cases. It checks
the expected owner claim, citation text and eligible revision hashes, and
requires both the owner and alias-link witnesses when the alias is on a separate
page. Safe withholding and explicit conflict recognition are visible separately
in the case details.

## Frozen seed 20 baseline

Engine revision `d497b0009eb079b475259ffef04f9d2da4277284`, using the D20 runner
added in this update. The native engine code was unchanged. The canonical field
question returned the expected owner, and its competing-owner control reported
a conflict. The alternate owner question and three alias forms missed their
supported cases. All 15 controls withheld a single-owner answer.

| Measurement | Result |
|---|---:|
| Expected supported cases | 1/5 |
| Expected single-owner withholds | 15/15 |
| Incorrect or unsupported answers | 0 |
| Explicit conflict among competing-owner cases | 1/5 |

Retained [fixtures](fixtures.json), [key](answer-key.json),
[raw native run](native.json.gz), and [per-case score](score.json).
Keep these files when a rule changes and write the replay to a new path.
See the [Test Index](../../docs/TEST_INDEX.md) for the training loop and other
testing methods.

## Large study and class-level probes

The same engine revision ran 64 seeds from 1000 through 1063, for 1,280
primary cases and 320 diagnostic replays. Replay the grouped counts and
per-seed input, key, and output digests with:

```sh
python -m test_tools.d20 study --first-seed 1000 --count 64 --output /tmp/d20-study.json
```

| Family | Supported / expected | Canonical selector recovered the misses | Additional result |
|---|---:|---:|---|
| Canonical field question | 64/64 | — | All 64 competing-owner cases reported conflict |
| Alternate owner question | 0/64 | 64/64 | Rephrasing alone recovered support |
| Inline alias field | 0/64 | 64/64 | Using the canonical record ID alone recovered support |
| Separate alias register | 0/64 | 64/64 | The owner page remains usable through its canonical ID |
| Inline prose before owner field | 0/64 | 0/64 | Moving that same prose after the owner field recovered 64/64 with the canonical question |

All **960** competing, missing, and retired-source controls withheld a single
owner. Of 320 competing-owner cases, 64 reported an explicit conflict. The
other 256 withheld without establishing the conflict. The diagnostic probes
measure the ability to read the owner through the canonical route. They do
not count as answers to the original alias questions.

Three candidate rule classes follow from these observations:

1. **Owner-question grammar.** The canonical ID and evidence already work with
   the literal field request. A bounded alternate request should preserve the
   same field selector and competing-owner behavior.
2. **Explicit record-alias binding.** In the inline field and separate-register
   cases, the canonical ID reaches the owner without a source change. A proposed
   alias route needs a unique, eligible binding and evidence for the owner.
   Independently test duplicate aliases, conflicting links, and retired links.
3. **Field placement in mixed records.** The canonical selector alone could not
   recover the inline-prose cases. Moving the prose isolated a header-boundary
   effect. The current parser ends the declared header at the first non-field
   line. Any broader rule needs independently verified boundaries so quoted
   examples and later commentary cannot acquire field authority.
   [Declared fields implementation](../../mplpb_answers/relation_graph.py)

These are repeated results across changed identifiers and names in five
authored structures. A new seed within those structures measures repeatability.
New structures and independent real-source review measure transfer. No
runtime rule was changed in this study.
[Grouped counts and per-seed receipts](study-seeds-1000-1063.json)
