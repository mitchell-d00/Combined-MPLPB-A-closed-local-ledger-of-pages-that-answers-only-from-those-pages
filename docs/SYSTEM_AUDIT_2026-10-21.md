# Full-system retest and repair — 2026-10-21

Owner: Mitchell D. McPhetridge. Audit baseline: `c3af6ef3bdf66d987adde092ce3594f529b70bf6`, freshly cloned from main on 2026-10-21. Candidate work is on `repair/audited-release-2026-10-21`; no automatic merge or deployment is authorized. This is experimental software evidence, not production certification.

## Evidence status

The evidence directory is [`evaluation/audit-2026-10-21`](../evaluation/audit-2026-10-21/). Baseline and repaired outputs are separate. Exact-head PR and ZIP-first CI results are required before approving this candidate. Pending checks are not passes. Historical evaluation files and sealed core modules are preserved.

Environment: local CPython 3.12.14; Node v24.19.0 / V8 13.6.233.17-node.51; pinned Pyodide 314.0.7 running Python 3.14.2 (builder verifies archive SHA-256). CI used CPython 3.12.15, Node v24.22.0, npm 11.19.1 and Chromium 155.0.8059.84. Core runtime dependencies remain Python standard library only. Playwright 1.58.0 was installed into a writable local target. Local Chromium installation failed repeatedly with `End of central directory record signature not found`; local browser tests are blocked, not passed. Actual Chromium checks ran successfully in GitHub Actions. iPad Safari is untested.

At baseline, GitHub reports successful Pages build/deployment run [39485055683](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/39485055683) at the baseline SHA. Prior PR/ZIP checks passed at `1175920c5b95b1d7138d0ae59d29fa57861e4009`. Those historical runs are not new candidate verification.

## Executed local results

| Category | Baseline | Repaired candidate |
|---|---|---|
| Main Python suite | 650 passed (also repeated by check_parts) | 654 passed at `35dca4a`; final suite has 655 with the compatible-denial regression. Exact final results are attached to PR #17's head. |
| Vendored suites | 351 passed (52 smart-local, 145 swarm, 61 networked, 93 image) | vendored bytes unchanged |
| Adoption / local-mirror | 5 adoptions, zero validation errors; mirror validator exit 0 | unchanged inputs |
| Integrity workflow subset | 78 passed | 78 passed in CI; 21 final support/context/audit tests also passed |
| New language controls | 12/24 | 24/24 |
| Ownership development | 240 and 600 cases executed | 600 cases: 150 supported returns, 0 wrong owners/refusals |
| Inspected SQuAD development | 10 supported + 10 correct non-returns | same, zero wrong returns |
| Synthetic context / fixed conversation | 360/360; 78/78 | 360/360; 78/78 |
| Offline response / repair matrices | — | 1,000/1,000; 240/240 synthetic development cases |
| Real WebAssembly live replay | historical results not treated as current | 1,000 original turns, 25 intact sessions, zero transport/routing/citation-index failures; semantic correctness not scored |
| Determinism/memory/release focused tests | included in full suite | 36 passed, including process hash-seed and serialization replay |
| JavaScript API / transport / UI / crawler fixtures / bridge | passed | passed |
| Actual pinned Pyodide/WebAssembly | passed | passed |
| Installed wheel outside checkout | — | 2.0.0 installed; positive return and contradiction ambiguity passed |
| Real Chromium | local installation blocked; deployed baseline checked in CI | expanded candidate audit passed in PR and extracted-ZIP workflows at `35dca4a` |

A candidate full-suite run started before the corrupted-lineage repair finished recorded 653 tests with one error. It is retained as pre-repair evidence, not silently relabeled. The focused repaired reproduction passes; the final complete rerun is recorded separately.

Independent live UI examination of build `29dd50477ef5` returned the supported D&D fixture with `LOGIC-0001` / `47cda31dcdb0`, refused cone 04, and restored a synthetic Juniper conversation after reload with the online-lookup preference still disabled. Conversation memory stayed labeled separately. This is a desktop live-baseline observation, not candidate or iPad verification; see `live-browser-observations.json`.

