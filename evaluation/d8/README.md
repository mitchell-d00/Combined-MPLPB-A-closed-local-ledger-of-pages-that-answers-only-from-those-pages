# D8 ownership handoffs

Last reviewed: 2026-11-23.

D8 tests the handoff from page ownership to strict source proof and answer
assembly. Run `python -m unittest tests.test_d8_owner_boundaries -v` from the
repository root.

| Boundary | Expected behavior |
|---|---|
| Zero owners | Withhold when there is no proof. |
| One complete owner | Return its bounded answer with an exact original citation. |
| Two competing owners | Preserve each checked source statement with its own source ID and citation. Withhold the single answer. |
| Two agreeing owners | Preserve both accounts separately. Agreement does not select a unique owner. |
| Evidence budget | Keep a competing set together. If the set cannot fit, preserve the conflict status and show the budget limit. |
| Lexical ambiguity | Expose eligible candidate IDs for inspection. Their lexical ownership supplies no claim. |
| Explicit comparison | `Compare shelf code for record ARCH-A and record ARCH-B` checks each body field independently. Both must verify for a complete answer. |
| Incomplete comparison | Keep a verified side when the other is missing, restricted or merely proposed. Keep a conflicting side's witnesses together when the shared budget permits it. |

The [initial failing regression](baseline.log) was run against `a2abb27`. Two
of eight controls passed. Five failed assertions and the lexical inspection
case found a missing result field. The changed implementation distinguishes
competing statements from compatible statements in source verification
metadata. The legacy lookup result still models the question's page owners.
The CLI displays competing citations and keeps its legacy answer text empty
for an ambiguous result. A named comparison reports two separately sourced values. It does not infer
that the pages refer to the same event.

The historical pilot also exposed a question interpretation error. A request
for the wording that appeared in a final publication was sent to the
draft-comparison rule. A separate control verifies that comparing two proposed
passages cannot answer a request for published wording. [Comparison tests](../../tests/test_comparison_completion.py)

[Original frozen historical pilot](../d12/solo-post-freeze/README.md)

## Historical regression replay

The candidate `7c478caa70b89da46deb3664f8f9c0d7fd7e0365` ran on the
same 24 questions and originals from the D12 solo pilot. All three
discovery outputs matched the original per-case outputs exactly. The
request for wording in the final communiqué moved from an irrelevant
local wording comparison to a clean abstention. All five missing-evidence
questions now withhold without irrelevant text. Strict Ask still completed
zero of 19 answerable questions. The remaining gap is outside this ownership
repair. [Candidate scores](d12-score.json) · [Exact changed case](d12-delta.json)

The separate historical 22 replay retained each case's strict status,
diagnostic, and citation count. The totals remained four full answers,
three cited partials, three conflicts, and twelve abstentions. Advanced
preserved the Strict Ask contract on each case. [Historical 22 replay](historical-modes.json)

Reproduce from a clean checkout of the candidate revision. Use new output
paths and the unchanged D12 input packet.

```sh
study=evaluation/d12/solo-post-freeze
out=$(mktemp -d)
PYTHONPATH=. python "$study/run.py" "$study/inputs" "$out/study" \
  --commit "$(git rev-parse HEAD)"
python "$study/score.py" "$study" --raw "$out/study/run.json"
python -m test_tools.historical_mode_replay --include-advanced \
  --output "$out/historical-modes.json"
```

## Native regression checks

The focused source ZIP of the final candidate passed 87 checks. The full
native run on frozen candidate `970abb919c4490d998d30ea117e610c2976e2f57`
reported `OK (skipped=2)` across 1,680 tests. The command wrapper returned
exit 1 despite the successful test footer. The first attempt exposed a
legacy CLI text regression and loopback restrictions. The loopback retry
caught a CLI source edit during a code-pin test. That test passed on the
frozen candidate. [Retained attempts](native-suite-retries.log)
