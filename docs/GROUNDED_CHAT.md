# Deterministic conversation and grounded answers

The browser uses explicit intent, context and response-construction rules; no language model or provider account is required. These rules cover common phrasing, not arbitrary human language.

## Modes and collections

Chat mode clears the active serious scope and page focus while retaining saved collections, notes and history. Casual turns carry a notice that they are not MPLPB evidence. Topic requests can consult eligible saved pages without entering Serious mode.

Serious mode restores the previous selected collections, or the current collection when no previous scope exists. Load selected uses the current selector; Load all snapshots all available collections. The selector and loaded-count status reflect the returned session state. Conversational turns remain available in both modes; they do not change the serious scope. Each collection keeps its own eligibility, source pins and delivery boundaries.

## Question and response construction

`tools/question_frames.py` normalizes polite wrappers and common overview requests: tell me about, walk me through, share facts about, fill me in on, and similar frames. Normalization is never evidence. Attribute questions retain their question type and use the existing grounded rules.

A request such as “Say hi to the OpenAI forum and tell them what you are” composes a greeting and an authored system description. It drafts text in the conversation; it does not post externally. “Say hello to the astronomy club and tell them about Moon” composes a greeting with a locally sourced overview; source references remain attached. Exact repetition remains literal. The system description is labeled conversational system information, not an MPLPB citation.

Source conversation reads eligible local pages first and displays excerpts with sources beneath the answer. Follow-ups remember per-source offsets and previously shown sentences. New captures start at their own first unread sentence. Exhausted sources do not offer an endless “Tell me more” button. This is deterministic excerpt selection, not unrestricted factual synthesis or independent validation.

## Reference data and optional network access

The pinned Open English WordNet 2025 archive provides definitions, synonyms and separate word senses. Conservative plural fallback requires a real headword. It aids navigation and dictionary lookup; it never rewrites ledger ownership rules or proves factual equivalence.

CMU Link Grammar data is archived as a reference; its parser is not running. The bundled encyclopedia contains 23 revision-pinned Simple English Wikipedia captures, not an entire offline encyclopedia. English Wikipedia is the default online choice; Simple English Wikipedia remains available.

With automatic Wikipedia lookup enabled, missing or exhausted topic text can trigger one bounded acquisition, capture revision-pinned pages, and retry the same conversation. A successful lookup is remembered per topic and wiki to avoid repeatedly downloading the same answer. Explicit search can still request another source. Network errors retain the local response; search snippets are never evidence. Online Wikipedia availability and browser network policy still apply.

## Verification

Regression tests exercise mode restoration, both-mode conversation, multi-collection boundaries, source exhaustion, newly added material, plural navigation, compound greetings, exact echo, and transcript integrity. Script tests check controls and state rendering; the WebAssembly check exercises the packaged Python engine. These checks are developer-authored and do not substitute for independent human evaluation or browser layout testing.

## Conversation controls

The composer has a fixed Everyday controls row and a Conversation choices row derived from the latest response, subject and source-aware suggestions. Topic choices are replaced when the conversation changes; historical suggestions remain in the transcript. Composer buttons send the same natural-language requests through the normal engine, with busy-state guards. A short topic question such as “Dogs?” enters topic exploration. Button labels are authored actions; the buttons do not contain stored answers. Deterministic response construction still uses authored rules and phrase components.

## Shared discourse planner

`tools/language_planner.py` parses common frames, compound greeting/overview acts, subject references, negation and hypothetical intent. Every App.chat path calls it after the evidence gate and before transcript hashing; transcript payloads pin the planner version and source hash. Existing echo, emotional, dictionary, help and proof realizers retain their contracts. The common planner composes supported overview framing from subject, number agreement and a deterministic turn-selected clause grammar, and constructs hypothetical invitations from bound subject slots. It does not paraphrase source sentences or turn eliminated alternatives into evidence.

Automatic Wikipedia acquisition reads the plan's bounded query; unresolved references, negated requests and explicit imagined ideas cannot trigger it. Explicit search/import commands keep their existing transport rules. Replies have small support labels; detailed plans, distinctions and source decisions remain in the expandable evidence panel. This is finite rule-based composition, not an unrestricted language generator.

## Local self-knowledge

`tools/self_knowledge.py` answers recognized capability and current-session questions before topic retrieval. Its descriptions are authored software metadata; they are neither independent validation nor MPLPB world evidence. The active mode, loaded collection identifiers and topic names come from the session. Self-description preserves scope and cannot initiate automatic source lookup. Creator attribution retains the existing sealed system-page route. The [system guide](SYSTEM_GUIDE.md) is generated from the capability model; a regression test checks they remain synchronized.
