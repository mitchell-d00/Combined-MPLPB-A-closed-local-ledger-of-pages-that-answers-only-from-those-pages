# Topic search and deterministic chat

Start with `python3 launch.py` or a platform launcher. Choose **Chat**.
No API key, model or additional Python packages are required.

## Basic help chat

New visitors can accept a guided introduction. Use **Guide me** in the header at
any time for the saved four-step tutor. “Show my MPLPB” presents available pages
in chat. Suggested questions fill the composer; Send submits them. See
[guided chat](GUIDED_CHAT.md).

Say “hi”, “how do I use this?”, “how do I search?”, “how do I save?” or
“how do I reset?”. The Get started, Search help and Save help buttons fill the
composer; Send submits the question. Help gives fixed interface instructions,
keeps the selected source context, and makes no network request. It is not a
source-fact answer. Unsupported world questions still go through the lexical reader.
The help vocabulary and procedural patterns are finite, not general natural-language
understanding. App-help questions work in Ask even when source pins are blocked.

## Search, build, then follow up

1. Choose Simple English or English Wikipedia beside Send. Send `search dinosaurs`.
   The first result becomes a pinned revision seed; a bounded literal-link crawl
   builds up to five pages in a new independent saved collection.
2. Send `what is it?`, `summarize it` or `show source`. Exact source text and named
   rules are shown separately from inferred relations.
3. Open Explore to see page titles. Use `topic Exact page title` to change focus.
4. `find dinosaurs` lists Wikipedia candidates without capturing them;
   `import Exact title` explicitly captures a chosen revision into the collection.

Wikipedia mode needs no search API account. General Web mode requires the separate
[hosted crawler](../crawler/README.md), its URL and an access token; GitHub Pages
does not deploy that backend. Search snippets do not become source facts. HTTP or
pin failures stop the operation without a fabricated answer or evaluation score.

Successful operations save sources and sessions locally. Refresh resumes the chat.
Export transcript saves chat/pins, not a complete source-store backup. Restart
clears the selected session while retaining source pages. Clear saved MPLPBs lets you select one, several or all named collections, with
a confirmation. Sources and chats are archived locally; bundled corpora remain.
Changing corpus/profile clears topic focus. Context source pins are rechecked.

## Relations and rules

The reader still decides ordinary questions using its existing lexical rule.
The chat layer adds a separate bounded inference mode, not semantic retrieval.
It recognizes explicit source assertions in standalone paragraphs:

```text
Fact: Dungeons and Dragons | instance_of | tabletop RPG

Fact: tabletop RPG | subclass_of | game
```

Supported predicates are `instance_of`, `subclass_of` and `related_to`.
These are **assertions on the source page**, not independently authenticated facts.
Do not add them automatically just because an imported paragraph mentions terms.
Ordinary Wikipedia prose is not automatically converted into triples.

Only eligible, intact sources passing the provenance gate and the profile may
support a rule. The literal quote, source ID and sealed hash accompany each premise.

| Rule | Meaning |
| --- | --- |
| CTX-1 | Resolve explicit it/its/this-topic references using a checked topic pin |
| CTX-2 | Literal more/continue/show-page requests return the selected page verbatim |
| REL-1 | Recognize only the documented relation-question grammars |
| FACT-1 | Read a literal structured assertion from an eligible sealed page |
| TYPE-1 | Subclass chains can compose |
| TYPE-2 | An instance of a class is an instance of its superclass |
| REFUSE-1 | No supported path means unknown, not false |

Choose **Chat logic · synthetic facts**, then:

```text
topic Dungeons and Dragons
is it a game?
relate it -> budget
```

The first relation uses both synthetic premise pages and TYPE-2. It is labelled
`rule_inference`. The budget relation remains `unknown_relation`; its D&D and
budget source pages are shown separately without inventing a D&D budget.
These fixtures are marked synthetic, not historical evidence.

You can also use `relate SUBJECT -> OBJECT` or `is SUBJECT related to OBJECT?`.
A literal `is SUBJECT a OBJECT?` uses the same typed assertion graph. No inverse,
negation, causal, numeric, temporal or arbitrary semantic rules are implemented.
`related_to` does not compose transitively. Traversal and fact counts are bounded.

## Source tree

User captures live under ignored `local/topics/`, separate from the published
`evaluation/wiki` kit. Each import creates an immutable raw source capture. A new
bundle contains the currently selected source revision for each topic, with a
pinned head. Earlier bundles and source captures remain.