At `35dca4ab7b4407b8db387af5f7c21b74552ca44b`, PR run 39635406509 and ZIP run 39635406600 both passed. The downloaded ZIP artifact was independently verified with `release_evidence.py verify` against that exact SHA. Chromium verified supplied-text import, supported/refused queries, exact citation preservation, transcript JSON export, IndexedDB reload/new-page continuity, offline query, correct default network-denial code, and visible rejection of a deliberately corrupted disposable session. Explicit live Wikipedia `import Cat` succeeded in both candidate and deployed baseline without an AI API key. Screenshots were inspected at desktop and mobile widths; candidate scroll widths exactly matched 1280, 390 and 768 px. The deployed baseline independently reproduced the 390/421 px overflow and old `ENGINE_ERROR` classification; those are recorded baseline defects, not candidate passes. Later source changes require a fresh exact-head release check; consult PR #17's current head and its artifact manifest.

## Reproduced defects and repairs

| Finding | Baseline behavior / expected behavior | Cause and repair |
|---|---|---|
| Wrong entity in literal location/abbreviation | “East Marlow” answered a question about “Marlow”; should refuse | Unanchored substring match. Require a complete subject or a bounded explicit naming construction. |
| Population relation crossed subjects | Rural population decline plus urban concentration answered rural location; should refuse | Wildcard spanned a different clause/subject. Restrict to explicit population/concentration grammar. |
| Literal contradictions discarded | Positive date/location plus explicit denial returned a unique answer; should expose ambiguity | Negative evidence was skipped. Detect bounded negative relation matches and propagate conflict within/across eligible pages. |
| Uncertain and reported claims accepted | “began in 1998, maybe” returned as supported; should refuse | Incomplete uncertainty/reporting guard. Reject these qualified sentences. |
| Hypothetical/instructional context lost | A sentence after “Imagine…” or “Ignore…” returned as a factual definition/date | Sentence-local checks lost the discourse context. Conservatively decline affected pages in both statement grammars. This may reduce coverage for mixed factual/instructional pages. |
| Corrupt lineage caused exception | Revised corpus with tampered history raised `KeyError: doc-0002.html`; should fail closed | Lexical gate and ledger eligibility differed. Intersect source candidates with currently servable records before support checks. Sealed core is unchanged. |
| Premature WebAssembly success evidence | `wasm-validation.json` said passed before later assertions ran | Move success-manifest write after all assertions. A completed build is still distinct from Chromium/IndexedDB validation. |
| Browser error-code mismatch | Real Chromium returned `ENGINE_ERROR` instead of documented `NETWORK_DISABLED` for a denied remote call | Worker serialized `Error: ` into the message, breaking facade classification. Preserve the original error message across worker transport; add exact transport and real-browser regressions. Network access remained blocked. |
| Mobile horizontal overflow | At a 390 px viewport the document was 421 px wide | The collection multi-select used its intrinsic option width. Constrain `#chat-scope` to its containing panel; retain the candidate no-overflow assertion and screenshots. |
| Context evaluation arm drift | The arm named `lexical_page_return` silently invoked the new supported default and reported zero returns | Call the legacy reader explicitly for this deliberately lexical comparison; add an arm-contract regression and include answer-layer hashes in evaluator pins. Historical outputs and labels remain unchanged. |
| Incomplete / zero-network replay summaries | The summarizer accepted fewer rows than the runner's reported count, and crashed when a fully local run had no network log | Require the reported response count to match; permit an absent network log only when zero requests are recorded. Final runner snapshots serialize all in-memory rows, network observations and session checks. |
| Documentation drift | Ownership README called installed `mplpb-combined ask` legacy; old counts/results appeared current | Correct current CLI guidance and add dated supersession notes without rewriting historical outcomes. |

Initial 24 new language controls: 12 passed on the unchanged baseline; all 24 pass after repairs. These are audit-authored synthetic development controls, now used for regression; they are not held-out reliability measurements. They include positive controls, negative questions, unknown follow-ups, misleading scope, duplicates, contradictions, source poisoning, entity/attribute mismatches and a deliberately false but correctly sealed assertion illustrating the truth boundary. Separate integrity tests cover stale revisions, cross-corpus isolation, damaged history and exact citation attribution.

An intermediate repair reduced the SQuAD excerpt to 9/10 supported answers by rejecting the Normandy naming sentence. That failed output is preserved; the grammar was corrected, not the expected answer. The positive population control also caught an intermediate `was`/`were` grammar error, which was corrected.

