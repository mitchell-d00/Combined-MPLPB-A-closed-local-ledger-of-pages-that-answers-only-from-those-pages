# Combined MPLPB development history index

Last reviewed: 2026-11-23.

The Advanced MPLPB implementation and README were reviewed at `3a7b09e` and merged to main at `4c7cbe9` after the PR checks passed. Older entries point to the revisions that introduced or measured them. Begin with the type of work you need to continue, then open the pinned result and its reproduction procedure.

## Find the record you need

| Question | Start here |
|---|---|
| What should the next person pick up? | [Current handoff](../HANDOFF.md) and [structured update](../handoff/update.json) |
| Which component owns this behavior? | [Package guide](../docs/PACKAGE_GUIDE.md) and [repository contents](../CONTENTS) |
| When did a choice change, and why? | [Fix log](../FIXLOG.md), [historical documentation register](../PAST_DOCUMENTATION.md), and the Git revisions below |
| Which experiment supplies the number? | [Results and test index](../docs/RESULTS_AND_TESTS.md) and [machine-readable inventory](../docs/results.json) |
| How do I run it again? | [Test tools](../docs/TEST_TOOLS.md), [Test Index](../docs/TEST_INDEX.md), and the experiment's input pins |
| What has the current public release verified? | [Release evidence procedure](../docs/RELEASE_EVIDENCE.md), [ZIP-first guide](../docs/ZIP_FIRST_RELEASE_TESTING.md), and the merged PR's exact-head and postdeployment checks |

## Follow the development phases

