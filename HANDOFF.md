# Repository handoff

Last reviewed: 2026-11-18.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `87bd22f38686d01c3c39faaf68e2ad8ea788c185` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `f5ba899707b972e4b2bcb49b99f7dd75d754d89b74d65bc436659756093da4b8`.

## Latest user update instructions

Add an opt-in workspace that compares sorter output with MPLPB-approved originals eligible under the current profile. Reuse the reader’s existing eligibility checks and the sorter’s source hashes, occurrence IDs, and exact byte spans.

For each useful match, create a candidate that links the processed passage to the original passage and explains the relationship. Show exact matches, possible references, conflicting wording, and possible corrections distinctly. Preserve unresolved or unmatched passages for topic exploration. A match to an approved original never transfers that original’s approval to the processed document.

Let users explore a topic across processed documents. Show what each document says, where it appears, and where documents disagree. Mark every processed passage and every conclusion drawn from it “Exploratory · outside MPLPB-approved evidence.” If an approved original is also shown, display its status alongside its citation so users can see which source supports which statement.

Keep the MPLPB decision visible alongside exploration when the user asks a question: One eligible owner: Return its page. Give a strict answer only when the original body supports it. Two or more eligible owners: Ask the user to disambiguate. Keep the competing sources visible. No eligible owner: Say there is no MPLPB-supported answer. Offer labeled exploration of the processed documents if relevant material exists.

Count only eligible owners in that decision. Candidate links and synonym matches must never change ownership or eligibility. Use a separate, bounded exploration budget so candidate review cannot displace passages needed for strict proof. Show when either budget truncates the results.

Test all three ownership outcomes, a processed passage that contradicts an approved original, and a topic found only in processed documents. Verify that exploration still works when the strict answer is withheld, and that H05 stays complete at its original strict-reader budget.

## Implemented scope

- Complete frozen22-question direct versus unreserved sorter-first retest before introducing review additions; preserve measured H05 regression and preparation-only layout pilot.
- Add opt-in lexical neighbor ranking and candidate relation review beside the byte-unchanged core sorter; retain exact spans, qualifications and non-authority.
- Add fresh replay/perusal and bounded user glossary, source/pin guards and explicit ambiguous-sense signals.
- Prepare all22 questions for the subsequent three-arm study using one strict reader pin and a common discovery-reservation guard; do not alter original questions, sources, budgets or proof rules.
- Finish all66 v1 option executions before repair; retain1/22 complete in all arms, draft spans26/32,26/32,24/32, and all1033 unique proposed links.
- Conservatively separate vocabulary ranking from relationship generation: remove995 neighbor-only pair proposals, retain explicit source-key/reference/literal-wording reviews, and stop automatic traversal of weak wording/subject cues.
- Preserve completed v2 trial; add generic reader-owned atomic proof-witness admission, question-part allocation, exact-span deduplication, class-gated inspection and final citation limits; leave documentary verifier byte unchanged.
- Inspect the eight supplied past-work repositories for reusable authority/discovery boundaries; no external code imported.
- Repair an existing legacy adapter regression through independent native retrieval when an adapter replaces every normal passage with review hints; search-only hints still receive no admission or traversal.
- Publish separate final frozen four-arm results, exact H05 witness traces, original-byte/proof audits, biased prior-sample retention, costs and two-reviewer packets; keep synthetic regression controls separate.
- Add opt-in native/CLI candidate workspace with dual evidence labels, exact processed/native byte mappings, separate bounded exploration, topic/disagreement/reference review and fresh source/decision replay.
- Reuse canonical ownership with an optional eligibility intersection; default native reader unchanged. Workspace owner policy and H05 multi-source evidence proof are explicitly distinct.

## Validation recorded

- Direct22 reproduced2 supported,1 partial,3 conflict,16 abstain; configured sorter-first completed22 with1 supported,2 partial,3 conflict,16 abstain. Draft span discovery27/32 to25/32.
- Original retest regression suite1225 tests passed356.255s; log retained.
- New focused sorter/adapter controls are executed separately; final three-arm/full regression results pending.
- 63 focused legacy sorter, new review-option and experiment adapter tests passed in1.445s, covering source pins, exact routes, current eligibility, qualification-preserving neighbors, ambiguity, embedded headers, shared subjects, missing targets, source replay and CLI perusal.
- V1 full suite1240 passed393.549s. All66 option workers completed with native reader files unchanged.
- Exploratory developer/AI short-passage sample16:4 useful textual reviews,4 false/misleading candidate links,8 irrelevant; not independent or representative. Remaining1017 unassessed.
- New unrelated-object neighbor-only control reproduced a failure under v1; v2 retains both search hits without proposing a relation. An unambiguous source-declared partial-correction positive control remains retained.
- 65 focused controls passed1.437s after conservative repair. Final v2 three-arm and full regression runs pending.
- V2 conservative trial completed66 executions:1 complete/22 and26/32 draft spans in every arm; full1242 tests passed408.304s.
- H05 pilot recovers identical four source spans4070 characters; source verifier SHA unchanged. Generic two-part, duplicate and counterevidence controls executed. Full updated study and regression pending at source freeze.
- Frozen4b6b1f6 four-arm study completed88 workers, H05 complete in every arm at4 spans4070 characters. Extracted source full1249 tests found1 compatibility failure in existing sorter-first adapter; preserve failure and fix without changing tests or verifier.
- Final runtime6aa4ecd4d052af2b554abd0da2fd465f11c9fef6: all88 workers completed,2 complete/22,1 partial,3 conflict,16 abstain in each arm;27/32 draft spans; no extra draft anchor or complete answer attributable to optional aids.
- Final extracted-ZIP full suite1249 tests passed479.177s; separate fictional finite-contract52/52 passed. Fresh audit12 native claims32 original-byte citations and44 complete suggestion replays passed.
- H05 all four arms: same4 original spans4070 characters within12/8000 limits;14 duplicate charges avoided; verifier byte unchanged. Relevant counterevidence over budget blocks completion; generic two-part proof controls pass.
- Prior biased developer16-item sample:4 misleading links removed,4 useful textual reviews retained,8 irrelevant wording matches retained; not general historical precision/recall.
- 59 focused workspace/ownership/gate/admission controls passed19.461s before source freeze. H05 standalone contract unchanged before/after tiny workspace budget. Full new-runtime regression and public-original demonstration pending.

## Limitations and blocked checks

- 2/22 complete coverage restored, no new complete answer beyond historical baseline. Correct-outcome judgments, semantic historical recall and global false-link rate remain unassessed.
- Independent human and unseen-original evaluation NOT RUN; packets prepared.22 questions remain development data.
- Concurrent local timings are measured, not controlled efficiency comparisons. Model/API use zero; compute price and real human times unknown.
- Exact final publication-head ZIP/browser release gates remain separate from executed runtime6aa tests.
- Workspace is an opt-in offline native/CLI surface; no new browser UI or independent semantic accuracy claimed.
- Legacy ownership finds no H05 owner, while standalone multi-source proof remains complete. Workspace route refusal is not a budget regression.

## Next steps

- Freeze workspace revision, run extracted-ZIP full regression, replay all22 native questions and publish bounded public-original workspace demonstrations with actual costs.
- Update PR52 with executed evidence and require exact final-head release gates; independent human/unseen review remains NOT RUN.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
