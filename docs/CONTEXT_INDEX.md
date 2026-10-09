# Deterministic conversation context

The context index is a session-local, role-aware view of the saved transcript. It runs before dialogue and source routing in both Chat and Serious modes. Zero loaded MPLPB collections do not disable conversation memory.

* Forward replay: extract explicit `my ATTRIBUTE is VALUE` declarations, apply later corrections and `forget my ATTRIBUTE` tombstones, and preserve originating turn numbers.
* Backward lookup: intersect term postings, select up to three recent matching user turns, and show each exchange with user/assistant roles intact.
* Cross-reference: preserve source pointers on historical entries without treating an old assistant reply as a fresh verified source answer.
* Language adaptation: `When I say flarn I mean a floating garden` supplies a local meaning; `What does flarn mean?` recalls the user's definition. It cannot install executable rules or change source boundaries.
* Reference resolution: `What's its name?` can use a unique possessive declaration such as `My dog's name is Rex`. Multiple candidate referents cause clarification.

`My name is M what are you?` recognizes the introduction even without punctuation between the two acts. `What's my name?` recalls M from the user's turn. Assistant prose cannot establish the user's identity.

The algorithm indexes the retained conversation, not other users or other sessions. It replays oldest-to-newest to resolve corrections and searches the resulting postings newest-to-oldest for recall. An unchanged transcript reuses its fingerprinted index; changed history triggers a rebuild. This is bounded by the existing 1,000-turn session limit. It is not an unbounded crawler or a neural model, and its extraction grammar remains finite.

User declarations are not verified world facts. Repetition does not increase authority. Forgetting a detail suppresses its use in current slot recall; historical transcript text remains available, including explicit historical recall, until the user clears the session through the existing controls. Ambiguous or unrecognized relationships do not become deductions.

Reproduce the synthetic context replay:

```
python -m tools.evaluate_conversation --scenarios evaluation/conversation/context-scenarios.json --output evaluation/conversation/context-results.json
python -m unittest tests.test_context_index -q
```

These developer-authored checks cover the reported screenshot, correction order, forgetting, role separation, changed-history invalidation, ambiguous pronouns, reload integrity and session isolation. They are not independent human validation or proof of general language understanding.

Version 2 adds anchored polite memory questions (`Can you tell me my …?`, `Please remind me of my …`, `Tell me what my … is`) and curly-apostrophe normalization. `Forget the meaning of flarn` removes that active user-defined meaning on replay; historical text remains. Definitions are explicit adaptive data, not executable instructions or verified evidence. See [expanded evaluation](CHAT_EVALUATION.md) and [packages](INSTALLATION.md).

## Dialogue-act planner

`conversation_engine.py` runs before individual chat handlers. It segments bounded multi-act turns, recognizes greetings, explicit introductions, identity/capability questions, topic intentions and user-declared person preferences, then composes a reply. A greeting plus “I’m M” bypasses dictionary part-of-speech rejection of initials. Replay reads only user turns, so corrections, forgetting and supported topic/person references survive reload. Ambiguous pronouns request clarification.

One unresolved factual question in a mixed turn is delegated to the existing environment reader. Its answer and source metadata are retained; the social introduction is prepended. Other unresolved clauses cause the planner to defer rather than silently discard instructions. This remains a finite parser, not arbitrary semantic understanding. People and preferences are attributed to user statements, never promoted to MPLPB facts.

## Clarification branches

After an introduction mentioning MPLPB and the little monster, “What’s that?” presents both meanings as selectable questions. Naming either, or choosing “the first one” / “the second one”, establishes an explicit branch. “No MPLPB what is it” corrects the branch and answers the intended question without treating the correction as a subject-description assertion. Follow-up definitions and “tell me more” use the selected branch.

The saved session retains pending choices, the active referent and up to 32 choice events with parent and turn identifiers. Unrelated substantive turns expire pending/active selection. Generic candidates come from typed page and conversation-topic context, not arbitrary assistant prose. Topic choices delegate to the existing source reader; clarification alone never creates evidence or changes loaded collections.

### Declared names

Name memory accepts uppercase single-letter initials, multiword names, hyphens, apostrophes and Unicode letters. Explicit `My name is …` and `Call me …` declarations take precedence over ordinary word meanings. Bare statements such as `I’m tired` remain states, not names. Names are user declarations, never MPLPB evidence; correction, recall and session reload use the conversation history.
