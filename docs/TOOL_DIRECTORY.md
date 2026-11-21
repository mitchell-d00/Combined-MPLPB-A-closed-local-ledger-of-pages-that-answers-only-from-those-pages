# MPLPB tool directory

Last reviewed: 2026-11-21.

Start with the job you want to do. The guides include examples and setup for each tool.

[Try MPLPB](#try-mplpb) · [Build a collection](#build-a-collection) · [Ask and investigate](#ask-and-investigate) · [Manage work and records](#manage-work-and-records) · [Connect and extend](#connect-and-extend) · [Research and maintenance](#research-and-maintenance)

## Try MPLPB

| I want to… | Start here | Choose this when… |
|---|---|---|
| Try one question | [Browser quickstart](../README.md#try-it-in-30-seconds) | You want a bundled example and a refusal you can see for yourself. |
| Use my own files from a terminal | [Compact native download and CLI example](../README.md#try-it-from-the-terminal) | You have Python and want an offline install with the ledger, reader, sorter and work tools. |
| Run the full app locally | [Desktop and standalone setup](INSTALLATION.md) | You want the interface on your own device. Choose the desktop filesystem store or a browser-origin store. |

## Build a collection

| I want to… | Tool and example | Result |
|---|---|---|
| Start with a few documents | [Create a collection and import](EXPLORATION_COLLECTIONS.md) | The browser imports supplied text or supported captures into the selected collection. Open **Explore** to inspect the imported records. |
| Organize a folder of rough text | [Offline sorter](PREPROCESSING_SORTER.md) · [Sorter v2](SORTER_V2.md) | Source-anchored observations and optional proposed links. Your raw text remains the original. |
| Find similar wording or review possible links | [Sorter review options](SORTER_REVIEW_OPTIONS.md) · [Candidate review workspace](CANDIDATE_REVIEW_WORKSPACE.md) · [Semantic triage](SEMANTIC_TRIAGE.md) | Suggestions and review flags with source context. Open the eligible original before drawing a conclusion. |
| Build a ledger from reviewed drafts | [Collection automation](COLLECTION_AUTOMATION.md) · [Classing](CLASSING.md) · [Ledger generations](LEDGER_GENERATIONS.md) | Validated, sealed pages. Clear drafts with unique declared identifiers can be accepted automatically. |
| Add, correct or retire one page | [Ledger operations](PACKAGE_GUIDE.md#ledger-and-eligibility) · [Source policy](USER_BUILT_COLLECTIONS.md) · [Scoped corrections](SCOPED_EVIDENCE_EXTENSIONS.md) | Native commands retain revision history and recheck which pages are eligible. |
| Maintain an existing ledger | [Native setup and commands](INSTALLATION.md#wheel-and-command-line-tools) · [Ledger and delivery](PACKAGE_GUIDE.md#ledger-and-eligibility) | Native commands list records, verify page seals, and show revisions. Run `mplpb-combined --help` for maintenance commands. |
| Bring in web material | [Wikipedia collection tools](EXPLORATION_COLLECTIONS.md) · [Optional web crawler](../crawler/README.md) | Captures retain provenance. General web crawling needs a configured backend and explicit network use. |

## Ask and investigate

| I want to… | Tool and example | Result |
|---|---|---|
| Ask for a supported answer | **Ask** in the app or [`mplpb-combined ask`](../README.md#try-it-from-the-terminal) | A cited answer, partial evidence, a conflict or an unresolved result. The result can explain what evidence is missing. |
| Find or read related pages | **Explore**, **Inspect**, or [`candidates`, `gate`, and gated retrieval](PAGE_RETRIEVAL.md) | Matching pages or an eligible owner page. Read the answer result separately when you need verified support. |
| Follow a declared relationship across sources | [`investigate` and Adaptive Search](HISTORICAL_EXPERT_PATH.md) | A bounded investigation that checks declared links and retains unresolved hops. |
| Compare wording, dates or accounts | [`reconstruct` and checked documentary assertions](HISTORICAL_RECONSTRUCTION_ENGINE.md) · [Event identity and co-reference](D4_EVENT_IDENTITY_COREFERENCE.md) | Cited documentary observations and explicit unresolved obligations. |
| Inspect a source procedure or its prerequisites | [Procedural constraints](PROCEDURAL_CONSTRAINTS.md) · [Operational evidence](OPERATIONAL_EVIDENCE.md) | Source-supported steps where available, with prerequisites and unresolved parts shown. |
| Assemble several checked reports | [`article` dossiers](DOCUMENTARY_ARTICLES.md) | A research snapshot with citations, conflicts, proposed links and open questions. |
| Discuss a topic or use local reference material | [Chat and Serious mode](CHAT_WORKFLOW.md) · [Dictionary, thesaurus and library](LIBRARY_ROUTING.md) · [Guided chat](GUIDED_CHAT.md) | Conversation and reference results carry their own labels. Serious mode uses the collections you load. |

## Manage work and records

| I want to… | Tool and example | Result |
|---|---|---|
| Check what can be shown or used | [Source restrictions and provenance](PROVENANCE_GATE.md) · [Delivery profiles](DELIVERY_AND_CLARIFICATION.md) | Eligibility and delivery checks under the selected profile. |
| Inspect changes or recover my work | [Revision tree and storage](BROWSER_UI.md#network-and-persistence) · [Recovery instructions](ROLLBACK.md) | Revision history and recovery options for the selected store. Keep copies of important source files and work databases. |
| Track tasks, claims, attempts and handoffs | [Specialist work CLI and API](SPECIALIST_CONTINUITY_API.md) | Local work history and scoped permissions. A covered executor requires current authorization and supporting evidence. |

## Connect and extend

| I want to… | Tool and example | Setup |
|---|---|---|
| Call the browser engine from JavaScript | [`window.MPLPB` API](../JAVASCRIPT-API.md) · [Browser agent bridge](AGENT_MIDDLEWARE.md) | An open MPLPB app page or caller-controlled browser. |
| Connect an AI client to a local ledger | [Local MCP setup](MCP_AGENT.md) | Native checkout, stdio-capable client and host-selected collections and profile. |
| Add model-assisted help | [Optional browser helper](FREE_PUBLIC_HELPER.md) · [Local reader](GENERAL_ANSWER_PIPELINE.md) · [Native narrator](LOCAL_NARRATOR.md) | Separate model setup. Look for strict source support independently of generated wording. |

## Research and maintenance

- **Check the evidence.** Find the measured results, exact revisions and reproduction commands in the [results and tests index](RESULTS_AND_TESTS.md) and [benchmark dashboard](benchmarks/dashboard.md). The [B-Tests repository](https://github.com/mitchell-d00/B-Tests) holds cross-system test work and its stated scope.
- **Find earlier work.** Use [preserved documentation](../PAST_DOCUMENTATION.md), the [evaluation archive](../evaluation/), and the [lab reference corpus](../reference_corpus/README.md).
- **Work on the implementation.** Use the [package map](PACKAGE_GUIDE.md#package-map), [developer quickstart](DEVELOPER_QUICKSTART.md), [repository map](../CONTENTS), and [release checks](ZIP_FIRST_RELEASE_TESTING.md).
- **Find a specific guide.** The [documentation index](README.md#all-current-guides-and-coordination-entry-points) lists the full set of guides.
