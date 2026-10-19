# MPLPB local JavaScript API · v1.0.0

`window.MPLPB` lets people, scripts and browser-capable AI agents use the same
MPLPB engine as the interface, without clicking buttons. No API key or account
is needed. This is a page-local JavaScript API, not a hosted service.

**MPLPB can be a local middleware layer for an AI frontend.** The AI sends
requests through `window.MPLPB`; MPLPB reads retained pages and returns its
structured decisions, citations and provenance. People and scripts use the same
engine. MPLPB itself needs no model provider, cloud processing, API key,
subscription, or hosted API service.

| Use | Internet / services |
| --- | --- |
| Local queries, local chat, supplied-text imports | Fully offline once the standalone HTML is available; no server or cloud processing |
| Optional Wikipedia lookup and capture | Internet to Wikipedia; no API key or hosted MPLPB service; processing and retained ledger stay local |
| Optional general-web crawler in the existing UI | Requires its configured hosted crawler and access token; not service-free |
| AI frontend | Can be local; a cloud AI has its own network, credentials and data handling, separate from MPLPB |

This lets an agent use MPLPB as **local middleware with optional online source
acquisition**. Online acquisition is not offline operation. A cloud AI does not
become local merely because it calls MPLPB. The API is not a remotely exposed
HTTP service: the frontend or agent must have access to the app's page context.

In the **generated standalone browser HTML**, operations run in the embedded
Python/WebAssembly worker with local IndexedDB saves. No Python server or
internet connection is needed after you have the complete HTML. The existing
engine is preserved: this is a JavaScript interface to Python, not a JavaScript
rewrite or a smaller replacement reader. The original repository `index.html`
also exposes the API when served by `python3 launch.py`; that desktop mode still
uses its local Python HTTP server. Opening the unbuilt source HTML as a file does
not start an engine. Download/build the standalone file for server-free use.

## Quick start

Run in the opened app's browser console:

```js
const mplpb = window.MPLPB;
await mplpb.ready();
mplpb.help();
await mplpb.listCorpora();

const result = await mplpb.query('What is Dungeons and Dragons?', {
  corpus: 'logic',
  profile: 'internal'
});
if (!result.ok) throw new Error(result.error);
console.log(result.data.reader.kind);
console.log(result.data.reader.text, result.data.reader.citation);
```

All engine methods return a Promise resolving to `{ok:true, data:...}` or
`{ok:false, code:'INVALID_ARGUMENT'|'NETWORK_DISABLED'|'ENGINE_ERROR', error:'...'}`.
`version`, `help()` and `functions()` are synchronous. Calls wait for browser
runtime startup automatically; `ready()` is optional. Startup/storage failures
return errors. Calls through this object execute in order and snapshot arguments
before waiting. There is no cancellation or transaction across multiple calls.

**`ok:true` means the operation completed, not that an answer was supported.**
Inspect `data.reader.kind`: `return`, `ambiguous`, `not_in_corpus`, or `help`.
Candidate mode can return `candidate_only`, which is not a supported answer.
The full reader decision, citation, gate and provenance fields are returned
unchanged. A successful chat can contain interface help, local calculations,
creative suggestions or other labeled non-source responses. Use `query()` when
you require the strict source-answer path; inspect chat authority/support labels
before treating a chat response as evidence.

## Methods

| Method | Result in `data` / behavior |
| --- | --- |
| `ready()` / `getState()` | Engine state: corpora, profiles, rules and notice |
| `listCorpora()` | Array of available corpus keys, labels and counts |
| `query(question, {corpus, profile?, mode?})` | Full query result; mode defaults to `supported`, or explicitly `candidates` |
| `listPages({corpus, profile?})` | Inventory with page paths, eligibility and reasons |
| `readPage(path, {corpus, profile?})` | Eligible page text, sealed fields and hash; withheld or invalid paths fail |
| `getHistory({corpus})` | Retained source-capture history, not chat turns |
| `chat(message, {corpus, profile?, session?, allowNetwork?, wiki?, autoWiki?})` | Chat result including session ID, response, turn and transcript pin; local by default |
| `resumeChat(session)` | Saved conversation data and `chain_intact`; does not select the UI conversation |
| `exportChat(session)` | Serializable transcript with integrity result; does not trigger a download |
| `resetChat(session)` | Explicitly resets that session; source pages remain |
| `createCollection(name)` | New persistent collection, including its `corpus` key |
| `importSource({corpus,title,url,text})` | Retains supplied text and capture metadata in a user-created collection; never fetches the URL |

Corpus keys come from `listCorpora()`; page paths come from `listPages()`. Profile
defaults to `internal`. Unknown options are errors rather than silently ignored.
Profiles are delivery rules, not authentication or access-control credentials.

## Local conversation and supplied sources

