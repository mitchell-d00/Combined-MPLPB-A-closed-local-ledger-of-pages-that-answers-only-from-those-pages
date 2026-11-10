# Repository handoff

Last reviewed: 2026-11-10.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `73b795634332e48aab499c16e07a2af4328f2f7a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `64e9ee0989d618cbc98c77aa1ae5384a00102f188b3c6c41ae3f667ae12a72e0`.

## Latest user update instructions

Codex Research and Implementation Task

Combined MPLPB — Investigate the No-Unverified-Promotion Principle

Repository:
https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages

Research author: Mitchell D. McPhetridge

Task type: Source-grounded research, technical audit, potential formalization, adversarial testing, and narrowly scoped implementation.

1. Objective

Investigate whether the Combined MPLPB research and implementation reveal a generalized failure mechanism across multiple domains:

A successful intermediate operation is incorrectly promoted into a stronger claim of validity, authority, correctness, or completion without the evidence required for that stronger claim.

Use the provisional working name:

The No-Unverified-Promotion Principle

This name is a research candidate, not an established term or an automatically accepted discovery.

The objective is to determine whether the principle is:

1. Explicitly supported by Mitchell D. McPhetridge’s existing research and implementation history.
2. A useful abstraction across multiple independently identifiable failure classes.
3. Already implemented through existing MPLPB contracts and gates.
4. Testable through adversarial and comparative experiments.
5. Distinct enough from existing engineering concepts to warrant a separate technical paper or specification.

Do not presume the principle is new, scientifically validated, universally applicable, or worth implementing before investigating those questions.

2. Initial hypothesis

Consider the candidate rule:

Success at one operational stage does not automatically authorize a stronger downstream claim.

A tentative formal representation is:

[
S_n \not\Rightarrow V_{n+1}
]

Where:

* (S_n) is successful execution at stage (n).
* (V_{n+1}) is a stronger downstream validity claim.
* Promotion requires evidence sufficient for the specific downstream claim.

Investigate whether this formulation captures a genuine common mechanism or merely restates ordinary requirements for testing, verification, authorization, or type-safe transitions.

If the formulation is inadequate, correct it or reject it.

3. Inspect the existing repository first

Before modifying code, read:

* AGENTS.md
* HANDOFF.md
* handoff/update.json
* README.md
* CONTENTS
* docs/ANSWER_RELIABILITY.md
* docs/PAGE_RETRIEVAL.md
* docs/RELEASE_EVIDENCE.md
* docs/ZIP_FIRST_RELEASE_TESTING.md
* docs/SPECIALIST_CONTINUITY.md
* docs/PRODUCTION_READINESS.md
* docs/RESULTS_AND_TESTS.md
* papers/Clarity_Is_Not_Validation.txt

Inspect the relevant source modules and tests, including mplpb_combined, mplpb_answers, mplpb_work, and the release-validation tools.

Follow additional repository references when they are relevant.

Use the existing historical source material as evidence. Preserve exact source revisions and commit identities.

4. Investigate four candidate failure domains

A. Retrieval versus supported answering

The October 13 answer-reliability audit describes candidate selection being presented as answering.

Investigate the transition:

candidate_found → answer_supported

Determine what evidence is required for a legitimate supported answer.

Identify existing safeguards and adversarial cases where a correct source selection nevertheless fails to support the requested proposition.

B. Artifact creation versus artifact verification

Investigate the distinction between:

artifact_created → artifact_verified

A generated file, archive, manifest, document, or application package may exist without satisfying its acceptance criteria.

Examine how MPLPB distinguishes successful creation, correct content, verified packaging, and an approved deliverable.

C. Software testing versus deployment verification

Investigate the transitions:

build_succeeded → candidate_tested → deployed → deployed_verified

Study ZIP-first validation, exact-head checks, source hashes, WebAssembly execution, browser tests, and postdeployment verification.

Identify which transitions are technically enforced and which depend on operational discipline.

D. Specialist handoff versus authorized task completion

Investigate:

handoff_created → successor_recovered → action_authorized → task_completed

Use the implemented specialist-continuity coordinator.

Determine how it distinguishes recovered evidence, contested claims, valid permissions, successful attempts, and accepted task outcomes.

Pay particular attention to stale authority, revoked capabilities, failed attempts, and false completion receipts.

5. Construct an evidence matrix

For each candidate instance, record:

* Original source file and revision.
* Exact location or source-code function.
* Historical date, where established.
* Initial operation and observed result.
* Stronger downstream claim.
* Why the initial result is insufficient.
* Required verification or authorization condition.
* Existing software enforcement, if any.
* Recorded failure and repair, if any.
* Reproduction command and expected behavior.
* Whether the example genuinely supports one shared principle.

Distinguish documented observation, implemented behavior, untested specification, and new inference.

Do not describe developer-authored test fixtures as independent scientific validation.

6. Challenge the hypothesis

Actively attempt to disprove the proposed unification.

Ask:

* Are these genuinely instances of one failure class, or several unrelated errors?
* Is there already a standard engineering term that explains the mechanism sufficiently?
* Does the principle make a prediction not already made by the individual source contracts?
* Does it prohibit legitimate inference or harmless transitions?
* Are there cases where downstream validity genuinely follows from upstream success by construction?
* Does an explicit promotion gate reduce errors, or merely introduce unnecessary refusals and complexity?
* Can the proposed principle be applied consistently by evaluators unfamiliar with the implementation?

Investigate relevant existing concepts, including design by contract, type systems, proof obligations, provenance validation, authorization boundaries, and continuous-delivery gates.

Do not claim novelty merely because this repository uses different terminology.

7. Build a falsifiable experimental protocol

If the source audit supports the candidate principle, design adversarial tests across the four domains.

Introduce cases such as:

* Correct page selected, unsupported answer requested.
* Accurate citation, incorrect interpretation.
* Correct source text, stale source authority.
* File successfully generated, wrong requested content.
* Source checkout tests passed, packaged artifact broken.
* Candidate browser tests passed, public deployment failed.
* Specialist handoff succeeded, authorization expired.
* Attempt returned success, but task acceptance criteria were unmet.

Compare systems with and without an explicit downstream promotion check, while controlling for task difficulty and other relevant differences.

Measure:

* Unsupported promotion rate.
* Correct task completion.
* False refusal rate.
* Undetected authorization failures.
* Human correction burden.
* Added computation and latency.
* Error recovery.

Include negative controls and boundary cases in which promotion is justified.

Freeze evaluation cases before measuring outcomes. Separate development fixtures from held-out tests.

8. Implementation requirements

Do not immediately add a new global promotion framework.

First determine whether existing MPLPB source, answer, release, and specialist-work contracts already enforce the relevant distinctions.

Avoid duplicating existing guards or introducing another authority layer without demonstrated need.

If a concrete uncovered defect is identified:

1. Write a failing regression test.
2. Implement the smallest sufficient correction.
3. Preserve existing supported-answer semantics and explicit refusals.
4. Preserve source hashes, lineage, supersession, historical results, and archival materials.
5. Re-run the relevant tests and record actual outcomes.
6. Keep the original failure and its repair traceable.

If no defect is established, deliver a research specification and test protocol rather than unnecessary code changes.

Do not weaken source eligibility or broaden model authority to make tests pass.

9. Expected research outputs

Prepare:

A. Research finding

A technical explanation of whether the proposed common failure mechanism exists across the inspected domains.

B. Attribution and provenance

Identify the original McPhetridge sources containing each component and distinguish the author’s existing formulations from this newly proposed synthesis.

C. Formal candidate specification

Define the proposed rule, scope, exceptions, falsifiers, and relationship to existing contracts.

D. Adversarial evaluation

Provide reproducible test cases and results for any tests actually executed.

E. Implementation assessment

Explain whether an implementation change is necessary, which existing safeguards already cover the problem, and any remaining enforcement gaps.

F. Final classification

Choose one of the following based on evidence:

* Supported generalizable engineering principle.
* Useful but limited design pattern.
* Existing principle expressed in MPLPB terminology.
* Insufficient evidence.
* Rejected hypothesis.

Explain the classification with specific evidence and limitations.

10. Research integrity and repository safety

* Attribute the underlying MPLPB research to Mitchell D. McPhetridge.
* Do not introduce external research frameworks as sources of this discovery.
* Do not rewrite preserved papers or frozen evaluations.
* Do not manufacture dates, tests, results, or claims of independent validation.
* Do not equate documentation, code existence, passing tests, and deployed behavior.
* Preserve the repository’s original source and answer-authority contracts.
* Follow all repository handoff, documentation, test, packaging, and release requirements.
* Report blocked tests honestly.
* Do not claim publication, peer review, deployment, or scientific validation unless the appropriate evidence exists.
* Do not modify protected source artifacts merely to make the hypothesis appear true.

11. Final research question

Does Mitchell D. McPhetridge’s Combined MPLPB research demonstrate a generalizable class of errors in which successful intermediate operations are incorrectly promoted into stronger claims of evidence, authority, correctness, or completion—and can explicit, claim-specific verification gates measurably reduce those errors across multiple software and research workflows?

Investigate the question, rather than assuming the answer.

A failed generalization is an acceptable research outcome.

The objective is not to make the principle sound convincing. The objective is to determine whether it survives technical inspection, counterexamples, and reproducible testing.

## Implemented scope

- Audit baseline 73b795634332e48aab499c16e07a2af4328f2f7a and historical McPhetridge sources across answer, artifact, release and specialist contracts. Retain a 40-source hash/revision inventory, 16-instance evidence matrix, qualified specification, adversarial protocol and research classification: Existing principle expressed in MPLPB terminology.
- Freeze 20 inspected development case specifications before new completion measurements. Retain failing old-implementation logs and reproduce the same five cases against archived baseline and candidate in isolated processes. Clearly distinguish these fixtures from held-out or scientific validation.
- Correct only the demonstrated atomic completion-contract substitution: a done write must preserve the prior goal, review budget, criterion set and task dependencies. Preserve harmless criterion reordering and explicit open revision with fresh execution. No global framework, source eligibility change or model authority expansion.
- Update affected specialist guides, research navigation, result/documentation indexes and repository handoff. Preserve original papers, imported sources, frozen evaluations, vendor assets, lineage and historical results.

## Validation recorded

- Focused replay passes 88 tests: 33 answer/retrieval, 12 release/handoff and 43 specialist tests. The retained five-case baseline comparison accepts three prohibited completion writes and two valid controls; patched store rejects all three prohibited writes and accepts both valid controls.
- An authored readable wrong-content ZIP with coherent fixture manifest is accepted by the narrower manifest consistency verifier; its semantic content criterion is false. This is a scope control, not actual CI, a production verifier defect or deployment proof.
- Read-only ruleset observation finds active strict main PR/archive-first/regression rules without bypass actors. No failing merge or bypass experiment was attempted.
- Validated all 33 matrix source references against exact Git revision bytes and SHA-256. Compared 860 protected baseline source-answer, paper, resource, vendor and historical evaluation files byte-for-byte with the audit baseline; all unchanged.
- Documentation inventory passes (225 documents, 26 evaluation families), infrastructure linkage and ten focused documentation/handoff tests pass. UI script, browser transport, JavaScript API, 45 helper, 18 loader, 12 GPU-negotiation and crawler checks pass. Node/Python subprocess sandbox EPERM was resolved by rerunning the two affected checks outside that sandbox; no implementation change was needed.

## Limitations and blocked checks

- No independently sealed held-out evaluation, human correction-burden study, independent rater agreement, gate-overhead measurement, four-domain causal benefit, novelty proof, scientific publication or peer review. Suite timings include setup and are not gate-latency estimates.
- Local replay identifies implementation/test bytes by SHA-256. Exact committed archive and CI are separate checks; do not infer their success from checkout tests. No research-related deployment or public-byte-identity fault experiment was performed.
- Existing artifact/release checks have trusted-CI and bounded smoke scopes; current public smoke does not establish full deployed-byte equality or all-device correctness. Host adapters and acceptance specifications remain trust boundaries.

## Next steps

- Freeze the committed candidate, archive/extract it, check its handoff and execute exact-head archive-first/regression checks. Keep subsequent CI evidence separate from this implementation candidate.
- For scientific efficacy claims, independently author and seal held-out cases, randomize paired conditions, measure all protocol outcomes and publish negative results. Keep domain contracts if a generic layer provides no incremental benefit.
- Future changes must preserve historical/vendor/source bytes, record actual checks and update handoff from the latest user instructions.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
