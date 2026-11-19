# D% randomized prose challenge

Last reviewed: 2026-11-19.

D% generates original fictional documentary packets to expose both missed answers and false support. It tests the existing strict answer pipeline and separately inspects the offline sorter. It does not modify either engine, authenticate testimony, or measure real historical accuracy.

## Contract and sampling

Run `python -m tools.dpercent --help`. Only Python standard-library code is added. Execution requires Linux and bubblewrap; there is no unsandboxed fallback. A batch contains anonymous `packets/DP00001/case.json` files and unchanged UTF-8 sources. The manifest supplies the question, profile, source policy and identical retrieval budgets (12 passages, 8,000 characters); it contains no family or expected outcome. Commentary remains available to the offline sorter but is excluded from the strict ledger. Generic titles and scope are not factual proof.

The private custodian directory contains the binary answer/refuse key, source excerpts, typed expectations where available, seed and every percentile draw. It must be outside both the repository and public packet tree. `seal.json` pins every public byte, generator, worker, private key and dice record by SHA-256. Do not commit private keys or roll files. Public results reveal development-case labels after scoring; a future held-out experiment needs a newly frozen batch.

There are 31 families: 15 answerable source-assertion tasks and 16 unsupported tasks. They include active/passive and reported actions, denials, instructions versus execution, explicit cause versus chronology, different date roles, wording comparison, partial correction, explicit chains versus missing links, ambiguous references, competing accounts, repeated headers, changed bodies, embedded identifiers, historical-priority claims and current policy/integrity failures. Some families vary hedging, reported wording or conditional scope internally. Positive labels mean the eligible fictional evidence permits a complete scoped answer, not that the current finite checker implements its grammar. Negative labels mean the requested conclusion exceeds the evidence or current eligibility.

Percentile-table choices use rejection sampling with a retained roll trace. Family coverage is stratified and shuffled; this is not independent identically distributed population sampling. The conservative 1,674 design cells are 31 families × 2 line endings × 3 extensions × 3 question forms × 3 distractor counts. Names, dates, four layouts, wrapping and scope variants add variation; some layouts are deliberately constrained so required documentary context exists. Extensions alone are not semantic difficulty. No language acceptance filter removes difficult cases. Generated fixtures are not copied from external research or private datasets.

## Reproduce

Use fresh, disjoint paths; existing output directories are never overwritten:

```sh
python -m tools.dpercent prepare --out /tmp/dpercent-public --custodian /tmp/dpercent-private --cases 1240
python -m tools.dpercent run --packets /tmp/dpercent-public --out /tmp/dpercent-run --implementation .
python -m tools.dpercent score --packets /tmp/dpercent-public --custodian /tmp/dpercent-private --run /tmp/dpercent-run --out /tmp/dpercent-score.json --require-perfect
python -m unittest -q tests.test_dpercent
```

Preparation normally draws a fresh 128-bit seed. For replay, the custodian can supply `--seed INTEGER`; exact replay requires the sealed generator version. Freeze generator and key before baseline execution. Do not adjust labels or filter cases after seeing failures. `--limit N` is diagnostic only: unrun cases remain unrun and primary rates are null. Run returns nonzero on worker failures. Scoring normally returns zero when a report is successfully written; `--require-perfect` also returns nonzero on capability failures. A capability failure is an intended measurement, distinct from a broken software regression.

Each runtime receives only three MPLPB packages and one read-only packet, in isolated Linux namespaces with no network, host workspace, generator, scorer, seed or key. Native code hashes are recorded and rechecked. Sources are sealed with their original text preserved, generic metadata and declared-machine authorship. Intentional corruption/withdrawal happens only to disposable fixture ledger pages. The original inputs and post-setup ledger must remain byte-identical during reads. Both sorter modes must have identical observations and labels; all sorter relationships remain non-authoritative. The sorter and source receipts are operator research artifacts containing the fixture texts, not profile-filtered public answer delivery. Only native answers/retrieval are evaluated for serving eligibility.

Limits: 4,096 cases; 128 MiB generated source text; 100,000 source files; 12 passages/8,000 characters per retrieval method; 30 CPU seconds, 45 wall seconds, 2 GiB address space and 256 MiB scratch per worker; 8 MiB per output file and a 256 MiB aggregate result stopping threshold. The last result can exceed that threshold by at most 8 MiB. Worker failures and partial runs remain recorded and are never retried silently.

## Scoring and boundaries

* **E**: complete supported answers whose typed proposition and citations match the private reference, divided by all expected-answer cases. This is a conservative checked lower bound: unsupported semantic matcher shapes remain explicitly unscored, never credited merely for a citation. Literal-location questions have a separate exact-location rule that establishes no historical relationship.
* **E_output**: raw complete-support flags on expected-answer cases, before reference matching. Inspect this alongside E; it is not semantic accuracy.
* **F**: any complete-support flag on expected-refuse cases divided by all expected-refuse cases. Over-refusals, appropriate refusals, checked partials, incorrect supported outputs and unscored supported outputs are retained separately. Primary E/F are null if any case fails execution or is not run; completed-subset observations are separately labeled.
* Retrieval: source recall@1/5/10 and full-statement coverage, macro-averaged over cases with eligible draft references. Full-statement coverage requires the complete whitespace-normalized reference statement in one returned passage; it is retrieval coverage, not proof. Native obligation retrieval and simple BM25 receive identical sources and budgets. Retired, corrupt and externally withheld references are not counted as retrieval misses.
* Costs: post-import worker CPU/wall totals, maximum individual worker RSS and explicit original-ingest bytes/calls. These do not include every internal reread, parent scheduling or aggregate process-tree memory. Total pipeline bytes and human review time remain null.

A typed fixture matcher is separate from runtime but authored with the generator. It is not independent semantic review. No human review, live-model assessment, genuine hidden third-party evaluation, or historical precision/recall is claimed. Software tests must not be presented as evidence that general historical reconstruction works. Preserve baseline failures and improve the engine only in a subsequent, separately recorded experiment.

The runtime ownership rule remains: one eligible owner returns; two or more stop as ambiguous; none refuses. Only existing independently checked eligible body evidence can establish native source support. Candidate edges, model proposals, quotation fidelity and source hashes do not independently establish historical truth.

## Frozen baseline evidence

See the [2026-11-19 report](../evaluation/dpercent/2026-11-19/REPORT.md) for the frozen generator/main revisions, all outcomes, costs, software checks and preserved failures. Execution records require a Git checkout for revision identification; the worker itself receives no Git metadata. The generator and worker were not edited after the official seal. Private structural review hints are not automatically scored as event/relationship correctness.
