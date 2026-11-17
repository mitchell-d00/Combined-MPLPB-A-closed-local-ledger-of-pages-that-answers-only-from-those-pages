# Constrained Local Narrator

Last reviewed: 2026-11-17.

The optional native narrator formats a result already accepted by
`mplpb_answers.pipeline.answer_query(..., mode='strict')`. It does not expand
the finite grammar, choose an owner, establish historical truth, import pages
or promote candidate interpretations. It needs no additional Python dependency.
The browser helper and assisted reader remain separate capabilities.

## Five frontend options

1. Browser-only WebLLM / transformers.js: the existing public helper path; no native service dependency.
2. Ollama: a thin client for an installed local model.
3. llama.cpp: a local OpenAI-compatible server or optional Python bindings.
4. LM Studio / another OpenAI-compatible local endpoint.
5. **Constrained Local Narrator:** one native interface for Ollama, llama.cpp's server and other local OpenAI-compatible servers. This is the implemented option.

This implementation uses raw HTTP through the existing bounded local-reader
transport. It does not install Ollama, llama-cpp-python, a model or a server.
Configure an already running server with already installed weights. No model is
required for ledger operation. Live neural generation is not established by the
mocked/protocol tests.

## Usage

```bash
mplpb-combined narrate 'Who owns the Juniper press?' --corpus ./my-ledger --no-model
python -m mplpb_answers narrate 'Who owns the Juniper press?' --corpus ./my-ledger --json
```

`--profile lab|internal|external` retains the existing delivery rules (default:
internal). Use `--json` to retain the complete strict answer contract, including
claims, source hashes, exact canonical body offsets, diagnostics, missing parts,
verification and source-assurance notices. The plain CLI prints source citations
and the source-assurance notice as deterministic output, not model-generated text.

Environment configuration (no YAML parser required):

```bash
export MPLPB_NARRATOR_BACKEND=ollama
export MPLPB_NARRATOR_MODEL=phi3:mini
export MPLPB_NARRATOR_BASE_URL=http://127.0.0.1:11434
```

| Backend | Base URL example | Protocol |
|---|---|---|
| `ollama` | `http://127.0.0.1:11434` | Existing installed-local-GGUF registry check, then `/api/chat` |
| `llamacpp` | `http://127.0.0.1:8080/v1` | `/v1/chat/completions`; set model to your served model name/alias |
| `openai` | `http://127.0.0.1:1234/v1` | Same protocol; LM Studio, LocalAI or another compatible local service |

These are backend-specific defaults if the base URL is unset. Set the model name
explicitly for your server; `phi3:mini` is a configuration default, not an automatic
download or a claim that those weights are present. Only literal loopback HTTP
addresses are accepted. DNS names (including `localhost`), credentials, remote
addresses, arbitrary paths, redirects, cloud model aliases and URL queries are
rejected. Compatible endpoints may use the server root or `/v1` as the base URL.

A loopback address cannot prove a server does not proxy to the cloud. The local
operator must disable remote forwarding. Ollama metadata is checked using the
existing adapter; other compatible servers have no uniform weight-identity
attestation. Outputs explicitly do not attest local inference or historical truth.
No API key is read or sent.

## Python contract

```python
from mplpb_answers.local_narrator import narrate, NarratorConfig

result = narrate('Who owns the Juniper press?', './my-ledger', 'internal',
                 config=NarratorConfig('openai', 'my-local-model',
                                       'http://127.0.0.1:1234/v1'))
print(result.text)
print(result.to_dict())
```

`NarratedResult` contains `question`, `profile`, `text`, `ledger_result` and
`narration`; `kind` and `answer_supported` are derived from the strict ledger
contract. They are never model verdicts. `narration.status` is `ledger_only` or
`validated_formatting`, with a reason code and validation state. Backend failures
and invalid configuration return the pure ledger result with a clear label.
`--no-model` skips configuration and inference entirely.

## Verification boundary

1. Run the normal strict path with the complete original question and profile.
2. Refusal, conflict, clarification and partial answers bypass the model. Their
   ledger text (or diagnostic message when text is empty) is displayed unchanged;
   missing obligations remain in the contract.
3. For supported answers, independently locate checker-issued spans at their
   exact offsets in intact eligible bodies. Send only those spans, the strict
   structured result and the explicit authority rules to the model.
4. V1 allows exactly three renderings of the **complete accepted text**: unchanged,
   a fixed documentary-evidence label followed by that text, or blockquote line
   prefixes. No fact-bearing word can be added, deleted or reordered. Quoted
   fragments must also occur in the checked spans. A correct citation alone never
   passes validation. Arbitrary paraphrases and keyword-based approval are disabled.
5. Re-run strict answering after the attempt, including on model failure. If any
   source, policy, eligibility, evidence or answer state changes, discard the old
   model rendering and show only the fresh ledger result. If the corpus cannot be
   rechecked, discard old claims and citations and abstain.

Inputs are capped at 28,000 UTF-8 message bytes; completed model text at 32,000
bytes; inference requests at 2,048 output tokens. The inherited transport caps
HTTP response reads at 1,000,000 bytes, rejects duplicate JSON fields/nonfinite
numbers and never follows redirects. Socket timeout defaults to 30 seconds;
`NarratorConfig.timeout` accepts 1–60 seconds. Ollama uses a separate registry
request. These socket timeouts are not a guarantee of total wall time against a
malicious trickle-response server; run only a trusted local service. There are no
retries, model downloads, tools or streaming of unvalidated text. Private model
reasoning, rejected text and raw server error bodies are not returned or saved.

Exit codes: supported answer `0`, conflict `2`, refusal `3`, partial answer `4`,
clarification `5`, invalid request/corpus `1`. Backend unavailability changes the
narration label, not a valid strict answer's exit code or authority.

## Tests and limits

```bash
python -m unittest tests.test_local_narrator -q
python -m unittest tests.test_local_narrator tests.test_answer_boundaries tests.test_local_reader tests.test_documentary_assertions -q
```

Protocol tests run real loopback fixture servers, requiring permission to bind
local sockets. They cover all three backends, exact output validation, invented
claims/citations, source corruption/retirement, a new conflicting owner, delivery
changes, partial evidence, no-model operation, malformed/oversized/truncated
responses, tool calls and redirects. These are authored software controls, not
independent historical evaluation or live-model quality measurements. This is a
bounded initial narrator implementation, not a production certification.
