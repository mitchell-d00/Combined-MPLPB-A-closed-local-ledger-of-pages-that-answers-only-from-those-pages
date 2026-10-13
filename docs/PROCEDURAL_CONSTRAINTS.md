# Procedural constraints and free-chat comparison

This adds a finite procedure format, not a general procedural language model.
Existing unstructured pottery pages are not silently rewritten or promoted.
Context selects a procedure or step; it never proves a claim, completion,
condition, permission, or warning exemption.

## Source-authored procedure format

Put one complete `MPLPB-PROCEDURE/1 ` JSON block on a body line in a normal sealed
ledger page. Use a preformatted body when authoring HTML. The source must remain
current and pass the existing provenance, lineage and delivery-profile gates.

```text
MPLPB-PROCEDURE/1 {"id":"paper-fold","steps":[{"order":1,"action":"Place the paper flat.","prerequisites":[],"conditions":["Use a dry sheet."],"warnings":["Keep the work surface clear."]},{"order":2,"action":"Fold the sheet in half.","prerequisites":[1],"conditions":["The edges must align."],"warnings":["Do not tear the sheet."]}]}
```

Every step requires all five fields. Order is contiguous, starting at one.
Prerequisites reference earlier steps, and each later step must explicitly
require its predecessor. This first schema supports linear sequences only;
branching, optional steps, loops and conditional execution need further rules.
Conditions and warnings are source text, not executable predicates. Empty lists
mean **none declared by that source**, not proof that no hazards or conditions
exist. The system attaches source ID, path, hash, exact block quotation and a
JSON pointer to each step. Conditions, qualifiers and warnings are never dropped
from the constrained rendering.

Use either chat, the Ask UI, or the supported CLI:

```sh
python -m mplpb_answers ask /path/to/corpus 'procedure paper-fold'
python -m mplpb_answers ask /path/to/corpus 'step 2 of procedure paper-fold'
```

These commands inspect source-declared instructions; they do not assert readiness
or completion. Conflicting definitions, missing fields/steps, forward or cyclic
prerequisites, and unavailable source evidence refuse. No procedure is assembled
from independently matching fragments or competing collections.

In chat, `next step` uses only the saved identifier and position, then rechecks
current eligible bytes. It does not advance on the assumption that a displayed
step was completed. Notes such as “step 1 is done” cannot override that boundary.
The reply identifies the prerequisite gap and offers explicit step inspection.
Automatic verification of real-world completion is **not implemented**. A changed
source/profile requires reselection; missing future steps never produce invented
continuations.

After language realization, procedural responses are checked again against fresh
source tags and exact constrained rendering. Ordinary supported answers, attribute
extractions and relation proofs also receive a final evidence check. Local source
pins and pinned dictionary resources retain separate verification paths. A guard
failure replaces the response with an explicit refusal before persistence.
These checks enforce their finite contracts; they do not establish unrestricted
semantic correctness for every possible construction.

## Automatic tagging

Source inspection automatically exposes draft tags for literal numbered body
lines (`1. ...` or `1) ...`). They can also be obtained without altering the ledger:

```sh
python -m mplpb_answers tag-procedure /path/to/corpus page-0001.html
```

The action and declared number are copied exactly and source-pinned. Explicit following lines named `Prerequisites:`, `Conditions:` and `Warnings:` are also copied, with individual quotation pins; repeated declarations remain ambiguous. `none` is accepted only as an explicit source declaration. Missing
prerequisites, conditions and warnings remain `null`, with
`eligible_for_generation: false`. The tool does not infer them from adjacency or
chat context. A human must reconcile these gaps with eligible source evidence,
then author a complete procedure block through the normal revision workflow.
When an eligible source already has an exact `Procedure: ID` heading, numbered
actions, and explicit `Prerequisites:`, `Conditions:` and `Warnings:` lines for
every step, the reader automatically tags and validates those source declarations
without requiring a JSON rewrite. Unknown lines or absent fields still refuse.
The standalone draft exporter does not itself promote or edit any source.
The original page and revision history are retained. Automatic tagging therefore
assists preparation; it does not automatically solve the frozen procedural
benchmark. Existing frozen labels are unchanged.

## Off-the-record free chat

Choose **Off-the-record free chat**, or type `free chat`. This runs the existing
deterministic conversational rules, with a bounded echo/question fallback for
unrecognized inputs. Free-chat messages introduce no model, randomness, source retrieval, web request,
import, or source-backed answer. Separate source-management controls still operate
on their own explicit requests. Same inputs and conversational state yield
the same wording. Context is conversational state only.

The response is labeled **not source-backed**. No free-chat transcript is saved
by MPLPB, no transcript hash is presented, and export/resume is unavailable.
State is held only in the running application. Restart clears it; `leave free
chat`, `chat mode` or `serious mode` ends that ephemeral session. Earlier saved
constrained chats are retained. This does not promise to suppress independent
browser, operating-system, server or network logging.

“Unconstrained” here means bypassing the source-answer construction path for
conversation. It does not mean that arbitrary generated factual/procedural claims
become supported, or that provenance safeguards are disabled for MPLPB.

Run the explicit synthetic comparison:

```sh
python tools/evaluate_chat_modes.py
python -m unittest tests.test_procedure_constraints -v
```

`evaluation/reliability/mode-comparison.json` contains public synthetic prompts,
not a captured off-the-record conversation. This is a behavior comparison, not an
accuracy comparison between equivalent factual answering systems.

## Limits

Hashes prove consistency with pinned bytes, not source truth or safe procedure
content. Finite grammar and deterministic generation do not establish general
language understanding. The numbered-line tagger cannot extract hidden conditions
or warnings, and the procedure reader cannot authenticate real-world execution.

## Compatibility and rollback

The archived core, original sources and capture pins are unchanged. The new
procedure layer is standard-library-only and ships in `mplpb_answers`; browser
and desktop chat share its validation code. The release is tracked in PR #6; GitHub Pages builds and deploys after a main
merge. To roll back a merge commit, use `git revert -m 1 MERGE_COMMIT` and push the
resulting revert through the normal review flow. Revert commits rather
than rewriting ledger history or recalculating archived pins. Ephemeral chats
have no saved transcript to migrate. Existing saved chats remain historical
records, not freshly validated answers.
