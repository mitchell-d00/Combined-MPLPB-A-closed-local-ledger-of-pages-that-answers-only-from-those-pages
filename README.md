# Combined MPLPB

A closed local ledger of pages, with supported answers, inspectable provenance, and deterministic conversation. Each page declares its identity, scope, status, sealed hash, origin, and lineage. Source-backed answers require eligible body evidence under a finite grammar; missing support refuses and competing support remains ambiguous.

**[Open the live application](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/)** · [Documentation index](docs/README.md) · [Installation](docs/INSTALLATION.md) · [JavaScript API](JAVASCRIPT-API.md)

The hosted application runs the Python engine locally through WebAssembly. No model, AI account, API key, or Python server is needed to use the standalone runtime. Saved visitor collections and conversations stay in that browser's storage. Explicit or enabled automatic source acquisition uses the network; the optional general-web crawler has separate service requirements.

## Choose how to run it

| Mode | Start | Requirements and storage |
|---|---|---|
| Live site | Open the link above. | A current browser with WebAssembly, workers, WebCrypto, IndexedDB, local storage, and Web Locks. Saves belong to that browser origin. |
| Standalone download | Extract `mplpb-monster-browser.zip` and open `MPLPB_Browser.html`. | Complete runtime works offline after download. Some browsers restrict local-file storage; static HTTPS hosting is an alternative. |
| Desktop source | Extract/clone this repository and run `python3 launch.py`. Windows: `Launch_MPLPB.bat`; Mac/Linux: `sh Launch_MPLPB.sh`. | Python 3.8+; no application dependencies. Keep the local server running at <http://127.0.0.1:8766>. Saves are local files. |
| Installed CLI | `python -m pip install .`, then `mplpb-combined --help`. | Installs the ledger/answer CLI, not the full chat application. Use the source or browser ZIP for chat. |

The root `index.html` is the desktop entry point; opening that source file alone does not run Python. The [standalone builder](docs/BROWSER_RUNTIME.md) produces `dist/MPLPB_Browser.html`; CI uses `dist/index.html` for Pages. The [Pages workflow](docs/GITHUB_PAGES.md) deploys `dist/` through **GitHub Actions**, rather than publishing the repository root.

Downloadable packages are attached to successful main-branch **Publish MPLPB browser runtime** Actions runs as `mplpb-monster`. See [package contents and verification](docs/INSTALLATION.md).

## Understand the four source interfaces

| Interface | What a successful result means | Answer authority |
|---|---|---|
| Supported answer: `mplpb-combined ask`, `python -m mplpb_answers ask`, `MPLPB.query()` / default `relay()` | Eligible body statements satisfy the bounded question grammar; result `return`. | Source-supported within that finite contract; a hash does not certify truth. |
| Candidate inspection: `mplpb-combined candidates`, legacy `python -m mplpb_combined ask`, `query(...,{mode:'candidates'})` | The lexical reader selected candidate material. | Inspection only; candidate selection does not establish an answer. |
| Gated page retrieval: Python `mplpb_combined.retrieval.retrieve`, `MPLPB.retrieve()` | Exactly one selected owner also passes the provenance gate; result `retrieved`. | Always `answer_supported:false`. Returns a page to inspect, not a supported answer. |
| Separate source bundles: CLI `gate` / provenance bench | All eligible lexical matches are retained separately; result `source_bundle`. | Co-occurrence or lexical coverage does not establish the requested relationship. |

`ok:true` in the JavaScript API means the call completed. Inspect decision kinds, authority, support, citations, and exclusions before presenting evidence. Page retrieval does not follow hub pointers or choose a different owner after a gate rejection. [Retrieval contracts and examples](docs/PAGE_RETRIEVAL.md).

The supported CLI distribution is **2.0.0**; the legacy core reports **1.0.0**. These are distinct from the JavaScript API's **1.0.0**, retrieval contract `gated-page-retrieval-v1`, paper versions, and content-derived browser build IDs. Compatibility does not mean legacy source bytes never change: the October 27 retrieval repair changed lexical matching while retaining its separate authority.

## Try the source checkout

