# Documentation index

[Repository overview](../README.md) · [Repository map](../CONTENTS) · [Live application](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/)

Current entry points and release-status wording reviewed on 2026-10-31 after PRs #21/#22. See [merged capabilities, checks and product gaps](CURRENT_STATUS_2026-10-31.md). The [October 29 review](DOCUMENTATION_AUDIT_2026-10-29.md) remains historical. Dated audits, papers, and experiment reports describe the revisions they measured; their counts and green workflows do not certify another revision.

## Start and operate

| Task | Guide |
|---|---|
| Install source, browser ZIP, or CLI wheel | [Installation](INSTALLATION.md) |
| Use the interface and understand storage modes | [Browser UI](BROWSER_UI.md) |
| Build standalone HTML / runtime requirements | [Browser runtime](BROWSER_RUNTIME.md) |
| Publish the generated runtime | [GitHub Pages](GITHUB_PAGES.md) |
| Preserve captures across compatible updates | [Capture compatibility](BROWSER_CAPTURE_COMPATIBILITY.md) |
| Recover code without rewriting user saves | [Rollback](ROLLBACK.md) |
| Understand decision traces and helper settings | [Monster helper](MONSTER_HELPER.md) |

## Answers, retrieval, and integration

| Contract | Guide |
|---|---|
| General answer contract, local reader, diagnostics and release scope | [Pipeline guide](GENERAL_ANSWER_PIPELINE.md) / [2.1 release candidate](RELEASE_2_1_RC1.md) |
| Supported answers, candidates, gated pages, separate bundles || Deterministic source-evidence relation graph, synthetic users and historical-score retest || Fixed-seed, deduplicated cross-domain evidence smoke tests (Mitchell-Tech testing pattern) | [Diverse question benchmark](../evaluation/relation-graph/DIVERSE_SMOKE.md) |
 [Evidence graph](DETERMINISTIC_EVIDENCE_GRAPH.md) |
 [Page retrieval and answer authority](PAGE_RETRIEVAL.md) |
| Proposed strict conditional and separation evidence, error classes, retained 6/59 score | [Operational evidence](OPERATIONAL_EVIDENCE.md) |
| JavaScript methods, options and error handling | [JavaScript API](../JAVASCRIPT-API.md) |
| Discovery, public snapshot and verbatim relay | [Agent middleware](AGENT_MIDDLEWARE.md) / [agent notes](../llms.txt) |
| Specialist tasks, claims, seat capabilities and handoffs | [Continuity model](SPECIALIST_CONTINUITY.md) / [API and operation](SPECIALIST_CONTINUITY_API.md) |
| Separate lexical source records and provenance checks | [Provenance gate](PROVENANCE_GATE.md) |
| Delivery profiles and clarification | [Delivery and clarification](DELIVERY_AND_CLARIFICATION.md) |
| Successors, withdrawal, restoration and stale derivations | [Supersession policy](SUPERSESSION_POLICY.md) |
| Constrained procedures, draft tags, off-the-record boundaries | [Procedural constraints](PROCEDURAL_CONSTRAINTS.md) |
| Building collections and bounded policy answers | [User-built collections](USER_BUILT_COLLECTIONS.md) |
| Independent collections, capture/import and clearing | [Exploration collections](EXPLORATION_COLLECTIONS.md) |
| Optional hosted general-web crawling | [Crawler setup](../crawler/README.md) |

## Conversation and references

| Topic | Guide |
|---|---|
| Generated description of the software's capabilities | [System guide](SYSTEM_GUIDE.md) — generated from `tools/self_knowledge.py`; edit the generator before regenerating |
| Chat commands, relation rules and saved state | [Chat workflow](CHAT_WORKFLOW.md) |
| Modes, grounded topics, discourse and construction | [Grounded chat](GROUNDED_CHAT.md) |
| Tutor, topic offers and clickable links | [Guided chat](GUIDED_CHAT.md) |
| User declarations, corrections, recall and adaptation | [Context index](CONTEXT_INDEX.md) |
| Request classes and finite conversation grammar | [Natural conversation](NATURAL_CONVERSATION.md) / [structured requests](STRUCTURED_CHAT.md) |
| Pre-execution planning, skills and evidence boundaries | [Conversation architecture](CONVERSATION_ARCHITECTURE.md) |
| Authored phrase graph | [Chat language graph](CHAT_LANGUAGE_GRAPH.md) |
| Deterministic brainstorming/replay | [Deterministic generation](DETERMINISTIC_GENERATION.md) |
| Explicit shelves/books and scoped queries | [Library routing](LIBRARY_ROUTING.md) |
| Creator/self-reference corpus history | [System and creator reference](SYSTEM_SELF.md) |
| Separate research-note attribution | [General chat references](GENERAL_CHAT_REFERENCES.md) |
| Offline resources, exact revisions and licenses | [Resources](../resources/README.md) |

