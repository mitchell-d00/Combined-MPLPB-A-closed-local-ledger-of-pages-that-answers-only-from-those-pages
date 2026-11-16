# Documentary scope engineering results

Last reviewed: 2026-11-16.

The native historical reconstruction objective remains unmet: supported answers are still **0/14 original questions and 0/8 familiar government-record questions**. This update repairs specific ordinary-prose interpretations and preserves source authority. It does not establish general historical understanding, relationship accuracy, production readiness or independent scientific validation.

Baseline: `38e273855e577cff038f704c63fe09b22ac6889a`. Final tested implementation: `c6f77bef76a90219ae6e2074f0302fa3d72ada19`. Working branch: `engineering/documentary-scope`. The final evidence/handoff commit is subsequent; runtime source and tests must remain byte-identical to c6f77bef76a90219ae6e2074f0302fa3d72ada19. Exact implementation file hashes are retained in every run receipt. The final source ZIP SHA-256 is `8e118b8431fb0cd662b2f034094d56931a89c9cbceedbf0a503a8dce4467ba71`. It was extracted before testing. Generated browser build assets stayed outside the repository source.

## Measured comparison

| Records | Arm | Completed | Draft spans covered | Native supported | CPU s | Worker wall s | Peak RSS bytes | Logical source HTML bytes read |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| original | before | 14/14 | 18/23 | 0 | 932.267 | 1131.478 | 49700864 | 9452711906 |
| original | after | 14/14 | 18/23 | 0 | 875.295 | 916.862 | 50634752 | 9452711906 |
| original | bm25 | 14/14 | 5/23 | 0 | 18.154 | 27.079 | 33669120 | 40035688 |
| original | keyword | 14/14 | 0/23 | 0 | 11.543 | 14.383 | 31875072 | 40035688 |
| unfamiliar | before | 8/8 | 9/9 | 0 | 57.692 | 57.715 | 21237760 | 188246268 |
| unfamiliar | after | 8/8 | 9/9 | 0 | 63.532 | 84.581 | 21237760 | 188246268 |
| unfamiliar | bm25 | 8/8 | 1/9 | 0 | 0.722 | 1.679 | 19611648 | 1135296 |
| unfamiliar | keyword | 8/8 | 0/9 | 0 | 0.691 | 1.283 | 19800064 | 1135296 |

BM25 and keyword are retrieval-only controls; they do not attempt supported answers. Their zero support count is not a semantic failure score.

All arms use unchanged questions/originals, the same frozen seals, 12 passages/12,000 context characters and the existing worker limits (180-second wall timeout, 300-second CPU, 2 GiB address space). Native investigations also retain 2 hops, 12 sources and 200,000 examined characters. The current checkout baseline uses `--mode updated` so both native implementations execute the same investigation path; `--mode baseline` denotes a different historical code seal and is not used as a shortcut. Source envelopes, hashes and non-answer-bearing import metadata are unchanged.

Costs are query-worker measurements, not the total engineering cost. Import costs are separate in receipts. Logical read bytes include repeated native HTML reads, not physical disk I/O or only original input size. Peak RSS includes imports; Python allocation tracing remains disabled in both arms. Jobs overlapped on a shared host, so these wall/CPU observations do not establish a controlled performance comparison. Audit/review packet generation is outside the query-worker budget and costs shown here.

Draft span coverage uses incomplete developer references. It is not source retrieval recall@k, complete relevant evidence coverage, event recall or relationship recall. All required semantic metrics and human times remain null in [metrics.json](metrics.json). Zero native support claims does not establish that all refusals are appropriate. Initial failed and canceled attempts remain visible under [intermediate](intermediate/).

## What changed and what did not

- `mplpb_work/prose_relations.py`: retain shared negation/conditional scope, identify literal report/request complements, keep unverified action completion null, expose complete explicit passive agent phrases with canonical offsets, and distinguish publication/receipt/revision cues from a referenced document's `dated` cue. Add candidate/abstain report kind and explicit non-support fields.
- `tests/test_documentary_scope.py`: 24 adversarial controls covering source integrity, restrictions, missing bridges, changed message bodies, event identity uncertainty, orders/requests/reports, cancellations, dates, conditional/negative scope and causal overclaiming. Existing tests remain unchanged.
- `tools/compare_documentary_scope.py`: verify identical frozen inputs and per-case hashes; retain every changed interpretation; map every final rich finding to unchanged original bytes; prepare blank two-reviewer/adjudication sheets. A tampered run is rejected and an unchanged run compares without interpretation changes.
- Strict support, serving eligibility, source revisions, conflict/correction write operations and original-record bytes are unchanged. Read-only reconstruction never applies a correction.

[Source-linked examples](examples.json) retain the full Eisenhower and presidential by-phrases, the repaired letter-date error and a native refusal. These are developer observations about source-consistent fields, **not verified historical relationships or independent labels**. Citation fidelity does not certify the interpretation. The comparison includes new, changed and removed interpretations rather than selecting only favorable additions. New planned/promise propositions remain unverified and receive no benchmark credit.

## Failures preserved

The first full-suite attempt ran in an outer sandbox that denied loopback sockets; editing the checkout while it ran also invalidated a study pin. It is not a valid baseline measurement. Clean archive baseline and final suites were run separately with the required host permissions; no safety test was disabled.

