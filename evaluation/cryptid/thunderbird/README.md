# THUNDERBIRD — local retained study

Last reviewed: 2026-11-25.

Mechanism: Bounded discovery misses competing evidence or hides incomplete scans.

Baseline **12/12** → candidate **12/12**; positive misses 0 → 0; false-supported claims 0. Transfer once: **8/8**, 0 positive misses, 0 false support. Completed, unscored and budget counts remain in each score.

Claim decisions12/12 unchanged; no coverage gain and no cap increase. Resource visibility11/12->12/12: exact unparsed relevant-unit spans and phrase-limit reason now exposed with checked partials. Eight source-answerable positives:5complete,3fixed-cap misses. Transfer8/8decisions and resource checks:5source-answerable positives,3complete,2cap misses. Counterevidence at/beyond limits never yields a definitive answer.419prior contracts and280release contracts exactly unchanged;21focused guards pass. Local query wall0.11-0.56s and peakRSSabout20MB are observations, not general performance claims.

Tested committed candidate `2b6561c971aa1cab4ffbca773142c170155a7afd`. Scoped ZIP SHA-256 `95c2dbb9acf1a3707e3e47ecf43df672fee9d598b12327ab839a0d45b78c6594`. This is not the final full-repository delivery ZIP.

[Development seal](development/freeze.json), [expected claims and withholding](development/key.json), [baseline](scores/baseline.json), [candidate](scores/candidate-1.json), [once-only transfer](scores/transfer-once.json), [archive receipt](candidate-freeze.json). Input records link source hashes, origin, protected operation, budgets and raw run locations. Keys/scorer/generator remain outside the isolated worker. Transfer is now consumed preservation material.

Reproduce development from an extracted candidate with `python tools/cryptid_trial_v4.py --registry evaluation/cryptid/thunderbird/development/registry.json --implementation EXTRACTED_ROOT --source-commit 2b6561c971aa1cab4ffbca773142c170155a7afd --output NEW_RUN_DIRECTORY`; use the versioned scorer recorded by the score. Run with functioning host Bubblewrap; never fall back to an unisolated worker.

Same-operator templates, implementation and scoring. Independent preparation/blinding, semantic and historical adjudication, outside-custodian scoring and native OOCC remain **NOT_RUN**. Publication remains **LOCAL_ONLY**.