Feature guides can contain dated validation sections. Those sections report their original runs; they are not fresh measurements for the latest code. Historical walkthroughs within them remain identifiable as such.

## Develop, evaluate, and release

- [Developer quickstart](DEVELOPER_QUICKSTART.md): architecture and terminal demonstration.
- [Browser testing runbook](BROWSER_TESTING_FOR_AGENTS.md): real hosted baseline versus candidate tests.
- [ZIP-first release testing](ZIP_FIRST_RELEASE_TESTING.md): package/test the exact candidate before merge.
- [Release evidence and settings](RELEASE_EVIDENCE.md): artifact identity, required checks, and dated ruleset observations.
- [Production threat model](PRODUCTION_THREAT_MODEL.md): trust boundaries and unresolved production concerns.
- [Evaluation protocol](../evaluation/README.md), [chat evaluation](CHAT_EVALUATION.md), and [independent conversation trial](INDEPENDENT_CONVERSATION_TRIAL.md): distinguish development fixtures from independent evidence.
- [Synthetic researcher pilot](../evaluation/researcher-pilot/README.md): six full native research journeys, literal-note recovery repair, candidate Chromium journey, and explicit product-readiness gaps.

## Dated reports and historical documents

| Material | Status and route |
|---|---|
| Current implementation/status review | [October 31 status](CURRENT_STATUS_2026-10-31.md): local reader, researcher pilot, exact-head checks and remaining gaps. |
| Latest fix chronology | [Root FIXLOG](../FIXLOG.md), including October 31 general-reader and researcher-pilot updates. |
| Full-system audit | [2026-10-21 audit](SYSTEM_AUDIT_2026-10-21.md); measured its named revisions before the later retrieval repair. |
| Answer reliability development review | [2026-10-13 review](ANSWER_RELIABILITY.md), with dated follow-ups. |
| October 19 repairs | [Integrity](INTEGRITY_AUDIT_FIX_2026-10-19.md), [literal coverage](LITERAL_COVERAGE_FIX_2026-10-19.md), and [new collection chat](NEW_MPLPB_CHAT_FIX_2026-10-19.md). |
| Earlier feature/recovery reports | [Supersession fix](SUPERSESSION_FIX.md), [wiki capture repair](WIKI_CAPTURE_FIX.md), [deterministic mind delivery](DETERMINISTIC_MIND.md), [publication history](PUBLISH_AND_ROLLBACK.md), and [October 19 recovery checkpoint](RELEASE_MONSTER_ROLLBACK.md). Their commit IDs and counts are historical, not universal rollback targets. |
| Original Combined MPLPB v3 paper | [Markdown](Combined_MPLPB.md), [text](Combined_MPLPB.txt), [PDF](Combined_MPLPB.pdf), and [paper-era FIXLOG](FIXLOG.md). Preserved October 7 specification/results, not current application instructions. |
| Supplied papers/manuscripts | [Papers and byte manifest](../papers/README.md), [upload review](UPLOAD_REVIEW.md), and [background sources](sources/README.md). Original attribution and claims remain intact. |
| Earlier docs and code | [Past documentation](past-documentation/README.md), [superseded papers](superseded/), [patch experiment](patch-canned/README.md), and [five retained implementations](../parts/README.md). |

New code or documentation must not silently update frozen results, rewrite source seals/capture pins, or turn historical observations into current certification. Generated standalone HTML is a separate build artifact; check its footer and embedded bytes when verifying deployment.
