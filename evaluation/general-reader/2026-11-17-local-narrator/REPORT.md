# Constrained Local Narrator implementation evidence

Baseline revision: `937b15712714f5155807b2478ef51592a14fc0d7`.
Date: 2026-11-17. Scope: authored software tests and HTTP protocol fixtures;
not independent historical accuracy or live neural-model quality evidence.

## Implemented boundary

`mplpb_answers/local_narrator.py` calls the existing strict coordinator first.
Refusal, ambiguity, clarification and partial evidence bypass inference. For an
accepted result, checker-issued citations are re-located in intact eligible
canonical bodies. The model sees only those verbatim spans, the question/profile,
structured strict result, authority prompt and allowed complete renderings.

Output must exactly equal one of three full-answer renderings. Keyword overlap,
an exact quotation alone, unrelated text elsewhere in the same eligible page and
model confidence cannot pass. Quotes must also match checked spans. A fresh strict
query rechecks source and policy state after every attempt. Changes discard old
narration; loss of the corpus discards old claims and citations and abstains.
No unvalidated text is streamed, retained as evidence or printed in error traces.

Ollama uses the existing loopback reader transport and installed-weight registry
check. llama.cpp and generic OpenAI-compatible local servers use the same bounded
transport for `/v1/chat/completions`. No new dependency, cloud client, server or
model download is added. Existing ask/ownership/grammar/hash rules are unchanged.
The CLI adds `mplpb-combined narrate QUESTION --corpus PATH [--no-model] [--json]`.

## Baseline and material failures

`python -m unittest tests.test_answer_boundaries tests.test_local_reader -q`
initially exited1 with seven loopback socket PermissionErrors in the sandbox;
`baseline-sandbox-failure.log` preserves the failure. With local socket permission,
the same baseline command exited0:17 tests passed in3.662s (`baseline.log`).

The first new non-HTTP test run exited1 with two fixture failures
(`initial-fixture-failures.log`): the fixtures asserted conflict after adding a
second exact-field source with the same value. The existing coordinator accepts
agreeing explicit field values, so the fixtures did not create their alleged
conflict. They were changed to conflicting field values, and a separate real
statement-grammar duplicate-owner control was added. No core behavior or frozen
fixture was changed to make these assertions pass.

## Focused results

```bash
python -m unittest tests.test_local_narrator tests.test_answer_boundaries tests.test_local_reader tests.test_documentary_assertions -q
```

Exit0:66 tests passed in5.406s (`focused.log`). This includes18 narrator tests,
actual loopback protocol fixtures for all three backends, refusal/partial bypass,
exact rendering validation, false claims and citations, qualifiers, source
corruption/retirement/deletion, a new conflicting owner, a delivery-policy revision,
restricted/not-for evidence, budgets, tools, redirects, duplicate JSON fields,
oversized and truncated responses, configuration, and CLI exit codes.

## Frozen validation

Pending: freeze the implementation and run the full Python and public-evidence
commands from an extracted committed archive. Subsequent evidence-only edits must
not change the tested runtime or test bytes.

## Limits

Arbitrary paraphrasing is deliberately disabled; this improves presentation without
raising answer coverage or historical accuracy. Live Ollama/llama.cpp/LM Studio
model generation: **NOT RUN**. Independent semantic/human review: **NOT RUN**.
A loopback service can still forward remotely; the operator must disable that.
Generic compatible servers do not expose uniform verified weight identity. Socket
timeouts and response/token/input budgets do not establish an absolute wall-time
bound against a malicious trickle-response server. Only trusted local services
should be used. No production certification is claimed.
