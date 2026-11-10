# No-Unverified-Promotion: source audit and research finding

Last reviewed: 2026-11-10.

Research author: **Mitchell D. McPhetridge**. Prepared through a Codex-assisted
repository audit. Status: technical research draft and implementation audit;
not a published scientific discovery, peer-reviewed paper, independent validation,
or claim of novelty. The working name was proposed in the task. It is not
retroactively attributed to the preserved papers.

**Final classification: Existing principle expressed in MPLPB terminology.**

The inspected work supports a recurring engineering error: treating evidence for
one proposition as sufficient for a different, more demanding proposition without
meeting that proposition's contract. The four requested domains contain identifiable
instances and safeguards. They are not four independent scientific replications.
Their checks address different properties, including meaning, byte identity,
runtime behavior, freshness and permission. No single Boolean success or new
generic authority layer can replace those checks.

The abstraction proved useful as an audit question: it exposed one additional
completion-contract defect. It has not shown incremental predictive power over
well-specified existing contracts, or a measured four-domain benefit over the
current system. The literal, unconditional reading of `S_n ⇏ V_(n+1)` is too
strong: some operations establish the downstream property by construction.
The qualified specification preserves those legitimate transitions.

## Deliverables and evidence identity

| Output | Retained material |
| --- | --- |
| Finding, attribution, implementation assessment and classification | This report |
| Exact original/current source locations, dates, guards and reproduction | [Matrix summary](MATRIX.md), [canonical 16-instance matrix](evidence-matrix.json), [40-source inventory](sources.json) |
| Formal candidate, scope, exceptions and falsifiers | [SPECIFICATION.md](SPECIFICATION.md) |
| Frozen development cases and future controlled evaluation | [PROTOCOL.md](PROTOCOL.md), [20 case specifications](development-cases.json), [freeze SHA-256](development-cases.sha256) |
| Executed regression and paired implementation results | [contract-replay.json](contract-replay.json), [initial baseline record](baseline-results.json), [failing baseline log](baseline-regressions.log), [patched log](patched-regressions.log) |
| Read-only enforcement-setting observation | [ruleset-observation.json](ruleset-observation.json) |
| Reproduction runner | [audit_unverified_promotion.py](../../tools/audit_unverified_promotion.py) |

Audit baseline: `73b795634332e48aab499c16e07a2af4328f2f7a`. Source identity
is pinned by revision, Git blob and SHA-256. New implementation/test/runner bytes
are independently hashed in the replay report. That report was produced from a
working candidate; its file hashes, rather than the old checkout HEAD, identify
the tested correction. Exact committed ZIP/CI outcomes remain separate evidence.
The local freeze is not a public preregistration or an independently sealed holdout.

## Findings in the four domains

### A. Retrieval versus supported answering

The [October 13 audit](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/75cbbd0794e891e0e8e4759e0993a0de7c5eab9f/docs/ANSWER_RELIABILITY.md)
explicitly identifies candidate selection presented as answering. Its example
class is reproducible: metadata selects Aster's service page while the body gives
the Other service's port. The accurate returned body and its citation do not
answer the Aster proposition. Current `supported_answer` and `answer_query`
require eligible body evidence under a finite grammar and retain refusal or
ambiguity when support is absent or competing. `retrieve` can return that page
successfully while always setting `answer_supported:false`.

Current source eligibility also checks seals, unique identities, explicit origin,
pinned lineage, status, dependency freshness, exclusions and delivery profile.
Intact historical bytes are not sufficient current authority. Assisted citations
and model review are a different claim again: assisted outputs do not become
deterministic supported answers or verified truth. Unknown wording can still be
refused despite a human being able to answer it from the body.

The historical audit reports four wrong legacy returns on its held-out/adjacent
pottery sets being refused after the repair. It also reports zero supported
returns on the three frozen pottery sets at that historical revision: answer
precision was undefined and answerable coverage zero. Later extensions have
different measurements. These old numbers were not rerun or revised here.
They are evidence against equating stronger gating with a cost-free improvement
in useful completion. The present replay measures assertions about the current
contracts, not historical or general-language accuracy.

