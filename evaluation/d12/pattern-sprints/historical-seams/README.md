# Historical 22 evidence seams

Last reviewed: 2026-11-23.

This replay traces the same frozen historical questions through finite question planning, ordinary passage discovery, graph record discovery, an explicit section edge, native verification, and final citation display. The graph edge identifies an eligible record and its uniquely numbered summary. Its output carries no support claim. The verifier reconstructs source-attributed statements from eligible bytes and checks their source offsets and scope.

Two different blocks produced the initial abstentions. The lease question already had its drafted anchor visible in both passage probes. Its question form did not establish a proof obligation. The summary question had a graph record hint, but the record-only ranker failed to surface the relevant summary anchor. The new report-to-summary edge uses the report label and numbered heading to find the window. The window can support local citations, with corrections outside it left unresolved.

## Frozen results

| Historical 22 outcome | Before | After |
| --- | ---: | ---: |
| Full supported answer | 3 | 4 |
| Cited partial answer | 2 | 3 |
| Conflict | 3 | 3 |
| Abstention | 14 | 12 |

Only two native answers changed. The Yellowstone lease answer now cites the discretionary grant clause and its ten-year ceiling. The Apollo 13 answer now cites the report’s stated cause of the abort and its description of lunar-module support. The graph record probe alone surfaced zero complete drafted anchors for Apollo 13. The section edge surfaced one. The two actual answer citations cover 337 of the 530 drafted anchor characters. All 19 native citations matched their sealed source projections, and the 40 follow-ups had identical native contracts apart from code fingerprints. [Per-case seam trace](replay.json) · [Before/after comparison](comparison.json) · [Prepatch failures](before-unittest.log)

## Corpus-scoped prompt

> Use only the supplied corpus. State the strongest conclusion that the currently eligible passages support. For each claim, quote the exact passage and give its document and location. Distinguish a recorded event from an instruction, report, plan, condition, or later correction. Identify what a correction changes and what it leaves open. Preserve conflicting accounts. Give a cited partial answer when only part of the question is established, and state what evidence would settle the rest. Attribute every conclusion to the corpus. Leave external historical truth unassessed.

## Reproduce

```sh
root=$(mktemp -d)
python -m tools.article_study --output "$root/original-22"
python -m test_tools.historical_seams --original-replay "$root/original-22" --output "$root/seams.json"
python -m unittest tests.test_historical_seams tests.test_report_section_probe -v
```

The replay uses the frozen developer reference anchors for passage and citation coverage measurements. Partial or full support codes report behavior under the strict reader's rules. Independent historical verification and the proposed human pilot remain separate.
