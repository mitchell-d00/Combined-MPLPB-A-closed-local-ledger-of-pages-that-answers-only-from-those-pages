# General answer pipeline — 2.1.0rc1

This release candidate adds domain-independent passage reading without changing
MPLPB's source eligibility rules or promoting model output into deterministic
support. Default strict queries stay offline and use the bounded compatibility
reader. An explicitly configured native host can additionally use installed local
Ollama models to interpret arbitrary saved prose.

The new path is implemented and protocol-tested. Live-model accuracy, calibration
and independent cross-domain evaluation remain unverified in this environment.
The strict pottery result remains 6/59; this patch does not claim a measured
increase by relabelling model-assisted answers as supported answers.

## One response policy

CLI Ask and the desktop/browser query bridge call `mplpb_answers.pipeline.answer_query`.
The answer contract is `answer-contract-v1`. Existing strict `reader.kind` values
and CLI exit codes remain compatible. `reader.answer_contract` supplies the richer
contract; `reader.answer_diagnostics` supplies the reason. Explicit inspection and
legacy reproduction remain separate interfaces.

| Contract kind | Meaning | `answer_supported` |
| --- | --- | --- |
| `supported_answer` | Existing bounded grammar/procedure checks passed, with source-body citations. | true |
| `model_assisted_answer` | Exact citations and separate model assessment passed; semantics remain probabilistic. | false |
| `partial_answer` | Only the displayed claims passed review; unresolved parts are explicit. | false |
| `clarify` | Subject, conditions or requested scope need clarification. | false |
| `conflict` | Deterministic ownership conflict or explicitly labelled model-reported competing evidence. | false |
| `abstain` | The pipeline cannot currently establish an answer. | false |

Neither a successful HTTP request nor CLI exit code 0 proves deterministic support.
Assisted results never use legacy `kind=return`; strict clients remain conservative.
The default relay continues to request strict mode. Chat is still its existing
rule-based workflow; configuring an Ask reader does not enable model-generated chat.

## Eligibility before retrieval

The passage index calls the existing provenance gate with the **complete original
question**. It verifies the gate policy version, exclusions, profile and corpus
snapshot before preparing body text. Source hashes, current status, pinned lineage,
depth, external restrictions and original not-for terms remain authoritative.
The core and frozen source/benchmark files are unchanged.

For prose-enabled profiles, eligible pages remain available even with no shared
query words. BM25 term frequencies and a page-diversity discount rank paragraphs;
strong second paragraphs precede unrelated zero-overlap fallback pages. The local
reader may propose up to three retrieval paraphrases. Those affect ranking only;
they cannot remove original question restrictions or admit excluded pages.
Prose-disabled profiles retain their original scope-match boundary.

Retrieval records the selected passages, query variants, eligible-page count,
search completeness and shared evidence roots. A finite selection never proves
that absent or conflicting evidence does not exist elsewhere. Shared ancestry
never becomes independent corroboration merely because several pages repeat it.
This patch does not add embeddings or claim general semantic retrieval accuracy.

## Evidence and review

The body projection `body-text-no-headings-v1` uses an HTML parser, excluding
headings, scripts, styles and metadata. Paragraphs retain their context. Oversized
paragraphs use overlapping windows marked `context_truncated`; an answer relying
on one becomes partial and asks for inspection of the complete conditions.

The reader proposes atomic claims, qualifications, exact passage quotations,
missing parts, a possible clarification and an outcome. The coordinator:

1. Preserves the original question, rather than deleting awkward modifiers.
2. Validates a closed JSON schema with bounded fields and no tools or commands.
3. Requires every claim to identify a supplied eligible passage and exact quote.
4. Computes Unicode-code-point offsets itself. Repeated quotations require enough
   context to identify a unique location; the model does not count characters.
5. Rejects proposed numeric literals absent from their cited passage context.
6. Requests a separate review of subject, relation, conditions, negation, temporal
   scope and completeness against all supplied competing passages.
7. Rechecks source state, serving policy and model digests before accepting output.

The reviewer may be a different local model. Separate calls or different names do
not prove independent errors; `independence_verified` remains false. Exact quotes,
matching numbers, structured JSON and agreement between models do not prove
entailment or source truth. Model assessments stay explicitly labelled. Rejected
claims are not silently presented as a complete answer.

Model-reported confidence is uncalibrated. The default 0.8 threshold is an
experimental configuration, not a measured safety guarantee. It must be chosen
on separate calibration data before a final test. Model results are not written
into the source ledger or specialist work state automatically.

## Native local-reader setup

Install a suitable local model separately, with hardware and at least a 32K context
configuration appropriate to that model. MPLPB does not install/download weights,
choose a hosted provider or use an API key. For a trusted Ollama service, disable
cloud features before supplying private source text. Ollama documents, for example:

