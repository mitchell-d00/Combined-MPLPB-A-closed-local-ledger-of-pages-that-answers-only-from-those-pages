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
and the JavaScript API suite. New source tests and an actual official MCP SDK
client check exercise the adapter; exact local evidence is retained under
[evaluation/mcp-agent](../evaluation/mcp-agent/README.md). Later exact-head CI and
publication outcomes belong to their PR/Actions runs. Do not infer deployment
verification from local source tests.

Use [MCP setup](MCP_AGENT.md) for a copyable connection configuration.
[Production readiness](PRODUCTION_READINESS.md) distinguishes feature coverage
within local trusted-operator scope from shared hosting, client-obedience and
independent human-validation gaps. Existing finite source-language limits and
honest ambiguity/refusal remain. The authored 73/73 reference fixture and inspected
pottery results have not become independent general-language validation.