```sh
# Supported answer from explicitly marked synthetic relation facts:
python3 -m mplpb_answers ask examples/chat-logic "What is Dungeons and Dragons?"

# Inspect lexical page ownership without asserting body support:
python3 -m mplpb_answers candidates examples/studio "how fast should I heat raw clay on its first firing"

# Keep independently matched game and budget material separate:
python3 -m mplpb_combined gate examples/provenance-gate/separate "1974 dungeons and dragons budget" --json
```

For supported/candidate CLI queries, exit codes are 0 (return), 2 (ambiguous), and 3 (not in corpus). The gate uses 0 (source bundle) and 3 (not in corpus). The synthetic D&D fixture and a general budgeting page do not establish a historical D&D budget.

Create your own ledger with the existing writing commands:

```sh
mkdir notes
python3 -m mplpb_combined write notes --prefix NOTE --title "Bisque schedule" \
  --scope "Bisque firing schedule" --when-to-use "first firing; raw clay" \
  --body "Climb 100 C per hour to 600 C."
python3 -m mplpb_combined revise notes NOTE-0001 --body "Climb 80 C per hour to 600 C."
python3 -m mplpb_combined history notes NOTE-0001
python3 -m mplpb_combined validate notes
```

These demonstrate record management, not certified kiln instructions. Changes create successors; derivations pin their basis and increment depth. Retired or stale bases do not silently become valid again. See [supersession policy](docs/SUPERSESSION_POLICY.md), [delivery restrictions](docs/DELIVERY_AND_CLARIFICATION.md), and [the original format paper](docs/Combined_MPLPB.md).

## Use the interface

- **Explore / Ask / Revision tree:** inspect pages and eligibility, submit supported questions, and review retained source history. Source inspection and decision traces remain distinct from supported answers.
- **Chat / Serious:** deterministic conversation, source-bound topic discussion, saved context, explicit collection loading, and library routing. Chat clears active Serious scope but retains saved pages; outside-scope references remain labeled.
- **Off-the-record free chat:** ephemeral conversation, with no saved transcript or source acquisition from its messages. Leaving the mode discards that session; separate source-management controls retain their explicit behavior.
- **Build and search collections:** named collections, Wikipedia capture, permitted URL/pasted-text import, and explicit source management. General-web crawling needs a separately configured backend.
- **Monster helper / Reason Mode:** presentation settings and visible decision traces; they do not change evidence rules or permissions.

Try `guide me`, `show my MPLPB`, `What can you do?`, `browse library`, `define dog`, or `brainstorm lantern gardens`. API network access is opt-in on each call; the visible UI has its own automatic Wikipedia setting. Source passages, user declarations, dictionary entries, research notes, calculations, and imagined ideas carry different authority. Finite grammar does not provide unrestricted language understanding.

Read [interface controls](docs/BROWSER_UI.md), [chat workflow](docs/CHAT_WORKFLOW.md), [the generated system guide](docs/SYSTEM_GUIDE.md), and [all feature guides](docs/README.md).

## Local resources and saves

The bundle includes Open English WordNet 2025 (128,009 entries and 107,558 synsets), 111 CMU Link Grammar data/reference files, and 23 selected Simple English Wikipedia captures. The grammar parser is not running, and the encyclopedia selection is not all of Wikipedia. Resources retain [licenses, exact revisions, and attribution](resources/README.md).

Browser IndexedDB stores normal chats and imported captures; desktop mode uses its local save store. Reloading the same origin can resume saved sessions, but browser clearing, eviction, quotas, or origin changes can lose them. **Export transcript** backs up conversation/pins, not the complete source ledger. Clearing named collections archives retained files locally; it is not a browser-storage purge. See [context](docs/CONTEXT_INDEX.md), [collections](docs/EXPLORATION_COLLECTIONS.md), and [capture compatibility](docs/BROWSER_CAPTURE_COMPATIBILITY.md).

## Connect an AI or script

Run in the opened application's JavaScript context:

```js
const hello = await window.MPLPB.handshake();
const result = await window.MPLPB.relay('What is Dungeons and Dragons?', {
  corpus: 'logic'
});
if (!result.ok) throw new Error(result.error);
console.log(result.data.kind, result.data.reply);
```