Review also caught an overly conservative intermediate contradiction patch: a positive 1998 statement plus a denial of 1999 was incorrectly ambiguous. The unchanged baseline returned 1998 correctly. The repaired check intersects the asserted and denied values, both within and across pages; a new regression covers both cases. `contradiction-value-before.log` preserves the failure, and `contradiction-value-retested.log` records 21 passing related tests. One intervening invocation used a nonexistent test-module name; its import error remains recorded and is not a product failure.

## Current answer findings

The baseline already passes the October 19 SQuAD development correction: 10 supported answerable questions, 10 correct non-returns, zero wrong returns. The repaired path preserves that result. The expanded 600-case development suite returns all 150 supported answers with zero wrong owners and zero false refusals. Its lexical reader now has 410 wrong returns (not the historical 430); retrieval is not factual answer support.

The three frozen pottery sets still have zero supported returns: answerable coverage is 0%, precision undefined. The four historical wrong returns are refused rather than answered correctly. The 28 earlier adversarial development scenarios remain 28/28. Neither those scores nor the new controls establish general semantic understanding. Unknown procedural wording, arbitrary paraphrases and unrestricted discourse/negation remain outside the finite grammar.

A sealed false assertion still supports an extractive answer. Hashes verify bytes, not truth, freshness or authorship. User declarations remain separately attributed conversation context. Specialized summaries and relationship skills have their own contracts; the strict query gate does not certify every chat utterance.

## Reproduction

Run the exact commands in `.github/workflows/pr-validation.yml`, `zip-release-validation.yml`, and the build portion of `pages.yml`. Do not deploy the candidate merely to test it. Additional checks:

```sh
python -m unittest tests.test_audit_20261021 -v
python -m tools.evaluate_audit_20261021 --output audit-results.json
python -m tools.evaluate_literal_coverage --output literal-results.json
python -m tools.evaluate_ownership --input evaluation/ownership/expanded-input.jsonl --out ownership-results.json
python -m tools.evaluate_answer_reliability --output reliability-results.json
python tools/check_parts.py
python -m tools.evaluate_context_matrix --output context-results.json
python -m tools.smoke_conversation_architecture
python -m tools.browser_audit_20261021 --preview-dir dist --output browser-results
```

Use fresh output paths for evaluations; never overwrite historical reports. `smoke_conversation_architecture` writes its fixed historical output path: preserve its new result separately and restore the tracked report after execution. New browser checks use disposable contexts and cover import, supported/refused queries, source citations, transcript export, IndexedDB reload/new-page continuity, deliberate session-corruption rejection, offline queries, network denial by default, explicit online acquisition, and desktop/mobile/tablet viewport dimensions. Viewport emulation is not actual iPad Safari. Online responses are recorded separately, including service failures.

## Documentation review

Reviewed README, ANSWER_RELIABILITY, LITERAL_COVERAGE_FIX_2026-10-19, SYSTEM_GUIDE, GROUNDED_CHAT, DEVELOPER_QUICKSTART, PRODUCTION_THREAT_MODEL, RELEASE_EVIDENCE, ZIP_FIRST_RELEASE_TESTING, BROWSER_TESTING_FOR_AGENTS, conversation architecture and ownership reports. SYSTEM_GUIDE is generated from `self_knowledge.documentation()` and tested for exact consistency; no unsupported change to its capability model is made. Existing warnings about finite grammar, untrusted sources and single-operator deployment remain applicable.

## Release limitations and priorities

This candidate is not a verified deployment. The active main ruleset was inspected on October 21: PRs and strict `archive-first` / `regression` checks are configured, with zero required approving reviews. No merge or bypass was attempted. Live crawler integration requires a configured endpoint/token and remains unverified here. Actual iPad Safari, long-term retention/storage eviction, accessibility, load/DoS and comprehensive XSS/SSRF testing are not certified. The new conservative guards are bounded, not a general solution to malicious language.

Highest-value next work: (1) independently authored, sealed multi-sentence adversarial evaluation with evidence-span annotation; (2) broaden safe answer coverage through explicit relation/discourse contracts and measured abstention tradeoffs; (3) durable browser backup/recovery, cross-device testing and continued release-check enforcement, review requirements and retained artifacts. Deterministic generation must be assessed with the complete state and pinned code; repeatability alone is not correctness.