```sh
OLLAMA_NO_CLOUD=1 ollama serve
```

See [Ollama's official local-only guidance](https://github.com/ollama/ollama/blob/main/docs/faq.mdx),
[chat API](https://docs.ollama.com/api/chat), and
[structured outputs](https://docs.ollama.com/capabilities/structured-outputs).
The adapter uses `/api/tags` to identify installed local GGUF weights and capture
digests, then nonstreaming `/api/chat` requests. It rejects reported remote models,
cloud aliases, redirects, unpinned changes and unfinished/tool-call responses.

```sh
python -m mplpb_answers ask /path/to/corpus "How should an operator restart safely?" --answer-mode assisted --reader-model YOUR_INSTALLED_MODEL --json
```

Optional flags include `--reviewer-model`, `--reader-digest`, `--reviewer-digest`,
`--max-passages` and `--max-context-chars` (defaults: 12 passages and 8,000
characters). A configured model is contacted only
for an explicitly assisted query that the strict reader cannot already answer.
A strict body-evidence conflict is not overridden by a model.

To enable the local web form:

```sh
python tools/ledger_ui.py --root /path/to/corpus --reader-model YOUR_INSTALLED_MODEL
```

Select **Assisted** under Evidence standard. Its results show model-assessed
claims, exact quotes, qualifications and unanswered parts. The option is disabled
on hosts without a configured reader. Connection/model settings are host arguments;
query JSON cannot redirect the reader to a different endpoint or model.

The default endpoint is `http://127.0.0.1:11434`. Only literal IPv4/IPv6 loopback
HTTP addresses are accepted, with no credentials, arbitrary URL paths, DNS names,
redirects or proxy handling. Calls have bounded requests, responses, context and
timeouts. No model tools or thinking output are enabled, persisted or exposed.
The adapter requests 32768 context tokens and 4096 output tokens, rejecting wire
requests above a conservative 28000-byte input budget. The trusted runtime must
honor the configured context; reducing retrieval size is preferable to accepting
silently truncated model input.

Loopback alone cannot stop a local server from forwarding requests. Cloud-disabled
configuration and a trusted runtime are host responsibilities. Model digests are
service metadata, not hardware/provider attestation. Prompt injection can still
mislead a model's semantic judgment; the adapter gives it no execution tools or
source-write authority, and its accepted prose is never a deterministic proof.

## Diagnostic abstentions

| Code | Interpretation |
| --- | --- |
| `interpretation_unsupported` | Eligible passages exist but the strict grammar cannot interpret the request. |
| `evidence_not_established` | No accepted answer was established; corpus absence is unknown. |
| `restricted_or_unavailable` | Eligibility/profile restrictions prevent a usable evidence set. |
| `no_eligible_sources` | No eligible body passages are available under this request/profile. |
| `retrieval_ambiguous` | Candidate ownership is ambiguous, without necessarily conflicting body facts. |
| `reader_unavailable` | No reader is configured, a model is missing, or local inference is unavailable. |
| `reader_budget_exceeded` / `retrieval_budget_exceeded` | The configured evidence/request budget was exceeded. |
| `invalid_citation` / `ambiguous_citation` | A quotation is fabricated, mismatched or not uniquely located. |
| `verification_failed` | Claim review rejected subject, relation, scope or support. |
| `below_assisted_threshold` | An uncalibrated score is below the configured threshold. |
| `source_changed` / `model_changed` | Current source policy/state or model identity changed; rerun. |

Legacy strict `not_in_corpus` remains for compatibility. Its diagnostic explicitly
avoids treating unsupported interpretation as proof that the information is absent.

## Evidence required before a general-quality shipping claim

Use the [packaged evaluation workflow](../evaluation/general-reader/README.md).
It freezes suites and policy, exports answers and exact evidence for human review,
and scores pinned judgments independently of model self-assessment. It separates
strict support, model-assisted return precision, partial answers, complete
answerable coverage, retrieval recall, per-domain results and risk/coverage curves.

The reference release policy requires fresh test data, a prior calibration-run
reference, live inference, attributed complete human review, at least 200 reviewed
model-assisted returns, at least three domains, at least 60% complete answerable
coverage per domain and a Wilson 95% error upper limit no greater than 2% per domain
for assisted returns. These are declared candidate targets, not achieved results.
Freeze a different justified policy before a run if the product's risk budget differs.

A six-answer result, zero observed errors, a large number of strict answers, or a
scripted HTTP fixture cannot certify this reader. Statistical checks do not verify
reviewer independence, dataset freshness or distributional assumptions. Even a
passing report is only eligible for human release review. General-quality release
is currently blocked until the missing live and independent evidence is supplied.