### B. Artifact creation versus verification

`build_handoff.check` binds the current inventory and rendered handoff to recorded
inputs. `release_evidence.verify` binds submitted artifacts, expected candidate
identity and report labels under its declared trusted-CI assumption. Neither is
a generic semantic oracle for an arbitrary requested deliverable.

The new boundary control constructs a readable ZIP containing the wrong requested
text and a coherent manifest/preview with **authored fixture gate labels**. The
native manifest verifier accepts its narrower consistency claim, while the
separately stated content criterion is false. This is not an executed CI success,
a forged production release, or a newly discovered manifest-verifier bug. The
verifier documents its trust boundary. Calling that result proof of requested
content, factual correctness, or deployment would be the promotion error.

Packaging also depends on the caller supplying the intended tested browser input.
The packaging function identifies bytes and source state; its name or generated
checksums do not establish every application acceptance criterion. A useful
specification must replace the ambiguous word `verified` with the exact property
being checked: readable ZIP, complete tracked inventory, matching digest, tested
behavior, requested content, or approved delivery. These properties differ.

### C. Testing versus deployment verification

The ZIP-first workflow selects the actual PR head, records commit/tree and archive
hash, extracts the archive and runs source, WebAssembly and Chromium checks from
that extraction. The candidate manifest deliberately reports
`candidate_checks_passed_not_deployed`. A different expected head or altered
artifact fails the verifier. This is implemented evidence-scope discipline.

The historical release guide records an October 20 setup gap: workflow text alone
did not require successful checks before merge. The retained October 29 observation
records the later ruleset configuration. A fresh read-only observation in this
audit finds an active main-target ruleset requiring PRs and strict
`archive-first`/`regression` checks, with no listed bypass actors. That is a
configuration observation; no deliberately failing merge or bypass was attempted.
Settings can change and GitHub remains a trusted enforcement service.

Pages deployment is ordered after build, then followed by actual public-URL
Chromium smoke/helper checks. Failed checks fail the job **after** deployment;
there is no automatic rollback or technical prevention of a human announcing
success early. The current smoke checks bounded behavior, not every feature or
device. They do not compare the entire deployed HTML digest with the candidate
preview. Consequently, a pass is observed-site smoke evidence, not a general
proof of whole-site correctness or exact public-byte identity. The audit records
this limit; it did not execute a stale-site fault experiment or add a new release
identity framework. Trusted CI labels, current settings and accurate public
reporting remain distinct responsibilities.

### D. Handoff, permission and accepted completion

`WorkStore.handoff` reconstructs a visibility-filtered view under the successor's
current capability. `_actor`, `_permission` and `execute` check expiry, revocation,
fencing, operation/tool/scope permissions, current source dependencies and task
revision. Recovery does not copy a predecessor's authority. A current capability
still does not authenticate arbitrary provider metadata or prove real-world safety.

Working assessments, contested claims, source roots, failed attempts, proposed
actions, execution receipts and task acceptance are distinct. Copied reviews add
no independent roots. Failed attempts may inform a decision without becoming
successful prerequisites. A crash/unknown external outcome remains indeterminate
until host reconciliation. External effects and local transactions are not atomic;
revocation cannot retroactively undo an already dispatched external action.

**New concrete defect:** the completion branch checked receipt task revision and
the criteria in the *proposed* done record. It did not compare that record's task
contract with the pre-completion contract. An authorized writer could therefore:

1. Obtain a real `passed` receipt that covers one criterion but not another.
2. Submit one revision that both drops the unmet criterion and sets `state=done`.
3. Consume the old receipt because its revision matched the record being replaced.

Changing the goal or substituting task input dependencies in the same completion
write produced the same mismatch. These are real native coordinator writes using
normal capabilities, not forged host receipts. Authorization to revise a task is
not evidence that execution under the previous contract met the replacement one.

