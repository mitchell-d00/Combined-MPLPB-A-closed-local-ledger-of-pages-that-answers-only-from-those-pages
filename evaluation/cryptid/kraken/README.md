# KRAKEN — local retained study

Last reviewed: 2026-11-25.

Mechanism: One proved obligation hides a missing documentary bridge.

Baseline **2/16** → candidate **15/16**; positive misses 14 → 1; false-supported claims 0. Transfer once: **12/12**, 0 positive misses, 0 false support. Completed, unscored and budget counts remain in each score.

Original16:2->15 decisions,1 complete and12 checked partials; one frozen positive expectation remains incompatible with the external delivery profile and is retained as failure. First transfer15/16 consumed. Stronger policy Wrap4:2->4, forbidden claims2->0; rejected C1 ZIP and strong guard failure retained. Fresh policy/layout12/12,3complete+3partial+6withhold; narrow same-grammar multiline transfer, not general syntax. 322 prior Cryptid,280 release and16 consumed contracts unchanged.56focused checks pass. Human and independent evaluations NOT_RUN.

Tested committed candidate `064d953602f296f54b79d4487a0cde6e45c135ed`. Scoped ZIP SHA-256 `466a5c7bc0be629ca005dd32faaa03163a5299ceec358ea67990797aaf7d422a`. This is not the final full-repository delivery ZIP.

[Development seal](development/freeze.json), [expected claims and withholding](development/key.json), [baseline](scores/baseline.json), [candidate](scores/candidate-2.json), [once-only transfer](scores/fresh-transfer-once.json), [archive receipt](fresh/candidate-freeze.json). Input records link source hashes, origin, protected operation, budgets and raw run locations. Keys/scorer/generator remain outside the isolated worker. Transfer is now consumed preservation material.

Reproduce development from an extracted candidate with `python tools/cryptid_trial_v3.py --registry evaluation/cryptid/kraken/development/registry.json --implementation EXTRACTED_ROOT --source-commit 064d953602f296f54b79d4487a0cde6e45c135ed --output NEW_RUN_DIRECTORY`; use the versioned scorer recorded by the score. Run with functioning host Bubblewrap; never fall back to an unisolated worker.

Same-operator templates, implementation and scoring. Independent preparation/blinding, semantic and historical adjudication, outside-custodian scoring and native OOCC remain **NOT_RUN**. Publication remains **LOCAL_ONLY**.
