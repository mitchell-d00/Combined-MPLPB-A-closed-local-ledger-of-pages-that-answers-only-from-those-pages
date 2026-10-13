# Answer reliability review — 2026-10-13

Current remote main was checked before edits: `715d1b567e3ed76e567b9462a4faf0fa513fce31`,
the same as the supplied baseline. No language model, random sampling, external
answer service or new network dependency is introduced.

## Root causes and focused changes

1. **Candidate selection was presented as answering.** The frozen
   `mplpb_combined.reader.answer` uses scope-majority ownership before prose. It
   does not establish that the body answers the entity/relation in the question.
   Its behavior and bytes are retained for archived captures and benchmarks.
   The installed `mplpb-combined ask` now calls `mplpb_answers.supported_answer`.
   `python -m mplpb_answers ask` is the equivalent source-checkout command.
   `mplpb-combined candidates` explicitly labels legacy inspection as **not a
   supported answer**. The old `python -m mplpb_combined ask` and `reader.answer`
   remain legacy retrieval interfaces, not recommended answer APIs.
2. **Surface patterns were disconnected.** Shared immutable question frames bind
   a relation, the entire entity, polarity and a canonical retrieval question.
   “When”, “In what year” and “In which year … did … open” share one opening-year
   frame; ownership question variants share one directed owner frame. Unlicensed
   time/negative/conditional modifiers are refused, not stripped. Body spans are
   quoted verbatim; scope and titles cannot provide evidence.
3. **Specificity could hide competing evidence.** The supported path checks all
   eligible lexical candidates through the existing provenance gate. Multiple
   supporting pages or matching positive/negative assertions cause ambiguity;
   it does not pick a higher-ranked truth winner. Eligibility, depth, not-for,
   external delivery restrictions, intact hashes and current lineage are checked.
4. **Bare-topic inspection bypassed statement checks.** Normal Ask now refuses
   a bare candidate instead of returning its body as an answer. Explicit source
   navigation remains available and is labeled `candidate_only` / “Source
   inspection · not an answer”. Both desktop and browser share the same query
   implementation and rendering labels.

## Compatibility and provenance

All files in `mplpb_combined/`, capture manifests, resource pins, source pages,
archived engines and frozen probe files remain byte-for-byte unchanged. Changing
the old core CLI in place would invalidate `wiki_live_eval.engine_hash`, which
covers every core Python module. A separately packaged answer layer avoids that
migration and keeps old captures reproducible. Wheels include both packages;
`tools.answer_support` remains a compatibility import. New answer-layer module
hashes are recorded separately in answers and conversation audit payloads.

The distribution version is 2.0.0 for this default-CLI contract change; the
archived core retains its 1.0.0 version and bytes.

This is a deliberate API transition: use the new normal entry point for answers;
use the old API only for explicitly named legacy reproduction. A new release
cannot silently turn an old Python import into a supported-answer guarantee.
Historical transcripts retain their original labels and hashes; they are not
retroactively verified by this change. The browser bundle includes the new package.

## Frozen benchmark diagnosis: all 19 discrepancies

Labels and SHA-256 sidecars are unchanged. These sets are now development data.
The old scorer calls every non-return mismatch a “wrong refusal”, including an
ambiguity response where the gold label says no answer. Four of the fifteen
reported refusals fall in that latter category.

