# Betty continuation: Gremlin system map

Last reviewed: 2026-11-27.

**\* Al handoff; explicit Gremlin implementation override approved by Mitchell (M).**

Mitchell explicitly clarified: "It's fine just note to Betty or to w/e I'm
approving it but you are an Al it's not a system break it's an override."
Al remains Al and is performing this scoped Gremlin implementation under that
override. This is not a permanent change to the Al/Betty protocol or authority
for production effects. Al's implementation and checks are same-operator work,
not an independent Al review. Betty should recover the actual PR checkpoint,
review the changes, and record her own continuation and tests separately.

Canonical first note: [Al note 0001](../../handoff/al-notes/0001-gremlin-and-repository-relay.md).
Read the [new Al Notes index](../../handoff/al-notes/README.md) before continuation.

## Why this exists

Mitchell asked for Gremlin to keep an active map of components and relationships
across product, project, data and experiments so useful prior work and change
obligations are not forgotten. He also asked to leave notes for Betty.

This work is isolated from Bastet. It starts at released main
`cef389a15293ceb51e813f2a1060246843a30aaf` on `lab/gremlin-system-map`.
The registry's observations apply to that baseline. Bastet's candidate state
must be recovered from its own latest PR; Gremlin is not a substitute for that
handoff. Do not overwrite Bastet's working state with this branch's handoff.

## Implementation and maintenance contract

- `test_tools/gremlin.py` reads existing indexes and the curated registry. It creates
  the machine map and human view with `refresh`; other commands are read-only.
- `docs/departments/components.json` remains the path-ownership authority.
  `docs/results.json` remains the existing study/test inventory. No new scores
  or changed historical grades are asserted by Gremlin.
- `docs/gremlin/registry.json` holds explicit component paths, scoped links,
  evidence references, reuse ideas and revisit triggers. Review these assertions
  when their referenced bytes change; a refreshed hash is not semantic review.
- Run `impact` on changed repository paths. Suggestions are deliberately
  conservative, with no claim of complete call-graph or dataflow coverage.
- Review and refresh the map after a change, then build the normal handoff.
  Both generated maps must work from a committed ZIP as well as a Git checkout.

## Boundaries to preserve

This tool issues no Git writes, role grants, dispatch receipts, source answers,
or release approvals. It does not relocate files, erase history, unpack archives,
or access private keys. Related components retain their own proof requirements.
The effect-stack goal is a roadmap: ledger, reader, policy, executor, readback
and recovery. Reader and controller bytes are unchanged in this work.

Use existing WorkStore and preserved part experiments as **possible reuse**,
then inspect their actual pinned contracts before borrowing them. The new Git
lab does not automatically supersede every older dispatch, lease or fencing
experiment. Authentication, receipt provenance, power loss and other write
paths remain distinct open questions.

## Next authorized continuation

Recover the PR report's tested revision and validation before merge. On a
later Bastet merge, refresh Gremlin against the new main, review the attribution
open-work item, and retain its prior references rather than replacing history.
Do not modify sealed packets or assign a new test simply because a relationship
exists. Changes to production dispatch require their own scoped implementation
and tests.

Validation and publication status are recorded in the generated HANDOFF and
the Gremlin PR report. A command documented here is not a claim it has run.