Use `listCorpora()` for valid corpus keys. Preserve MPLPB's reply, ambiguity/refusal, authority, and citations. `retrieve()` is explicitly page inspection. Chat sessions require reusing the returned session ID; online acquisition requires `allowNetwork:true` for that call, with `autoWiki:true` additionally needed for automatic fallback.

The deployed project publishes `.well-known/mplpb.json`, `llms.txt`, and `mplpb-public-ledger.json` relative to its site URL. The public snapshot contains externally eligible bundled pages, not visitor saves. An HTTP-only client can inspect discovery/public data; running the engine requires a browser context. See [JavaScript API](JAVASCRIPT-API.md), [agent middleware](docs/AGENT_MIDDLEWARE.md), and the optional `tools/mplpb_agent_bridge.mjs`.

## Development and release checks

From the repository root:

```sh
python3 -m unittest discover -s tests -t .
python3 tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
node crawler/test_worker.mjs
```

The Python application uses the standard library. Node is needed for developer checks; real browser tests additionally use Playwright/Chromium and a generated runtime. Start with the [developer quickstart](docs/DEVELOPER_QUICKSTART.md) and [browser testing runbook](docs/BROWSER_TESTING_FOR_AGENTS.md).

The repository requires **`archive-first` and `regression`** checks on `main`. Before merge, [ZIP-first validation](docs/ZIP_FIRST_RELEASE_TESTING.md) packages the exact PR head and tests the extracted source, Python, JavaScript, pinned WebAssembly runtime, live baseline, and candidate Chromium interface. A passing candidate is not deployment evidence. After merge, the Pages workflow builds/deploys and tests the public site again. See [release evidence and ruleset verification](docs/RELEASE_EVIDENCE.md).

Additional legacy checks and frozen-probe checksum verification:

```sh
python3 tools/check_parts.py
python3 -m mplpb_combined killtest examples/studio killtest/probes.json
python3 -m mplpb_combined killtest examples/studio killtest/probes_heldout.json
python3 -m mplpb_combined killtest examples/studio killtest/probes_adjacent.json
(cd killtest && sha256sum -c probes.sha256 probes_heldout.sha256 probes_adjacent.sha256)
```

## Documents, evaluation, and limits

[CONTENTS](CONTENTS) maps the current repository. [The documentation index](docs/README.md) separates operational guides, dated audits, original papers, and earlier implementations. Original PDFs/texts, source manifests, frozen corpora/probes, and recorded evaluations retain their historical bytes and claims. They do not describe every later feature.

The latest lexical retrieval repair is recorded in [FIXLOG.md](FIXLOG.md); the broader [October 21 system audit](docs/SYSTEM_AUDIT_2026-10-21.md) and [answer reliability review](docs/ANSWER_RELIABILITY.md) record their own revisions and limits. Development fixtures and inspected external excerpts are not independent production accuracy measurements. See [evaluation protocol](evaluation/README.md) and [ownership failures/comparisons](evaluation/ownership/README.md).

The [October 31 practical coverage repair](evaluation/practical-coverage/README.md) adds six supported returns across the frozen pottery sets, with no observed wrong returns and substantial remaining coverage gaps. The [specialist continuity proposal](docs/SPECIALIST_CONTINUITY.md) describes revisable claims, instance identity, seat permissions and interruption recovery; it is a design, not an implemented multi-agent runtime.

Lexical relevance is not entailment; statement support covers bounded forms, not all semantics. Hashes establish consistency with pins, not truth, authenticated authorship, authorization, or protection from an operator replacing both data and seals. General conversation is rule-based; imagined ideas never become page evidence. Shared deployment needs separate [threat-model review](docs/PRODUCTION_THREAT_MODEL.md). [Recovery and rollback](docs/ROLLBACK.md) preserve history and distinguish source code from user saves.

## Licence

MIT for code, CC BY 4.0 for documentation. See [LICENSE](LICENSE); retained parts and resources keep their own notices.

Mitchell D. McPhetridge · October 2026
