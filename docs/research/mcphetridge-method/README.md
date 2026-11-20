# The McPhetridge Method for Evidence-Gated Software Engineering

*Directing AI-assisted work from controlled experiment to live deployment in Combined MPLPB*

**Mitchell D. McPhetridge**

20 November 2026 · Technical case study

## Abstract

I call this the **McPhetridge Method** for evidence-gated software engineering. When I apply it to MPLPB, the method is recursive. The same distinction between a proposed claim and checked source support governs how I accept changes to the software. I start from a failure in the running system, design a comparison that can distinguish its cause, and direct an AI coding agent to implement a repair that preserves the boundary the system already enforces. The same witnesses then go through the repaired program. A release earns its place when the exact candidate passes regression checks and the deployed version passes an observable live check. In Combined MPLPB, this process turned two deficiencies into bounded improvements. The strict reader gained source-backed collection predicates, and documentary investigation gained verified traversal across ingestion batches in three 1,004-page ledgers. The same release preserved unresolved evidence, the foreign-ledger boundary, and a known limit on natural-language questions.

## The method

I started with a practical question. Could the native MPLPB program take a substantial collection, organize it, and answer questions about it? MPLPB is a closed local ledger with distinct operations for classing source material, retrieving candidates, verifying answers, and investigating declared relationships. Each operation has its own output and authority. If a retrieval call returns a page with the word *cook*, that tells me where to look. When the question asks which recipes require no cooking, the answer has to establish the preparation condition from the record. I want the system to keep that distinction when I give it a new ability. [1, 3]

The method puts my judgment at the points where the work can change direction. I choose the question, the evidence that would count, and the conditions the repair has to preserve. Codex implements changes, runs comparisons, and monitors release checks. I use its reports to choose the next experiment or authorize the next step. That division matters most when a result looks promising. A list containing every expected record can still contain hundreds of wrong candidates. An investigation can find a link in a small ledger and lose it in a large one. A successful merge can precede an unsuccessful deployment.

The unit of progress is a capability backed by a repeatable comparison. I record the inputs, the software version, the expected positive, the case that must stay unresolved, and the output the program actually produced. I keep the earlier failure so the repair can be judged against it. If I can change one factor while holding the rest constant, I do. The same logic applies at release time. The archive, merge tree, and deployed version each need a traceable connection to the code that was tested. [1, 2, 4–6]

## Evidence-gated recursive engineering

The recursive part appears when I apply MPLPB’s own governing rule to the work that changes MPLPB. In a ledger, a retrieved passage can bring a claim into view. The verifier still has to check whether the eligible source supports it. In development, a Codex report that a repair works brings a result into view. I still need the original failing case, the candidate revision, the replay, and an observable result from execution.

The work passes through five decisions. I define what counts as a success, a failure, or an unresolved case. Codex implements the bounded repair. The native program runs against the baseline fixtures, source-boundary controls, and regressions. GitHub runs the checks against the exact candidate, records the merge, and exercises the deployed version. The outputs then enter the project record as evidence for the next decision. The paper itself follows that last step. It records the process that produced the release, cites the evidence, and returns to the same repository as documentation.

I describe this as **evidence-gated recursive engineering**. The recursion is in the workflow. The authority to define the requirements remains with me. The tests observe specified behavior, and GitHub Actions supplies a separate execution record for the checked revision and deployment. The people who write the requirements and tests can still miss a case. The separation keeps an agent’s report or a program’s result from serving as the only evidence for its own correctness. [1, 2, 5, 6]

A failed run can improve more than the implementation. The 256-to-257 comparison gave us a new test that future changes have to survive. The no-water result gave us a durable example of the difference between evidence of absence and an absent field. Both now guide the next round of work. That is the sense in which I use *antifragility* here. A failure can strengthen the software, its tests, and its documentation when I preserve the evidence and act on it. [1–3]

## Finding the failure

The original comparison used three separate 1,000-record collections. The first comprised synthetic recipe cards. The second used openly licensed Star Trek episode and cast metadata from TVmaze. The third used factual tabletop RPG cards drawn from the fifth-edition SRD 5.1. Each collection was ingested through the native classing workflow and validated before querying. I used the three domains to see whether a pattern repeated when the subject matter changed. Their source claims stayed within their respective ledgers. [1]

The retrieval results were a good first signal. A cilantro search returned the 50 expected recipes. Voyager returned the 175 expected records. The three-condition query for cilantro, birthday, and no cooking returned 487 eligible pages containing one expected match. Across the separate 1,000-phrase recipe sweep, native retrieval returned the intended card every time. An all-terms diagnostic isolated it in 800 cases. In the other 200, the words in *no cook* also matched the corresponding stovetop card through *cook*. That result identified the distinction the answer rule needed to protect. [1]

The graph test gave me a different kind of evidence. I put four reference cards into two ingestion batches so both expected hops crossed a batch boundary. Those hops worked in the four-record ledgers and stopped when I placed the same cards in 1,004-page copies of each collection. In the paired recipe control, both links worked at 256 records. Adding one unrelated page made discovery incomplete at 257. The link declarations, seeds and hop budget stayed fixed. That comparison isolated a discovery boundary. A second control exposed an extraction error when a continuation of the `Related` field picked up a neighboring `SHA-256` provenance label as a candidate target. [1]

This is where I use the Jeet Kune Do analogy. You isolate the weakness, practice a response under controlled conditions, and test whether it holds when the circumstances change. Recipes, television metadata and game-reference data gave me three kinds of material on which to try the same software rules. Changing the setting helped expose recurring behavior. Holding an input fixed helped locate the specific failure. The useful part of the analogy is the discipline of adapting a technique under pressure from evidence.

## Repairing the rule and preserving its limits

