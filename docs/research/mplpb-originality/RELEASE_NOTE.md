# Research and completion-integrity release note

Last reviewed: 2026-11-10.

Research author: **Mitchell D. McPhetridge**. This release presents MPLPB as an
**attributable engineering contribution and technical case study**. Its research
and experimental evaluation are **still being tested**.

**For MPLPB, the particular combination may be distinctive, but it is unproven
as world-first.** The present evidence does not establish a new universal law
or confirm the architecture's worldwide priority. Established general verification
principles and the originality of a particular implementation are separate questions.

## Included work

The release combines the [claim-boundary audit](../../../evaluation/no-unverified-promotion/README.md)
and the [mechanism-level originality reassessment](README.md), including source
references, development chronology, prior-art comparisons and a prospective
adversarial protocol. The scope and date qualifications in those reports remain
part of the findings. Older papers, archived implementations and frozen evaluation
records retain their original bytes and scope.

The specialist coordinator includes the completion-integrity correction developed
in PR #38. Previously, a completion write could reuse a passing receipt while
dropping an unmet criterion, changing the task goal, or replacing task inputs.
Completion now preserves the preceding goal, review budget, criterion set and
dependency revisions. To change that contract, revise the task while open and
obtain fresh execution evidence. Reordering identical criteria remains allowed.

The [API guide](../../SPECIALIST_CONTINUITY_API.md) documents this behavior.
This is a native specialist-work fix; it does not add a browser-hosted agent team
or change source-supported answer authority.

## Evidence and continuing tests

The retained development cases report invalid completions accepted **3/3 before,
0/3 after**, with valid controls accepted **2/2 before and after**. These are
authored regression cases, not universal effectiveness or independent replication.
The original logs, implementation identities and cases remain preserved.

Candidate regression, ZIP, WebAssembly and browser checks establish only their
tested software scope. Their exact revision/run evidence is separate from a
successful deployment, and neither proves novelty. The independently authored,
held-out cross-domain comparison, evaluator agreement, human correction burden
and gate-overhead measurements remain future work under the [protocol](../../../evaluation/no-unverified-promotion/PROTOCOL.md).

This note records the intended release content and research status. Merge,
deployment and postdeployment outcomes must be recorded from the actual completed
workflow runs rather than inferred from this document.
