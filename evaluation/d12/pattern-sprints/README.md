# D12 evidence-pattern fix sprints

Last reviewed: 2026-11-23.

The nine coordinator questions initially returned nine abstentions even though a separate passage probe exposed all supplied excerpts. The questions reached the strict reader without a recognized question form or documentary plan. This experiment adds four finite readers for small, complete packets. Each one checks the body of every eligible record in scope and emits exact source excerpts. The ordinary pipeline rechecks source state and enforces the combined citation budget.

| Sprint | Added reading rule | Frozen questions that changed | Matched controls |
| --- | --- | --- | ---: |
| 1. Recorded stage and later outcome | Preserve stated authority and limits. Cite a recorded petition or draft separately from any open outcome. | Q2 full. Q7 and F1 partial. | 8 |
| 2. Labeled item row | Read one unambiguous pipe-delimited row with unique explicit field labels. | Q5 full. | 6 |
| 3. Condition and exception | Preserve the limiting clause with its permission or schedule. Require a matching request type and stated duration for the two-sentence schedule form. | Q1, Q4 and Q8 full. | 7 |
| 4. Scope of a causal statement | Distinguish dated events from a supplied cause. Preserve an explicit causal statement when the bounded text identifies the relation. | Q3 and Q6 partial. | 7 |

A full result means the new reader supports the requested answer from this packet. A partial result provides a cited statement and identifies the requested relation or outcome that remains open. For example, the draft date and margin question do not establish a finalized deed.

## Historical graph and proof sprints

Two additional fixes on the unchanged historical 22 recovered one full answer and one cited partial. The [historical seam report](historical-seams/README.md) distinguishes graph passage visibility from native proof and includes a corpus-scoped reviewer prompt.

## Retained replay

- [Original questions, excerpts and source locators](original-questions.json) · [Before any changes](before.json)
- [After the recorded-stage rule](after-stage-and-outcome.json) · [After the item-row rule](after-item-row.json) · [After the condition rule](after-conditions.json) · [After the causal rule](after-causal-boundary.json)
- [Matched control fixtures and expectations](expanded.json) · [Prepatch test failures](before-unittest.log)

The original nine moved from zero cited answers to five full and four partial answers. In the initial baseline, 13 matched cases failed their expected outcomes. All 28 matched cases pass after the sprints. The additional state-change and quoted-context checks confirm that the route withholds stale or quoted body evidence.

```sh
python -m unittest tests.test_d12_pattern_sprints -v
python -m test_tools.d12_pattern_sprints --output /tmp/d12-pattern-sprints-replay.json
```

## Public archival prose check

After the four sprints, a separate exploratory check froze three U.S. National Archives transcript passages with their download hashes. The passage probe found all three excerpts. The baseline and candidate both abstained on all three. The new planner recognized the question forms, and the source checks withheld answers on the archival clause structures. These examples were selected after implementation and remain exploratory.

```sh
python -m test_tools.d12_pattern_sprints \
  --input evaluation/d12/pattern-sprints/archival-exploration.json \
  --output /tmp/d12-archival-exploration.json
```

[Source transcripts, URLs and hashes](archival-exploration.json) · [Baseline](archival-before.json) · [Candidate](archival-after.json)

The supplied document locators are reported as provided. The nine excerpts and authored controls test rule development. The original PDFs, broader historical retrieval, and independently adjudicated historical accuracy remain separate measurements. The [human pilot](../HUMAN_PILOT.md) retains its own pending status.
