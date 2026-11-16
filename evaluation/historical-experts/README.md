# Historical expert path: source-declared relationship replay

Last reviewed: 2026-11-16.

This family tests the [bounded historical expert path](../../docs/HISTORICAL_EXPERT_PATH.md).
The documentary, chronology and independent verification roles execute through
the existing specialist work coordinator. A successful receipt validates the
bounded documentary operation; it does not certify the truth of a synthesis.

Run `python -m tools.evaluate_historical_experts --output /tmp/new-history.json`
to import four byte-pinned original MPLPB papers into an isolated temporary
ledger, start from Combined v3, and inspect its explicit relations to Local Web,
Smart Local and retained Combined versions. The replay preserves originals and
reports actual observed traversal counts, exact source citations, missing targets,
declared date bases, independent verification and expert receipt status.

The retained tests cover changed hashes/policy, code-example metadata, stale or
restricted sources, original-question exclusions, version ambiguity, cycles,
traversal budgets, exact offsets, source changes during extraction, and refusal
to turn documentary links into historical truth. Preformatted source contexts
retain adjacent wrapped conditions and negation without changing source bytes.

The initial inspected challenge used MPLPB's original papers and Git records.
Its strict-mode refusals exposed missing reconstruction capability; safe refusals
were not counted as successful reconstruction. Later review corrected incomplete
failure-mode anchors, distinguished declared-date ordering from development order,
and required a file/ref/blob witness before associating a commit with a document.
These are development findings, not a blind historical-accuracy benchmark.

The current expert report remains `answer_supported:false`. It does not solve
unrestricted multi-hop reasoning, as-of event reconstruction, causal inference,
human authentication, historical priority, or interpretation outside its declared
documentary grammar. Original frozen evaluations and reports remain unchanged.

> Update 2026-11-16: The [public 52-case evidence suite](../../docs/PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](../../docs/HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.

The [public 52-case protocol](../../docs/PUBLIC_EVIDENCE_TESTS.md) adds visible fictional inputs, expected results, a checksum-pinned manifest, per-case measurements and explicit gap scoring. Run `python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/new-results.json`. Source-event candidates and scoped source corrections are bounded operations; their success does not establish historical truth.

## Retained public results

The clean implementation at `8fb3eb82cde1781c1402d57986b63179b82ad4e5` passed **52/52** published cases with zero observed false supported bridges. The earlier pinned `257e54a51edac272eb6b2441457f38a40485ee4d` implementation records 10 passes and 42 explicit capability gaps under the same case/evaluator hashes. These are interface and boundary controls, not an accuracy comparison on arbitrary history.

Inspect [current per-case results](current-results.json), [baseline per-case results](baseline-results.json), [version and hash comparison](comparison.json), and [original-paper replay](original-paper-replay.json). Runtime/CPU/allocation/source-read measurements and unknown human-effort fields are retained per case. Missing, restricted, ambiguous and over-budget targets remain visible. Exact final-head archive/regression and postdeployment results are recorded separately in the PR/Actions receipts.
