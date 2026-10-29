# Combined MPLPB: agent middleware via one URL

The live page embeds the **entire Python Combined MPLPB engine** (ledger, reader, provenance, chat, source capture, and retained session storage) in WebAssembly. GitHub Pages hosts the downloadable runtime, but Python executes in the visitor's browser. No separate server API, cloud model, or smaller replacement engine is required.

## Handshake by link

Supply a client/AI with either:

- Live page: https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/
- Repository: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages

Resolve the machine-readable `.well-known/mplpb.json` relative to the full project
site URL, including its repository path and trailing slash. For this project it
is not `https://mitchell-d00.github.io/.well-known/mplpb.json`. Follow the manifest
in the repository if hosting has a custom URL. The companion `llms.txt` explains
the contract. `mplpb-public-ledger.json`, at the same project base, publishes
**only bundled pages eligible under the external profile**; the builder generates
it for deployment, never from saved visitor data.

**Two connection levels:** (1) an HTTP-only client can read the manifest and published eligible-page snapshot; it cannot run the live engine. (2) A browser-capable client opens the app, waits for its embedded WebAssembly runtime, and invokes `window.MPLPB` inside that exact page. That is a real call to the full MPLPB engine. The browser maintains its own source ledger and sessions. Giving a URL never unlocks another browser's private IndexedDB.

## Strict relay: MPLPB between AI/UI and the engine

```text
User/UI → client/AI → MPLPB browser API → full Python reader/chat/ledger
                                        → optional source search/capture
User/UI ← client/AI (verbatim only) ← MPLPB answer + status + citations
```

```js
await page.goto(siteUrl);
await page.waitForFunction(() => Boolean(window.MPLPB));
const hello = await page.evaluate(() => window.MPLPB.handshake());
if (!hello.ok) throw new Error(hello.error);
const result = await page.evaluate(() => window.MPLPB.relay(
  'What is Dungeons and Dragons?',{corpus:'logic'}
));
if (!result.ok) throw new Error(result.error);
// The outer AI prints result.data.reply verbatim and conveys result.data.kind;
// it does not rewrite a refusal into a sourced answer.
```

The full API returns `{ok:true,data}` or a labeled error. A successful method execution is not proof of answer support. The relay's default mode is **strict query**. A supported answer requires `data.kind === 'return'`; `ambiguous`, `not_in_corpus`, `candidate_only` and help are not source-supported answers. Preserve the citation and gate information. This layer does not browse/search on its own.

## Conversation and optional searches

For **page inspection**, use `window.MPLPB.retrieve(question,{corpus,profile})`.
Its successful kind is `retrieved`, with `answer_supported:false` and
`authority:'source_page_retrieval'`. Preserve those labels; the default relay
continues to use the supported-answer path. The optional Node bridge does not
expose a dedicated retrieve flag; use page-context JavaScript for that method.
See [retrieval contracts](PAGE_RETRIEVAL.md).

```js
const first = await window.MPLPB.relay('hello',{
  corpus:'logic',mode:'chat'
});
const session = first.data.session;
const next = await window.MPLPB.relay('Tell me about cats',{
  corpus:'logic',mode:'chat',session,
  allowNetwork:true,autoWiki:true,wiki:'simple'
});
// Reuse next.data.session and next.data.corpus if they have changed.
const suggested = await window.MPLPB.relay('What can I explore next?',{
  corpus:next.data.corpus,mode:'chat',session:next.data.session,
  includeSuggestions:true
});
```

Only MPLPB supplies the response. The middle AI/UI forwards `data.reply` without
paraphrasing, adding knowledge, inventing citations, appending personal suggestions,
or hiding unsupported results. Structured suggestions are **off** unless the caller
explicitly passes `includeSuggestions:true`; an engine-authored offer embedded in
`response.message` remains unchanged because editing it would violate the verbatim
contract. API chat can be conversational, so inspect its support labels instead of
calling every chat result source-supported.

Local chat is the default. Optional network lookups must be requested on the specific
call with `allowNetwork:true`, and automatic Wikipedia fallback additionally needs
`autoWiki:true`. Online browsing and source capture remain controlled by MPLPB's
existing logic and CORS restrictions. No new network authority is given to the
outer AI. The optional general-web crawler retains its separate hosted worker
and access-token requirement.

## Launch with an external program

The optional `tools/mplpb_agent_bridge.mjs` accepts a repository URL or live URL.
`--handshake` performs just a GET with Node (no browser package).
Live calls require Playwright installed separately (`npm install playwright`, then
`npx playwright install chromium`), because the entire engine runs inside the page.

```sh
node tools/mplpb_agent_bridge.mjs "https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages" --handshake
node tools/mplpb_agent_bridge.mjs "https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/" --question "What is Dungeons and Dragons?" --corpus logic
node tools/mplpb_agent_bridge.mjs "https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/" --chat "hello" --corpus logic --profile-dir ./mplpb-browser-profile
```

Results print as JSON, including the verbatim `data.reply`, status and citation.
A persistent browser profile can retain sessions and imported sources, so protect
that profile as private data. A new blank profile starts with bundled corpora only.

The project does not claim that any third-party AI must obey the manifest or can
reach the browser merely from a URL; it gives capable clients a discoverable,
documented API and an executable bridge.
