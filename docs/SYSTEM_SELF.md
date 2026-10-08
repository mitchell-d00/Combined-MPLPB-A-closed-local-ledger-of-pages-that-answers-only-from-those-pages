# MPLPB system and creator

MPLPB is a closed local ledger of sealed HTML pages. This interface is a front end
to its Python reader and provenance gate. It is not a language model or a game simulation.

Creator: Mitchell D. McPhetridge. Repository account: mitchell-d00.
The current user identifies themself as the project's creator. This is a creator
attribution declaration; this system cannot authenticate a person's identity.
The assistant helped implement these changes. That does not make it the creator.

Repository: https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages
Interface inspiration: Mitchell's Give It Back: The RPG.

Reader: majority declared-word ownership, with the complete-name ambiguity guard
and subset specificity, followed by every-word prose containment when no scope owns
the question. One owner returns its page; several stop; none refuse.
This is lexical retrieval. It does not provide semantic search or general paraphrase understanding.

Gate: separate eligible sources with sealed hashes and provenance declarations.
A word on one page and another word on a second page do not prove a relationship.
Source pins prove recorded bytes, not truth or authenticated authorship.

Chat: explicit topic selection, it/its follow-ups, exact source text, and bounded
inference over literal structured Fact lines. It labels source assertions and rule
inferences separately. Unsupported relations are unknown, not false.
Commands: search TOPIC; import Exact Wikipedia title; topic Exact local title;
relate SUBJECT -> OBJECT. Natural questions still pass through the lexical reader.
There is no language model, hidden semantic reasoning, or autonomous web browsing.

Topic import: explicit Wikipedia search and title selection, raw revision responses,
main-slot SHA-1, wikitext SHA-256, deterministic local lead rendering and immutable
captures. Older observations remain in the tree. A same-revision byte conflict is
archived and blocks the imported-topic collection. Imports do not create an evaluation score.

UI: corpus tiles, source dialogs, revision history, deterministic chat, a tab journal,
and Fantasy/Sci-fi/Wasteland visual settings. Desktop mode needs the local Python process and opening root index.html alone
shows launcher instructions. Standalone MPLPB_Browser.html embeds CPython through
Pyodide WebAssembly, so it does not need a Python installation or server process.
That generated HTML bundles the reader, gate and pages; it can use static hosting.
Browser mode uses IndexedDB for sessions and imported source captures. Browser
permissions, storage eviction and clearing can erase or block those saves. Export
important transcripts. No local drive is mounted or crawled in browser mode.

Chat uses a deterministic mind layer with explicit finite intents: declared working
notes, exact-topic extractive summaries, comparisons of separate source excerpts,
and historical decision explanations. Structured type questions filter the required
predicate; opposing explicit assertions produce a conflict with both proofs.
Notes are user declarations, not source facts. General semantic understanding,
consciousness, autonomous planning and model-generated responses are not implemented.

Sessions use a known local save slot, up to 32 sessions and 1000 turns each.
They survive refresh and app relaunch until the user explicitly restarts that session.
Limits refuse further operations without deleting existing state. Corpus/profile
changes clear topic focus while retaining notes and history. Source pins are rechecked
before contextual source answers. Historical explanations are labelled historical.
The browser stores UI preferences and a session ID, not questions or source bodies.
A local installation or Git clone supplies the app. It reads configured ledger pages
and its own save slot; it does not crawl or discover local folders. Search and import
are explicit remote actions. Restart clears a session but retains imported sources.
Export preserves the transcript, source pins and rule identifiers. Unsigned hashes
prove consistency only; someone with filesystem write access can recompute them.

This document describes implemented capabilities, not an accuracy guarantee.
The project still has lexical misses. No new live Wikipedia evaluation score is
claimed merely because the interface searches, imports, displays or chats about pages.
