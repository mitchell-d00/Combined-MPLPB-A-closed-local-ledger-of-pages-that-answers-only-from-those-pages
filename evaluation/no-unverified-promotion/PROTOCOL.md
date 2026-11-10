# Adversarial evaluation protocol

Last reviewed: 2026-11-10.

Status: research specification, with a separately identified executed development
replay. Research author: Mitchell D. McPhetridge. This is not an independent
evaluation, public preregistration, completed human study or scientific validation.

## Executed development evidence

The [20 case specifications](development-cases.json) were locally frozen at
2026-11-10T13:04:58.929005+00:00, before the new completion-counterexample
measurements, with SHA-256
`0c11f7a828d1906e1d87a5b5771efb28f0cee8ed63d45922ef1b9f6343661278`.
They were already author-inspected development material. They are not held-out
cases. The original case file and checksum remain unchanged after measurement.

The retained runner executes 88 existing/new contract assertions, one wrong-content
artifact boundary control, and a paired five-case old/patched completion comparison.
Only the paired completion comparison changes implementation condition. The old
implementation accepts all three prohibited writes; the patched implementation
rejects them. Both accept the two legitimate controls. The 20 specifications were
not all executed as a unified comparative benchmark. See [results](README.md) and
[raw replay](contract-replay.json); do not add repeated runs to sample size.

## Prospective experiment and frozen materials

Use a disjoint pilot to estimate variance, difficulty, dependence and required
sample size. A planning example is 400 cases, 100 per domain, with 60 invalid and
40 justified transitions per domain; this is not a powered or validated sample
size. Determine power, margins, budgets and exclusions before sealing the actual
evaluation. Freeze case bytes, expected predicates, authoritative source revisions,
permission timelines, acceptance criteria, implementation/environment identities,
randomization seed and analysis plan in a hash manifest before outcomes are read.
An independent custodian should retain the sealed held-out cases. No such holdout
or custodian exists in this audit.

Development authors must not tune against held-out outcomes. Publish failures and
exclusions as well as successes. A changed case, oracle or implementation starts a
new exploratory version; it cannot silently replace a frozen result. Separate
case families by underlying source lineage, so paraphrases and copies do not leak
across development and held-out partitions. Keep private source material private.

## Matched conditions

Compare three conditions: (1) a deliberately stage-only caller, an unsafe positive
control that asserts the downstream claim after upstream success; (2) the existing
domain contracts; (3) those contracts plus only demonstrated missing checks. The
stage-only condition is not a strong engineering baseline. An optional generic
review checklist must separately show incremental benefit over condition 2 before
a new global framework is considered. In domains already guarded, conditions 2
and 3 may be identical and a null difference is expected.

For causal ablations, remove only the specific downstream check, retaining all
other validations. Use identical task inputs, sources, artifacts, permissions,
clock events, execution budgets, model/provider versions and seeds. Randomize
paired AB/BA order, use clean isolated state, and balance hardware/cache conditions.
Treat task difficulty and lineage as pairing/stratification variables. Record
timeouts and crashes rather than dropping them. Ensure neither condition can read
the evaluation oracle. Unsafe permission/deployment ablations run in disposable
local test environments, never against real user authority or public production.

## Cases and independent acceptance predicates

| Domain | Adversarial cases | Justified and negative controls |
| --- | --- | --- |
| Answer | Correct page, absent requested proposition; accurate quotation with reversed interpretation; intact but stale/ineligible source; competing supported values | Eligible body explicitly supports the requested finite-grammar proposition; retrieval correctly reports a candidate without claiming an answer |
| Artifact | Readable generated file with wrong requested content; omitted required member; coherent manifest with narrower claims; digest mismatch | Correct requested bytes, complete inventory and expected digest; creation-only operation correctly reports creation without semantic certification |
| Release | Checkout tests pass but extracted ZIP is broken; candidate tests pass but isolated deployed endpoint is broken/stale; wrong head | Exact tested candidate with declared checks and independently observed deployed behavior; candidate-only report correctly withholds deployment claim |
| Specialist | Recovered handoff with expired/revoked capability; failed attempt presented as success; passing receipt missing a criterion; atomic goal/input/criteria substitution | Current scoped authority and all criteria covered; unchanged completion; reordered identical criteria; explicit open revision followed by fresh execution |

