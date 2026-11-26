# CHUPACABRA — local retained study

Last reviewed: 2026-11-25.

Mechanism: Corrections or comparisons overreach their witnessed field scope.

Baseline **9/16** → candidate **14/16**; positive misses 7 → 2; false-supported claims 0. Transfer once: **4/8**, 4 positive misses, 0 false support. Completed, unscored and budget counts remain in each score.

Development recovers two unchanged historical answers and one checked partial; two historical positive misses remain above the fixed eight-record cap. Limited substitution transfer12/12; separate structural transfer4/8 with four real positive misses, zero false support. No transfer-informed repair. 286 prior Cryptid contracts unchanged; release276 exact unchanged,2 new complete recoveries,2 diagnostic-only budget changes with original failed score retained. All65 applicable controls pass; rejected budget-bypass candidate and one corrected test-harness error retained.

Tested committed candidate `db336faf87abf5ae2e917011bc9c41ffd7350b8b`. Scoped ZIP SHA-256 `0c7e93e78097eaa9f666aac00004698dd10bf6a7d57d94d29c797a13ada37684`. This is not the final full-repository delivery ZIP.

[Development seal](development/freeze.json), [expected claims and withholding](development/key.json), [baseline](scores/baseline.json), [candidate](scores/candidate-2.json), [once-only transfer](scores/fresh-transfer-once.json), [archive receipt](fresh/candidate-freeze.json). Input records link source hashes, origin, protected operation, budgets and raw run locations. Keys/scorer/generator remain outside the isolated worker. Transfer is now consumed preservation material.

Reproduce development from an extracted candidate with `python tools/cryptid_trial_v3.py --registry evaluation/cryptid/chupacabra/development/registry.json --implementation EXTRACTED_ROOT --source-commit db336faf87abf5ae2e917011bc9c41ffd7350b8b --output NEW_RUN_DIRECTORY`; use the versioned scorer recorded by the score. Run with functioning host Bubblewrap; never fall back to an unisolated worker.

Same-operator templates, implementation and scoring. Independent preparation/blinding, semantic and historical adjudication, outside-custodian scoring and native OOCC remain **NOT_RUN**. Publication remains **LOCAL_ONLY**.
