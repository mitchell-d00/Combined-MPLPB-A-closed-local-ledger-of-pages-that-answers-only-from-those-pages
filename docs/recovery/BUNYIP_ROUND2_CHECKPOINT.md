# Bunyip round 2 recovery checkpoint

Last reviewed: 2026-11-26.

**Documentation and working-state checkpoint only. The local C3 implementation and raw evidence have NOT been uploaded in this checkpoint.** The managed environment became offline/unavailable before a source commit or push. This file records the retained session state so recovery can continue without assuming acceptance.

## Verified repository state and publication boundary

GitHub main was checked at `2622813aba9ee1f1880693eeb71ae015cb3da999`, tree `78ffea54e3ad0e35ac1dd27f6db16c32a8ec23dc`; PR105 was merged. No open PR existed at this checkpoint's discovery. Local work was on `local/bunyip-round2`, based on that main, with uncommitted C3 changes. No round-two native candidate commit or committed source ZIP had been frozen.

Mitchell explicitly authorized a recoverable branch/PR push despite blocked verification, then required exact-head checks, merge only after acceptance/protection gates, and deployment verification. This checkpoint uses the GitHub connector because the local machine cannot be reached. It is not a release of C3.

Canonical [Al/Betty definitions](../TEAMBUILDING.md#al-and-betty-work-steps), unchanged [Outside](../TEAMBUILDING.md#outside), [shared-rule criterion](../TEAMBUILDING.md#shared-rule-criterion-for-betty-al-and-outside), and [broader-coverage criterion](../TEAMBUILDING.md#broader-coverage-with-preserved-constraints) apply. Broader language is the objective; source eligibility, attribution, polarity, qualifications, memory/provenance and native admission remain invariants.

## Active implementation and decisions

Session-recorded C3 changes concern shared whole-question argument binding; literal entity names containing “and” without swallowing extra obligations; explicit positive/negative classification witnesses; separate structured/readable yes/no output; object-free instruction questions with a unique actor/recipient/task; opening-time body-field counterevidence; shared quotation/report-caption scope; and carrying relevant unresolved evidence to final admission.

The general failure is that inability to interpret relevant evidence had been treated as absence of competing evidence. Relevant unresolved evidence must block affected admission while irrelevant unreadable material must still permit valid answers. Ownership policy and native budgets are unchanged. No entity/case/benchmark-specific runtime branches are authorized.

The museum refusal-copy change has its own protocol. The synthetic CLI reconstruction is not the exact Outside live case, and software checks are not participant observations.

## Recorded comparisons and unresolved objections

These numbers are carried from retained local session receipts. The offline workspace prevents re-reading their raw bytes here; they are not newly executed or independently adjudicated measurements.

- Primary baseline:444 completed/scored executions;21/78 positive answers;360/366 correct withholds;57 positive misses;6 unsupported competing-time completions;0 worker/citation failures.78 question strings,396 unique source-question-state inputs,48 repeated memberships. Positive discovery78/78 does not establish counterevidence completeness.
- Routing baseline:54 cases;10/16 positives and38/38 withholds. Six misses stopped at entity parsing. Title-decoy cases already worked and are preservation, not new routing gains. A separate18-case polarity set had4/6 positives,12/12 withholds and6 prospective output-contract failures.
- C1 recovered78/78 primary positives and366/366 primary withholds, but two reported-field guard completions were unsupported. Reject C1. Its849 released-reader contract memberships were exact matches, representing825 unique earlier inputs.
- C2 passed560 earlier development decisions, then failed four new mixed-binding controls with unsupported completions. Eight irrelevant-evidence positives still passed. Reject C2. C2 full native1902 passed; original1000 strict-key failure remains beside a separate prospective source-checked assessment. Bunyip BB remained900/900 answerable,200/200 withholding controls and900 citation checks.
- C3 focused37 tests passed. Full native attempt was interrupted with exit130 during process exhaustion. Development and legacy attempts exited1 and require log inspection; a preservation wrapper exit0 does not prove child success. No broad C3 acceptance, no full preservation result and no fresh-transfer gain are claimed.

Original keys, scores, packets, rejected candidates and failure classifications must stay unchanged. Separate source-support correctness, output-contract compliance, routing, ownership, conflict, coverage, consolidation and infrastructure outcomes. Existing coverage gaps may remain backlog; unsupported admissions and lost valid support require investigation.

Bunyip BB — Ben Gelhaus external adversarial benchmark remains unchanged consumed regression evidence:150 canonical +750 paraphrase positives and200 negative controls. Credit Ben for the benchmark/analysis and Mitchell for the implementation. Do not pool it with new generated suites or call it unseen transfer.

## Evidence locations recorded before loss of access

The following archives were byte-verified on the persistent workspace before the outage; their current accessibility is blocked. They are **not attached to this remote checkpoint**. Do not restart or discard the old environment before recovering needed volatile files.

| Local archive under /workspace/cryptid-custody/ | Bytes / files | SHA-256 |
|---|---|---|
| bunyip-r02-completed-attempts-v1.tar.xz |4375048 bytes;19414 files|7505d07161e0f3b71c12591112c58704357ebfe4a7cc125b9bbb0ad495f6d27a|
| bunyip-r02-resource-attempt-v1.tar.xz |1306564 bytes;11084 files|efc4bb889a4dc53e536b404b3726262e3eb35d16ad9b3fc5c663c588d036208d|
| bunyip-r02-pre-edit-v1.tar.xz |69416 bytes;354 files|a34fc987e90b52fe2f3638b26bccad7eeec80d1050e1d01706b44279171821d5|
| bunyip-r02-routing-retained.tar.xz |97348 bytes;821 files|91dc743647921582e67d18809890a6d04c2d7c14f4d07bd1578ad197597ca00e|
| bunyip-r02-rejected-c1-native-v1.tar.xz |272332 bytes|b6b43fa0a3032a530732be4ab929cdbbe8114b885826060d71652c9c78c05db0|
| bunyip-r02-rejected-c2-native-v1.tar.xz |272616 bytes|87ccdb4f41f37c48af1ff1969fba17d0e9568a529de533701161b40180ee794a|

Adjacent receipts record byte verification. Additional recovery pointers: `/workspace/cryptid-local`, `/workspace/BUNYIP-R02-RESOURCE-BLOCK.json`, `/workspace/cryptid-custody/bunyip-r02-full-native-c3-resource-attempt.log`, and `/workspace/cryptid-custody/bunyip-r02-roles-handoff-checks-v1.json`. The original source archive `/workspace/artifacts/MPLPB-attribution-fresh-source.zip` remains untouched.

The completed-attempts/resource archives contain mixed material and must **not** be blindly published: separate public outputs/source from held inputs/keys and private correspondence. This remote checkpoint publishes metadata only.

## Custody: do not open held packets

Both the36-case routing packet and64-case cross-family final packet remain sealed, unopened for evaluation and unrun. They were prepared before reader edits. Packet/key/generator receipts are in their designated local custody; their contents are excluded here. Same operator prepared templates, implemented and scored. No independent preparation, blinding, semantic or outside-custodian claim follows from role names.

Freeze and verify the designated committed candidate ZIP before opening either packet once. If results inform a repair, consume that packet as development and prepare genuinely fresh material. New names/seeds alone establish repeatability, not structural transfer.

Human onboarding execution, independent historical/semantic adjudication, independent preparation/blinding, outside-custodian scoring and native OOCC remain NOT_RUN.

## Infrastructure and approval failures

Approximately32285 zombie processes, including32002 bwrap processes adopted by PID1, were observed. Child/thread creation failed EAGAIN. Last measured free workspace space was2494464 bytes; a full candidate ZIP needs a fresh storage measurement and a distinct versioned filename, preserving historical archives.

Automatic approval rejected a PID1 ptrace seize/interrupt/detach diagnostic probe: interrupting a system supervisor risks environment disruption and had not been authorized. The probe was NOT_EXECUTED and no bypass occurred. Later, environment status reported connectivity offline and execution tools reported no usable environment. These are infrastructure/tool-approval failures, not reader decisions.

Local handoff generation/check and Git staging/revision probes could not launch. The last local HANDOFF working-state text was rendered with the unchanged builder but its inventory was explicitly stale. This remote checkpoint separately requires CI to rebuild/check its own committed inventory; passing it would validate this documentation tree, not unavailable C3.

## Authorized next actions

1. Publish this limited recovery checkpoint/PR and retain its failed/pending remote checks.
2. Restore access to the **same** workspace without discarding volatile state; verify archive hashes, source diffs, branch/index, tests and custody before further work.
3. Upload the actual C3 implementation and reviewed public evidence, excluding sealed inputs/keys and private material. Reconcile local and remote documentation; do not overwrite either history.
4. Inspect C3 execution failures, rerun affected checks with bounded concurrency and no unsandboxed fallback, audit claims/citations and compare preservation/BB.
5. Update the authoritative Test Index and department ownership with actual tests/results; this recovery note adds no reader test or new score.
6. Freeze the committed candidate ZIP, then run each designated held packet once and retain every result.
7. Complete all required exact-head remote and protection checks; merge only when applicable acceptance passes. Verify deployment and live fingerprints. Mitchell's publication authorization persists; no further confirmation is needed.

Existing coverage misses alone do not require perfect scores. Missing implementation/evidence, unresolved unsupported admissions and blocked required gates cannot be described as release-ready.
