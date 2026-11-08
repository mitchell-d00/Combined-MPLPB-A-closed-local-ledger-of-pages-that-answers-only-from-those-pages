# Intended scope, completeness and production readiness

Last reviewed: 2026-11-08.

MPLPB is a local research system with bounded source-language rules. Its local
MCP adapter now gives compatible AI clients a standard route to the existing
reader and conversation engine. That closes an integration gap; it does not
establish unrestricted language understanding or shared-service readiness.

| Intended capability | Implemented boundary | Evidence / remaining gap |
|---|---|---|
| Humans inspect and ask about local pages | Native/browser UI, supported query contract, source inspection and revisions | Existing native, JavaScript, WebAssembly and Chromium suites. Historical source-language failures remain. |
| AI discovers and asks through standard tools | Local stdio MCP; explicitly authorized collections and host-fixed profile | MCP unit/real-subprocess tests and official Python SDK client; third-party AI application usability is not measured. |
| AI inspects evidence and uncertainty | Full original reader decisions, citations, gate, partial/ambiguity/refusal labels | Shared App parity and altered/withdrawn/contradictory-source tests; tool success is not answer support. |
| User corrects an interpretation or continues a procedure | Native conversation rules; bounded step clarification, corrections and persisted selectors | Actual SDK process restart and focused tests; arbitrary references and arbitrary prose procedures remain unsupported. |
| User adds a new topic | Existing source authoring/import paths; explicit MCP registration of leaf ledgers/native saved collections | Unfamiliar synthetic entities and native collection capture-integrity test; no independent collection-builder trial. |
| AI writes or acquires sources | Deliberately absent from this MCP connection | Use existing explicit human source-management routes. User context is not automatically authenticated or ratified. |
| Reliable local operation | Bounded request/output/source/storage sizes, error recovery, policy-scoped sessions, staged chat saves and an exclusive namespace process lock | No hard CPU timeout, OS sandbox or complete disaster-recovery product. One trusted operator/process is the declared scope. |
| An internet-facing multi-user service | Outside the declared supported deployment | Authentication, tenant isolation, quotas, egress controls, secrets, monitored operations and incident/recovery drills require deployment-specific engineering and evidence. |
| Independently validated answer quality | Not established | Pottery is inspected development data; 73/73 is authored lab-only source coverage. Live assisted-reader calibration and independent human semantic/usability review remain outstanding. |

For local MCP use, connection setup, discoverability, faithful result transport,
source inspection and bounded conversational recovery are implemented and tested.
A user must still configure a capable client and authorize the intended data.
Client-side obedience to relay instructions is a separate trust boundary: MCP
cannot prevent a model from inventing text or invoking another service.

Before widening scope, define the deployment and release criteria first. Shared
hosting needs the controls in the [threat model](PRODUCTION_THREAT_MODEL.md), not
just a passing local test suite. Consequential automated decisions require their
own source review and evaluation; a seal or test count does not authenticate truth.

See [setup and enforced MCP rules](MCP_AGENT.md), [current status](CURRENT_STATUS_2026-11-08.md)
and [result/test index](RESULTS_AND_TESTS.md). Source tests, an extracted-ZIP test,
a candidate browser check and a postdeployment check are distinct evidence.

## Free public helper update

The [public browser helper](FREE_PUBLIC_HELPER.md) adds reviewed collection/source
building and a visible execution trace using the existing page API. The optional
pretrained model runs on compatible visitor devices; no shared AI server is
configured. Nine actual Chromium workflow checks, 33 real-engine contract checks
and eight Python asset/data checks pass locally. These do not validate live model
generation: the test environment lacks required shader-f16, and iPad/Safari neural
behavior is unverified. Free hosting/CDN limits and device memory remain material.
No fine-tuning or automatic visitor-chat training has run. This is an experimental
public interface, not a shared inference service or production-quality model claim.

## Reported iPad initialization failure

An actual user reported `exit(1)` after a 100% download. The model has not been
shown working on that device. A separate bounded loader report now preserves
available runtime evidence, distinguishes progress from readiness, and attempts
cleanup before requiring a page reload for another initialization. Authored
simulated-runtime cases validate this handling; the real pinned WebLLM constructor
and unload API are checked without weights. These are not live inference tests
or proof of the user's hardware failure cause. See [failure recovery](FREE_PUBLIC_HELPER.md#when-the-model-fails-to-initialize).