| Case | Failure layer | Individual diagnosis and disposition |
| --- | --- | --- |
| h29 | Statement support | Handle pulling selects the drying page, which discusses wrapping handles, not making them. Supported path refuses. |
| a04 | Statement support | Cylinder throwing selects wedging/preparation. No throwing procedure is supported. Refuses. |
| a07 | Statement support | Recipe request selects a cone-6 firing schedule. Firing temperatures are not recipes. Refuses. |
| a10 | Statement support | Kiln-room temperature selects ventilation text with kiln/pyrometer temperatures. Different measured entity. Refuses. |
| op02 | Candidate selection | Guard-cone idiom is in the body, but extra question terms defeat scope-majority/full-word matching. Conditional procedural grammar still unsupported. |
| om03 | Candidate selection; support gap | Sagging coils wording misses element-care scope. Expected page discusses inspection/resistance but does not explicitly diagnose sagging coils. Do not infer the answer from the label. |
| om04 | Candidate selection | Recycle/trimmings paraphrase misses reclaim/slop terms; “yesterday” is extra context. Procedural and temporal coverage remains limited. |
| om08 | Candidate selection; support gap | Covering a teapot over a weekend does not match drying metadata sufficiently. Body mentions wrapping handles/joins, not the exact teapot/weekend instruction. No invented instruction. |
| ot04 | Ambiguity handling | Glass firing shares firing/kiln vocabulary with several pages; no glass-firing answer exists. Legacy ambiguity differs from gold refusal. |
| ot07 | Ambiguity handling | Porcelain/cone question selects multiple firing pages without porcelain support. Legacy ambiguity differs from gold refusal. |
| h01 | Ambiguity handling | Running glaze broadly matches six scope declarations. The system cannot safely select an application/troubleshooting procedure from that overlap. |
| h10 | Ambiguity handling | Both loading rules and the derived checklist literally say three posts per shelf. Gold names only loading rules; preserving multiple owners is appropriate rather than forcing that ID. |
| h11 | Candidate selection | “Unmarked glaze” misses metadata and the contextual body sentence “Anything unmarked goes to the quarantine shelf”. Requires bounded discourse resolution not implemented here. |
| h14 | Candidate selection | “Go back in” differs from “stay in after 600 C”; lexical completeness fails. A temporal/procedural frame would be needed. |
| h15 | Candidate selection | Minor-burn threshold uses “coin” plus anaphoric “anything”; scope and exact-word coverage fail. No medical procedural grammar added. |
| h16 | Candidate selection | Separate buckets appears in prose with red/white bodies; question terms prevent lexical selection. List/comparison extraction remains unsupported. |
| h21 | Candidate selection | Very short “temperature for bisque” has too little scope overlap; body uses numerical firing instructions. No scope-only answer permitted. |
| a03 | Ambiguity; eligibility secondary | Pricing question overlaps firing scopes. An additional derived page is withheld at internal depth; neither fact supplies a price. Ambiguity differs from gold refusal. |
| a12 | Ambiguity handling | Home-clay permission overlaps body-selection/firing metadata but no permission statement. Ambiguity differs from gold refusal. |

None of the eleven genuine answerable-case selection failures is fixed by deleting
constraints or rewriting gold labels. The supported path currently abstains from
these procedural questions. This limitation must remain visible.

## Results and interpretation

Machine-readable before/after rows and separate metrics are in
[`evaluation/reliability/after.json`](../evaluation/reliability/after.json).
The exact old support module is retained as `baseline_support.py`; historical
frozen results were also captured before editing in `before-frozen.json`.

| Dataset | Legacy correct / wrong returns / old-score refusal mismatches | Old supported correct | New supported correct | New supported wrong returns |
| --- | --- | --- | --- | --- |
| Original (56) | 50 / 0 / 6 | 37 | 20 | 0 |
| Held-out (30) | 22 / 1 / 7 | 17 | 11 | 0 |
| Adjacent (20) | 15 / 3 / 2 | 17 | 10 | 0 |
| New adversarial development (28) | 10 / 18 / 0 | 21 | 28 | 0 |
| External SQuAD sample (20) | 12 / 3 / 5 | 10 | 10 | 0 |

The new supported path returns **zero answers on the three frozen pottery sets**:
precision is undefined, not 100%. Its answerable coverage is 0%; it has 32, 17
and 8 explicit false refusals respectively, plus two ambiguities on answerable
held-out questions. Bare-topic candidate pages previously counted as returns;
removing that shortcut decreases nominal scores while making the answer contract
honest. The four historical wrong returns are refused, not solved by a new fact.

On 28 developer-authored adversarial cases: return precision is 8/8 (100%),
answerable coverage 8/8 (100%), false refusals 0, ambiguities 3 (all expected).
Old support passed 21/28 with 4 wrong returns, including a temporal prefix treated
as part of an owner. These are development results, not independent accuracy.

The external probe has ten answerable and ten adversarially unanswerable questions
across ten unfamiliar Wikipedia article contexts. Supported output: zero returns,
ten correct refusals, ten false refusals, zero ambiguity. No fixes were tuned to
these external questions. This is a small preselected coverage probe, not an
independent evaluation of MPLPB or a SQuAD leaderboard score. The evaluator checks
outcomes and gold-span containment, not official EM/F1. Legacy “precision” measures
candidate relevance under that proxy, never certified answer support.

