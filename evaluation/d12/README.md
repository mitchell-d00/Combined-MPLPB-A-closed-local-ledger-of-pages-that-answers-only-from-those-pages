# D12 historical truth and relations

Last reviewed: 2026-11-23.

D12 starts with a complete D6 evidence path and varies one input, selector, source state, required link, or budget. It records each control and variant with the expected and observed outcome, the full citation trail, and the first unresolved operation in execution order. A verified negative comparison and a correctly reversed year difference are successful outcomes. The historical arm replays answers and traces observations on frozen source material for review.

## Twelve generated classes

| Stage | Paired controls |
| --- | --- |
| Record selection | Wrong record identity |
| Eligibility | Competing owner, withdrawn source |
| Field read | Missing field |
| Comparison | Explicit contrast, nearby year, lost precision |
| Relation | Wrong operand role, reversed year operands |
| Branch | Unknown condition |
| Composition | Missing required link, insufficient citation budget |

These controls vary dates, year gaps, and literal source values across seeds. They exercise D6 on declared fields and distinguish a recorded difference from missing evidence. For a prose case, a missing passage in both probes is a place to inspect discovery. Visible drafted anchors with incomplete native support are a place to inspect proof, including other evidence the reference may omit. A native conflict gets its own review. These observations do not identify a cause or confer historical truth.

## Reproduce

```sh
root=$(mktemp -d)
python -m tools.article_study --output "$root/original-22"
python -m test_tools.historical_22_graph --original-replay "$root/original-22" \
  --output "$root/original-22-graph.json"
python -m test_tools.historical_patterns --output "$root/followups"
python -m test_tools.historical_graph_study --historical-replay "$root/followups" \
  --output "$root/graph"
python -m test_tools.d12 --seed 12 --count 12 \
  --original-replay "$root/original-22" --original-graph "$root/original-22-graph.json" \
  --expanded-graph "$root/graph/report.json" --output "$root/d12.json"
```

Run only the synthetic pairs by omitting the three historical inputs. To include a [sealed Dice Bag operator packet](../dice-bag/README.md), add `--dice-bag-inputs /path/to/operator`. This repeats the D6 corpus check on declared fields and missing-field controls. It preserves the separate Dice Bag scores and does not require the custodian key.

## User and AI training sprints

The [rule-training coordinator](coordinator/README.md) freezes cases, groups native failures, runs one user-authored D6 rule, and compares it with the baseline. It also provides a scoped automatic repair and repository benchmark triage.

## Use with the other dice tests

D4 supplies examples where identity or co-reference can break a relation. D20 groups repeated owner and alias misses into candidates for a shared rule. D% samples broader prose and refusal behavior. External D100 exercises sorter and workspace behavior. Dice Bag supplies fresh collections for testing transfer. D12 gives a way to isolate one changed obligation on a matched pair. Keep the original fixture, the failing result, the proposed rule and its counterexamples, and the rerun. Compare both missed answers and false support before changing a default rule. [Test Index](../../docs/TEST_INDEX.md)

## Evidence-pattern fix sprints

Four bounded rules now cover staged outcomes, labeled item rows, conditions, and causal boundaries on the nine supplied coordinator excerpts. [Before/after replays and controls](pattern-sprints/README.md)

## Planned live experiment

The proposed human pilot assigns eight frozen historical cases to two independent reviewers and a third adjudicator. A separate fresh Dice Bag draw is planned for testing transfer after review. Both runs are pending. [Pilot protocol](HUMAN_PILOT.md) · [Reviewer worksheet](HUMAN_PILOT_WORKSHEET.md)

## Review a historical case

1. Read the question and named source before looking at the native answer or reference draft. Write the minimum claims the question requires.
2. For each claim, record the exact supporting or contradicting passage. Distinguish direct source wording, reported speech, conditions, dates, inferred links, and missing evidence.
3. Check whether each citation supports the claim as phrased. For relations, verify both entities, direction, date roles, and qualifications. Record whether anything changes if a competing source is included.
4. Score the full answer, partial answer, conflict, or refusal against the source packet. Record external historical corroboration separately, with its source and any disagreement. Leave the truth field blank where no independent assessment was made.

The original 22 had 3 native full answers, 2 partials, 3 conflicts, and 14 abstentions. All 16 native citations matched their sealed hashes, paths, offsets and excerpts. The ten original-record projections declared no fields recognized by D6. The historical lane therefore measures source readback, retrieval and native proof behavior on prose. Independent historical judgment remains open. [Run summary](study-summary.json) · [Per-case historical traces](history-traces.json)
