# 2.1.0rc1 capability and release scope

The 2.1.0rc1 source on `main` adds the general answer contract, opt-in local reader,
explicit abstention diagnostics and a packaged human-scored evaluation workflow.
It preserves default strict behavior and frozen corpus/core bytes. The previous
2.0.0 results remain historical; release-candidate code pins are recorded separately.

| Capability | Native CLI | Local web host | Standalone WebAssembly |
| --- | --- | --- | --- |
| Default bounded strict reader | Available | Available | Available |
| General answer diagnostics/contract | Available | Available | Available |
| Candidate inspection / gated pages | Available | Available | Available |
| Assisted local-model reading | Explicit configured opt-in | Explicit configured opt-in | Unavailable; option disabled |
| Model downloads or hosted inference | Not performed | Not performed | Not performed |
| Specialist transactional work store | Native coordinator | Dedicated authenticated work-only host | Unavailable |
| Evaluation runner and human scoring | Packaged `mplpb-evaluate` | Operator workflow | Unavailable |
| Synthetic researcher pilot | Source-checkout HTTP/CLI/fresh-process runner | Tested service behavior | One scripted Chromium UI journey |
| Investigation overview / portable user backup | Not implemented as product features | Not implemented as product features | Not implemented as product features |

Assisted mode is experimental, with `answer_supported:false` even when exact
citations and model review pass. Default strict queries require no model and do
not contact the configured adapter. No installed model was available in the build
environment: loopback protocol and pipeline fixtures establish interface behavior,
not live semantic accuracy or improved general coverage.

The [general reader report](../evaluation/general-reader/README.md) records tests,
package checks and release blockers. Existing strict pottery coverage remains
3/32, 2/19 and 1/8; no increase is attributed to untested model inference.

Local validation covers Python regressions, explicit opt-in/no-call behavior,
quoted evidence and computed offsets, malformed/prompt-injection-shaped outputs,
wrong-subject/condition review rejection, source/model drift, local-only connection
validation, exact human-judgment pins, partial-answer scoring, rendering/escaping
and installation outside the checkout. Those premerge requirements passed for
[PR #21](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/21).
The subsequent [PR #22](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/22)
also passed regression, extracted-ZIP, pinned WebAssembly and actual Chromium
checks at `3f160ffacb6545e30a0c2752359c2bf15d0dafee`, then merged as
`bfba98786e54b45d7a18a9396517b61726ed97b7`. Its local full suite passed
764 tests; its synthetic pilot passed 108 native workflow checks and eight
browser checks. The [current status](CURRENT_STATUS_2026-10-31.md) separates
these results from postdeployment verification and independent answer accuracy.

Do not claim hosted-browser assisted inference, OS/provider isolation, prompt
injection immunity, independent reviewer/model errors or unrestricted natural
language correctness. A local service is trusted infrastructure; it must have cloud
forwarding disabled and honor its context configuration. A citation proves a text
location, not the correctness of an interpretation.

Deploy/rollback uses the existing [release workflow](RELEASE_EVIDENCE.md) and
[rollback guide](ROLLBACK.md). No source pages or saved work records are migrated
by enabling the reader. Stop selecting Assisted or remove native reader flags to
return to strict-only operation. Existing legacy core imports and finite-grammar
APIs remain compatibility paths; the public Ask pipeline provides the new contract.