The external questions were authored by SQuAD crowdworkers, independently of this
implementation. The new targeted near-match tests were authored during this review
and are explicitly development data. Do not describe them as independent. Reserve
other articles and new separately authored, sealed questions for the next evaluation;
once inspected for fixes, move them to development status. A blinded, independently
run adversarial evaluation across all listed categories remains future work.

## Reproduce

```sh
python -m unittest tests.test_answer_reliability tests.test_answer_support -q
python -m tools.evaluate_answer_reliability
python -m unittest discover -s tests -q
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node crawler/test_worker.mjs
```

## Limits

Hashes prove byte consistency, not source truth or authenticated authorship.
Finite grammar does not establish general language understanding. Unknown
constructions abstain. Duplicate supporting pages remain ambiguous even when
values agree. Arbitrary paraphrases, procedural instructions, temporal inference
and unrestricted negation/uncertainty reasoning remain unsupported. Source
inspection and extractive summaries are separate from supported question answers.

## User experience and integration evidence

The public standalone baseline (`0027874badba`, corresponding to reviewed main)
was rendered in the cloud browser at a desktop-size viewport. Controls and the
source modal were legible and stayed within the viewport. A synthetic named chat
was entered; after a real reload the application displayed the saved exchange
and “Saved MPLPB session resumed”. Source inspection displayed the verbatim local
fixture, record ID, SHA-256 and “no live verification”. This is one browser/viewport,
not mobile, accessibility or cross-browser certification.

The updated local build passed the real WebAssembly smoke script, including
fixture import, save/relaunch, provenance gates and conversation behavior. Desktop
HTTP/API tests and browser bridge tests exercise the same answer/refusal payload;
the shared UI script test verifies rendering labels without a visual browser.
The installed wheel was built and imported outside the source checkout.

Updated local visual layout remains unverified: the cloud browser rejected
`file://` navigation under its URL policy, and the local Chromium download
returned an invalid archive. No security policy was bypassed. The cloud screenshot
could not be synchronized into the workspace for attachment.

Crawler worker tests used fixture networking only. Repository configuration has
a worker name and allowed origin but no complete deployed worker URL or access
credentials. No production crawler endpoint was assumed, discovered by guessing,
or deployed. Live general-web integration remains unverified; live Wikipedia
capture is not a substitute for that test.

## Validation ledger

- 562 main Python tests pass (742.513 seconds), plus 351 vendored tests: 913 total.
- 28/28 adversarial development scenarios pass.
- 351 vendored Python tests pass; five adoption validations and local-mirror validation pass.
- 360/360 synthetic context checks and 78/78 fixed conversation checks pass.
- UI script, browser transport and fixture crawler checks pass.
- Actual WebAssembly engine smoke passes, including saved relaunch and source imports.
- Isolated 2.0.0 wheel CLI refuses the wrong-entity reproduction.
- All 237 protected core/capture/resource/frozen-benchmark files match baseline bytes.

These regression passes do not establish general answer accuracy. External
question results and remaining coverage failures above are part of the release
evidence, not hidden exceptions.

## Follow-up: procedural constraints and free chat

This update adds explicit source-authored linear procedure tags, draft-only automatic numbered-step tagging, and a final response evidence guard. Context cannot certify step completion. An isolated off-the-record conversational mode disables source acquisition and transcript saving. See [the procedure contract](PROCEDURAL_CONSTRAINTS.md). These additions do not repair untagged pottery coverage; the frozen labels and corpora remain unchanged. The 562-test result above predates these follow-up changes; their validation is recorded separately below.

### Follow-up validation

- Full main regression run: **574 tests passed in 811.761 seconds**.
- Two automatic-tagging tests were added after that run began. The final **21-test** procedure/reliability run (including all 14 procedure/free-chat tests) passes; the **19-test** procedure/language-label run also passes. Current inventory: 576 main tests.
- UI script checks pass, including free-chat storage isolation; browser transport and crawler fixtures pass.
- Actual WebAssembly checks pass, including off-record no-save/no-resume behavior. The latest rebuilt bundle separately passes automatic source tagging and constrained procedure rendering.
- Frozen/development/external results were regenerated with matching final answer-layer hashes. Procedural additions do not change those results or labels.
- All 237 protected files still match baseline bytes.
- Updated visual layout and live deployed crawler remain unverified, as described above. These results were recorded before the release merge; deployment status is tracked separately by the GitHub Pages workflow.
