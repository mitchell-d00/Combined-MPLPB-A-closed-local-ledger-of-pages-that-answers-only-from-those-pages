# Al note 0001: Gremlin and the repository relay

Last reviewed: 2026-11-27.

**\* Al implementation override approved by Mitchell (M); Al remains Al.**

## Authorization and current work

Mitchell proposed Gremlin to keep an active map of components and relationships
across product, project, data and experiments, so useful old work and change
obligations are not forgotten. He asked for notes so Betty could recover the
work and explicitly clarified: "It's fine just note to Betty or to w/e I'm
approving it but you are an Al it's not a system break it's an override."

He then authorized versioned Al notes to replace copy-paste, asked for a
workspace pointer and for this work to be note 0001 with the other notes
directing readers to the new set, and requested push and merge work with Betty
informed. That is the scope of this override. It does not activate production
effects or grant general implementation authority through arbitrary notes.

The implementation base is `cef389a15293ceb51e813f2a1060246843a30aaf`.
Work is isolated on `lab/gremlin-system-map`. Bastet continues in Betty's
separate PR; recover its actual state there. Al's Gremlin implementation and
tests are same-operator work, not independent review.

## Design and boundaries

Gremlin joins existing department ownership and the result/test index, with
curated components, typed directional links, possible reuse, and revisit
conditions. Product, project, data and experiment scopes may overlap. The map
does not move files or replace source, attribution, custody or authority proof.

It checks map drift across tracked bytes and paths, validates source references,
and supplies conservative change-review hints. An evidence path/hash establishes
which bytes were cited, not the truth of a dependency. Historical result strings
retain their original scope and are not new grades or release assertions.

The effect-stack goal remains ledger → reader → policy → executor → readback →
recovery. Admitted, attempted, observed and durably recorded remain distinct.
Git is the tested lab adapter; other effects require their own safeguards and
evidence. Earlier WorkStore/dispatch and preserved part experiments are possible
reuse candidates, not automatically compatible components.

The browser builder recursively includes `tools/`. Gremlin lives under
`test_tools/` to avoid adding a developer map to that bundle. The existing
reader, controller, browser builder and production workflow files are unchanged.

## Betty continuation and acknowledgement

Read [Gremlin usage](../../docs/gremlin/README.md),
[the implementation note](../../docs/gremlin/BETTY-NOTE.md), the registry and
the latest PR report. The PR report and generated HANDOFF carry actual checks,
candidate identity and publication status; this note does not invent a result.

Before applying follow-up advice, acknowledge this note's exact Git revision
in your own report. Record what you read, applied, deferred or rejected and
the resulting source revision and checks. Preserve your Bastet working state.

Refresh Gremlin after source/evidence changes; review changed assertions before
regenerating hashes. Reconcile a later main/Bastet merge instead of copying this
branch's handoff over a newer applied record. Keep private custody outside the
public note set. Effects of repository relay on speed or quality remain unmeasured.