Initial original/familiar worker attempts failed bubblewrap NETLINK_ROUTE namespace setup. The retry ran the existing bubblewrap isolation outside the outer sandbox; no direct execution fallback or private expected-answer mount was added. Full failed per-case outputs remain. Superseded jobs were explicitly canceled to reserve resources for the corrected candidate, with commands, reasons and phase checkpoints retained; missing unexecuted cases were not scored as passes.

The 3790547 candidate misclassified prepositional “to Ruth” as an infinitive governor and truncated “Gen. Dwight D. Eisenhower.” The c1352c1 candidate passed 1,033 tests but an original sentence exposed the wrong receipt-date role for “your letter ... dated February 16th.” Those source-linked errors, intermediate runs and direct reproduction probes are retained. Final controls repair these specific failures; unknown semantic error rates remain unknown.

## Verification

Clean baseline: 1,011 Python tests passed in 629.069 s. Final extracted archive: 1,035 Python tests passed in 485.354 s. Final public evidence suite: 52/52 with zero observed false supported bridges in those prepared controls. Original-paper replay: four pinned originals, 31 verified documentary declarations, six traversed declared relations, 15 unresolved relations, all three software stages passed, answer support false. These deterministic software stages are not independent human historians.

Final archive infrastructure/documentation/handoff checks, UI/transport/JavaScript API/helper/model-loader/WebGPU contract checks, crawler fixtures, pinned real WebAssembly engine checks, and fresh Chromium published-baseline/local-candidate smoke checks passed. The browser persona is scripted and does not count as human review. No merge, push, deployment or postdeployment validation was performed. Full logs and source-archive/build hashes are under [validation](validation/).

[Preservation audit](validation/preservation-audit.json): all 1,445 existing files in the two frozen historical families remain byte-identical to baseline; all original tests remain unchanged. Tested safety controls have no observed regressions. This is a scoped test result, not a proof of universal integrity or authorization security.

## Why support remains absent, and how to fix it

The [14-case refusal diagnosis](REFUSAL_ANALYSIS.md) identifies the strict pipeline's missing atomic verification/composition path. Candidate extraction is intentionally non-authoritative. Add separately checked evidence obligations carrying the full original question/profile, complete statements, qualifier/date roles, identity witnesses, required links and contrary evidence. A shortened subquestion must not drop original delivery exclusions. Emit supported partial claims only when that verifier succeeds; require every requested claim to pass before top-level supported_answer. Keep historical truth and independent review separate. The present patch does not implement that verifier or demonstrate a supported-answer gain.

Remaining limitations include incomplete retrieval (five draft spans still missing), finite/fallible grammar, unresolved aliases/pronouns/passive identities, indirect attribution, OCR damage, incomplete correction scope, uncertain event co-reference, distant conditions, missing intermediary records and unsupported causality/priority claims. Native supported reconstruction and full relationship precision/recall remain unproven. No candidate-count increase is scored as success.

## Independent review and reproduction

Independent review, adjudication and a genuinely unseen evaluation are **NOT RUN**. Two blank review sheets and an adjudication record accompany each comparison. Complete review packets for each native run include original projections, source receipts, full outputs and explicitly incomplete developer drafts. Use the existing two-human `tools.unprepared_challenge score` workflow on complete packets; delta sheets alone cannot establish accuracy. See [the prospective independent protocol](../../docs/DOCUMENTARY_SCOPE.md). Genuine independent authors/reviewers must supply the missing reference scope, semantic judgments and measured human times.

```sh
# Run each command from the repository; use new output paths.
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/mplpb-public-evidence.json
python -m tools.evaluate_historical_experts --output /tmp/new-experts.json
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation CHECKOUT --mode updated --commit SHA --seal freeze-v2.json --output NEW_ORIGINAL_RUN
python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-followup/unfamiliar --implementation CHECKOUT --mode updated --commit SHA --output NEW_FAMILIAR_RUN
# Repeat with --mode bm25 and --mode keyword for retrieval controls.
python -m tools.compare_documentary_scope CORPUS BEFORE_RUN AFTER_RUN --output NEW_COMPARISON
python -m tools.unprepared_challenge packets CORPUS ONE_RUN --output NEW_PACKETS
python -m tools.unprepared_challenge score NEW_PACKETS HUMAN_REVIEW_1 HUMAN_REVIEW_2 --adjudication HUMAN_ADJUDICATION --output NEW_SCORES
```

The frozen runner requires real Linux bubblewrap and must fail closed if isolation is unavailable. Runtime workers see only native source inputs and the question; expected drafts/reviewer data stay outside. The original family uses freeze-v2.json; the familiar family uses freeze.json. Prior source/questions/expected drafts/reports are never overwritten. Frozen runtime harness and importer remain unchanged. Exact archive and browser reproduction commands are retained in the repository's ZIP-first guide; validation/browser_driver.py selects an installed Chromium binary explicitly.

## Original-byte audit cost

All 641 final rich findings passed the comparison tool’s original-byte mapping and non-authority checks (417 original-family appearances and 224 government-record appearances). Repeated appearances are not independent relationships. The bounded audit children had a 600-second wall limit.

- original: 238.929 CPU s, 239.562 wall s, peak RSS 132718592 bytes. Audit source read bytes were not instrumented and remain null.
- unfamiliar: 3.369 CPU s, 3.375 wall s, peak RSS 34435072 bytes. Audit source read bytes were not instrumented and remain null.

These costs are additional to query-worker costs. The audit reparses originals repeatedly and can take minutes; no efficiency improvement is claimed. Complete measurements are in validation/original-audit-metrics.json and validation/unfamiliar-audit-metrics.json.
