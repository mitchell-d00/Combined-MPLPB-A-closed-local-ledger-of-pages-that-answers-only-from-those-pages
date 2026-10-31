# User-built collections: growth, policy answers and limits

This is a focused local implementation on top of `f425a05`, not a claim that
MPLPB autonomously improves its own engine. No independent participants were
available. Development and separately frozen developer evaluation inputs are in
`evaluation/user-collections`; neither is independent human evidence.

## What actually builds automatically

| Stage | User action / permission | Automatic behavior | Boundary |
| --- | --- | --- | --- |
| Supply text | Create/select a collection and import pasted text | Preserve raw bytes, capture manifest, sealed page and later revision lineage | Pasted text has unknown authorship; its machine-created record is withheld externally |
| Acquire sources | Explicit Wikipedia search/import; automatic lookup only with the visible setting enabled | Bounded capture/crawl, source pins and collection construction | New UI profiles now default automatic Wikipedia lookup **off**; previously saved choices remain in force |
| General web acquisition | Configure the separate crawler and token, then request it | Validate returned bytes, capture and seal sources | Search snippets are not evidence; server-reported acquisition is not independently verified authorship |
| Rebuild collection | Successful import or source selection | Reconstruct the readable collection from pinned records | No new factual authority; damaged captures stop rebuilding |
| Index and retrieve | Ask a question | Normalize terms; construct eligible passages/ranking when needed | Derived representations do not certify an answer or change source bytes |
| Answer | Ask in strict mode, or explicitly select configured native Assisted | Apply bounded support rules or separately labelled model review | A relevant page or quotation alone does not establish support |
| Save context | Ordinary saved chat; explicit working-note command | Persist transcript, source pointers and notes | Notes cannot establish source facts or execute instructions; free chat is ephemeral |
| Revise | Reimport a changed source under the same title/URL | Create a successor and pin the predecessor; recheck on later queries | Retired citations are historical; stale derived evidence is not freshly valid |
| Interpret more wording | Install a reviewed software update, or configure an installed local reader | No autonomous grammar learning from added documents | Collection growth is not engine improvement |
| Modify code | Developer edits and verifies code | Nothing in an imported source can authorize code changes | No self-modifying code, model training or automatic permission escalation |

Import responses expose `collection_build`: acquisition transport, source origin,
unknown authorship, current source count, external withholding, derived-view
behavior and explicit `engine_changed:false` / `application_code_changed:false`.
The source form displays the distinction after import. Ask diagnostics provide
non-executing next-step guidance; inspecting a citation remains separate from
claiming that the source is factually true.

## Focused answering repair

The retained researcher pilot retrieved all 18 gold passages but answered only
12/18 questions. On the new user-imported development collections the unchanged
engine answered 4/12 answerable questions despite zero retrieval misses. The
measured bottleneck was interpreting policy language, not finding the pages.

`mplpb_answers.policy_evidence` adds two finite, domain-independent relations:

| Question examples | Licensed body statement |
| --- | --- |
| What does SUBJECT require? / What is required for SUBJECT? / What are the requirements for SUBJECT? / What requirements apply to SUBJECT? | SUBJECT requires REQUIREMENTS. |
| When can SUBJECT be ACTION? / Under what conditions may SUBJECT be ACTION? | SUBJECT can/may be ACTION only when/if/after CONDITION. The modal and action must match. |

Subjects are complete bounded noun phrases, never benchmark IDs or topic-specific
answers. Only an indefinite singular such as “a loan” licenses a regular plural
such as “loans”. Unknown modifiers, dates, negation in the question, and unresolved
pronouns are not discarded. Other grammar paths remain separate.

Answers copy the complete policy sentence, including inline conditions, negation,
exceptions, quantities and alternatives. A neutral document-description sentence
may precede the final policy statement in an imported paragraph. Other surrounding
prose, inherited conditional context, unresolved list references, quotation and
speculation conservatively abstain. Competing declarations and explicit denials
do not pick a ranked winner. The finite guards are not unrestricted discourse or
semantic understanding; unfamiliar contextual qualifications can remain outside
this contract.

This is deterministic extraction of a **source-declared policy**. Necessary
conditions do not prove sufficiency, real-world readiness, safe execution, factual
truth, or authenticated authorship. It does not execute a procedure or infer a
missing step. Model-assisted output retains `answer_supported:false`.

## Failure diagnosis

