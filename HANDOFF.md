# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `876b4f6c9b4e0a58c9bbf68fc747a339d37ecbce` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `1ddf9304c5f1438cb6481e934834e4a241f88a45e650603794a553252df371b5`.

## Latest user update instructions

Implement the following extensions inside the existing Combined MPLPB codebase. Use its current answer-contract-v1, diagnostic codes, supersession rules, relation-graph families, and work-event model. Do not weaken eligibility gates, hash pins, origin/depth checks, or the rule that assisted/candidate output stays answer_supported=false.
1 Precise refusal diagnostics
Extend the diagnostic table in the answer pipeline. When a query fails, return a specific code instead of a generic abstain. Add or tighten:
exact_field_missing
contradictory_passages_pruned
event_identity_unresolved
correction_scope_unclear
Example shape:
if exact_id_match and not field_support:
    return Answer(kind="abstain", diagnostic="exact_field_missing", answer_supported=False)
2 Exact-field source routing
When the query supplies a pinned record ID or unique field value, route directly to matching eligible pages and skip ranking/diversity discounts. If multiple eligible pages conflict, return a conflict answer with the passages visible rather than pruning them.
3 Distinct event identities
Add an optional event_id / occurrence_id that can be declared on a source page or created only when two or more appearances share an explicit source-declared key. Appearances stay separate evidence records. The event identity is a distinct node and does not inherit answer support from any single appearance.
4 Versioned / time-scoped correction
Extend supersession so a correction page can name:
supersedes pin (predecessor hash)
optional corrects_field
optional valid_from / valid_until
A query as-of a time outside the correction window continues to see the predecessor. Withdrawing the correction does not restore the predecessor.
5 Optional evidence-gated relation exploration
Add a mode that permits relation hops only when every hop is backed by an eligible source quote. Any hop lacking a quote returns as candidate only (answer_supported=false). Keep the existing prohibition on reverse causality and unrestricted multi-hop.
6 Operational receipts stay independent
A completion receipt or external READ/ACK is recorded in the work-event stream but never promotes a claim to supported_answer. Source support still requires a pinned eligible quote. Handoffs continue to carry answer_supported=false and content_truth_verified=false.
7 Operator-burden measurement
Add an optional operator_seconds field on work events (self-reported or measured). Expose it in handoffs and study scoring. Do not use the value for eligibility or answer support.
Keep all new paths inside the existing pipeline, relation_graph, and mplpb_work modules. Preserve current refusal, fencing, and recheck-on-source-change behavior. Add focused tests that demonstrate each diagnostic, the exact-field route, time-scoped correction, and that candidates/receipts remain non-authoritative.

## Implemented scope

- Extend answer-contract-v1 diagnostics and gated exact source/body-field routing without ranking or diversity pruning; keep conflicts and budget omissions explicit.
- Add sealed optional event/occurrence declarations and distinct non-authoritative event nodes; repeated Event-Key requires two appearances. Message IDs alone never become event IDs.
- Extend pinned supersession with optional field and UTC validity windows. Query-local serving views are isolated, do not mutate source bytes, and cannot resurrect withdrawn corrections or override terminal-head write rules.
- Add at most two independently quoted relation hops within existing families; candidates and all exploration/assisted outputs remain unsupported.
- Keep completion/host-declared READ/ACK receipts independent of source support. Add optional finite operator effort on work events, visibility-filtered handoffs and study scoring; never use effort for eligibility.
- Update affected operational documentation/result index while preserving historical/vendor files, frozen source corpora and published result artifacts.

## Validation recorded

- 27 focused extension tests pass, including all four diagnostics, exact-field conflicts and gates, source-change discard, distinct event keys, window boundaries, withdrawn corrections, concurrent query views, quoted-hop candidates, receipt separation and private operator metadata.
- 80 existing/focused coordinator, relation-graph and response checks passed in an earlier integrated run. 59 source/record/supersession/study controls passed before the final concurrency/correction tests. The unchanged public suite passed 52/52 with zero observed false supported bridges.
- Full final extracted-source Python regression, required documentation/handoff checks, actual Linux worker isolation, exact-head archive/WebAssembly/browser CI and postdeployment verification remain to complete.
- Existing strict-first compatibility and extension checks pass together: a deterministic strict-first proof is labelled strict; actual assisted and candidate outputs remain unsupported. The superseded full run was stopped before completion and is not reported as a pass.
- Final field-context control also retains competing later source field mentions outside the initial header instead of selecting a supported header answer. Final extension and strict-first controls pass together (47 tests); exact final-head full CI remains required.
- An extracted pre-final candidate completed 966 tests with one portability import-allowlist failure for the new standard-library contextvars dependency. The allowlist now permits contextvars; no other import restriction was removed. A final guard also prevents historical query views from authorizing current work and requires an explicit field at the provenance gate for scoped sources. Final exact-head full CI remains required.
- The 26 final scoped-extension controls pass with an explicitly pinned fixture clock, so declared correction-window tests do not depend on the year the suite runs.
- Final event identity control keeps declared IDs and generated shared-key nodes in separate namespaces; a matching display label cannot merge their appearances. All 39 scoped and historical-investigation tests pass together, including the new collision control.

## Limitations and blocked checks

- Only explicit initial body-field headers and declared identity keys license exact field answers. This is bounded source extraction, not general semantic interpretation or historical truth certification.
- As-of serving applies only to explicit correction windows. It does not reconstruct arbitrary historical ledger states, infer event identity from resemblance, or license causal composition.
- External READ/ACK is host-declared, not independently attested external-world verification. Operator measurements and reviewer identities remain unattested; no independent human burden/accuracy study has been performed.

## Next steps

- Freeze and test an extracted committed candidate, complete all required exact-head checks, and publish/merge under the existing authorization only after those checks pass.
- Observe production deployment and live Chromium verification; record exact tested revision/tree and actual outcomes on the pull request.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
