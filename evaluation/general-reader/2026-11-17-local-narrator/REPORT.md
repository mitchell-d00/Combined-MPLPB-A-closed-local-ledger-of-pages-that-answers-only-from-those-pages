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

Tested implementation: `cc49d6e9a31b3f39a6f92f34e84b797768d8a6d4`.
Source ZIP SHA-256: `87e5b302ed564add37d912dd4b27fa3c51adc78cbb1a4207abf4a3ea3b28f092`.

```bash
python -m tools.reproduce_boundaries --revision cc49d6e --output /tmp/mplpb-narrator-frozen-cc49d6e --suite full
```

The runner and all three extracted-source commands exited0:

| Check | Outcome | Wall seconds | CPU seconds |
|---|---|---:|---:|
| Native boundaries |51 tests passed |0.766 |0.694 |
| `python -m unittest discover -s tests -q` |1219 tests passed |362.109 |345.241 |
| `python -m tools.evaluate_public_evidence --require-capabilities --output NEW.json` |52 passed; zero observed false-supported bridges |20.609 |19.982 |

Environment: Linux x86_64, Python3.12.14,5 reported CPUs. Peak child RSS:
299,597,824 bytes, a process-lifetime child maximum rather than aggregate browser/
process-tree memory. Other compatibility checks ran concurrently; these costs
are not isolated latency benchmarks. Source bytes read and human review time are
unknown/null. Full commands, outputs and metrics are retained as `archive-*`.

The following compatibility commands ran from that same extracted revision:

```bash
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
node tests/documentary-render.cjs
node tests/browser-ai-helper.cjs
node tests/browser-model-loader.cjs
node tests/browser-webgpu-limits.cjs
node crawler/test_worker.mjs
node crawler/test_historical.mjs
node --check tools/mplpb_agent_bridge.mjs
python tools/build_browser_runtime.py --core-archive /tmp/mplpb-pyodide-core.tar.bz2 --output /tmp/mplpb-narrator-browser/index.html
node tools/check_browser_wasm.mjs /tmp/mplpb-wasm/pyodide /tmp/mplpb-narrator-browser/index.html
python tools/browser_release_smoke.py --live-url https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/ --preview-dir /tmp/mplpb-narrator-browser
```

Final exit codes were0 for each. `frontend-initial-report.json` retains all initial
commands, durations and results. Two initial Node checks (model-loader and WebGPU)
exited1 because the sandbox rejected their Python child process with EPERM; both
passed unchanged with subprocess permission (`frontend-*-retry.log`).
The initial Chromium command exited1 before any page load because Playwright's
required headless shell was missing (`browser-launch-failure.log`). After
`python -m playwright install chromium --only-shell` exited0, the unchanged smoke
command exited0 and logged PASS for both the public baseline and candidate preview
(`browser-smoke.log`). This is not deployment of this feature branch.

Actual Pyodide314.0.7 tests completed exit0 (`wasm.log`, `wasm-validation.json`).
The builder verified core release SHA-256
`2abdcc2e35208af406e07724cffa85bc582ced97e9028383ecf5462541393f95`.
The candidate HTML SHA-256 was
`b71312aa6f0ce60650b307d7a138973cf902cc047c5db7b8edd2ca4199f61041`.
Build details are in `browser-build.log`; the generated38MB HTML is not committed.
No neural weights or inference were exercised by these browser checks.

Subsequent changes only retain evidence and update documentation/handoff. Runtime
and test hashes must remain identical to the tested implementation. `checkpoint.json`
records the implementation pins, verification rules and unresolved measurements.

## Limits

Arbitrary paraphrasing is deliberately disabled; this improves presentation without
raising answer coverage or historical accuracy. Live Ollama/llama.cpp/LM Studio
model generation: **NOT RUN**. Independent semantic/human review: **NOT RUN**.
A loopback service can still forward remotely; the operator must disable that.
Generic compatible servers do not expose uniform verified weight identity. Socket
timeouts and response/token/input budgets do not establish an absolute wall-time
bound against a malicious trickle-response server. Only trusted local services
should be used. No production certification is claimed.
