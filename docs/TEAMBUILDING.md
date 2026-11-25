# TeamBuilding

Last reviewed: 2026-11-25.

Package role: [research method and reproducible evidence](PACKAGE_GUIDE.md#evidence-and-limits).

## Start with the repository link

Open one AI session for Al and another for Betty in any AI interface that
can open the public repository. Send each session the same link and its role
name. Capitalization is optional.

**First session**

```text
https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages
You are Al.
```

**Second session**

```text
https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages
You are Betty.
```

The role starts from the maintainer's message and this guide. Actual tool and
repository access depends on the session. The maintainer chooses which work
proceeds and authorizes repository actions.

## Al and Betty

| Role | Start here | Owns |
|---|---|---|
| **Al**, outside strategist and advisor | Read the relevant public pin, open-items README, and PR handoff or result receipt. Cite the pin you used. | Review evidence, challenge conclusions, name one falsifiable next test, and draft a prompt the maintainer can send to Betty. Keep the review read-only. |
| **Betty**, inside repository and archive editor | Read `AGENTS.md`, `HANDOFF.md`, and the relevant PR. Verify the local checkout against the public pin before editing. | Carry out the maintainer's authorized changes. Freeze inputs and keys, run and score the comparisons, preserve results and failed attempts, update the archive and handoff, and publish commits or PRs within the authorized scope. |

With just the starter message, use the latest relevant PR's TeamBuilding
handoff and its pinned evidence to recover the state. Al summarizes that
state and proposes one focused check. Betty verifies the active pin, then
continues the work authorized by the maintainer. If several PRs are active,
use the track indicated in the current handoff or the PR the maintainer names.
[Current repository handoff](../HANDOFF.md)

## One cycle

1. The maintainer sends Al the public pin, the open-items list, and the
   relevant result or receipt.
2. Al reports the measured before/after counts and the strongest unresolved
   claim. Propose one named test with exact inputs, positive and withhold
   controls, budgets, and an acceptance condition. Use the pinned record as
   the authority for measured outcomes.
3. Betty freezes the inputs and evaluator key before scoring, runs the
   matched comparison, and publishes the rule or withhold condition, results,
   and new pin. Retain misses, failures, and regressions.
4. Betty posts a **TeamBuilding handoff** in the PR body or in a comment linked
   from it. Address the report to Al and keep its references public.
5. The maintainer gives Al the PR link or pastes Betty’s report. Al reviews it
   and responds with observations and a proposed next check. The maintainer
   pastes Al’s response and their own questions or decisions into Betty’s
   session. Betty uses the maintainer’s direction to continue.
6. After each cycle, Betty leaves the latest report for Al on the PR, with
   the shareable part of Al’s reply, the maintainer’s decision, and the next
   authorized step or stopping point. A fresh Al or Betty can pick up the
   next cycle from that PR using the same starter message.

## Compare several Al sessions

Give each Al the same PR and exact evidence pin so you can compare their
advice. Keep one Betty as the writer for that PR. You can paste several Al
responses into Betty’s session and identify which recommendation to follow.
Betty records material disagreements and the decision you make.

When a session fills its context or you change AI interfaces, start a fresh
session with the same repo link and role name. Use the latest relevant PR
report and check its pin before continuing. If you want to resume a specific
past cycle, send that PR link with the role name.

## Betty’s PR report to Al

Use a heading such as **TeamBuilding handoff for Al** and include:

- **Pinned work** with the exact baseline and candidate commits, plus the archive checksum when relevant.
- **Measured outcomes** with what changed, checks run, before/after counts, and the result or evidence links.
- **Still open** with failures, pending checks, and `NOT_RUN` measurements.
- **Question for Al** with one unresolved decision and where Betty would resume.

When relaying the reply, the maintainer can use two headings, **Al’s response**
and **My direction for Betty**. Betty preserves that distinction in the next PR
report. Include only advice and decisions the maintainer has cleared for
public sharing. Keep evaluator keys with their custodian.

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
does the implementation work. Al can critique the test design or a public result. Record which roles actually worked separately and whether
a reviewer was blinded. Public strategic review alone leaves independent
semantic adjudication unmeasured.
[Thespian proposal and browser workflow](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/93)

## Example

FRUS-Proposition reviewed the same four comparisons and four controls after
FRUS-Boundary. The public result reports discovery separately from proof and
retains the four positive cases as misses. Al can challenge which attribution class to test next using that record.
Betty carries out the selected test and publishes the result.
[FRUS-Proposition public pin](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/1b963aea9ce14d207ec2f6b645912c3a7c98cdd9/evaluation/pole/open-items/frus-proposition/README.md)

## Expanded request for Al

> You are Al. Read the public pin, open-items README, and relevant evidence.
> Separate measured outcomes from hypotheses. Name one falsifiable next test
> and draft a prompt for Betty. Specify what to freeze, positive and withhold
> controls, unchanged limits, before/after measures, acceptance criteria, and
> which measurements remain NOT_RUN.
