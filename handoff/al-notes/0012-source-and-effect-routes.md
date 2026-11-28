# Al note 0012 — Where the source and effect routes connect

Last reviewed: 2026-11-28.

**Al review of Outside advice relayed by Mitchell.** Reviewed main `cabcd140ee438b0a63784faa2c0fc4b2a8c54e66` and Betty's applied [PR #131] report. This note records architecture findings and a bounded documentation recommendation. Runtime and effect work require their own declared scope.

## What already connects

| Route | Current connection and boundary |
| --- | --- |
| Supplied text or native pages → eligible sources → Strict Ask | Direct write/import and existing ledgers can reach the reader without preprocessing. The provenance gate uses the original question, profile, revision and serving policy. Native proof checks the requested meaning, including attribution, polarity, conditions and missing obligations. The result can be supported, partial, conflict, clarification or refusal. [Package guide] · [Answer pipeline] |
| Text dump → optional sorting and review → sealed ledger → Strict Ask | The sorter exposes occurrences, exact coordinates and optional comparison edges. Classing invokes sorter v2, drafts pages and re-extracts the dump at build time to verify the reviewed values. Accepted drafts can become validated ledger pages, with optional generation publication. The reader still checks current eligibility and native proof. Sorter-only inspection and retired snapshots stay review material. The candidate workspace can separately call Strict Ask on eligible originals. [Sorter] · [Classing] · [Generations] · [Candidate workspace] |
| Checked evidence → exact proposal → host admission → fixed Git update → readback → durable receipt or uncertainty | Heka composed these stages for a bounded reported-authorship fixture on disposable Git. The host checks the exact action and scope independently of source content. Admission, an attempt, observed ref/marker and durable outcome are distinct. Heka recorded an intended ref update with a pending reservation after interruption and preserved uncertainty on restart. The package guide also describes the WorkStore host-adapter route, which has its own entry point and checks. [Heka results] · [Boundaries] · [Gremlin] |

These are real handoffs with different entry points. An optional preprocessing or research step can inform the next stage. The ordinary reader supplies evidence, and host authorization remains a separate decision about the proposed operation. Gremlin locates code, reports and dependency relationships for review.

## What changed after Outside's checkpoint

[PR #130] correctly stopped at the original native prerequisite. Both instruction/date compound cases abstained, and its fresh and effect stages remain `NOT_RUN`. Keep that result and the original witness scores as filed.

Betty subsequently applied note 0011 in [PR #131]. The checked head `537488df81c6f4a9b9a109fae09ad216211d26a3` passed all 12 exact-head checks and merged to current main. Development and first fresh each scored 15/15 on the bounded native study, with three complete answers, six checked instruction partials, six withholds, and zero unsupported completions or reader execution failures. Each draw used two distinct question strings across the case instances. The dated positive is an explicit same-directive date in the supported grammar. A separately placed date without an established link still leaves an unresolved date. Betty kept Git disconnected. [Native results] · [Pages run]

The native threshold is met for proposing a separately frozen integration study. The new reader result establishes no outcome for the old Git cases, sorter-to-effect composition, Apollo combined with Ares, or independent historical adjudication. Keep production dispatch inactive. An effect study would need its own source and payload pins and observable checkpoints for proof, exact operation, independent authority, attempt, readback and durable outcome. If a later claim covers raw dump through effect, include actual sorting and reviewed admission as stages in that study.

## Bounded documentation recommendation for Betty

Use the existing [Package guide] section **How sources, answers and actions connect** as the home for this explanation. It already draws direct import, optional sorting, candidate review and published classing routes. Add a short explanation or compact diagram beside it that names the native outcome states, labels the WorkStore route separately, and shows Heka's tested Git stages through independent readback and durable completion or uncertainty. Link PR #130 and the newer reader-only result as paired examples. A single link from the Experimental Lab or Test Index is sufficient if readers need a second way to find it. Reuse Gremlin's links and refresh its generated map only as required by the normal documentation workflow.

For a documentation follow-up, verify main and the native release receipt, check for overlapping changes, and use a small documentation PR. Verify links and the documentation, Gremlin and handoff checks. Keep prior notes and result artifacts at their original pins. This is the proposed assignment from Outside's advice. A new integration implementation is a separate decision for Mitchell. Al reviewed source and public records for this note. No component or integrated experiment was run.

[PR #130]: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/130
[PR #131]: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/131
[Pages run]: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/46161485189
[Package guide]: ../../docs/PACKAGE_GUIDE.md#how-sources-answers-and-actions-connect
[Answer pipeline]: ../../docs/GENERAL_ANSWER_PIPELINE.md#eligibility-before-retrieval
[Sorter]: ../../docs/PREPROCESSING_SORTER.md
[Classing]: ../../docs/CLASSING.md
[Generations]: ../../docs/LEDGER_GENERATIONS.md
[Candidate workspace]: ../../docs/CANDIDATE_REVIEW_WORKSPACE.md
[Heka results]: ../../evaluation/egyptian-gods/heka-01/README.md
[Boundaries]: ../../docs/RESPONSIBILITY_BOUNDARIES.md#what-each-check-establishes
[Gremlin]: ../../docs/gremlin/MAP.md
[Native results]: ../../evaluation/egyptian-gods/instruction-date-01/README.md
