# SASQUATCH — local retained study

Last reviewed: 2026-11-25.

Mechanism: References lack unique eligible identity bindings.

Baseline **28/32** → candidate **32/32**; positive misses 4 → 0; false-supported claims 0. Transfer once: **22/22**, 0 positive misses, 0 false support. Completed, unscored and budget counts remain in each score.

Only complete explicit local glossary declarations are newly admitted. Ambiguous, quoted, missing and initials-only evidence withholds. Identity is not substituted into action proofs; broader references remain unresolved. 232 prior Cryptid and 280 release contracts unchanged; 30 corrected native controls pass. Same-operator templates and scoring, not independent blinding.

Tested committed candidate `16d4e7a825bd0117ab740e9ad624f6f32c05fba1`. Scoped ZIP SHA-256 `c47889dcd9e271ee7842da93b386a723a87fbf8a9c9654a1d8df7f19b5151efa`. This is not the final full-repository delivery ZIP.

[Development seal](development/freeze.json), [expected claims and withholding](development/key.json), [baseline](scores/baseline-v4.json), [candidate](scores/candidate-1-v4.json), [once-only transfer](scores/transfer-once-v4.json), [archive receipt](candidate-freeze.json). Input records link source hashes, origin, protected operation, budgets and raw run locations. Keys/scorer/generator remain outside the isolated worker. Transfer is now consumed preservation material.

Reproduce development from an extracted candidate with `python tools/cryptid_trial_v3.py --registry evaluation/cryptid/sasquatch/development/registry.json --implementation EXTRACTED_ROOT --source-commit 16d4e7a825bd0117ab740e9ad624f6f32c05fba1 --output NEW_RUN_DIRECTORY`; use the versioned scorer recorded by the score. Run with functioning host Bubblewrap; never fall back to an unisolated worker.

Same-operator templates, implementation and scoring. Independent preparation/blinding, semantic and historical adjudication, outside-custodian scoring and native OOCC remain **NOT_RUN**. Publication remains **LOCAL_ONLY**.
