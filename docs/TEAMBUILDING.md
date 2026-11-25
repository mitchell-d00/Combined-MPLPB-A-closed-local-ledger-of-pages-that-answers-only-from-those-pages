# TeamBuilding

Last reviewed: 2026-11-25.

Package role: [research method and reproducible evidence](PACKAGE_GUIDE.md#evidence-and-limits).

TeamBuilding is a workflow for getting outside strategic input and criticism
on a pinned software project. The maintainer and the implementing agent own
the checkout, implementation, test execution, scoring, commits, and publication.
The outside agent reads the public record, challenges the evidence, and writes
a focused prompt for the implementing agent. The maintainer chooses what proceeds.

## One cycle

1. Give the outside agent the public commit, the current open-items README,
   and the relevant result or test receipt.
2. Have the outside agent summarize the measured before/after outcomes and
   outstanding questions. Keep observed results, hypotheses, and proposed work
   explicit. A private conversation can suggest a check. The pinned record is
   the authority for an outcome.
3. Ask for one named test and a ready-to-send implementation prompt. State the
   failure to distinguish, exact inputs to freeze, positive and withhold
   controls, budgets, and the decision the result should enable.
4. The implementing agent freezes the inputs and evaluator key before scoring,
   runs the matched comparison, and publishes the rule or withhold condition,
   results, and new pin. Retain misses, failures, and regressions.
5. Bring the published evidence back to the outside agent for review. End the
   cycle when the evidence answers the question at the declared resolution.
   Record unexecuted measurements as `NOT_RUN`.

## Evidence and review roles

For Pole, measure discovery separately from Strict Ask. A bridge requires
exact witnesses from eligible originals, unique resolution, chronological
order where applicable, and the declared budget checks. Zero false-supported
bridges is an acceptance condition for the frozen comparison. Preserve the
previously closed cases and the original labels. Independent historical
accuracy and native OOCC stay `NOT_RUN` until the corresponding evaluations
actually run.

Thespian covers separation within a test run. The asker freezes the cases,
the answerer receives the inputs, and the evaluator scores the retained
outputs with a separately held key. TeamBuilding covers who advises and who
does the implementation work. The outside agent can critique the test design
or a public result. Record which roles actually worked separately and whether
a reviewer was blinded. Public strategic review alone leaves independent
semantic adjudication unmeasured.
[Thespian proposal and browser workflow](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/93)

## Example

FRUS-Proposition reviewed the same four comparisons and four controls after
FRUS-Boundary. The public result reports discovery separately from proof and
retains the four positive cases as misses. An outside checker can challenge
which attribution class to test next using that record. The implementing
agent carries out the selected test and publishes the result.
[FRUS-Proposition public pin](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/1b963aea9ce14d207ec2f6b645912c3a7c98cdd9/evaluation/pole/open-items/frus-proposition/README.md)

## Copyable request for an outside agent

> Read the specified public pin, open-items README, and relevant evidence.
> Summarize the observed baseline counts and identify the strongest unresolved
> claim. Name one falsifiable next test and draft a prompt for the implementing
> agent. Specify the frozen inputs, positive and withhold controls, unchanged
> limits, before/after measures, and criteria for keeping or rejecting a change.
> Identify measurements that must remain NOT_RUN. Return your analysis and
> prompt. The maintainer and implementing agent will run, score, and publish
> the test.
