# Conversation interpretation and planning

The conversation router is separate from the MPLPB ledger. It consolidates the
former top-level first-answer-wins chain in `App.chat`. Both typed requests and
buttons enter that same endpoint.

## Interpretation before execution

`conversation_continuity.prepare` normalizes the request and resolves supported
references and corrections. The shared frame retains the original request,
resolved request, original and resolved dialogue acts, subject, choices, typed
user relationships, and route candidates.

`conversation_router.propose` recognizes candidate intents without invoking
answer constructors or source readers. Explicit commands, pending referents,
personal declarations, compound dialogue acts, capabilities, reasoning skills,
and subject descriptions contribute candidates. Each proposal records its
specificity priority, basis, and allowed authority categories. These priorities
are authored policy, not calibrated probabilities. Equal-priority conflicting
routes ask for clarification rather than depending on module registration order.

`plan` records the selected action, authority constraints, and answer obligations
**before** execution. Fully recognized compound local requests can have one plan
per clause. For example, `My pet is Juniper; what is my pet?` processes the
statement before answering the question. A partially recognized compound request
is not executed as a subset of instructions.

Only the selected executor commits conversation state. Execution uses a session
copy so a declined candidate cannot leave partial memory updates behind. An
explicit definition handoff from user descriptions to the existing source reader
is recorded separately. The reply plan is not made by splitting generated prose.
`realization` records the resulting text and source attachments separately.
The plan's `sources` field remains as a backward-compatible attachment populated
after execution; it is not evidence that sources were known before retrieval.

## User relationship graph

The frame includes typed person and topic nodes and user-declared relationship
edges: family/social roles, likes/dislikes, and explicit possessive attributes.
Arbitrary names and slot values are retained; they do not need a dictionary entry.
Forward replay applies supported corrections, with turn references. Personal
slot replay now handles declarations inside compound messages as well as whole
turns. Assistant prose is excluded from premises. The graph is reconstructed
from the current transcript; it is not autonomous learning or code modification.

This is a bounded conversation graph, not an unrestricted semantic or event
parser. A relation is recorded only when a supported declaration grammar matches.
Unknown wording remains unresolved. The authored base phrase graph still handles
its six categories of command synonyms; it is distinct from conversation memory.

## Authority and evidence

Plans distinguish conversation, user declarations, system descriptions,
calculations, hypothetical premises, lexical references, research notes, and
existing gated source results. Composed replies retain separate `claim_units`.
Mixed dialogue/source replies keep conversational units separate from the source
reader's text and pins. Older specialized source skills retain their existing
result-level attribution and separate `scope_results`; this release does not
claim sentence-level entailment checking for all legacy prose.

The router never turns a declaration or repeated assistant answer into ledger
evidence. It does not select a truth winner between conflicting pages. The core
reader and provenance gate are unchanged: lexical ownership selects candidates;
it does not prove that their prose answers the question. Hashes establish byte
integrity, not factual truth. Authority metadata is an audit contract, not a
replacement for the existing source gates.

## Migration boundary and remaining work

The top-level competing-handler chain is replaced. Source acquisition, social
realization, and other legacy skills inside the environment still contain bounded
subrouters. They are reached through an explicit legacy-skill candidate. Their
recognizers can be extracted into further proposals incrementally. No claim of
unrestricted natural conversation or complete semantic consolidation is made.

The current priorities and several skill recognizers remain hand-authored.
Broadening a recognizer requires collision tests against personal memory, literal
requests, negation, and source controls. Favor extracting shared recognizers, as
with self-knowledge and dialogue acts, over duplicating patterns.

## Validation

`tests/test_conversation_router.py` checks pre-execution planning without reply
construction or retrieval, losing-handler isolation, deterministic plans,
compound memory after reload, corrections, literal/negation boundaries, and
assistant/user role isolation.

`python -m tools.smoke_conversation_architecture` runs 78 turns in two modes from
a fixed fixture covering eight conversation scenarios. The questions are not
generated by enumerating the implementation's phrase forms. The checked-in report
contains every request and reply, including any failures. Fragment expectations
are narrow regression checks, not human judgments of fluency or correctness.

The existing 140-turn continuity smoke run is retained. All these tests are
**developer-authored**, not independent validation. External testers should use
unprompted conversations and unfamiliar corpora under the existing independent
evaluation protocol. The project must publish those failures as well as successes.
