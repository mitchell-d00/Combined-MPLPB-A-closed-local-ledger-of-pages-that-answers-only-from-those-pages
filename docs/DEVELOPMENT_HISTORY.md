# Combined MPLPB development history index

Last reviewed: 2026-11-26.

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

## Public MPLPB, preserved implementations, Combined MPLPB and BOA

Mitchell uses public publications and repositories as a distributed working
record: artifacts carry claims, scope, instructions and revisions; cross-links
provide navigation; search locates them; a search-capable session can attempt
reconstruction for inspection and continuation. This is the proposed mechanism,
not a guarantee of correct reconstruction or source truth.

The [Google protocol, MPLPB-TEST-001 v1.3](https://www.academia.edu/170061082/MPLPB_as_a_Public_Experiment_A_Replication_Procedure_Anyone_Can_Run_With_Google)
has a July11,2026 header and records five author-run observations. Identity
recovery was supported; stronger mechanics and longitudinal checks remained open.
The [multi-apparatus protocol, MPLPB-TEST-002 v2.0](https://www.academia.edu/170721448/MPLPB_as_a_Public_Experiment_Multi_Apparatus_Edition_A_Replication_Protocol_for_Any_Search_Capable_AI)
has a July26,2026 header and records a Grok/search run reporting mechanics
reconstruction, with longitudinal synthesis less complete. These are the papers'
recorded observations, not runs performed or independently adjudicated here.
The [Cognitive Strategy paper](https://github.com/mitchell-d00/Multi-Platform-Linked-Public-Building-as-a-Cognitive-Strategy-/blob/9dcc77d0729e07eb5441db305d8ead305ec05b9f/CORPUS/05-Public-Building/Multi-Platform-Linked-Public-Building.md)
describes publication, linking and retrieval as semantic stabilization and also
states failure modes. Proposed mechanisms and recorded observations stay separate.

BOA continues the public-entry approach through a role description and repository
pointer; see [TeamBuilding](TEAMBUILDING.md). Mitchell reports screenshots showing
search recovering its role menu and commands. Those are author-supplied
observations, separate from verified role execution or independent replication.
No search experiment, participant trial or historical-accuracy evaluation was run
for this documentation update.

The recurring responsibility is a recoverable record of claims, decisions,
corrections and evidence. This compact map describes the path from personal
capture to selected local enforcement; it does not extend local guarantees to
the whole web.

| Stage and purpose | Actual artifact | Recovery method | Measured limits |
|---|---|---|---|
| iNotes: capture working material | Mitchell's author-described note-taking workflow; no private note export supplied here | Mitchell selects records for the manual relay | Personal capture was not inspected or independently tested in this update |
| Repositories: preserve revisions | [Five preserved implementations and upstream repositories](../parts/README.md), [paper provenance](../papers/manifest.json), Git history | Recover an exact revision, original bytes and applicable contract | Preservation/adoption receipts have their own dates; old features are not all enabled in Combined |
| Hubs: connect projects | [Component map](COMPONENT_MAP.md), [history index](DEVELOPMENT_HISTORY.md), three documentation entry areas | Follow links to implementation, current status and evidence | Navigation structure exists; newcomer success is not established by links alone |
| Platforms: expose records | The two public experiment protocols and earlier research repository linked above | Open the named publication/revision and its source addresses | Their reported observations are scoped to their original apparatus and trials |
| Linked platforms: connect the public record | Publication/repository cross-links and the [TeamBuilding public entry](TEAMBUILDING.md) | Traverse named source links; verify the checked pin before continuation | Link persistence and successful role execution are separate; automatic chat synchronization is not claimed |
| Web: discovery and reconstruction | TEST-001/002 cold-search procedures and recorded observations | Search, recover instructions, complete a bounded task and inspect its sources separately | Author-run/reported apparatus observations are not current independent replication or proof of source truth |

The [versioned engineering criterion](TEAMBUILDING.md#broader-coverage-with-preserved-constraints)
states how to make the next small responsibility computable and test it.

Keep these records distinct: protocol/manuscript header dates; public posting
dates where independently recorded; upstream code revisions; Combined import
dates; execution dates; and this November26,2026 review. For example, Git records
the preserved part/tool import at `f70e5e78fb0af8c0adffac3533512f7497eaba35`
(October11,2026); the [parts receipt](../parts/README.md#as-run) reports an
October7 execution. Neither date silently replaces the other or a paper date.

### Small historical-reuse map

| Old artifact and revision | Current implementation or existing reuse | Remaining contribution and next test | Classification |
|---|---|---|---|
| Public TEST-001 v1.3 / TEST-002 v2.0; earlier [research repository at `9dcc77d`](https://github.com/mitchell-d00/Multi-Platform-Linked-Public-Building-as-a-Cognitive-Strategy-/tree/9dcc77d0729e07eb5441db305d8ead305ec05b9f) | Public entry links and the Al/Betty/Outside continuation guide exist. This does not establish cold-search recovery or successful role execution. | Reuse separate recovery, task-completion and traceability measurements in the single experiment below. | Candidate extension |
| Complete-artifact headers/navigation; [preserved specifications](../docs/Combined_MPLPB.md), [papers and original-byte manifest](../papers/README.md) | Three entry areas already state scope and review dates; [handoff generation](../tools/build_handoff.py) pins instructions and source inventory. These are inspectable current mechanisms, not proof that public reconstruction works. | Keep release/experiment/evaluation and continuation cues linked; test the same task from different entry paths. | Already incorporated, with bounded scope |
| Swarm ablation v2 / MPLPB-TEST-014 v2, preserved at `f70e5e7`: [runner](../parts/swarm/tools/ablation/run_ablation.py), [tests](../parts/swarm/tests/test_ablation.py) | [check_parts.py](../tools/check_parts.py) runs standalone suites and seals copied example sites. The current native reader does not import the Swarm ablation ranker. | Reuse matched arms, fixed inputs, interleaving, navigation-versus-evidence separation and explicit ceiling/confound checks when designing comparisons. Historical scores are not rerun results. | Reusable test/control |
| Earlier scope, precedence and revision contracts: [five parts and upstream links](../parts/README.md), [historical documentation](../PAST_DOCUMENTATION.md) | Current [ownership](../mplpb_combined/reader.py), [ledger](../mplpb_combined/ledger.py), [provenance gate](../mplpb_combined/provenance_gate.py), [assertion conflicts](../mplpb_answers/assertions.py) and [admission pipeline](../mplpb_answers/pipeline.py) enforce their own contracts. Compatibility/adoption is visible in check_parts; direct code descent or universal feature activation is not implied. | Bunyip must preserve full-question policy, current eligibility, exact witnesses, correction scope, conflict and unresolved obligations. Existing frozen preservation suites test these boundaries. | Already incorporated contracts; preserved controls reusable |

One near-term reuse experiment is proposed, **not run**: a small matched
discovery-to-first-citation software walkthrough. Freeze the released engine,
the same Museum-hours plain-text input, questions and existing CLI checks; vary
only the old versus three-area entry documentation across four starting links.
Record correct-instruction reachability/navigation hops, command completion and
exact citation inspection separately. Expected benefit: each new entry route
reaches the working task within two links, without changing its answer or refusal.
Falsifier: any route misses that bound, needs more navigation than its matched
old route, changes the checked quote, or changes the missing-closing-time refusal.
Reuse the [existing quick-start task and transcript](../evaluation/newcomer-navigation/README.md)
and current link/command checks, rather than adding another reader harness.
This software walkthrough would not establish human or cold-search success.
The twelve-participant trial remains NOT_RUN pending Mitchell's observations.

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
