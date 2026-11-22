# D12 live experiment and proposed human pilot

Last reviewed: 2026-11-22.

**Status** · Proposed and pending. The run date, reviewers, and results are open.

The pilot tests whether D12's trace points to the stage where Combined MPLPB lost an answer or made an unsupported inference. It uses eight of the frozen historical 22. A separate live Dice Bag draw is planned after reviewers identify a repeatable issue and a candidate repair is ready. The pilot is a diagnostic sample selected by prior trace, so its counts describe these eight cases.

## Prepare the historical run

- Assign two independent readers and a third reviewer to adjudicate disagreements. Ask the first two to work separately and record their judgments before comparing notes.
- Freeze the exact engine revision, question files, corpus seals, and native output for the run. Use the original replay and graph commands in the [D12 reproduction guide](README.md#reproduce). Keep the automated trace and reference draft in the coordinator packet. If preparing passage probes, capture the actual excerpts and order from the [graph runner’s discovery helper](../../test_tools/historical_graph_study.py). The retained original-22 trace records anchor counts.
- Give each reviewer the original question wording, the complete frozen source collection assigned to that question, and the [reviewer worksheet](HUMAN_PILOT_WORKSHEET.md). Provide the same collections to both reviewers and use neutral case labels in the packets. Keep native answers, trace categories, and drafted references private until the worksheet's second pass. The historical sources are public. Record whether a reviewer has already seen a benchmark answer and keep that case's blinding status in the report.

### Coordinator-only case selection

| Prior D12 signal | Frozen case IDs |
| --- | --- |
| Inspect passage discovery | H08 Apollo 13 summary, U02 Eisenhower's contingency message, U05 Emancipation Proclamation exceptions |
| Inspect proof after discovery | H01 Lyell's reading and publication chronology, H09 Apollo 13 revision dates, U07 Yellowstone leasing discretion and term |
| Inspect conflict | H03 Huxley's letter and publication |
| Native full-support control | H07 Fort Sumter date roles |

The case IDs refer to the frozen [original questions](../unprepared-originals/2026-11-16/questions.json) and the [government follow-up questions](../unprepared-originals/2026-11-16-followup/unfamiliar/questions.json). The pilot uses the same source collections as the native replay. The categories above are hypotheses for review. [Historical trace data](history-traces.json)

## Conduct and report the pilot

1. **Source-only pass.** Each reviewer writes the minimum answer the packet supports and marks the exact passage for each claim. Record attribution, conditions, dates, competing readings, and questions the source leaves open. Lock both worksheets before showing engine output.
2. **Native-output pass.** Show each reviewer the pinned answer and its citations. Compare it against their locked assessment. If proof and discovery remain hard to distinguish, show the ordinary and graph-guided passage probes and record what that additional evidence changes.
3. **Adjudication.** The third reviewer records a judgment from the source packet for disagreements, then reconciles the two ratings with cited reasons. Retain both initial judgments. Keep unresolved cases in the denominator.
4. **Report.** Record counts out of eight for reviewed, agreed before adjudication, unresolved, and each observed failure stage. Separate missed full or partial answers, appropriate refusals and conflicts, and answer claims that lack support in the packet. Include the cited reasoning for each case. Any external historical corroboration gets its own source and finding. Leave it unassessed until someone performs that review.

## Planned live Dice Bag transfer run

1. Use the human review to select one repeated failure mechanism. A candidate to test is the promotion of a reported instruction or conditional message into a completed event. Confirm the pattern across different documents before proposing a shared rule.
2. Build matched D12 cases around the confirmed mechanism and record D6 step traces for the declared-field controls. Freeze independently written historical prose cases as a separate held-out check. Retain a baseline for every case before changing the rule.
3. Draw a fresh Dice Bag collection using the [Dice Bag acquisition guide](../dice-bag/README.md). Freeze the seed, sources, operator packet, and separate custodian key. Run the pinned baseline and candidate against the same packet. Use D12's `--dice-bag-inputs` arm for the declared-field and missing-field checks alongside the separate blind Dice Bag score.
4. Advance the candidate only when it recovers supported answers on the reviewed failure class and preserves citation fidelity, appropriate refusals, and valid conflict stops. Record any new unsupported answer, lost support, or unscored case. The live draw checks transfer on unfamiliar structured records. The held-out prose checks transfer of the historical relation rule.

Retain the frozen inputs, initial reviewer judgments, adjudication, baseline, and candidate results as a dated run. This proposal contains no human pilot or live transfer measurements.
