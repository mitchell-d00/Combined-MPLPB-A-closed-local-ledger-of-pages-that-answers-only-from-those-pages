# Browser exploration collections

Open “Build and search your MPLPB collections” and create a named MPLPB. Select
it in the corpus selector. Wikipedia searches run in chat; importing a title adds
its pinned main revision slot to that collection. The existing shared imported
topics collection remains available, as do all bundled corpora.

Send `search TOPIC` to build a new independent collection. Wikipedia mode captures
the first search result's pinned revision and follows literal wiki links breadth-first,
up to five pages, ten page requests and depth two. `find TOPIC` lists candidates for
manual exact-title import. Search rank and links do not prove semantic relevance.

Web mode uses the separately configured [hosted crawler](../crawler/README.md).
It searches Tavily or Brave, fetches public HTML/plain text and follows bounded
same-origin links. The browser verifies returned byte hashes and builds local pages.
Without the backend URL/token it refuses, rather than silently using Wikipedia.
The token is held only in the tab, outside saved chats; the provider key stays on the
server. A crawl record pins limits, source captures, server times, links and failures.
General-web deployment is not part of GitHub Pages deployment.

“Search web” also opens Bing for manual research. Explicit browser URL imports still
require CORS; pasted text remains labelled supplied. Desktop mode supports pasted
sources and Wikipedia exploration; hosted web crawling is a browser operation.

Each capture records source URL, UTC observation date, raw SHA-256, derived text
SHA-256 and transport. HTML scripts/styles/head text are excluded from the derived
body. Raw captured HTML is never executed. Authorship stays unknown, origin machine,
external delivery withheld. The pins establish recorded bytes, not truth, identity,
semantic relevance or a Wikipedia revision. Sources at different URLs with the same
title remain separate and can correctly trigger ambiguity. A refreshed source at
the same URL/title writes a successor; previous pages and captures are retained.

Each collection has its own chat pointer and saved session. The chat view has a
scrolling transcript, distinct user/assistant messages and a composer. Enter sends;
Shift+Enter inserts a newline. All engine calls continue through the Python reader.
Saving finishes before the browser acknowledges an operation. Refresh restores the
session and marks old answers historical. Clearing browser storage can erase saves;
export important transcripts. There is no promise against browser storage eviction.

Restart MPLPB clears the selected chat, retaining its sources. Reset selected
collection requires confirmation, removes the active collection and its sessions,
and retains its prior source files in a local reset archive. Other collections and
bundled corpora are preserved. The collection limit is 32; session/turn limits still
refuse without automatic deletion. Source text is limited to 100000 characters,
downloaded payloads to 2 MB. Desktop JSON requests retain the smaller HTTP size limit.

The registry, capture manifests, raw source bytes and page inventory are pinned.
Tampering refuses rather than silently serving inconsistent source data. A failed
write can leave retained files that fail validation; no automatic repair is claimed.
No evaluation probe, published wiki capture or live evaluation score is rewritten.

Walk back: revert the collection UI/store/bridge change together. Prior desktop
corpora and shared topics are untouched. Preserve or export browser saves first;
old builds cannot understand the new collection selector. Source archives and saved
slots belong to the origin where the browser build was opened.

## Clear some or all collections

Open Build and search your MPLPB collections, then Clear saved MPLPBs. Tick named
collections and choose Clear selected MPLPBs, or Clear all my collections. A
confirmation lists the affected collections. Bundled corpora and the separate
legacy imported-topics collection are excluded. The chosen collections and their
chats leave active state; prior source files and session snapshots stay in local
archives. This is a workspace clear, not a browser-storage purge. No archive
restore UI is provided yet. Failed registry writes roll moved collections back.