Runtime diagnostics distinguish unavailable/restricted sources, unsupported
interpretation, unresolved policy wording, lexical ambiguity and matching body
conflicts. They include a next step rather than silently acquiring new material.
No eligible page is not proof that the requested fact does not exist anywhere.
When source wording is unknown, missing evidence cannot always be distinguished
from a reader limitation without additional review.

The evaluation runner has frozen gold passages and can additionally distinguish
retrieval misses, unsupported wording and answers absent from its **fixture**
sources. That oracle-assisted diagnosis is not an omniscient runtime capability.
Application/capture integrity errors are errors, not correct refusals. Deliberate
capture-damage checks confirm rejection; their counts remain separate from
answer correctness.

## Changing state and permissions

The public answer pipeline fingerprints corpus state, exclusions and serving
policy before answering and rechecks before returning strict or assisted results.
If state changes, it clears claims, quotations, supporting records and old passage
data. The native app serializes query/import operations with its existing lock
and returns the pipeline's checked source bundle. A changed source cannot keep
an old supported answer merely because its earlier quote was valid.

These are optimistic state checks, not an atomic transaction with arbitrary
external filesystem writers or proof of an unchanged world after delivery.
Query a directly selected collection; unresolved routing is not a source grant.
Existing seals, origin/depth rules, lineage, exclusions and delivery profiles
continue to decide eligibility. Source text cannot grant itself a different
origin, external-delivery policy, execution right or application rule.

## Backup and recovery assessment

The study copies a quiescent complete application workspace to a new directory,
then reopens sources, lineage and associated notes in a fresh process. This tests
these fixtures' filesystem portability and recovery; it is not just transcript
export. Deliberate capture corruption must produce an error rather than an answer.

There is still no versioned, validated, user-facing portable collection backup
format or restore UI. Transcript export does not include the complete raw-source
and lineage store. Browser IndexedDB clearing, schema upgrades, large collections,
concurrent backups and relocating a specialist database with absolute corpus
registrations need separate work. Do not substitute an unchecked ZIP import.

## Reproduction and evidence

```sh
python -m unittest tests.test_policy_evidence -v
python -m tools.evaluate_user_collections evaluation/user-collections/development.json --output NEW_DEV.json
python -m tools.evaluate_user_collections evaluation/user-collections/evaluation.json --output NEW_EVAL.json
python -m unittest discover -s tests -q
```

Inputs and acceptance thresholds were frozen before implementation. The separate
evaluation uses new task names, values and wording; the same developer created
both sets, so it is not an independently authored or blinded benchmark. Historical
reports and the original pottery/NPC question files are not rewritten. The NPC
runner accepts an exact-gold supported improvement without changing its frozen
old refusal label; refusals still reduce coverage.

Reports record the suite and acceptance pins, exact code hashes, base/code revision,
all answers, literal correctness, answerable coverage, unnecessary refusals,
conflicts, citation checks, retrieval failures, workflow completion, query latency,
retrieved characters, storage and zero model/source-network use for pasted cases.
The oracle requires the complete frozen policy sentence and valid citation; it
cannot certify general semantic accuracy or human usefulness.

Packaged verification commands:

```sh
python tools/build_browser_runtime.py --core-archive PINNED_CORE.tar.bz2 --output PREVIEW/index.html
node tools/check_browser_wasm.mjs PYODIDE_DIRECTORY PREVIEW/index.html
node tools/check_collection_wasm.mjs PYODIDE_DIRECTORY PREVIEW/index.html NEW_WASM_REPORT.json
python -m tools.browser_collection_policies --preview-dir PREVIEW --output NEW_BROWSER_REPORT.json
```

The focused WebAssembly check executes actual packaged Python, source revision,
citations, saved-state reopening, conflicts, withholding and fixture acquisition.
It is not a DOM/IndexedDB browser test. The Chromium script separately checks
visible answers, citation clicks, revision, reload, offline queries and denied/
permitted acquisition against an HTTP fixture. The current environment's Chromium
launch failed; no local real-browser pass is claimed. The policy-specific check
also runs in PR and extracted-ZIP CI; consult the exact-head Actions result for
subsequent browser verification.
Wikipedia fixture networking is not live Wikipedia verification.

Independent collection builders, their own questions, semantic grading and human
usability remain outstanding. The next high-value product addition is a validated
complete backup/restore workflow; broader interpretation should follow new
failure evidence rather than benchmark-specific rules.