A source update must pass revision-slot and local-byte checks. Older revisions
are archived and cannot lead. Same revision ID with different source bytes is
archived, blocks the imported collection, and does not move its head. The retained
conflict is checked even if the mutable blocked flag is deleted. Importing a newer
revision can resolve that topic's block. Requests also recheck captured raw bytes,
served pages, renderer pins and engine/checker pins. A code change may require
fresh captures before this collection can be served.

Imported source authorship is unknown. Imported pages declare machine origin and
external=no. External profile cannot deliver their bodies; use internal for local
inspection. Multiple imported topics share a local collection, but loading them
beside each other does not establish a relationship.

The UI revision view displays the imported topic tree separately from historical
wiki evaluation captures. No import or chat turn is reported as an evaluation score.

## System and creator

`who made you?`, `what can you do?`, `what are your limits?` and other explicit
system prompts read the sealed self-reference corpus. Its human-readable source
is [SYSTEM_SELF.md](SYSTEM_SELF.md). It names Mitchell D. McPhetridge / mitchell-d00
as the declared creator, as requested by the user. The page does not authenticate
identity or invent a biography. The assistant is an implementation collaborator.

## Save and check a conversation

Sessions now persist in `local/sessions/state.json`, a known save slot rather than
filesystem discovery. Up to 32 sessions and 1000 turns per session; limits stop further
operations without evicting saved state. The browser remembers a session ID and
resumes the matching transcript after refresh or server relaunch. **Restart MPLPB**
explicitly deletes that session. Imported source captures remain. Changing corpus or
profile clears topic focus while keeping declared notes and historical turns.
Use **Export transcript** before restart when you want a separate historical copy.
Browser-storage clearing loses the automatic resume pointer; the saved server slot
is not implicitly deleted. Save slots are local, unsigned records, not authentication.

Mind commands: `remember NOTE`, `memory`, `forget notes`, `forget topic`,
`summarize it`, `summarize Exact title`, `compare Title A vs Title B`, and `why?`.
Notes cannot establish facts or trigger commands. Summaries quote at most three
source text fragments, bounded to 1600 characters. Comparisons retain sources
separately. Why explains the historical trace; it does not re-certify old evidence.
Exact titles are required; unknowns are not silently guessed. Explicit negative
structured predicates can conflict with positive evidence; both proofs are returned.
An `is X a Y?` query accepts type evidence, never merely `related_to` evidence.

Each turn links to the prior turn hash and records the chat-logic version and file
byte hash. Export reports hash-chain consistency. This detects changes relative
to the saved chain; it does not authenticate an author or certify source truth.
A forger can recompute an unsigned chain. This is an auditable local record, not a
signature or independent evidence.

## Verification and walk back

A live Simple English Wikipedia search for Dinosaur returned six suggestions.
A live import captured revision `11003304`, checked slot SHA-1
`32503eea97df17d8041b4e265868042c3ebca402` and wikitext SHA-256
`cb47e388db6da470d703632a077321843b4f77009731513cd24b001efe4bcab6`.
The follow-up “what is it?” returned the captured Dinosaur page. This was one
workflow exercise, not a blind evaluation or an accuracy score.

The raw response, retained renderer, wikitext, sealed page, collection head and
original validation report are retained in `chat-validation/live-source/`.
`offline-chat-replay.json` is a separate later replay, clearly offline, with a
hash-linked transcript. The original live observation/report was not rewritten.
No user chat history or private source files are in that fixture.


256 package tests passed, including twelve HTTP UI tests and eighteen new
chat/source tests. The optional local front-end script checks also passed.

The new unit/integration tests cover inference versus co-occurrence, scope/profile
changes, stale context, raw-source tampering, revision conflicts, older revisions,
canonical redirects, network failure, creator answers, transcript changes and
actual HTTP chat/export/reset routes. Optional Node tests cover chat rendering
alongside the earlier UI logic. Those are element-stub tests, not browser rendering.
Browser visual verification and Windows launcher execution remain unverified.

The original reader patch, frozen probes, original experiment files, published
source captures and papers are preserved. No new blind/general accuracy claim
is made. The earlier RPG UI commit is retained in published history;
reverting the chat commit removes this layer and retains that front end. Imported data is separate under `local/`; retain or archive it yourself
when changing versions. See PUBLISH_AND_ROLLBACK.md for the publication history.
