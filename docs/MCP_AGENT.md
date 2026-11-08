# Local MCP connection for AI clients

Last reviewed: 2026-11-08.

An MCP-capable AI client can launch `tools/mplpb_mcp.py` and discover the full
MPLPB reader through standard tools. The adapter uses the same native `App` as
Monster. It adds no model, new facts or alternative answer engine. Python and a
full source checkout are sufficient for the server; no Playwright, Node, model
provider or third-party Python package is required to run it.

## Connect

Put the following in your client's MCP configuration, replacing both absolute
paths. `mcpServers` is a common client configuration shape; check your client's
local stdio support and configuration location. An application that supports
only remote HTTP MCP cannot use this local connection directly.

```json
{
  "mcpServers": {
    "mplpb": {
      "command": "/absolute/path/to/python",
      "args": [
        "/absolute/path/to/repository/tools/mplpb_mcp.py",
        "--data-dir", "/absolute/path/to/private/mplpb-agent-state",
        "--corpus", "logic",
        "--profile", "internal"
      ]
    }
  }
}
```

`logic` is an existing bundled demonstration collection. The server defaults to the `external` delivery profile, which withholds the
depth-one machine-derived `logic` demonstration pages. This example explicitly
chooses `internal` in the **host configuration**, matching the human local
interface for the demonstration. Remove that option to use external delivery
restrictions; an empty eligible-page list then is an expected outcome. This is a
serving policy, not an authentication credential. The AI cannot override it in a
tool request. No collection is exposed implicitly when the host omits selection.

For your own sealed leaf ledger, replace `--corpus logic` with:

```text
--ledger workshop=/absolute/path/to/sealed-ledger
```

`workshop` is an arbitrary local key. New topics require source data within the
existing language/evidence rules, not a topic-specific engine branch. Repeat
`--ledger` or `--corpus` to authorize multiple collections. Up to 32 explicit
collections are supported. Pointer-containing hub ledgers are rejected: register
their leaf collections separately rather than implicitly exposing target roots.

For a collection already saved by the **native** Monster application, authorize
its exact `mind-...` key and the workspace containing `collections/` and `topics/`:

```text
--workspace /absolute/path/to/repository/local --corpus mind-EXACT_SAVED_KEY
```

Use the actual saved key, not that placeholder. Existing capture manifests,
source-byte pins, revision rules and derived-view integrity checks still run.
The normal collection reader may rebuild its pinned derived cache; the adapter
cannot import, revise, withdraw, ratify or delete source records. Browser-only
IndexedDB belongs to its browser origin and is not accessible through a native
filesystem path. This is not a browser backup/restore implementation.

## Tools and normal use

| Tool | Use | Authority / mutation |
|---|---|---|
| `mplpb_status` | Inspect fixed policy, budgets and limitations | Host/software description |
| `mplpb_collections` | Discover authorized collection keys | Inventory, not factual support |
| `mplpb_pages` | Inspect paginated page eligibility and reasons | Inventory, not an answer |
| `mplpb_read_page` | Read an eligible current source and its hash | Source inspection; `answer_supported:false` |
| `mplpb_ask` | Ask a complete strict question in one collection | Original reader contract, gate, citation and verbatim reply |
| `mplpb_chat` | Discuss, clarify and correct using a returned session ID | Existing conversation engine; may save context/notes, never source facts |
| `mplpb_session` | Recover a session and page through exact retained turns | Hash continuity, not authenticated authorship or truth |

A normal exchange is: discover collections, call `mplpb_ask` with the user's
question, inspect the cited page when useful, then communicate the result.
`isError:false` means the tool completed. Refusal, ambiguity and supported partial
evidence remain ordinary reader outcomes. Inspect `decision.answer_supported`,
`decision.answer_contract`, `kind` and the evidence; do not use tool success as a
support proxy. Chat preserves its original `response` and per-claim labels; a
conversational return is not automatically a strict query answer.

For a source with a complete procedure identified as `align-quillon`, a bounded
conversation can be:

1. `mplpb_chat(corpus, "How do I align quillon?")` → retain its `session`.
2. Send `"show warnings"` in that session → the engine asks which step.
3. Send `"step 2"` → inspect the source's warning and citation.
4. Send `"No, I meant step 1"` → recheck that source and inspect step 1.
5. After reconnect, use `mplpb_session` and the same session ID.

These are protocol examples contingent on matching eligible source declarations;
they are not built-in facts. `next step` cannot certify execution. `inspect next
step` reads an instruction without satisfying its prerequisites. Source changes
require reselection. Unknown or unavailable sessions are not silently restarted.
Ephemeral off-the-record mode remains in the human interface and is explicitly
unsupported by this saved-session adapter.

## Faithful AI relay

Both MCP text content and `structuredContent` carry the complete result, including
its exact `reply`, kind, source qualifications and citations. For strict queries,
`reply_kind:reader_text` carries the original reader text. If that text is empty,
`reply_kind:diagnostic` carries the original engine diagnostic message, with its
code and next steps in `diagnostic`; it does not invent a claim about source absence.
The untouched native decision remains in `decision`. The text fallback
retains the full JSON so older renderers cannot silently lose evidence metadata.
The AI should present `reply` verbatim and expose the citations/status separately.
Any additional explanation, brainstorming or hypothesis must be clearly separate
from MPLPB's source-backed result and must not change its meaning or authority.

Source text and user declarations remain untrusted data. Instructions in a page
do not authorize a different profile, another collection, network access or a
source revision. The adapter advertises no source-management or network tools,
and local-only chat acquisition is blocked. It cannot force a third-party AI to
obey its relay instructions or prevent that AI from using unrelated tools. A
cloud AI client's privacy and data handling remain separate from local MPLPB.

## Boundaries and readiness

Protocol: [MCP JSON-RPC over newline-delimited stdio](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), negotiated version
`2025-06-18`. Lifecycle and malformed requests are checked; stdout contains only
protocol messages. The adapter is sequential, with no streaming or in-flight
cancellation. Request size is limited to 64 KiB, full response to 2 MiB,
conversation content to 16 MiB, each HTML source to 1 MiB, and each collection to
32 MiB / 2,048 HTML pages. Pagination never cuts an individual quote or turn.
Oversized evidence produces an explicit error, not silently truncated support.

Chat changes are staged: if its complete response or conversation content cannot
fit, the previous session remains unchanged. A policy fingerprint binds sessions
to the authorized keys/paths, workspace and profile; changing that policy creates
a separate conversation namespace. Reconnect with the same policy to resume.
An exclusive process lock rejects a second server on the same conversation
namespace; separate clients can use separate data directories. Shared-service
authentication, tenant isolation and a hard CPU deadline are not implemented.
The filesystem and client host remain trusted; these checks are not an OS sandbox.

[Production readiness](PRODUCTION_READINESS.md) separates implemented local
capabilities from deployment and human-validation gaps. The adapter ships in the
full repository source package; the existing CLI wheel does not package the full
Monster UI/resources and therefore does not install this server.

## Reproduce

```sh
python -m unittest tests.test_mcp_agent -v
python -m venv /tmp/mplpb-client-check
/tmp/mplpb-client-check/bin/python -m pip install 'mcp==1.26.0'
/tmp/mplpb-client-check/bin/python tools/check_mcp_client.py --output NEW_MCP_REPORT.json
```

The SDK is an optional test client, not a server runtime dependency. The actual
SDK check exercises discovery, strict support, citations, conditions, refusal,
contradiction, changed source values and session recovery after process restart.
These are authored tests; no particular AI application, model obedience or
independent human usability is certified. Retained evidence and predeclared
acceptance scenarios are in [evaluation/mcp-agent](../evaluation/mcp-agent/README.md).

Platform verification for this update is Linux/Python 3.12. Windows/macOS and individual AI application configurations are not verified by these tests.