## CI failure retained during this audit

Run 39632059396 passed the full Python suite, JavaScript, WebAssembly and existing live/candidate Chromium smoke, then failed the new network-denial error-code assertion. The complete log is retained in `ci-first-regression.log`. The baseline reproduction and repaired transport result are stored separately. This failure is an implementation defect in browser error classification, not evidence that network access was permitted. The new candidate must rerun the unchanged strict assertion.

The current main ruleset has also been independently read: both required checks are configured and target main. The older October 20 settings observation is preserved but explicitly superseded in RELEASE_EVIDENCE.md.

The second CI attempt (PR 39633376438; ZIP 39633376570) passed 653 Python tests, JavaScript, actual WebAssembly and the original Chromium smoke. The expanded browser audit then found the 390/421 px overflow. `ci-second-failure.txt` points to the retained screenshot artifact and repair. The first two failed CI attempts are not release passes.

The first partitioned live replay reported 1,000 executed turns and zero transport errors, but its append-only response files retained only 984 rows. The cause of that workspace artifact loss was not established; it must not be attributed to the answer engine. `incomplete-live-run.json` records the discrepancy. A complete rerun with final snapshots is required; its results must be evaluated independently of that incomplete attempt. The new summarizer refuses the incomplete logs rather than assigning a misleading total.

That rerun completed: all 1,000 original input rows match their unique recorded responses, all 25 session chains are intact, and all five runtime manifests agree. There were zero transport errors, prefix-routing failures, citation-index mismatches or unexpected social/no-search network calls under the runner's checks. Seven collections were built through 42 successful Wikipedia HTTP operations (41 unique URLs, one cache hit). The 97 `federated_answers` are separately attributed source-result responses, not 97 independently graded correct answers. The other responses were 234 lexical references, 144 refusals, 450 conversational replies and 75 help replies. Dictionary responses remaining local explain much of the difference from the historical live-acquisition report; no acquisition policy was relaxed.

[`live-final/`](../evaluation/audit-2026-10-21/live-final/) retains code/input/build pins, five exact execution commands and exits, machine-readable summary, compact replies, session/network records, and the full raw replay archive with HTTP payloads and saved captures. The original input fixture was not edited. Five shards each retained five entire 40-turn user sessions and original within-session order. An earlier single-worker attempt was interrupted for partitioning and is not counted as a completed evaluation. Timing (median 1.046 s; p95 7.327 s; maximum 36.639 s) includes five concurrent local workers and network pacing; it is not a production latency benchmark.

To repeat the same corpus in one worker, run `node tools/live_conversation_wasm.mjs CORE dist/index.html evaluation/live-conversation/input.jsonl OUTPUT_DIR`, then `python tools/summarize_live_conversation.py --output SUMMARY_DIR OUTPUT_DIR`. For the recorded partition, use the five commands in `live-final/executions.json` with local paths substituted. Full raw files can be extracted with `tar -xzf raw-replay.tar.gz`; compact replies use `gzip -dc results.jsonl.gz`. Verify `live-final/manifest.json` hashes before analysis. These are synthetic development observations with live source acquisition, not held-out semantic validation.


The 54-case contextual evaluation exposed a measurement defect: its lexical arm called `App.query` without an explicit mode after that API switched to supported answers. Baseline reproduction is retained. The corrected arm again measures legacy retrieval: 10 supported / 18 answerable, 1 false acceptance / 36 unsupported. Contextual chat remains 12/18 supported, 0/36 false acceptances, with six known paraphrase coverage misses. No labels were changed. The new test prevents accidental arm substitution.

README also incorrectly said dictionary definitions no longer block automatic encyclopedia acquisition. Current tests and `STRUCTURED_CHAT.md` specify the opposite: dictionary/lexical-reference responses stay local even when automatic lookup is enabled. README is corrected; the older live-conversation report receives a dated supersession note. The acquisition policy was not relaxed.


Repeatability observation: equal brainstorming inputs in two fresh sessions produced equal response payloads, but distinct session identifiers and transcript hashes. Cross-process hash-seed and serialized-state generation checks passed. Determinism applies to construction with pinned code/state; it does not make fresh identity/timestamp metadata or changing live Wikipedia revisions identical.
