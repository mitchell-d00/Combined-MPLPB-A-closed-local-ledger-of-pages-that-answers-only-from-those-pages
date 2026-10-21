# Full-system retest and repair — 2026-10-21

Owner: Mitchell D. McPhetridge. Audit baseline: `c3af6ef3bdf66d987adde092ce3594f529b70bf6`, freshly cloned from main on 2026-10-21. Candidate work is on `repair/audited-release-2026-10-21`; no automatic merge or deployment is authorized. This is experimental software evidence, not production certification.

## Evidence status

The evidence directory is [`evaluation/audit-2026-10-21`](../evaluation/audit-2026-10-21/). Baseline and repaired outputs are separate. Exact-head PR and ZIP-first CI results are required before approving this candidate. Pending checks are not passes. Historical evaluation files and sealed core modules are preserved.

Environment: CPython 3.12.14; Node v24.19.0; pinned Pyodide 314.0.7 archive (builder verifies SHA-256). Core runtime dependencies remain Python standard library only. Playwright 1.58.0 was installed into a writable local target. Local Chromium installation failed repeatedly with `End of central directory record signature not found`; local browser tests are blocked, not passed. CI browser runs record their actual versions. iPad Safari is untested.

At baseline, GitHub reports successful Pages build/deployment run [39485055683](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/39485055683) at the baseline SHA. Prior PR/ZIP checks passed at `1175920c5b95b1d7138d0ae59d29fa57861e4009`. Those historical runs are not new candidate verification.

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
| Documentation drift | Ownership README called installed `mplpb-combined ask` legacy; old counts/results appeared current | Correct current CLI guidance and add dated supersession notes without rewriting historical outcomes. |

Initial 24 new language controls: 12 passed on the unchanged baseline; all 24 pass after repairs. These are audit-authored synthetic development controls, now used for regression; they are not held-out reliability measurements. They include positive controls, negative questions, unknown follow-ups, misleading scope, duplicates, contradictions, source poisoning, entity/attribute mismatches and a deliberately false but correctly sealed assertion illustrating the truth boundary. Separate integrity tests cover stale revisions, cross-corpus isolation, damaged history and exact citation attribution.

An intermediate repair reduced the SQuAD excerpt to 9/10 supported answers by rejecting the Normandy naming sentence. That failed output is preserved; the grammar was corrected, not the expected answer. The positive population control also caught an intermediate `was`/`were` grammar error, which was corrected.

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

Use fresh output paths for evaluations; never overwrite historical reports. `smoke_conversation_architecture` writes its fixed historical output path: preserve its new result separately and restore the tracked report after execution. New browser checks use disposable contexts and cover import, supported/refused queries, source citations, transcript export, IndexedDB reload/new-page continuity, offline queries, network denial by default, explicit online acquisition, and desktop/mobile/tablet viewport dimensions. Viewport emulation is not actual iPad Safari. Online responses are recorded separately, including service failures.

## Documentation review

Reviewed README, ANSWER_RELIABILITY, LITERAL_COVERAGE_FIX_2026-10-19, SYSTEM_GUIDE, GROUNDED_CHAT, DEVELOPER_QUICKSTART, PRODUCTION_THREAT_MODEL, RELEASE_EVIDENCE, ZIP_FIRST_RELEASE_TESTING, BROWSER_TESTING_FOR_AGENTS, conversation architecture and ownership reports. SYSTEM_GUIDE is generated from `self_knowledge.documentation()` and tested for exact consistency; no unsupported change to its capability model is made. Existing warnings about finite grammar, untrusted sources and single-operator deployment remain applicable.

## Release limitations and priorities

This candidate is not a verified deployment. Branch-rule enforcement is an administrative control, not established by workflow text. Live crawler integration requires a configured endpoint/token and remains unverified here. Actual iPad Safari, long-term retention/storage eviction, accessibility, load/DoS and comprehensive XSS/SSRF testing are not certified. The new conservative guards are bounded, not a general solution to malicious language.

Highest-value next work: (1) independently authored, sealed multi-sentence adversarial evaluation with evidence-span annotation; (2) broaden safe answer coverage through explicit relation/discourse contracts and measured abstention tradeoffs; (3) durable browser backup/recovery, cross-device testing and enforced release checks with retained artifacts. Deterministic generation must be assessed with the complete state and pinned code; repeatability alone is not correctness.
