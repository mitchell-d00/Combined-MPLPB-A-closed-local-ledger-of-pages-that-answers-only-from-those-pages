# TeamBuilding

Last reviewed: 2026-11-25.

Package role: [research method and reproducible evidence](PACKAGE_GUIDE.md#evidence-and-limits).

Betty and Al name work steps in the TeamBuilding pipeline. Use your normal
assistant capabilities and follow the maintainer’s direction. Each step
operates with the tools and permissions available to that session.

## Start with the repository link

Open Betty first. After Betty leaves a report, open a separate chat for Al
in any AI interface that can open the public repository. Send each session
the same repository link and its role name. Capitalization is optional.

**First session**

```text
Run Betty https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages
```

**Second session**

```text
Run Al https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages
```

The maintainer chooses which work proceeds and authorizes repository
actions. Older “You are Betty” and “You are Al” starters select the same
work steps. Use the task-based starters above for fresh chats.

## Al and Betty work steps

| Role | Start here | Owns |
|---|---|---|
| **Al**, outside strategist and advisor | Read the repository deeply first, including the relevant implementation and tests. Then read Betty’s handoff and the frozen evidence. Cite the pin you used. | Review evidence, challenge conclusions, name one falsifiable next test, and draft a prompt the maintainer can send to Betty. Keep the review read-only. |
| **Betty**, inside repository and archive editor | Read the repository deeply first. Then read the last Betty report on the live PR and verify the local checkout against its current head before editing. | Carry out the maintainer's authorized changes. Freeze inputs and keys, run and score the comparisons, preserve results and failed attempts, update the archive and handoff, and publish commits or PRs within the authorized scope. |

With only the starter message, both roles follow the
[full-package inspection directions](../README.md#directions-for-an-ai-to-inspect-the-full-combined-mplpb-package)
before reading the last Betty report on the live PR. Verify its head and
last applied state and begin there. With just the repository link, open the
newest PR by creation time across all states, including merged and closed.
A PR link from the maintainer overrides that selection. If its report is
missing or stale, read the handoff at the actual PR head.
[Current Betty report for Al](../HANDOFF.md#betty-report-for-al)

## Read the pipeline over HTTP

An assistant with public web access can complete Al’s review by reading
the repository, the live PR, and the pinned evidence. The public JSON
manifest returns the workflow and archive information over an ordinary
HTTP GET. The JavaScript and terminal commands offer the same metadata
to clients that have those runtimes.
[Public manifest](https://raw.githubusercontent.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/HEAD/.well-known/mplpb.json)

## API commands and source archives

The [agent API manifest](../.well-known/mplpb.json) exposes both roles, the
live PR discovery URL and the tested source archive catalog. A plain repo
link exposes the same entry points in its README. In the app, call
`await window.MPLPB.betty()` or `await window.MPLPB.al()`. From a checkout
with Node.js, run either command with the repo or Pages URL.

```sh
node tools/mplpb_agent_bridge.mjs "$REPO_URL" --betty
node tools/mplpb_agent_bridge.mjs "$REPO_URL" --al
```

Both terminal commands fetch the newest PR and return its current body,
head, and a handoff link pinned to that head. A specific GitHub PR URL selects
that PR. The local browser API returns the live discovery URL as metadata
for clients that want to fetch it. The discovery methods run no corpus queries. The archive catalog gives each tested
source commit, SHA-256 and GitHub source-snapshot link. For the exact tested
ZIP, use the rebuild command and compare its digest. The snapshot downloads
may have different ZIP bytes.

## One cycle

At startup, both Betty and Al inspect the repository, then read the last
Betty report on the live PR. That report is the starting state.

1. **Betty calls Al.** Betty leaves a current report for Al in `HANDOFF.md`
   on every push. When there is a PR, Betty puts the report in its body or
   a comment linked from it. The maintainer starts Betty first, then opens Al
   in a separate chat with the repository link and role name.
2. **Al reads the repository, then the report.** Inspect the relevant
   implementation, tests, and evidence before reading the Betty report.
   Verify its pin and distinguish measured results from hypotheses.
3. **Al calls Betty.** Judge Betty’s reported results against the pinned
   evidence and draft a ready-to-send prompt for one falsifiable next test. Include exact inputs, positive and withhold controls, budgets,
   and an acceptance condition. Return the response to the maintainer.
4. **The maintainer relays.** Copy **Al’s response** from Al’s chat and
   paste it with **My direction for Betty** into Betty’s chat.
5. **Betty tests and updates the same PR.** For an authorized evaluation, freeze the inputs
   and evaluator key before scoring, run the matched comparison, and record
   the rule, outcomes, and archive details. Retain misses, failures, and
   regressions. Leave the shareable part of Al’s reply, the maintainer’s
   decision, and the next authorized step in the PR. Repeat from that
   applied state. When the maintainer pauses, the last report stays in
   place. A fresh Al or Betty resumes by reading the repository and that
   same report.

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

The live PR report is the last state Betty actually applied. Update the
current report in place after each push, completed check or maintainer
decision. A fresh Betty or Al reads the repository, opens the live PR, and
compares the report’s pin with the current head. If the pins differ, use
`HANDOFF.md` at the current head and reconcile the report before continuing.

Use a heading such as **Betty report for Al** and include:

- **Current PR head** on its own line, followed by the last applied change, baseline, and archive checksum when relevant.
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
bridges is an acceptance condition for the frozen comparison. In the active
PR report, record the before/after counts, the rule or explicit withhold, the
observed false-support count, the new commit, and the tested ZIP SHA-256.
Preserve the previously closed cases and the original labels. Independent historical
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

> Run the Al review step for this repository. Read the repository, then the
> live Betty report, public pin, open-items README, and relevant evidence.
> Separate measured outcomes from hypotheses. Name one falsifiable next test
> and draft a prompt for Betty. Specify what to freeze, positive and withhold
> controls, unchanged limits, before/after measures, acceptance criteria, and
> which measurements remain NOT_RUN.
