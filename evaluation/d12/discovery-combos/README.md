# MPLPB mode flags and historical discovery paths

Last reviewed: 2026-11-23.

The experiment was first run at `3a7b09e` and reproduced for publication against `4c7cbe9`. All path decisions were produced before the scorer opened the historical reference drafts. The reference drafts are development anchors and have no independent semantic adjudication. A discovery match requires the drafted quote in a passage from the named record, with whitespace and case normalized.

## How mode selection developed

| Date | Repository evidence | Purpose |
|---|---|---|
| July 9, 2026 manuscript date, committed October 7 | Navigation mode controller and the Five-Module Combinator | The retained design describes explicit switching, context-based suggestions, priority overrides, and tests for benefits and failures that only appear when modules are combined. The architecture document is a design record. |
| October 9 and 19 | `8745682`, `4ee6219`, `2efcb9f` | Conversation/focus modes set the source environment. Reason Mode is a browser inspection control. |
| October 31 | `faca0a5` | `ask --answer-mode strict\|assisted` declares the answer policy. Strict records support. Assisted interpretation uses a separate authority label. |
| November 17 | `8364639`, `cc49d6e`, `49b2360` | Explicit documentary reconstruction and constrained narration were separated from Ask. The preprocessing sorter acquired a documented `--mode not-compared\|compare` contract. Compare adds candidate edges while keeping the same observations and source spans. |
| November 19–22 | `bc6f25c`, `dbf85b2`, `f6b1d17` | Article assembly retained per-section decisions. `investigate --adaptive-search` changed scheduling inside link hops. The historical graph study reported discovery independently from proof. |
| November 23 | `85f0116` | `advanced --follow-up auto\|none\|lookup\|investigate\|assisted` coordinates one strict result and at most one inspection. Training uses `advanced-train --candidate` or `--objective`. |

The delivery `--profile` applies independently of the follow-up choice. The native Advanced command has no synonym-graph follow-up flag. Graph discovery below ran as a separate probe. [Development history index](../../../docs/DEVELOPMENT_HISTORY.md)

## Matched discovery experiment

All rows at 12 passages used the same 8,000-character constraint. The 16-passage rows used the same 11,000-character constraint. The 24-passage comparison used 16,000 characters. The combined packs deduplicated exact passage identities. The expert lane ranked passages from records visited in the archived investigation.

| Method | All drafted anchors visible, out of 21 scorable cases | Total visible anchors / 32 |
|---|---:|---:|
| Ordinary, 12 | 4 | 6 |
| Synonym-graph guided, 12 | 5 | 8 |
| Investigation-visited records, 12 | 1 | 1 |
| Ordinary and graph interleaved, 12 | 5 | 7 |
| Ordinary, graph, and expert interleaved, 12 | 3 | 4 |
| Ordinary, 16 | 4 | 6 |
| Ordinary first, then graph suggestions, 16 | 5 | 7 |
| Ordinary first, then expert suggestions, 16 | 4 | 6 |
| Ordinary, 24 | 5 | 9 |
| Three-way interleaving, 24 | 5 | 8 |

The graph added a passage in H09 and H13 at 12 slots without losing visible anchors on any case. Three-way interleaving displaced both H01 anchors at 12 slots. At the extended budget, keeping the ordinary results and appending graph candidates recovered H09 without a loss. On the 40 historical follow-ups, ordinary retrieval found all drafted anchors in 29 cases. Graph-guided and ordinary-plus-graph each found all anchors in 30. Passing the same combined locations to the native strict checker changed zero answer statuses and zero claim lists on the historical 22.

## Cases to follow

- **H09, Apollo 13.** Graph-guided retrieval showed both the May change sheet and September title-page anchors. Strict Ask still abstained. Use documentary inspection to distinguish the two document dates, then seek a separately identified mission-time passage for the elapsed-time part.
- **H13, Fort Sumter.** Graph-guided retrieval surfaced one of two drafted anchors. Inspect the full underlying telegram and the page's archival framing as distinct layers before making a proof claim.
- **H01, Lyell's letter.** Ordinary retrieval already supplied both drafted anchors. Keep those passages when showing additional candidates. The remaining task is proving the relation among the letter date, early copies, and publication.

I also ran the existing `investigate --adaptive-search --source ID` and `reconstruct` commands on H01, H09, and H13. The three graph-seeded investigations produced evidence reports with zero verified observations or traversed links. The three reconstruction reports retained the corresponding strict abstentions. The follow-up CLI flags therefore supply inspection routes on these cases, with no added proof. The sorter, Advanced, and investigation regression suites passed 101 tests. [Flag replay](flag_smoke.py) · [Recorded flag outcomes](flag-results.json)

The case packet groups all 22 by the suggested next step. It keeps record candidates, visited records, strict status, and matched references visible separately. A useful order from this run is to keep the strict outcome and ordinary passages, then show graph suggestions in a separately labeled shortlist. Use investigation when the question has an eligible declared link to follow. Keep semantic interpretation and historical adjudication separate from discovery.

## Reproduce

From the repository root, use a new output directory.

```sh
out=$(mktemp -d)
suite=evaluation/d12/discovery-combos
python -m tools.article_study --output "$out/article"
PYTHONPATH=. python "$suite/replay.py" --article-replay "$out/article" \
  --mode-report evaluation/d12/mode-replay/historical-modes.json \
  --output "$out/historical-22.json" --paths-output "$out/flag-sorted-cases.json"
PYTHONPATH=. python "$suite/followups.py" "$out/followups.json"
PYTHONPATH=. python "$suite/flag_smoke.py" --replay "$out/historical-22.json" \
  --output "$out/flag-results.json"
```

[Historical 22 results](historical-22.json) · [40 follow-ups](followups.json) · [Flag-sorted case packet](flag-sorted-cases.json)
