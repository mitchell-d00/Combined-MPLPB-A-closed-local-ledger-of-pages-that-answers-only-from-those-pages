# Current status — November 8, 2026

Last reviewed: 2026-11-08.

Inspected baseline main: `acf7800a5f8320ec29ee957d002eaaba8ed4e816`.
Its Pages build, deployment and postdeployment check completed successfully in
Actions run 41502464401. That evidence belongs to that baseline, not this update.
The [November 2 status](CURRENT_STATUS_2026-11-02.md) remains an unchanged historical
snapshot. Unaffected guides retain their actual earlier review dates.

This update adds a local MCP stdio adapter to the existing full native App.
AI clients can discover authorized collections, ask strict questions, inspect
sources, converse within existing rules and recover sessions. A host-fixed
profile and collection list, disabled acquisition/source management, response
budgets and staged session saves preserve boundaries. No source-language rule,
ledger fact, frozen benchmark question or original label is changed.

The preimplementation baseline passed 18 focused agent/procedure/polarity tests
and the JavaScript API suite. Implementation candidate `94249884391442bc6b05f51f27640249d77d73df` passes
31 authored MCP tests and 45 official SDK checks. Its committed extracted source
ZIP passes 46 combined focused tests, those 45 SDK checks, JavaScript API,
documentation, infrastructure and handoff checks. Exact local evidence is retained under
[evaluation/mcp-agent](../evaluation/mcp-agent/README.md). Later exact-head CI and
publication outcomes belong to their PR/Actions runs. Do not infer deployment
verification from local source tests.

Use [MCP setup](MCP_AGENT.md) for a copyable connection configuration.
[Production readiness](PRODUCTION_READINESS.md) distinguishes feature coverage
within local trusted-operator scope from shared hosting, client-obedience and
independent human-validation gaps. Existing finite source-language limits and
honest ambiguity/refusal remain. The authored 73/73 reference fixture and inspected
pottery results have not become independent general-language validation.

## Optional public helper and zero-cost constraint

The later [free public helper](FREE_PUBLIC_HELPER.md) targets a shared website
address without a paid AI backend. It adds reviewed source building, native/model
labels and recorded proposals versus actual tool results. Local authored evidence
records nine real Chromium checks (including reload recovery), 33 checks against
the real engine and eight Python asset/data tests. Live Phi-4 generation and iPad
behavior are unverified; the test GPU lacks shader-f16. No model is fine-tuned.
Owner-authorized public README material is prepared separately as candidate prose,
not a ready conversation dataset or default source authority. Exact newer source,
archive and publication checks belong to [its evidence directory](../evaluation/free-browser-helper/README.md)
and corresponding Actions runs; prior MCP results above retain their own scope.

## Later model-load failure report

Baseline main `0c8199257e23c4030ab8ccb72cb687d399b9b115` passed its required
873-test regression/ZIP workflows and public Chromium deployment checks in
PR #32 / Pages run 42490859108. The user then reported an iPad model download
reaching 100% before `exit(1)`. Download completion is not successful inference.
The follow-up adds local stage/error/logger diagnostics and export, bounded
cleanup, explicit reload before initialization retry and an AI-unavailable label.
Source evidence rules and the selected model/runtime bytes are unchanged.
See [loader test cases](../tests/browser-model-loader.cjs); test/runtime stubs
are authored development cases, not independent validation or a repaired-device
claim. The physical device root cause remains unresolved pending its report.
