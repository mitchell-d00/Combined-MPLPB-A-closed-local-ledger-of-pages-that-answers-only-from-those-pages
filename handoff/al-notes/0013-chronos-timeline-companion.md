# Al note 0013 — Chronos, Gremlin's timeline companion

Last reviewed: 2026-11-28.

**Bounded lab implementation requested by Mitchell.** Reviewed main `6942df4670196405797114cbe25317577c3118e1`, the applied [FRUS baseline], HANDOFF, [Test Index], [results inventory], [open-work dispositions], and [Gremlin's contract]. Betty's active relationship diagnosis is [PR #134] at `aee8312b97cab51d6e81ca1d20fa42696c57fbd3`. Keep its branch and grades separate. Recheck actual main before freezing the Chronos sprint.

## One reference system, two timelines

Gremlin remains the component and dependency map. Chronos adds dated events and typed links using the same stable IDs. The results inventory and Test Index remain authoritative for experiment evidence, OPEN_WORK for current disposition, and existing source and review records for source or reviewer status. Chronos stores references to those authorities and records dated observations or changes. A new disposition or repair adds an event and may link back to the older one. Original failures, unrun stages, and evidence at their original pins remain navigable. [Open-work dispositions] · [Gremlin's contract]

| Timeline | Content and authority |
| --- | --- |
| Project history | Proposals, authorized scope references, freezes, attempts, failures, interruptions, repairs, merges, deployments, and changed dispositions. Use pinned note, test, PR, Git and release receipts. Preserve the existing research timeline's author-declared, archive and Git date distinctions. |
| Source-reported history | Dated assertions and documented relationships tied to literal appearances, revisions, witnesses, and attribution. Unresolved identities and proposed underlying events have their own IDs and basis. A typed cross-link can identify the project event that imported, examined, challenged or corrected an interpretation. The documentary event time and the later review time retain separate roles. |

## Minimal schema and reuse

Use one small tracked catalog of project events, public source references and typed links, plus one generated metadata index. Event rows need `id, revision_id, timeline, event_kind, subjects, times, evidence_refs, assessment`. Use stable Gremlin component IDs, result or experiment IDs, and source record IDs with revision hashes. A source appearance adds a stable locator scoped to its source revision and coordinates. A proposed event ID is distinct from appearance IDs. Link rows need `from, to, kind, basis, evidence_status, evidence_refs`. Evidence references identify their authority and version, such as commit plus path and digest, run/PR receipt, or source ID plus revision, coordinate system and span. A curated annotation identifies its author, annotation revision and basis. Current eligibility and proof status come from their existing authorities.

Represent each time as `literal, role, precision, timezone, basis_ref`, with optional bounded normalized value and an explicit unknown or conflicting status. Preserve separate roles for reported event, document creation, publication, acquisition, execution, Git author/committer metadata, merge, deployment, and review. Unknown timezone and missing calendar components stay unknown. Retain contradictory declarations. For revision ancestry, use pinned Git parent links or ancestry checks. Missing history yields unknown; an unrelated revision remains distinct. A stable display order never establishes causation, underlying chronology, invention, or priority. [Existing project timeline]

- Reuse `test_tools.gremlin` and its map schema for IDs, declared relationships, indexed tests, and open-work links. Reuse the existing handoff inventory and archive receipts for publication verification.
- For FRUS use the pinned source-map and its XML/page coordinates, plus `historical_evidence.extract`, `historical_verifier.verification_snapshot` and `verify_observations` for bounded source declarations. Use the existing documentary or Strict Ask proof when making a checked source assertion. Coordinate fidelity and a verified declaration have their own status. Publication or transmission metadata carries its literal role.
- Reuse `event_candidates.inspect_events` for occurrence and explicit-key candidates, and investigation's chronology and `source_mapping.relationship_graph` for bounded discovery and relationship suggestions. Keep explicit-key clusters as candidates and preserve every appearance and changed-body flag. Matching names, dates, and subjects confer no identity. Reuse the historical-review record scheme to link accountable reviews and challenges with their existing scope and exposure. Use separate evidence statuses for candidate, checked source assertion, challenged interpretation and independently assessed conclusion. A checked source assertion establishes source support only. [Source verification] · [Investigation] · [Event candidates] · [Source mapping] · [Historical review]

## Read interfaces and freshness

Provide local typed reads over explicit snapshots. The method names here describe the interface and may be CLI subcommands. No background watcher or dispatch.

| Query | Bounded response |
| --- | --- |
| Gremlin → Chronos `component_timeline(component_id, timeline?, cursor?, limit?)` | Dated events, experiment/evidence references and relevant linked dispositions. Use Gremlin's canonical component ID. |
| Chronos → Gremlin `event_context(event_id, cursor?, limit?)` | From the event's pinned component and experiment references, return declared dependencies, tests, evidence links and relevant open work. Preserve relationship basis and unresolved IDs. |
| Chronos `event(event_id, profile?, question_scope?)` | Return a typed event and links, including source appearance → project examination/import/challenge/correction. Source details require the original question or declared scope, existing delivery profile and rechecked evidence. |

Every response carries schema, snapshot IDs for both maps as applicable, checked evidence pins, coverage and limits, unresolved references, and freshness. “No matches in covered inputs,” “truncated,” and “source unavailable” are distinct. Use bounded pages (proposed maximum 64 results), a total expansion budget, a visited set keyed by typed reference and snapshot, and at most one peer lookup per request. Peer lookups use a shallow, non-expanding read. A cycle or exhausted limit is a reportable result. Stale project pins return an explicit stale or unresolved status. For source-detail reads, gather current eligibility for the selected profile and original scope, check exact source revision and witness, and recheck the source snapshot after reading. Changed, withdrawn, restricted or conflicting dependencies keep an explicit status. Withhold ineligible bytes and derived quotes or details reachable through either map, including error and nested results.

Use explicit `refresh` and `check`. Build against a pinned input manifest. Gremlin may fingerprint the Chronos schema, code and tracked catalog, with Chronos generated outputs excluded from Gremlin content hashes and evidence inputs. Chronos then pins the checked Gremlin snapshot in one direction. Neither generated artifact fingerprints itself, and the handoff inventory runs last. The generated public index holds references and permitted metadata. Live source-detail eligibility applies even when a previously built snapshot exists. Repeat generation against identical inputs must produce identical bytes.

## Frozen first sprint and acceptance

Use separate fixtures for authentic FRUS observations and synthetic controls. Freeze baseline, catalog/input hashes, expected fields and evidence statuses, exact limits and expected stops before implementation.

1. Demonstrate project events for [PR #130] → [PR #131] → [PR #132], including the original blocker and `NOT_RUN` stages, the independently scoped native result, and the separately frozen disposable Git integration. Preserve ancestry and receipt times as different bases.
2. Demonstrate source observations on a small public FRUS subset. Include usable literal/role dates, at least one checked declaration and one candidate or unresolved relationship. Link an appearance to the project import or examination event. PR #134's supplied-evidence diagnosis produced zero native relationship certificates; carrying the references into Chronos gives them no stronger status. Demonstrate a component → experiment → project event → source evidence round trip. [FRUS baseline] · [PR #134]

| Frozen contrast | Required result |
| --- | --- |
| Repeat generation and reciprocal lookup | Identical output bytes and snapshot pins on unchanged inputs; each direction resolves to the same canonical IDs, evidence and dispositions. |
| Unknown, partial and contradictory dates | Preserve originals, roles, precision and timezone as known. No invented date parts or silently chosen conflicting date. |
| Reversed commit timestamps | Known parent order wins for revision ancestry. Timestamps retain their literal values and basis. |
| Duplicate appearances and ambiguous identity | Preserve all appearances, a typed possible-link basis and distinct event IDs. Changed bodies remain reviewable. |
| Unsupported relation, challenged interpretation, assessed conclusion | No promotion from a candidate, map link or quotation. A review reference carries its actual scope. Neither map grants authority. |
| Withdrawn, changed, restricted or conflicting dependency | Report the observed state. Source eligibility and pinned coordinates are checked before returning any detail. No leaked old quote or derived restricted detail. |
| Missing reference, stale map and cyclic cross-query | Report explicit unresolved/stale states and the query limit. Bound traversal with both visited references and a budget. |
| Appended repair or disposition | Keep previous failures and unrun stages queryable. Resolve the current disposition from its canonical record. |

**Betty assignment.** Acknowledge this note at its publication commit, recheck main and #134, and use a separate Chronos lab PR. Implement only the two small timelines, metadata index, typed read bridge and freshness checks. Run the frozen acceptance grid, existing Gremlin/handoff checks and applicable source-verifier and investigation preservation checks. Keep separate original and rerun outputs. Verify remote byte readback and exact-head checks for the recoverable checkpoint. Qualifying lab merges follow Mitchell's existing authorization. Reader proof, production dispatch and controller behavior stay unchanged. The sprint establishes navigation and freshness across the frozen examples. Historical accuracy, event identity, priority and general relationship proof retain their existing evidence requirements.

Al inspected live records and maintained code for this design. Chronos was not implemented or tested in this review.

[PR #130]: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/130
[PR #131]: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/131
[PR #132]: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/132
[PR #134]: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/134
[FRUS baseline]: ../../evaluation/archival-inspection/frus-correspondence-01/RESULTS.md
[Test Index]: ../../docs/TEST_INDEX.md
[results inventory]: ../../docs/results.json
[open-work dispositions]: ../../docs/OPEN_WORK.md
[Gremlin's contract]: ../../docs/gremlin/README.md
[Existing project timeline]: ../../docs/research/mplpb-originality/TIMELINE.md
[Source verification]: ../../mplpb_work/historical_verifier.py
[Investigation]: ../../mplpb_work/investigation.py
[Event candidates]: ../../mplpb_work/event_candidates.py
[Source mapping]: ../../mplpb_work/source_mapping.py
[Historical review]: ../../docs/HISTORICAL_TRUTH_RULES.md