| Phase | Revisions to inspect | Code, records, and entry points |
|---|---|---|
| **Design and earlier standalone parts** | Manuscript dated July 2026, imported at `e99a344` | The Navigator and Five-Module Combinator describe modes, interface contracts, and testing combinations. The earlier parts preserve independently runnable designs. [Manuscript](../docs/sources/Continuity_Without_Memory_manuscript.md#the-five-module-combinator) · [Combined specification](../docs/Combined_MPLPB.md) · [Earlier parts](../parts/README.md) |
| **Closed ledger and conservative source answers** | `07176b4` ownership evaluation, `f27966c` support checks, `d39d893` provenance-gated retrieval | Follow sealed status and revision handling through the ledger and provenance gate, then the answer pipeline and verifier. [Ledger](../mplpb_combined/ledger.py) · [Provenance gate](../mplpb_combined/provenance_gate.py) · [Pipeline](../mplpb_answers/pipeline.py) |
| **Local conversation, apps, and optional readers** | `8745682` chat/focus, `de18255` Reason Mode, `6840971` general reader, `9f03116` local MCP, `0c81992` browser helper | Reproduce local source queries and conversational behavior independently of model transport. [General answer paths](../docs/GENERAL_ANSWER_PIPELINE.md) · [MCP](../docs/MCP_AGENT.md) · [Browser helper](../docs/FREE_PUBLIC_HELPER.md) |
| **Reference and prose coverage studies** | `c0eb212` reference reproduction, `3a79603` D%, `9e2c2b8` question wording, `61cc7c0` field aliases, `27f6fe9` D4 | Follow each reported score to its own pinned fixtures and match criteria. [Reference reproduction](../evaluation/reference-corpus-reproduction) · [D% known weaknesses](../docs/DPERCENT_KNOWN_WEAKNESSES.md) · [D4](../docs/D4_EVENT_IDENTITY_COREFERENCE.md) |
| **Ingestion, candidate review, and bounded investigation** | `49b2360` dual-mode sorter, `bbf6690` candidate workspace, `bc6f25c` article assembly, `fef46d1` Adaptive Search | Compare sorter observations, exact source spans, and proposed relations. Inspect source layers or traverse declared links without promoting a candidate. [Sorter](../docs/PREPROCESSING_SORTER.md) · [Candidate workspace](../mplpb_work/candidate_workspace.py) · [Expert investigation](../docs/HISTORICAL_EXPERT_PATH.md) · [Article assembly](../docs/DOCUMENTARY_ARTICLES.md) |
| **WorkStore, approvals, and auditable effects** | `cc21ce3` coordinator source support, `ddde79f` dispatch study, `fa13b0e` governance experiment | Scope a seat, pin an action, and read back the actual effect. Preserve indeterminate outcomes and host reconciliation. [WorkStore API](../docs/SPECIALIST_CONTINUITY_API.md) · [Dispatch controls](../evaluation/comparative-tests/dispatch-enforcement/README.md) · [Governance gate](../evaluation/comparative-tests/governance-gate/README.md) |
| **Training and transfer benchmarks** | `692f72e` Primary Book, `f9e71b9` synonym graph, `f6b1d17` historical discovery, `273e5ba` D6, `323492d` rule-training coordinator | Freeze data and outcome keys. Diagnose classes of misses. Test a class rule against the same baselines, controls and holdouts. [D6](../evaluation/d6/README.md) · [D12](../evaluation/d12/README.md) · [D20](../evaluation/d20/README.md) · [Dice Bag](../evaluation/dice-bag/README.md) · [Coordinator](../evaluation/d12/coordinator/README.md) · [Primary Book](../docs/TEST_TOOLS.md#primary-book-test) |
| **Advanced MPLPB** | `85f0116` routed Ask and training, `d60c6cd` archived replay, `3a7b09e` README | Start with Strict Ask. Use an explicit follow-up or let the coordinator choose a bounded inspection. Run the training command as the evaluation-key custodian. [Advanced guide](../docs/ADVANCED_MPLPB.md) · [Historical mode comparison](../evaluation/d12/mode-replay/README.md) · [PR #81](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/81) |

## Navigation by task

- **A strict miss with no source visible.** Start with passage ranking and graph/candidate discovery. Record the selected path and exact eligible spans. Use the reference key for scoring after the route is fixed. [Passage preparation](../mplpb_answers/passages.py) · [Historical graph study](../test_tools/historical_22_graph.py)
- **A strict miss with the right source visible.** Trace the missing proof obligation in the documentary checker. Keep nearby dates, roles, and competing text visible. [Documentary engine](../mplpb_answers/documentary.py) · [D12 historical seam replay](../evaluation/d12/pattern-sprints/historical-seams/README.md)
- **A conflict, old revision, or unavailable page.** Recheck current eligibility and retain the competing records. [Reader and source eligibility](../mplpb_combined/reader.py) · [Delivery profiles](../mplpb_combined/delivery.py)
- **A useful candidate repair.** Replay the original cases and separate holdouts, retain both outputs, and record whether the verdict was selected or blocked. A training pass leaves promotion as a separate change. [Training code](../mplpb_work/training.py)
- **A release or continuation handoff.** Record the source revision, corpus or fixture hashes, mode and profile, budget, native output, guard results, and the predicted observation for the next experiment.

## Where today's mode work fits

The historical 22 has four full answers, three cited partials, three conflicts, and twelve abstentions. Advanced MPLPB preserved those 22 strict contracts. The follow-up experiment tested whether its paths add useful discovery. Ordinary passage retrieval found all drafted anchors in 4 of 21 scorable cases. Graph guidance raised that to 5, while interleaving ordinary, graph, and expert passages in the same budget lowered it to 3. At an equal larger budget, appending graph suggestions after preserving the ordinary shortlist recovered one case without loss. Strict claims and answer statuses stayed identical when fed the location hints. [Mode history, combined replay, and case packets](../evaluation/d12/discovery-combos/README.md)

To verify a historical revision or dig past this map, use `git show REVISION`, `git log --first-parent --oneline main`, and `git log -G 'FLAG_OR_FUNCTION' -- PATH`. Start a continuation note with the exact revision and a link to the new evidence. Preserve the original result and disclosure of its limitations.