The correction is local to `_validate_record`: consuming receipts to mark a task
done cannot simultaneously change its goal, review policy, criterion set or task
input pins. Deliberate changes remain possible as an open revision followed by
fresh execution. Identical criteria reordered are accepted because coverage is a
set property. Existing receipt, current-source, permission and revision checks
remain in place. No new global promotion framework, answer semantics or authority
layer was added, and prior events/history are not rewritten.

## Attribution: original formulations and the new synthesis

McPhetridge's preserved [Smart Local manuscript](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/c665337492a4aa5c3619c57c439a0583732c68bd/papers/Smart_Local_MPLPB.txt)
is internally dated August 12, 2026. Its first section distinguishes structural
corpus validation from reader behavior, provenance and local/public authority.
That is an existing component formulation, not proof that a new universal
promotion principle was already explicitly named.

The September 2026 [Continuation Must Preserve Revisability, Not Truth](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/c665337492a4aa5c3619c57c439a0583732c68bd/papers/Continuation_Must_Preserve_Revisability.pdf)
describes mechanical recovery preserving an unsupported supplier/component
inference and its consequences. Pages 1–3 distinguish recoverability from
revisability. The October 31 coordinator applies these ideas through explicit
records and guards. Its five-instance fixture is scripted software evidence,
not measurements from independent AI providers.

[Clarity Is Not Validation](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/c665337492a4aa5c3619c57c439a0583732c68bd/papers/Clarity_Is_Not_Validation.txt)
distinguishes visibility, clarity and validation. Its proposed retraction test
and kill conditions are not established empirical results; the paper says the
conditions were untested. Its reference to a PHA retraction is an attributed
self-report, not an experiment independently reproduced in this audit. The file
has no established internal authoring date; October 8 is repository retention,
not an invented publication date. The preserved joining text *What the
Specification Forbids* also supplies falsifiers; it does not independently
validate the asserted relation between its component theories.

The October 13 answer audit, October 19–20 release work, October 27 retrieval
contract and October 31 coordinator supply explicit implementation distinctions.
The new contribution here is the proposed cross-domain organization, corrected
formal candidate, evidence matrix, falsifiable evaluation plan and newly
reproduced completion defect. It is not a claim that the old sources used the
working name or already established the synthesis as a scientific result.

## Prior concepts and the novelty challenge

These references are comparison material, **not sources of McPhetridge's research
or an imported discovery attribution**. The bounded lookup is not a systematic
literature review or proof of exhaustive priority.

