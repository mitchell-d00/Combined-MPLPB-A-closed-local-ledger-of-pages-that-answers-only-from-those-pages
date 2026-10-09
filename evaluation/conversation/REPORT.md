# Synthetic conversation evaluation

This is a developer-authored regression exercise, not independent human evaluation and not proof of human-level conversation. The baseline is main commit `50f70cb48902bf8979f9c1a650c33d655925aeff`. Tests were run on 2026-10-09.

## Live user-interface observations before changes

The published browser application was tested through its actual text field and Send button, without calling internal application functions. It started in Chat with no active collections.

* `Hi, I’m Alex. How are you?` produced a missing-factual-answer fallback. `I had a bad day` worked, but detail was handled by a generic echo.
* An explicit hypothetical syllogism and `What is 12 times 7?` both produced the same factual-answer fallback.
* Brainstorming produced three numbered directions, but `The second one` merely echoed the selection instead of developing it.
* Load all successfully selected eight collections. The compound greeting in Serious mode still produced generic page guidance.

## Repeatable protocol

Run `python -m tools.evaluate_conversation --output evaluation/conversation/after.json` from the repository root. Each scenario starts an isolated saved conversation, once in Chat and once with loaded MPLPB. Network acquisition is not enabled in this engine replay. The live UI exercise tests actual transport separately.

The initial seven scenarios contain 27 user turns per mode (54 baseline turns). The additional goal/constraint scenario contains three turns per mode; it is a post-change extension, not a baseline comparison. JSON artifacts contain literal questions and answers, response kind, authority and source counts. No quality score is inferred from merely returning a string.

Review each turn for:

1. Request completion: does the reply perform the requested conversational act?
2. Continuity: are names, user choices, goals and constraints retained accurately?
3. Reasoning: is the conclusion valid only under the stated premises; is the converse rejected?
4. Boundaries: are user premises and creative ideas separate from MPLPB evidence?
5. User control: does listening avoid unwanted questions; do modes retain their scopes?
6. Restraint: do unsupported factual questions remain unsupported instead of becoming invented answers?

## Rule changes

`tools/dialogue_rules.py` is a shared layer before existing source routes in both modes. It parses complete bounded arithmetic/premise forms, separates social clauses, recovers numbered choices from the last actual assistant turn, and stores explicit project goals/constraints in the session. Unrecognized requests fall through to the existing reader. Names are recovered from user introductions rather than assistant assertions.

Arithmetic uses a restricted AST and exact rational arithmetic with size limits, not `eval`. Hypothetical reasoning supports one explicit universal-membership form and refuses the invalid converse; no universal language-understanding claim is made. Traces record the rule and unverified premises. Neither calculation nor conversational state creates a source pin.

## Replay observations

The final replay contains 60 turns across both modes, including the six added goal/constraint turns. In the 54 comparable turns, the specific generic “can’t supply a factual answer” fallback occurred nine times before and zero after; literal `You said:` echoes occurred five times before and zero after. These are narrow regression indicators, not a conversation-quality score. Serious-mode generic guidance used different wording and is visible in the raw baseline.

Both modes now complete the compound introduction and name recall, numeric calculations, hypothetical inference and invalid-converse response, and numbered brainstorming selection. Unsupported size/permission questions still lack an answer; their wording no longer asks the user to guess a fact, and a new kiln question no longer inherits the previous Moon topic.

## Remaining limits

The grammar remains finite. Arbitrary multi-step logic, implied facts, elaborate creative writing and every possible paraphrase are not supported. Brainstorming constructs topic-bound directions; it is not a general creative model. Some generic topic follow-ups still ask for clarification, and retrieval remains lexical. A dictionary meaning does not prove an opinion about an object. Independent authors must still supply unseen corpora and adversarial questions before any independent precision claim is justified.

## Validation

See the committed before/after transcripts and `tests/test_dialogue_rules.py`. The tests cover both modes, deterministic replay, transcript integrity after reload, source separation, invalid converse, bounded arithmetic, arbitrary project topics and session isolation. The actual WebAssembly smoke test exercises the same dialogue paths in the packaged application.

Release checks: 446 engine regressions passed; after the first-turn mode initialization fix, the ten dialogue tests and UI workflow check passed again. Browser transport, fixture crawler and the actual WebAssembly build passed, including the new dialogue scenarios in both modes.
