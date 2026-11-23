# Historical 22 by mode

Last reviewed: 2026-11-23.

The replay uses the same sealed historical 22 questions, imported records, and
internal delivery profile for Strict Ask, Assisted Ask, candidate lookup, and
expert investigation. The native article runner supplies the strict and
article comparison; the graph runner separately measures discovery against
drafted source anchors. No reference answers are passed to the mode runner.

## Reproduce

```sh
root=$(mktemp -d)
python -m test_tools.historical_mode_replay --output "$root/modes.json"
python -m tools.article_study --output "$root/articles"
python -m test_tools.historical_22_graph --original-replay "$root/articles" --output "$root/graph.json"
python -m test_tools.historical_patterns --output "$root/followups"
python -m tools.evaluate_public_evidence --require-capabilities --output "$root/public.json"
```

The first command defaults to Assisted Ask with no configured reader. To
exercise real inference, add `--reader-model NAME --reader-digest SHA256`
for an installed Ollama model on the local loopback service. Use a new output
path and have reviewers assess every assisted claim and its citations.
The retained run used the unconfigured path. Live model accuracy and
independent historical accuracy remain unmeasured.

## Other benchmark replays

| Benchmark | Path and observed result |
|---|---|
| Historical follow-ups | Strict citation checks matched all drafted anchors on 4/10 quote, 1/10 direct, and 1/10 paraphrase questions. All 10 boundary questions withheld full support. |
| Public evidence 52 | All 52 capability and evidence controls passed. Zero false supported bridges. |
| D20 seed 20 | Strict proved 2/5 positive cases and withheld all 15 controls. Three positive alias cases remained unresolved. |
| Primary Book Test | Strict located all three pinned excerpts and withheld all three altered quotes. |
| Dice Bag, frozen 72 | Strict gave 12/12 exact direct-field answers. Synonym lookup found the selectors for 12/12 natural-wording cases where strict initially withheld. Strict proved all 12 after confirmation. The 12 unknown-wording cases stayed unresolved. |
| Assisted protocol and governance controls | 56 Python checks passed across scripted model reading, the real loopback adapter against a fixture server, historical investigation, and the local report gate. The gate continued to use strict evidence. |

Keep Dice Bag lookup scores separate from proof: the scorer confirms selectors
after reveal. Primary Book measures quotation fidelity. The public evidence
suite and D20 use authored controls. A pass on one benchmark describes that
path and fixture. [Historical follow-ups](../../historical-patterns/README.md) · [Public evidence](../../../docs/PUBLIC_EVIDENCE_TESTS.md) · [D20](../../d20/README.md) · [Primary Book Test](../../../docs/TEST_TOOLS.md#primary-book-test) · [Dice Bag](../../dice-bag/README.md)

For the frozen D20 seed, run `python -m test_tools.d20 run` on
`evaluation/d20/fixtures.json` and score the output with
`evaluation/d20/answer-key.json`. Replay Primary Book or Dice Bag with the
recorded input packet and a separately held key. The book packet can be
recreated from its recorded seed and pinned originals. A fresh Dice Bag draw
can change when the USGS catalog changes. [Book packet pins](../coordinator/primary-book-pins.json) · [Dice Bag packet receipt](../../dice-bag/first-live-receipt.json)