| Existing concept / primary source | Relevant overlap and limit |
| --- | --- |
| [Hoare, 1969, axiomatic basis](https://doi.org/10.1145/363235.363259) | Program reasoning depends on specified assumptions and conclusions. Successful execution and an unstated postcondition are different assertions. This already explains the logical proof-obligation concern. |
| [Meyer, 1992, Design by Contract](https://se.inf.ethz.ch/~meyer/publications/computer/contract.pdf) | Preconditions/postconditions specify obligations; a routine's guarantee can justify a later step. Redundant checks add complexity. This is both a close antecedent and a counterexample to demanding a new gate after every success. |
| [Rust book, newtype safety](https://doc.rust-lang.org/book/ch20-03-advanced-types.html) | Distinct types prevent confusing values that share an underlying representation. MPLPB's different success kinds and authority flags address an analogous boundary, though Python dictionary labels are not static proofs. |
| [Saltzer and Schroeder, 1975, complete mediation](https://web.mit.edu/saltzer/www/publications/protection/Basic.html) | Current access authority must be checked and cached decisions refreshed when authority changes. This directly overlaps expiry, revocation and handoff boundaries. It does not establish factual truth. |
| [SLSA v1.2 artifact verification](https://slsa.dev/spec/v1.2/verifying-artifacts) | Artifact digests, trusted builder identity and consumer expectations have separate checks and trust assumptions. Provenance must be checked against its intended claim. This is comparison, not adoption of SLSA or an assertion that MPLPB meets a SLSA level. |
| [GitHub deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) | Effective protection depends on configured environment rules. A workflow file's existence alone is not a deployment guarantee. |

The unification adds no demonstrated prediction beyond those domain contracts.
The new completion defect is well explained as contract/revision substitution.
The shared language can guide reviewers to ask which property was actually
established, but renaming that discipline does not establish conceptual novelty.
The research manuscript's normative clarity criterion is also not interchangeable
with an executable authorization or program postcondition.

## Executed results and unmeasured claims

| Execution | Observed outcome | Interpretation |
| --- | --- | --- |
| Answer/retrieval regression replay | 33 tests pass | Current declared answer/source boundaries under development assertions |
| Artifact/release/handoff replay | 12 tests pass | Manifest and handoff consistency contracts, not semantic acceptance or deployment |
| Specialist replay including new tests | 43 tests pass | Current local work-state, authority and completion guards |
| Same five new tests against archived baseline | Three rejection assertions fail; two legitimate controls pass | All three prohibited atomic completion writes were accepted by the old implementation |
| Same five tests against patched store | All five pass | Three prohibited writes rejected; two legitimate controls accepted |
| Coherent wrong-content artifact control | ZIP readable, manifest accepted, requested content false | Expected narrower verifier scope; not a new production defect |

There are 88 tests in the focused replay. The paired runs reuse the same five
cases and are not ten independent observations. The initial failing test run is
retained separately; it is not added to sample size. In the three targeted invalid
writes, observed acceptance changes from 3/3 to 0/3. In the two legitimate controls,
acceptance remains 2/2, so no false refusal occurred in those two examples. These
are deterministic author-inspected development observations, not estimated
population error rates or a blinded cross-domain comparison.

Single-suite timing is retained for reproducibility and includes setup; it is
not a measurement of added gate latency or computational cost. Human correction
burden, independent evaluator agreement, held-out performance and controlled
four-domain promotion-rate reduction were not measured. The 20 locally frozen
case specifications include prospective cases; their existence does not mean all
20 were executed as one benchmark. The runner explicitly separates contract
replays, the artifact boundary control and the five-case implementation comparison.

## Implementation and research decision

Keep the existing answer, artifact, release and specialist contracts. Apply the
small demonstrated completion correction and retain its failing baseline trace.
Do not add a global promotion registry, new model authority or duplicated guard
layer. Named existing result types and claim-specific acceptance checks do most
of the work already.

A separate **technical case study/specification** is warranted if it presents the
source history, limits, counterexamples and defect honestly. A claim to a novel
universal principle or a scientifically demonstrated four-domain improvement is
not warranted by this evidence. The next useful research step is the independently
authored, blinded protocol, including positive controls, refusal costs and
evaluator consistency. A null incremental benefit over existing contracts is an
acceptable and informative outcome.

The answer to the final research question is therefore qualified: **the repository
demonstrates recurring claim-scope failures and existing defenses; one additional
gate measurably fixes three constructed completion errors. Whether the proposed
unification improves unfamiliar workflows across all four domains remains untested.**

## Reproduce without changing preserved evidence

Use Python 3.12 for the research runner's archive extraction, matching current CI.

```sh
python tools/audit_unverified_promotion.py --output /tmp/nup-current-NEW.json
# A Git checkout with full baseline history is required for this comparison:
python tools/audit_unverified_promotion.py \
  --baseline-ref 73b795634332e48aab499c16e07a2af4328f2f7a \
  --output /tmp/nup-paired-NEW.json
```

The comparison extracts the old commit into a temporary directory and supplies
the new, hash-recorded test module. It is explicitly an old implementation under
new tests, not an exact historical-suite reproduction. Existing output paths are
rejected to preserve earlier measurements. Do not overwrite frozen cases, papers,
historical reports, gold labels, source seals or imported user data. Exact-head
ZIP/CI and any later deployment verification must be recorded separately; this
research draft and its local test report are not publication or deployment proof.