```js
const first = await mplpb.chat('remember I study dinosaurs', {corpus:'logic'});
if (!first.ok) throw new Error(first.error);
const session = first.data.session;
const next = await mplpb.chat('what do you remember about me?', {
  corpus:'logic', session
});
const transcript = await mplpb.exportChat(session);

const created = await mplpb.createCollection('My local notes');
if (!created.ok) throw new Error(created.error);
const corpus = created.data.corpus;
await mplpb.importSource({
  corpus, title:'Workshop notes', url:'https://example.org/workshop',
  text:'The workshop opens at nine.'
});
await mplpb.listPages({corpus});
```

Omitting `session` starts a separate conversation every time. Reuse the returned
ID to continue; use matching corpus/profile values. API conversations do not
borrow the visible chat's ID. An explicit ID can access/reset that same saved
conversation, so use IDs intentionally. Normal saved turns survive reload in the
current browser origin. The engine's explicit off-the-record chat mode remains
ephemeral and cannot be exported/resumed through the saved-transcript methods.

`chat()` defaults to local-only execution. Without `allowNetwork:true`, `search`,
`find`, remote `import` and their resolved command variants fail before source
acquisition, and automatic Wikipedia lookup is disabled. Permission is explicit
**on each call**: it does not carry over from another turn, and the UI's Wikipedia
checkbox does not silently change API behavior. This is a method contract, not a
sandbox for arbitrary code executing in the page.

## Optional online lookups and an AI frontend

```js
// An agent explicitly asks MPLPB to capture sources from Wikipedia.
const built = await mplpb.chat('search Cat', {
  corpus:'logic', allowNetwork:true, wiki:'english'
});
if (!built.ok) throw new Error(built.error);
if (built.data.response.kind !== 'built') {
  console.log(built.data.response); // Inspect acquisition failure or other result.
} else {
  // Network permission is omitted again: this turn reads the retained collection.
  const reply = await mplpb.chat('what is it?', {
    corpus:built.data.corpus, session:built.data.session
  });
  console.log(reply); // Pass the full result/authority/source labels to the frontend.
}

// Standalone browser only: permit its existing automatic Wikipedia fallback.
const assisted = await mplpb.chat('Tell me about dinosaurs', {
  corpus:'logic', allowNetwork:true, autoWiki:true, wiki:'simple'
});
```

`wiki` accepts `simple` (default) or `english`. `allowNetwork:true` permits explicit
`search`, `find` and `import` commands; ordinary chat does not automatically search
unless `autoWiki:true` is also supplied. Automatic fallback uses the existing
bounded topic planner, not an unrestricted web search for every sentence. Inspect
`automatic_lookup` and the response kind for failed/deferred acquisition. The
desktop server supports explicit commands; `autoWiki:true` returns an argument
error there because automatic fallback belongs to the standalone browser bridge.

Network/CORS failures remain errors or the existing labeled acquisition-failure
results. An online call may create collections and retain captures and turns.
Use returned corpus/session IDs rather than assuming they stayed the same.
Subsequent local reads need no live source connection. Retained source metadata
and byte checks do not establish authenticated authorship or factual truth.

The JavaScript facade exposes Wikipedia lookup, not the optional hosted
general-web crawler. An agent can also obtain text through its own tools and
submit it with `importSource()`; MPLPB records that as supplied text. A frontend
should keep refusals, ambiguity and candidate-only results visible, and label
any AI-generated interpretation separately from MPLPB's returned source evidence.

`importSource()` records caller-supplied bytes, not a verified site download.
The existing engine validates URLs, collection identifiers, source length and
seals. Imported text is not executable JavaScript. Importing a title does not
automatically establish answer support. Browser input text is capped at 100,000
characters; desktop mode additionally caps the entire JSON request at 16 KiB.

Mutations use the existing save system. Standalone responses arrive after its
filesystem sync; storage failures are errors. Returned values are detached data,
not live engine objects. The API does not render results, switch UI selections,
or refresh an already-displayed inventory. Reload the interface to pick up
collections created by a script. Export important transcripts before clearing
browser storage. Exports do not back up an entire source ledger.

## Browser automation

```js
await page.waitForFunction(() => Boolean(window.MPLPB));
const result = await page.evaluate(() => window.MPLPB.query(
  'What is Dungeons and Dragons?', {corpus:'logic'}
));
```

The agent must be able to execute JavaScript in that page context. A URL alone
does not grant access to a user's browser or saved data. Another website cannot
directly reach this object across origins. An AI agent's own model/cloud use is
separate from this local API; results handed to that agent follow its data flow.

## Developer checks

```sh
node tests/javascript-api.cjs
python -m unittest tests.test_browser_bridge tests.test_ledger_ui -q
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
```

The API check uses the real Python bridge in an isolated temporary save folder,
including supported/ambiguous/refused answers, profile restrictions, sessions,
local imports, default remote-command rejection and explicitly enabled lookup
using synthetic Wikipedia responses. The existing WebAssembly check also
exercises the API from the generated HTML. No Node dependency is added to the app.
