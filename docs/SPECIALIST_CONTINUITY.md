# Specialist continuity: durable work and guarded handoffs

Last reviewed: 2026-11-16. See [current status and result-to-test index](CURRENT_STATUS_2026-11-02.md). Dates and numeric results in historical validation sections retain their original scope; this review is not a rerun or independent certification.

Status: **implemented local coordinator**, 2026-10-31, in `mplpb_work`. It provides
transactional work history, host-issued seat capabilities, revision and fencing
checks, filtered handoffs, and guarded host-adapter dispatch. Use the
[API and operation guide](SPECIALIST_CONTINUITY_API.md) or run
`python -m tools.demo_specialist_continuity`. AI providers and their operating-system
sandboxes remain external to this coordinator. Model/provider metadata is declared;
capability possession does not authenticate a human or attest a provider runtime.

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

The coordinator independently recomputes source support on every snapshot,
handoff, dependency check and dispatch. `supported_under_scope` in a submitted
payload is a requested assessment; it becomes effective only after this check.
The versioned `work-source-status-v1` checker supports unconditional statements
of the form `Subject is/remains [not] available/discontinued/active/inactive/enabled/disabled`.
It requires a complete matching source sentence in a directly pinned evidence
quote, compares the exact subject and polarity, and checks the full cited source
body for opposing status statements. Support requires the full body to stay within
this grammar; surrounding prose may contain unresolved scope. Conditions, assumptions, other language and
claim-only dependency chains yield `needs_recheck`; an explicit opposing status
yields `contested`. Neither a support vote nor challenge resolution bypasses this
check. Dependent decisions, actions and completions then require rechecking.
Existing ledger events remain intact and are re-evaluated without migration.
Each visible claim includes a `support_check` version and effective status.

This finite check does not establish general semantic entailment or factual truth,
and does not search unrelated or uncited pages for contradictions. New languages
and inference rules require explicit checker extensions and adversarial tests.
Unsupported inferences remain proposals rather than executable premises.

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

1. **Evidence specialist A** records the configuration statement and a matching
   scoped claim. An implementation fixture fails; its receipt and retry conditions persist.
2. A later component-wide inference contradicts the full cited source. The
   coordinator marks it `contested` before **Challenger B** adds a review.
3. **Implementer C** cannot execute an action using that contested revision.
4. **Successor D** recovers the claim, failed attempt and unresolved challenge in a
   fresh process with a new grant; the predecessor credential no longer works.
5. **Reviewer E** revises the claim to the directly quoted component statement and
   resolves the challenge. Fresh source checks permit a new scoped action.

The next permissible action might be “run experiment I2 on this fixture,” while
“publish the conclusion” remains blocked. If a grant or input pin changes between
planning and execution, the writer must refuse and recompute the permission.

## Transition enforcement

The implementation uses an append-only event stream and rebuildable projections. Each event includes
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
an author or prevent a privileged writer from rewriting history. Host-issued grants and compare-and-swap now run inside SQLite `BEGIN IMMEDIATE`
transactions. Every operation verifies the chain and reconstructs state; there is
no separately trusted mutable projection. A global host head and seat-specific view
heads reject stale writes without exposing private event counts. An independently
retained checkpoint remains a deployment responsibility. The Swarm fencing
principle is implemented transactionally here, without modifying the preserved
Swarm implementation.

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

## Validation and remaining research

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

The local implementation now has adversarial development tests for replay, fresh
process recovery, concurrent thread/process writers, stale heads, source changes,
revocation, fencing, historical visibility, explicit transfer, failed routes,
review budgets, guarded dispatch and receipt-backed completion. The
[five-instance fixture report](../evaluation/specialist-continuity/README.md) records
its observed behavior. These are deterministic development fixtures, not measured
performance of five AI providers. The sealed comparison and information-theoretic
experiments above remain research work.

The current coordinator is native Python/SQLite with a CLI and a dedicated local
HTTP API. It does not add a hosted browser work UI or invoke AI providers. A
registered adapter is host-controlled code with a versioned operation name and
known effect class. Unknown execution outcomes remain indeterminate until a host
operator reconciles them. External systems still need idempotency and suitable
isolation; a permission check cannot make an external side effect atomic with a
local database transaction.

The [November 10 contract audit](../evaluation/no-unverified-promotion/README.md)
adds a narrow completion correction: a done write cannot simultaneously change
the goal, review budget, criterion set or input dependencies covered by an old
receipt. Explicit open revision and fresh execution remain supported. Its paired
regressions are development evidence, not a cross-domain efficacy study.

> Update 2026-11-16: The [public 52-case evidence suite](PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.

Update 2026-11-16: See [scoped evidence extensions](SCOPED_EVIDENCE_EXTENSIONS.md) for exact source-field routing, correction windows, distinct event nodes, bounded quoted exploration, and non-authoritative receipt/operator-effort fields. These extensions preserve source eligibility and candidate/assisted support boundaries.
