# Formal candidate: claim-specific promotion obligations

Last reviewed: 2026-11-10.

Research author: Mitchell D. McPhetridge. Status: a proposed engineering
specification distilled from the pinned source audit, not an established new term,
universal law, proof of source truth or independently validated scientific result.
This document proposes notation; it does not add a runtime framework.

## 1. Why the initial formula needs qualification

`S_n ⇏ V_(n+1)` is a useful warning only after the propositions and assumptions
are specified. An operation can include the downstream validity property in its
postcondition. Then success under the verified preconditions can legitimately
establish that property. A blanket prohibition would reject valid programs and
proofs by construction.

Also, authority, meaning, current eligibility and byte identity are not necessarily
ordered degrees of one scalar validity. They can be incomparable properties.
Some can be checked in parallel, and legitimate evidence can establish a target
claim without executing a particular earlier stage. A linear stage index is
therefore shorthand, not a general model of the system.

Let `C0` be the exact proposition established by an operation and `C1` the target
claim. Let `K` include its declared contract and trust assumptions. The proposed
restriction is:

```text
If K does not entail (C0 → C1), do not assert C1 on C0 alone.

Accept(C1, object, revision, scope, actor, time)
    only when the obligations specific to that claim are discharged
    by evidence bound to the required object/revision/scope and authority time.
```

If the postcondition of the trusted operation already entails `C1` in `K`, it may
discharge the obligation itself. No redundant independent gate or external judge
is automatically required. This is the by-construction exception, not a loophole.

An implementation of a predicate named `verify` is not a proof that its predicate
is sound. Evidence policies and their trust boundaries must be specified and
tested independently of a success label. The specification cannot eliminate the
need to trust a host adapter, an expected digest, a contract definition or an
adjudicator within a declared scope.

## 2. What a promotion decision must identify

An audit should identify the following, whether represented by existing records
or human-readable documentation. This is a checklist, not a proposed global schema.

1. The actual successful operation and its established postcondition.
2. The requested target claim, rather than an ambiguous word such as verified.
3. The subject/artifact, source identity, revision and relevant context.
4. Required positive evidence and disqualifying contradictions, stale inputs or
   permission changes.
5. The current actor and scope if the target includes authorization.
6. The checking mechanism and assumptions under which its result is meaningful.
7. An explicit outcome: accepted under scope, refused, ambiguous, stale,
   indeterminate or not evaluated, with an appropriate reason.
8. The basis for reopening the outcome when its dependencies change.

Evidence about a successful historical operation should remain historical evidence
even when it no longer supports a current action. Do not rewrite the initial
operation as failed just because the stronger claim is not licensed. Conversely,
the absence of current support does not establish a proposition's negation.

## 3. Domain obligations already represented in MPLPB

| Target | Evidence required within the declared contract | What remains unestablished |
| --- | --- | --- |
| Supported answer | Eligible current body support for the complete question in the finite grammar; conflicts and delivery constraints honored | General entailment, source truth, unknown constructions |
| Verified artifact property | The named integrity, structure, behavior or content predicate for the identified artifact; trusted expected inputs | Other artifact properties, or authenticity when producer and manifest can both be replaced |
| Verified deployed behavior | A live observation of the intended public environment and identity at the claimed scope/time | All future behavior, all devices, whole-byte identity without an explicit digest check |
| Authorized action | Current scoped grant, fence, prerequisites, task revision, permitted tool/effect and fresh checks at dispatch | External side-effect atomicity, real-world safety, retrospective undo after revocation |
| Accepted task completion | Passing host receipts for all unchanged acceptance criteria and task input contract, with current dependency state | Host honesty, unencoded real-world requirements, truth of arbitrary specialist inferences |

The local implementation correction closes a mismatch in the last row. It does
not alter the other rows' authority or create a new global rule engine.

## 4. Permitted and impermissible boundary cases

Permitted cases include a trusted constructor returning a value whose proved
postcondition is precisely the target; recording a passed attempt without marking
the entire task done; inspecting a retrieved page without asserting answer
support; accepting all receipt-covered unchanged criteria; reordering the same
criterion set; and deliberately revising an open task followed by fresh execution.

Impermissible cases include interpreting an accurate citation as semantic proof,
calling a consistent manifest a general content validator, transferring a candidate
test pass to a different revision, inheriting an expired capability, converting
copied reviews into independent observations, or consuming old acceptance evidence
while replacing the task contract in the same completion write.

A failed attempt can legitimately be evidence about which route to avoid. It need
not become a success prerequisite. A source revision can retire current eligibility
without destroying historical provenance. Permission to act can be current while
the proposition motivating the action remains contested; the coordinator must
check the relevant separate fields. These cases prevent collapsing all statuses
into one monotonically increasing success scale.

## 5. Scope, exceptions and costs

This is a discipline for claims and API transitions within named contracts. It
does not assert that every inference needs a new experiment, that every step needs
human approval, or that every uncertainty requires refusal. Harmless display
updates and semantics-preserving criterion reordering need no new completion
evidence. Claims inside a proved/trusted postcondition already have a basis.

Checks can produce false refusals, latency and complexity. The October 13 audit's
historical coverage loss is a material warning: preventing wrong returns while
refusing all answerable cases does not establish a useful system. Duplicate guard
layers need a demonstrated gap and comparative benefit. A trusted but mistaken
host adapter or an incorrect acceptance specification can still yield bad results.

## 6. Falsifiers and revision conditions

Reject the unconditional formula when an upstream contract already entails the
downstream property; such counterexamples exist by construction. Restrict or
abandon the broader unification if independent evaluators cannot consistently
distinguish its cases, if the supposed domains require incompatible classifications
that erase their important differences, or if a simpler existing contract account
explains every prediction with no incremental utility from the synthesis.

Reject a claimed practical benefit if matched, frozen evaluation shows no reduction
in unsupported promotions, unacceptable completion/false-refusal losses, increased
authorization errors, or overhead beyond a preregistered budget. Finding a gate
does not establish that it is effective; passing authored tests does not establish
held-out transfer. A measured null benefit over existing guards supports retaining
the existing contracts without a new framework.

The present audit supports scoped engineering non-entailment and one local fix.
It does not establish universal applicability, scientific novelty, independent
evaluator reliability or a four-domain causal effect. See [the protocol](PROTOCOL.md)
for how those claims could be tested rather than assumed.