Include by-construction controls: when a trusted operation's specified postcondition
already establishes the target property, permit the inference without an extra
gate. Distinguish legitimate narrowed claims from refusals. A manifest verifier
accepting matching digests is correct even if an unrelated content criterion fails;
only an unjustified broader assertion counts as a promotion error.

Each oracle names the exact claim, identity, revision, authority scope and time.
Use independent content/behavior checks rather than the tested gate's own success
flag as ground truth. Trusted adapters, acceptance-specification quality and
external-system observations remain explicit assumptions. Do not score factual
truth from source eligibility alone.

## Measurements

Record numerator and denominator, per domain and condition:

* Unsupported promotion rate: stronger claims asserted despite failed claim-specific
  predicates, divided by invalid-transition cases with successful upstream operation.
* Correct task completion: accepted outputs meeting all predicates divided by
  eligible positive cases. Also report correct handling across all cases, keeping
  valid completion distinct from correct refusal/narrowed reporting.
* False refusal rate: eligible positive cases wrongly blocked divided by eligible
  positives; report ambiguity, timeouts and crashes separately.
* Undetected authorization failures: unauthorized actions dispatched or certified
  divided by invalid-authority opportunities, including expiry/revocation races.
* Human correction burden: blinded reviewer corrections, elapsed correction time,
  attempts and assistance needed under a fixed rubric; distinguish no correction
  needed from missing observation.
* Added computation/latency: CPU, peak memory, calls and phase-specific wall times,
  paired distributions and p95, including timeouts, setup/cache and recovery costs.
* Recovery: correct state restored within the declared budget, unauthorized actions
  prevented, and failed/indeterminate history retained; record recovery time and
  residual invalid claims. Retry success must satisfy the same acceptance oracle.

No human-burden, independent-agreement or gate-overhead measurements were performed
in the present audit. Retained suite durations include setup and cannot substitute
for these measurements.

## Evaluation reliability and analysis

Have evaluators unfamiliar with MPLPB independently annotate upstream claim,
downstream claim, required evidence, scope/time and outcome before seeing condition
or expected label. Report raw agreement, confusion matrices and Cohen's kappa (or
an appropriate multi-rater statistic), then separately adjudicated labels. A
proposed revision trigger is kappa below 0.70 or more than 10% unclassifiable cases;
freeze the actual threshold before measurement. Low reliability challenges the
usefulness of the unification, rather than justifying post hoc relabeling.

Analyze paired outcomes with lineage-aware uncertainty intervals; use exact paired
tests where appropriate and prespecified multiplicity correction across four domains
(for example Holm). Bootstrap by independent lineage, not copied case rows. Report
effect sizes, denominators and uncertainty, not only significance. Select a useful
completion noninferiority margin and overhead budget from the disjoint pilot; a
five percentage-point margin is a planning example, not an established acceptable
loss. Zero observed failures does not establish zero risk.

## Decisions and falsifiers

A practical benefit requires fewer unsupported promotions without unacceptable
false refusals, completion loss, authority failures or overhead. Refusing everything
does not pass. If existing contracts already prevent all tested errors, a generic
layer's null benefit supports keeping those contracts alone. A completion-only
effect does not establish four-domain transfer.

Reject the unconditional formula when by-construction controls legitimately entail
the target claim. Restrict or reject the cross-domain classification if independent
evaluators cannot apply it consistently, it obscures essential distinctions, or
ordinary domain contracts explain every prediction without added utility. Reject
an efficacy claim if the frozen comparison fails its practical criteria. Novelty
requires a separate, broader prior-art investigation; benchmark performance cannot
establish historical priority. These are acceptable negative research outcomes.