For collection questions, I wanted an answer to depend on the declared fields of the same eligible record. The repaired engine can combine bounded field conditions, including equality, list membership and explicit absence. A declared preparation of `No cook` can satisfy the preparation predicate. `Cook on stovetop` supplies different evidence. A blank or missing water field leaves the record unresolved. Each included result has to carry the source fields that support it, and the program checks the source state again before returning. [2, 3]

For relationships, I wanted the discovery step to see across ingestion batches while staying inside the selected ledger. The repair indexes declared document identities in the current eligible source inventory under explicit discovery limits. The verifier rereads the visited declarations and endpoints. A duplicate eligible identity stays ambiguous, and incomplete discovery withholds the hop. The reader also stops the `Related` span at classing provenance so the record of how a page was built cannot turn into a relationship target. [2, 4]

| Replay | Result in the repaired native program |
|---|---|
| Cilantro, birthday, and no cooking | One supported recipe with three field citations |
| Level-3 evocation spells | Seven supported records |
| Recipes using no water | 334 explicit zero-water matches and 333 unresolved records with no water declaration. The displayed list remained partial under the evidence budget. |
| Declared links in the three 1,004-page ledgers | Both hops verified in each ledger. The foreign-ledger target stayed unavailable and the provenance label stopped appearing as a target. |

The original natural-language Voyager question still requires an admitted query form. That result belongs alongside the successful replays because it defines the scope of the improvement. The collection answers check admitted predicates. The relationship reports verify declared documentary links within the selected ledger. The three corpora supply separate observations about how those rules behave. [1–4]

## Making the workflow usable

The automation guide describes the path from a messy text dump to a native ledger. The sorter proposes source occurrences and candidate references. Classing can automatically accept clean drafts with distinct declared identifiers. It retains literal fields and source positions. A person can inspect blocked or ambiguous drafts and make decisions from the originals. The builder rereads the inputs, stages and validates the pages, and can append bounded batches to a common ledger. Users can then ask a source-backed question or investigate links against the published collection. [3]

I want a user to see where the automation needs a decision and what evidence is available for making it. In the earlier plain-prose control, four inputs without declared identifiers produced four drafts and zero automatic acceptances. In the structured 1,000-record controls, the native tools built and validated each collection before search began. The difference gives the user a concrete expectation about what will happen when an input file has enough structure for automatic classing and what work remains when it does not. [1, 3, 8]

## Closing the release loop

I use the pull request as a decision point. PR #62 passed all nine checks. The exact archived source ran 1,553 Python tests with two skips and no failures in the recorded local run. The checks covered the bounded repair, earlier behaviors and the archived browser build. GitHub merged the candidate at `9c9212e` at 16:11:47 UTC on November 20, 2026. The merge tree matched the tested candidate tree. The Pages workflow for that merge completed successfully at 16:28:22 UTC, including the live Chromium smoke test. That smoke test exercised the deployed site. The three-collection replay supplies the separate evidence for the answer and traversal counts in the table. [2, 5, 6]

The session recap places the first screenshot at 10:25 a.m. and the final one at 11:29 a.m., a span of about 64 minutes on the displayed clock. It shows the final Codex report at 11:28 a.m. and reports 47 minutes and 35 seconds of Codex work. Those figures describe the observed session and its displayed timer. The GitHub timestamps give the separate release record. The recap also lists 10 files and +193/−40 lines. The complete GitHub PR and the merge diff record 19 changed files, 473 insertions and 71 deletions. The scope of the smaller counters is unspecified. [5–7]

The elapsed time tells how this case unfolded. The method itself can be judged by asking whether another person can inspect the baseline, repeat the controlled comparison, see what remains unresolved, and identify the exact version that reached the live browser. This case used authored controls on a project I develop. Independent replication would require another evaluator to run the method with their own cases, including cases designed to invalidate the predicates or break the release workflow.

## The design standard

In this release, the system accepted new source-backed answers while retaining uncertainty. It followed links across ingestion boundaries while retaining the boundary around the selected ledger. It exposed a limit in how users can phrase a question and carried that limit into the release record. The engineering aim I put behind the method is

> a system that can develop new capabilities while retaining the boundaries that make its answers trustworthy.

## Evidence record

[1] McPhetridge, M. D. (2026). *What MPLPB built, retrieved, answered, and traversed.* Three-collection baseline at `fef46d1`. [Retained baseline measurements](evidence.json).

[2] McPhetridge, M. D. (2026). *Verified collection filters and declared-link replay.* Candidate `1413747`. [Retained replay measurements](evidence.json) · [Candidate handoff](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/141374727a0890b163d3e296c61bef8ab4a5b7dc/HANDOFF.md).

[3] Combined MPLPB. *From a raw dump to a checked collection.* [Collection automation guide at the merged revision](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/9c9212e5b9789e3b3e1b28e0426b2bdc7c9ee79c/docs/COLLECTION_AUTOMATION.md).

[4] Combined MPLPB. *Historical expert path and bounded relation crawling.* [Investigation contract at the merged revision](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/9c9212e5b9789e3b3e1b28e0426b2bdc7c9ee79c/docs/HISTORICAL_EXPERT_PATH.md).

[5] Combined MPLPB. *Verify collection predicates and cross-batch source links.* [PR #62](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/62) · [Exact-head archive validation](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/44767918075).

[6] Combined MPLPB. *Publish MPLPB browser runtime.* [Pages deployment and live Chromium check for `9c9212e`](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/44770900656).

[7] McPhetridge, M. D. (2026). Author-supplied session recap of the November 20 engineering cycle. Source of the displayed screenshot times, work timer, and session diff counters.

[8] McPhetridge, M. D. (2026). *Native MPLPB recipe test.* Initial 1,000-recipe run and plain-prose control. [Retained plain-prose control](evidence.json).
