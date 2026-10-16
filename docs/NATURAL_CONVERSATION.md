# Natural conversation within deterministic boundaries

## Goal

MPLPB should hold ordinary conversations about itself, its loaded collections,
their content, user ideas and bundled reference information. Deterministic
construction applies across conversation classes, not only to brainstorming.
The system should identify the kind of request and its current subject before
choosing content and constructing language. Missing page evidence is not a
reason to refuse a question about the interface or its own operation.

## Implemented classes

| Conversation class | Examples | Content and authority |
| --- | --- | --- |
| Self-explanation | “How do you chat?”, “What are you explain exactly how you work” | Authored capability model; composed self-explanations, never page evidence |
| Current state | “What’s the loaded MPLPB?”, “What have I loaded?” | Actual session mode and collection names |
| Available content | “What content do you have?”, “Talk about your content” | Eligible page titles and collection labels, plus the bundled seed catalog; metadata is not proof |
| Topic discussion | “Can we discuss that?”, “That’s interesting” | Current subject resolved from recent replies; fresh eligible source inspection or separately attributed seed material |
| Clarification | “I am confused”, “Can you explain that part” | Conversational framing followed by freshly checked content; original source wording is retained |
| Perspective | “What do you think?” after a topic | An invitation to examine the topic, without claiming personal experience or treating opinion as evidence |
| Wording nuance | “Other words for that meaning” after selecting a dictionary sense | Synonyms from that exact sense; ambiguous meanings require a choice |

Existing greetings, social exchanges, emotional preferences, user declarations,
recall, calculations, hypothetical reasoning and brainstorming remain available.
These are bounded supported classes, not a claim of unrestricted conversation.

## Construction and context

`topic_dialogue` recognizes a conversational act before rendering a reply. It
resolves the current subject from conversation context, then obtains content
through existing retrieval gates. A source passage is not reconstructed from an
old assistant message. Ordinary discussion does not itself trigger automatic
remote acquisition.

The frame uses an authored grammatical pattern: conversational act + modal +
transitive verb + subject. The verb alternatives “discuss” and “talk about” are
checked against WordNet sense `01036184-v`; deterministic turn selection chooses
between permitted alternatives. If the lexical resource is missing or altered,
the frame uses the authored fallback without claiming a successful lexical check.
The trace records the rule, sense and resource digest.

Source quotations remain verbatim, including numbers, negation and qualifications.
Framing and content retain separate claim units. The final validator reconstructs
the frame and revalidates the child result and source pins; changed framing,
changed quotes and unavailable sources are withheld.

Dictionary wording follow-ups retain the selected sense across turns and saved
reloads. A fresh lookup and exact renderer validate the definition and synonym
list. Synonym membership does not establish equivalent register, connotation,
truth or fit in every sentence; the system does not invent those distinctions.

## Mode boundaries

Chat and Serious mode can discuss source content while preserving their existing
scope and provenance rules. Seed notes remain labeled research notes outside
MPLPB, including in Serious mode. The general skill fallback can use those notes;
it does not load them as a ledger collection or use them to repair a failed proof.

Free chat uses the same self-explanation, seed discussion and dictionary rules,
with ephemeral context. It still does not read ledger pages, fetch remote sources
or save a transcript. Leave free chat to inspect saved MPLPB collections.

## Verification and limitations

`tests/test_natural_content_conversation.py` includes the screenshot questions,
state reload, all three modes, source alteration/retirement, seed discussion,
ambiguous dictionary meanings, sense-specific alternatives, literal/negation
boundaries and deterministic framing. The standalone WebAssembly harness also
runs the self/content/nuance sequence in all modes.

These are development regressions, not independently measured conversational
quality. Clarification currently revisits the source with conversational guidance;
it does not promise unrestricted simplification or semantic paraphrase. The
bundled seeds are a small authored collection, and the Link Grammar parser is
still not running. More patterns can be added without relaxing the existing
ownership, eligibility, ambiguity, lineage or source-support rules.
