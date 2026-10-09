# Synthetic conversational evaluation

This is developer-authored regression evidence, not independent human evaluation or a fluency rating.

## Reproduce

```
python -m unittest discover -s tests -q
python -m tools.evaluate_context_matrix --output evaluation/conversation/context-matrix-after.json
python -m tools.evaluate_conversation --scenarios evaluation/conversation/expanded-scenarios.json --output evaluation/conversation/expanded-results.json
```

The context matrix checks 20 subjects × 8 personal-memory question forms × 2 modes, plus 40 forgetting checks: 360 checks. Each requires the corrected value, absence of the old value, user-declaration authority and no fabricated source. Each scenario has an isolated save profile; transcript integrity is checked. The runner exits unsuccessfully when an expectation fails. Latest recorded result: 360/360.

The phrasing ablation tests the memory router with normalization disabled and enabled: 80/160 versus 160/160 recognized questions. It is a controlled router comparison, not a historical full-system baseline. See `evaluation/conversation/phrasing-ablation.json`.

Generated unit checks also exercise 990 arithmetic expressions and wording variants, 40 syllogisms including invalid converses, and 160 memory paraphrases. These are subcases inside test methods, not 1,190 separately counted unittest methods.

The expanded replay records 220 turns across 28 scenarios in both modes: greetings, emotions, listening preference, source topics, arithmetic, explicit-premise reasoning, brainstorming, goals, and source boundaries. Its outputs are observations, not automatically graded fluency successes. Novel-topic brainstorming preserves the chosen topic and option but repeats a finite family of transformations. Some source extracts retain awkward imported wording; dictionary senses may require disambiguation. These remain limitations.

## Changes motivated by runs

* Normalize curly apostrophes in personal declarations.
* Recognize polite memory questions without expanding factual ownership rules.
* Apply correction and forgetting order reproducibly, including user-defined meanings.
* Explain missing evidence directly in Serious mode instead of asking the user to repeat an already specific question.
* Isolate evaluation save profiles so the session capacity limit is tested separately from language behavior.

## Independent protocol

Freeze a commit, rule configuration and source snapshots before evaluation. Have evaluators outside the project select unfamiliar corpora and author questions without inspecting the rules. Include answerable, unanswerable, ambiguous and misleading-overlap questions; paraphrases, corrections and multi-turn topic shifts; both conversation modes and zero loaded collections. Separate tuning examples from a held-out set.

Two independent reviewers should label answerability, citation support, scope compliance, memory correctness and conversational relevance; reconcile disagreements without changing the frozen run. Publish every prompt, response, source identifier and adjudication, including failures. Report unsupported-answer rate and abstention precision alongside coverage; report conversational quality separately. Synthetic passing counts cannot replace this evaluation.
