# Structured local chat requests

The chat router shares finite request slots across vocabulary: action, subject,
requested attribute, qualifiers, and a context reference. These slots select a
handler; they do not establish evidence or general language understanding.

An introduction followed by a recognized software question is composed into a
name acknowledgement and a separately attributed system explanation, including
without punctuation. Greeting forms include good morning, afternoon, and evening.
Names remain user declarations. State descriptions such as “I'm tired” are not
names. Existing identity clarification and role-aware dialogue routes remain.

Memory-duration questions explain the active mode. Chat and Serious use a saved
conversation, with no fixed retention timer or guaranteed storage lifetime.
Off-the-record free chat keeps only an in-memory session (up to 1,000 turns);
leaving it or restarting the running app discards it. Free chat does not persist a
transcript or fetch remote sources. Device/browser logging is outside that claim.

Generic indefinite-noun requests such as “Tell me about a dog”, “What is an
apple?” and “Explain a bee” select a bundled dictionary explanation when the
complete headword is available. Unknown terms still reach the normal source
routes in Chat and Serious; free chat reports missing support. Other topical
requests retain existing eligible-source lookup and dictionary fallback behavior.
Definitions are quoted, not expanded into newly inferred properties. Each sense
has its original identifier and part of speech. Multiple senses require a
numbered choice; they are never merged. The first 12 are displayed; explicit
Dictionary navigation can inspect the rest. Source URL, archive pin and license
remain attached. Normal modes retain the existing optional encyclopedia expansion
setting; free chat never acquires remote material.

“Sense 1” selects a sense. “Explain that” re-reads and validates that definition.
Unsupported attribute and cause questions remain unsupported. A new unrelated
request ends this dictionary discussion context. Final validation reconstructs
wording from the freshly verified dictionary data, checks sense IDs and the
archive hash, and rejects modified text. Context only selects the word and sense.

Selecting calculation asks for an expression and uses the existing bounded
exact-fraction arithmetic rules. Unrecognized input requests clarification.
A topic change ends that pending activity. No expression is executed as code.

A hypothetical-choice prompt records its pending structural type. A subsequent
preference is acknowledged as hypothetical, never as an event that happened.
Unrecognized choices request clarification rather than a past-tense emotional
follow-up. Explicit conversation changes clear the pending question.

All three modes apply the shared final response gate. Free chat preserves the
separate labels for software descriptions, user declarations and bundled lexical
references rather than overwriting them as unsupported casual prose. No legacy
reader, archived engine pin, resource content, or frozen benchmark label changes
are required by this implementation.

Tests in `tests/test_structured_requests.py` exercise composed requests,
mode-specific retention, sense choices and follow-ups, altered generated wording,
unknown entries, negation and entity modifiers, calculations, hypothetical
continuity, deterministic replay and browser free-chat network isolation. These
are developer-authored regression cases, not independent accuracy measurements.

## Verification for this change

Based on main `d05ce39ad31088caef59d1e4fe109df34241208c`:

- Full Python suite: 586 tests passed (327.634 seconds).
- Focused compatibility rerun: 55 tests passed after correcting source-routing
  regressions. Two older identity expectations were updated to require the new
  explicit system-description authority rather than generic smalltalk.
- UI script workflow, browser transport and crawler fixture checks passed.
- Standalone runtime built using the pinned Pyodide 314.0.7 archive; actual
  WebAssembly checks passed, including the new scenarios in all three modes.
- Protected legacy core, resources and frozen benchmark data were unchanged.

The checks exercise engine and transport behavior, not visual browser layout or
an independently deployed live crawler. Dictionary explanations stay extractive;
unsupported paraphrases and facts still require clarification or other eligible
sources. No independent human accuracy measurement is claimed.

## Live-site follow-up repairs

Dictionary references no longer request automatic encyclopedia acquisition, even
when automatic Wikipedia lookup is enabled. Explicit search remains available.
Composed introductions and self-explanations are labelled “Conversation + system
description”, including free chat.

Calculation explanation requests resolve only the immediately preceding
calculation or its explanation. The numeric expression is evaluated again with
bounded exact arithmetic; numbered binary-operation steps follow parentheses
and operator precedence. A final check recomputes and compares the explanation.
Context selects the expression but never supplies the calculated result. An
intervening topic does not revive an older calculation. Division by zero and
unsupported expressions retain their explicit error responses.

Repair validation: the 588-test full run completed with 587 passing and one
obsolete test expecting dictionary-triggered Wikipedia capture. That expectation
was replaced with a no-acquisition assertion; all 15 tests in the affected
structured-request and live-acquisition modules then passed. Actual WebAssembly
checks passed in all three modes with automatic lookup enabled, along with UI
script, browser transport and crawler fixture checks. The full suite was not
rerun after that test-only correction.
