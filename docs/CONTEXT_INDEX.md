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
