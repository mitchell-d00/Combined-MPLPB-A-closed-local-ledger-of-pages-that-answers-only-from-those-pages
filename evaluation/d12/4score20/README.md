# 4score20

Last reviewed: 2026-11-24.

**Understand what’s asked → find the relevant words → check what they prove in context.**

4score20 traces those steps on three unchanged questions and source packets
from the D12 solo pilot. It records the native documentary plan, retrieves
passages, then checks the original question in Strict Ask. The initial
native runs finish before the runner parses the reference key. A second
diagnostic run supplies the verified source locations from the key as
hints, keeping the original question and strict proof rules. Separate
exact-quote controls test whether MPLPB can locate the source wording.
[Source packets and original pilot](../solo-post-freeze/README.md)

## Observed breaks

| Case | Understand | Find | Check |
|---|---|---|---|
| Lodge’s half-hour meeting | No documentary plan for a reported duration. | The answer span appeared in the first three passages. | Strict Ask withheld even with the location supplied. An exact-quote request located it in Lodge’s record. |
| May telegram revision | No documentary plan for what changed between the draft and later instructions. | The first three passages contained 0 of 4 anchors. The 12-passage search found all four under the same character limit. | Strict Ask withheld even with all four anchors supplied as location hints. Three of the four anchors passed separate exact-quote requests. |
| Final communiqué | The requested wording is from the final text. The packet contains preliminary discussion. | Search found the passage about an undecided proposal. | Strict Ask withheld. Finding the proposal by exact quote establishes what was being considered and leaves the published wording open. |

The fourth telegram anchor exposed a smaller break. The combined quote
`2037. Your 3095.` appears in the canonical source and in the wider
retrieval results. The literal verifier split it at the first period.
Both fragments passed separately, while the exact combined quote withheld.
This is a citation-boundary issue in addition to the original question's
missing relationship plan.

A quote can establish that a document contains particular words. For the
telegram relation, the proof would also have to check the common reference,
the draft proposal, and the later authorization in their respective
contexts. The sources leave actual implementation of the instructions open.
The location-hint run does not establish how the relationship verifier would
behave if given a valid question plan. This is a diagnostic replay on three
previously seen cases. [Per-case output and source citations](results.json)

## Reproduce

The initial run used the native engine from `0c33369c70ea58593d8e0620fc46554915414022`.
The output records a hash of the native answer-module fingerprints and the
frozen questions. Run from the repository root with a fresh output path.

```sh
out=$(mktemp -d)
python -m test_tools.four_score_twenty --output "$out/4score20.json"
cmp "$out/4score20.json" evaluation/d12/4score20/results.json
```

Use `--case P05-1` to run one case, or repeat the flag to select multiple
cases from the frozen pilot. Run a fresh copy after a repair and compare
the three steps before interpreting any change in answer score.
