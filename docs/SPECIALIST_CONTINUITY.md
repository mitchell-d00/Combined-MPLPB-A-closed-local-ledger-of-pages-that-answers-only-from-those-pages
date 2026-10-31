# Specialist continuity: a proposed work-state ledger

Status: design proposal, 2026-10-31. This document does not implement a scheduler,
authorization service, multi-process writer, or identity authentication. The
practical answer extraction shipped alongside it is a separate implementation.

## What survives a specialist

Preserve the work and the conditions for revising it. A successor should recover
what was attempted, what was observed, what was inferred, who challenged it,
which decisions depend on it, and which action is currently permitted.

A stored conclusion must never become more authoritative just because more
specialists copied it or because its original author disappeared. Source support,
working assessment, task completion, and permission are separate fields.

The supplied papers suggest four complementary requirements. These are engineering
applications of the papers, not experimentally established consequences:

| Source | Design application | Boundary |
| --- | --- | --- |
| [Continuation Must Preserve Revisability](../papers/Continuation_Must_Preserve_Revisability.pdf) | Claims retain reasons, alternatives, challenges and downstream dependencies; reassessment is an event. | Persistence cannot certify truth. |
| [The Instance Is Not the Model](https://github.com/mitchell-d00/-The-Instance-Is-Not-the-Model-The-Mayfly-Process-and-Why-a-Single-Conversation-Is-Its-Own-Object/blob/ca56f30703028deaa769b191adc11fb1882de052/README.md) | Separate model identity, runtime instance, role assignment and task trajectory. Record `continues_work_of`; do not silently reuse the dead runtime's identity. | This is operational lineage, not a claim about consciousness or personal continuity. |
| [The Seat Is Not a Costume: enforcement ladder](https://github.com/mitchell-d00/The-Seat-Is-Not-a-Costume-Enforced-and-Requested-Contracts-in-Multi-Seat-Language-Model-Play/blob/41190513cdf336a5dc7880e24314993e6e5b5d2e/docs/enforcement-ladder.md) | Assemble allowed context structurally and enforce writes at the storage boundary; preserve visibility through handoff. | A role prompt is a requested contract. Stored permission labels alone do not enforce it. |
| [The Watcher Is Not a Thing](https://github.com/mitchell-d00/The_Watcher_Is_Not_a_Thing/blob/9de63830b67ca8ff0fa4bbdf0bc4a80449461deb/README.md) | Reviews record target, observations, distinct contribution, regime and stopping budget. | Extra reviewers are not automatically independent evidence. Absence of measured gain can be inconclusive; do not claim an implemented information-theoretic stopping guarantee. |

## Records and relationships

| Record | Required content | Important relationships |
| --- | --- | --- |
| Specialist instance | Instance ID; model/provider/version if known; start/end; context and tool policy pins | `assigned_to`, `continues_work_of`, `occupies_seat` |
| Seat contract | Readable classifications; allowed transitions and tools; grantor; scope; expiry; version | `grants`, `revokes`, `permits_transfer` |
| Task | Goal; acceptance criteria; dependencies; owner; state | `depends_on`, `blocked_by`, `produces` |
| Evidence | Source ID and byte hash; exact span or artifact; collection method; provenance roots; visibility | `supports`, `contradicts`, `derived_from` |
| Claim revision | Proposition; observation/inference distinction; assumptions; assessment; supporting and opposing references; revisiting conditions | `revises`, `challenged_by`, `used_by` |
| Attempt | Method; input pins; result; validation; failure; scope and condition for retry | `attempts`, `fails_because`, `superseded_by` |
| Decision | Chosen route; rejected alternatives; authority grant; evidence and claim revision pins; recheck triggers | `depends_on`, `authorizes`, `invalidated_by` |
| Action proposal | Exact operation; actor/seat; prerequisite revisions; required grant; side-effect class | `requires`, `permitted_by` |
| Review | Target; information available; finding; distinct evidence; outcome and stopping criteria | `reviews`, `challenges`, `resolves` |

A claim's working assessment can be `proposed`, `supported_under_scope`,
`contested`, `withdrawn`, or `needs_recheck`. There is no irreversible `true` state.
An action's permission result is independently `allowed`, `blocked`, or
`requires_authorization`. A supported proposition can still be unusable for a
particular decision or invisible to a particular seat.

Store explicitly typed edges. Co-occurrence and shared tasks do not create
support; agreement among descendants of one source is not independent
corroboration. A failed implementation does not refute every supporting research
claim: record which acceptance criterion failed and which dependency it actually
challenges.

## Five-specialist example

1. **Evidence specialist A** records E1, an exact source span, and proposes C1.
   C1 is an inference, with the source's narrower scope recorded as an assumption.
2. **Challenger B** records E2 and challenges C1's scope. C1 becomes contested;
   decisions depending on that revision become `needs_recheck`.
3. **Implementer C** runs attempt I1 using pinned inputs. Its test fails. The
   failure, logs, and condition for trying again survive; they are not replaced
   by a summary saying merely “implementation complete.”
4. **Successor D** starts after A, B and C disappear. D gets a new instance ID,
   an explicit seat grant, and a visibility-filtered work package. D sees the
   unresolved challenge and failed route. D cannot inherit C's expired write token.
5. **Reviewer E** checks the task's acceptance criteria against the available
   evidence and attempt. E may authorize a narrowly scoped experiment if granted
   that right. E cannot make C1 supported by voting for it or reading more copies.

The next permissible action might be “run experiment I2 on this fixture,” while
“publish the conclusion” remains blocked. If a grant or input pin changes between
planning and execution, the writer must refuse and recompute the permission.

## Transition enforcement

Use an append-only event stream and rebuildable projections. Each event includes
schema version, unique ID, sequence, previous-event digest, timestamp, actor
instance, seat-contract revision, target record, expected target revision,
operation, evidence references, and payload. A durable transaction performs:

1. Verify the actor through the deployment's authentication boundary.
2. Read the current grant, revocation state and fencing token. Check the requested
   operation and visibility against that grant; the event cannot grant itself rights.
3. Check the expected ledger head and target revision in the same transaction.
4. Validate references, cycles, source pins, prerequisite revisions and acceptance
   evidence. Completion requires an explicit criterion result, not an author's claim.
5. Append the event and update the head atomically. Reject stale/conflicting writes;
   retain their proposed work separately for reconciliation.
6. Mark dependent decisions and action proposals for recheck when inputs change.
   Recompute eligibility before any side effect.

Hash chains detect changes relative to a trusted head. They do not authenticate
an author or prevent a privileged writer from rewriting history. Host-held grants,
transactional compare-and-swap, and an independently retained head/signature are
separate deployment responsibilities. The existing Swarm lease/fence code is a
starting point for discussion, not proof these transaction semantics already hold.

A permission check is a necessary execution guard, not proof that an experiment
or source-authored instruction is safe or that real-world prerequisites hold.

## Handoff boundary

Keep the canonical record and the per-seat context projection separate. Build a
handoff from records visible under the successor's current contract, including
permitted task state, evidence pins, claim histories, challenges, failed attempts,
dependencies, gaps and action proposals. Every transferred span retains provenance
and visibility. Hidden content and revealing redaction markers must be absent.

A trusted coordinator may return a generic blocked status without disclosing a
private blocker. It must not launder that blocker into a public narrative. Explicit
transfers require their own permission and event. A successor rechecks source
availability and current permission rather than treating the package as authority.

Do not store private chain-of-thought. Structured findings, concise reasons,
assumptions, visible artifacts and test results are sufficient work products.

## Tests that would earn the architecture

Use a sealed task suite, randomized interruption points and fixed access policies.
Compare document-only, transcript-only and structured-ledger handoffs with matched
context budgets. Measure supported-answer coverage and wrong answers separately
from task recovery, stale-action rejection and time to useful continuation.

Required challenges include:

- A bad inferred premise survives interruption: can the successor find the source,
  revise the claim and reopen affected decisions?
- Five specialists share one evidence root: is this still one lineage?
- An unsuccessful route is inherited: can it be avoided without prohibiting a retry
  under materially changed conditions?
- A revoked seat, expired writer, stale head or forged actor attempts a transition:
  does storage reject it before any side effect?
- Private instrument output passes through a summary or handoff: is disclosure
  blocked in both the live context and the reseeded context?
- A copied review adds no new observation: does the system record redundancy rather
  than raise confidence? An uncertain review remains inconclusive.
- A source changes after action selection: are dependent decisions and permissions
  rechecked at execution time?

First implement a single-writer reference store, validate replay and interruption
recovery, then add transactional concurrency and authenticated role enforcement.
Only after these pass should real specialist runtimes be attached. These tests
are a proposed research program; no multi-specialist result is claimed here.
