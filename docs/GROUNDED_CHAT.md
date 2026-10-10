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


## Conversational reference fallback

Topic and definition requests search eligible local pages before a generic chat fallback. In serious mode loaded sources are checked first; if no answer is available there, saved sources outside that scope may supply a separately tagged reference answer. This never changes loaded collections or turns outside material into loaded-scope evidence. Explicit selected-page questions retain their selected-page boundaries. In either mode, matching WordNet headwords can supply a conversational definition with separate senses and related wording. Dictionary references remain distinct from MPLPB evidence; synonyms are not evidence for unrelated claims. Source sentences and their references remain intact. User listening preferences suppress unnecessary follow-up questions.

System definitions such as “What is a MPLPB?” and common overview phrasing resolve against authored system concepts before world lookup. This is finite rule coverage, not unrestricted language understanding. These are developer-authored regression checks, not independent validation.


## Subject-description conversation

`tools/proposition_chat.py` represents a turn as subject, predicate, polarity and speech act. Its subject slot is not a topic whitelist. It handles common copular statements, preferences and opinion questions, including user-invented names and descriptions. A small opinion lexicon distinguishes an aesthetic conversation from an objective claim; unknown descriptions stay unverified user declarations. Up to eight such descriptions can be retained as labeled user context. Pronouns resolve to the conversational topic; switching modes clears the active proposition focus.

Local page excerpts and dictionary senses may provide subject context, not evidence that an opinion is true. The output composes a conversational clause, immutable source spans when available and a topic-specific follow-up. Listening mode suppresses that follow-up. Source and command rules retain priority for their supported forms; ordinary opinion statements do not silently trigger network searches. The module version and hash are recorded in transcript payloads.

This is finite grammar coverage with authored grammatical fragments and explicit slots, not unrestricted semantic understanding or a claim that every possible question is understood. Research references informing the separation of representation and realization: [NLTK feature grammars](https://www.nltk.org/howto/featgram.html), [NLTK discourse](https://www.nltk.org/howto/discourse.html), and [SimpleNLG](https://github.com/simplenlg/simplenlg). Those libraries are not newly installed runtime dependencies.


## Conversation recall and introductions

`tools/conversation_memory.py` scans only the current session’s retained user questions; assistant outputs never establish the user’s name. Explicit introductions, name corrections, forgetting and compound identity follow-ups precede generic social fallback. A name is a user declaration, not authenticated identity. State/occupation phrasing is conservatively excluded from bare “I am” introductions; an explicit “call me” form removes ambiguity.

Topic recall such as “What did I say about orchids?” matches the requested terms against earlier user statements, allowing simple plural normalization, and returns up to three recent matching turns. This is bounded lexical recall, not unrestricted semantic memory. Replies carry turn references and a small Conversation memory tag, with no MPLPB source claims or automatic remote lookup. The name is reconstructed across reloads from the saved conversation; a forgetting command prevents older introductions from restoring it. Restarting the session uses the existing reset behavior. Historical transcript text is not erased by forgetting a name.


Explicit “brainstorm” requests compose three transformations around a supplied or remembered topic, without requiring loaded MPLPB pages or a dictionary entry. Subsequent “brainstorm” turns choose the next operation set deterministically. These are exploratory prompts, not factual claims or an unrestricted creative model. Existing conversation and name recall continue with zero loaded collections.


## Everyday social cues

Complete greetings such as “How are you today?”, “How have you been?” and
“How’s your day going?” receive short conversational replies, including
“I’m functional, thanks!” A session-local counter mixes authored openings and
follow-up questions deterministically and survives reload. These are social
phrases, not runtime health checks or claims of feelings.

Thanks, farewells and time-of-day greetings have brief responses. “And you?”,
“good thanks” and “could be better” are recognized after an immediately preceding
wellbeing exchange; they do not create personal facts. Existing listening,
emotional-preference, source-query and literal-repeat handlers remain in place.
The social replies carry conversation authority with no evidence citations, and
never load collections or grant source support. This is bounded phrase coverage,
not unrestricted social understanding.

Conversational lead-ins such as “Cool, tell me about the Moon” and “Great, how
big is it?” use the same request path as the words after the acknowledgement.
This bounded normalization runs before social listening and preserves the
original transcript plus a normalization trace. It does not strip adjectives
from topics (“cool water”, “Great Britain”), negation, or literal-repeat text.
Reference labels and source eligibility remain those of the underlying request.
