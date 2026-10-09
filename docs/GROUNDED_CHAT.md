# Topic-bound conversation

A selected topic is a title plus page ID, path and hash in the saved chat. Chat keeps
that focus through small talk and session reloads. Changing collection/profile or
clearing the topic removes the focus. Every factual attribute answer rechecks its
source pin and delivery rules. Changed or withheld pages require reselection.

Example with a loaded Moon page containing an explicit diameter statement:

```
topic Moon
how big is it?
and how old is it?
what are we talking about?
show source
```

`Let's talk about Moon` and `discuss Moon` explicitly select an exact eligible title.
If it is missing, chat offers source expansion. `how big is it?` requests diameter;
`what is its radius?`, age, height, length, width, mass, distance and orbital period
have explicit question grammars. Attribute extraction requires a named subject,
declarative statement, numeric value and unit. Answers quote complete source
statements, preserving qualifiers and offsets into the page's plain body text.
No unit conversion, calculation or general semantic entailment is performed.
Different values stop as a conflict, even if unit conversion might reconcile them.

A question about permission cannot be answered by firing instructions. Questions
with unsupported conditions or different subjects stay unsupported instead of
returning a page because its title overlaps. Unsupported replies retain the focus
and offer Wikipedia/search or source-import controls. Clicking a suggestion fills
the composer; sending it explicitly authorizes that search. Search builds a *new*
collection. Adding a URL/text through source-import controls adds to the chosen
collection. Bare `yes` does not silently initiate a source fetch. Imported material
still goes through the normal pin/profile checks and is not automatically true.

`what is it?`, summary and source commands remain explicit page/excerpt views, not
proof that every possible question has an answer. Structured relationship commands
remain governed by their separate fact rules. The core Ask/CLI lexical reader is
unchanged: these answer-suitability checks apply to the chat attribute layer.
Dictionary commands remain explicit lexical-reference operations.

`clear topic` removes focus; `just chatting` starts casual conversation. Without a
selected topic, casual statements receive open conversational prompts, and familiar
social questions have finite replies. Literal eligible title mentions can invite a
source-backed conversation, requiring acceptance. Working notes are declarations,
never evidence. Unknown world questions offer sources rather than fabricated facts.
This is an improved deterministic chat interface, **not an LLM or unrestricted
human-like conversation**. Source quotations are claims made by the source, not an
independent truth guarantee. Recognition is deliberately conservative and will miss
many valid paraphrases; see the recorded evaluation failures.

Validation artifacts and the independent protocol: `evaluation/contextual/`.

## Chatty conversation without a language model

Everyday conversation now has a small saved turn-taking state. For example:

```text
You: Iv had a bad day
MPLPB: I’m sorry it’s been rough. Want to talk about it?
You: sure
MPLPB: Okay, tell me about it. What happened?
You: My boss yelled at me
MPLPB: That sounds frustrating. Want to say a little more about that?
```

“Just listen” gives short acknowledgments without questions. “Change the subject”
offers a light prompt. “Not now” and “stop chatting” stop the invitation. Good-day
and tired-day openings have different replies. Common spelling/contraction variants
are accepted. Replies come from local phrase rules, vary with the turn, and avoid
immediate repetition. There is no provider, account, API key, model download or
network call. This is conversational turn-taking, not unrestricted AI generation.

The saved state contains the stage, reply style, turn count and last reply—not an
emotional profile or new ledger facts. Conversation text remains in the normal
saved transcript. Invitations resume after reload; unrelated turns or collection/
profile changes expire them. A literal eligible topic mention takes priority and
asks before selecting it. “Sure” can accept that offer too. Factual questions still
use MPLPB’s source rules, and casual replies retain but do not alter a selected
page. Social reactions are acknowledgments, not verified judgments about events.

Checks include consent/decline, reloads, listening mode, negation, factual-question
routing, topic-offer priority, transcript pins and absence of automatic fetching.
These are developer regression tests, not a human evaluation of conversational quality.
