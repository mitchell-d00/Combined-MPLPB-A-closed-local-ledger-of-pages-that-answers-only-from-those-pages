# Mothman: documentary date roles

Last reviewed: 2026-11-25.

Mechanism: ordinary paired date questions did not reach the documentary inventory; its checker had no explicit writing-date predicate and rejected wrapped source lines. The shared operation now plans sending/writing obligations and independently checks the eligible source's complete units. Catalogue, review and writing remain separate roles. A writing claim explicitly establishes neither sending, receipt nor event occurrence. Original date spelling and line wrapping stay in exact witnesses; no year is borrowed.

## Before and candidate

[Development registry](development/registry.json), [unchanged key](development/key.json) and [freeze](development/freeze.json) precede native edits. Twenty-eight cases include five unchanged old inputs from two suites. The baseline at `c01021c0b9983f9a607fbe782dea7ed5872d1f11` completed 28: **17/28 decisions**, five complete positive answers, eleven positive misses, zero false support. Candidate 3 completes **25/28 decisions**, thirteen complete positives, three misses, zero false support. Eight complete answers recovered, including all five old misses. There are no checked partials in this 28-case cohort.

The remaining three positives ask for standalone writing or review dates without the current checker's literal subject-bearing dated anchor. They remain misses against the unchanged key; no complete-series acceptance is claimed. Explicit relative dates retain their original expression, arithmetic assumption and unknown year. Withdrawal, ambiguous dates, conflicting owners, missing roles, quotation, conditions and extra obligations remain withholding controls.

[Baseline score](scores/baseline.json) and [candidate 3 score](scores/candidate-3-v2.json) link raw outputs through stable IDs. Candidate 1 is retained in its original and corrected scores. Scorer v2 only folds layout whitespace when comparing date values: exact source coordinates and hashes remain checked. [Amendment](scorer-amendment-v2.json). Inputs and expected decision labels are unchanged.

Candidate 2 passed the initial 28-case contrasts but failed an additional frozen writing-date denial. Its 7/8 result remains in [Wrap evidence](wrap/freeze.json). The repaired candidate passes all eight, plus 33 inherited date/inspection controls. It now treats unparsed writing-date counterevidence as unresolved instead of completing from a convenient positive sentence. [Rejected archives](rejected-archives.json).

## Preservation and overlap

The 280-case release comparison completed: **275 exact unchanged contracts + five fully checked complete recoveries**; complete answers 97→102, checked partials 6→6, conflicts 6→6, abstentions 171→166, claims 122→127. The original v3 scorer's five 'unaffected contract changed' failures remain [unchanged](scores/preservation-candidate-3-original-v3.json). The [supplementary full-claim audit](scores/preservation-candidate-3-reviewed.json) accepts only exact input-hash joins to the five previously frozen date keys, verifies complete claims/qualifications/citations equal the separately scored replay, and preserves all other contracts. This is same-operator verification, not independent adjudication.

The five historical inputs overlap both cohorts: **308 memberships represent 303 unique semantic inputs**, before the separate eight Wrap controls. Do not sum recovered counts across these cohorts as independent gains. All 169 inherited native controls pass (56 focused, 92 integrity/authority, 16 reported-content, five accounting). Raw restricted PE-02 bytes remain in private custody; public receipts retain hashes and comparisons.

## Reproduce locally

```sh
MPLPB_REQUIRE_SANDBOX=1 python -m unittest tests.test_study_sandbox -v
python tools/cryptid_trial.py --registry evaluation/cryptid/mothman/development/registry.json --implementation READER_ROOT --source-commit READER_COMMIT --output NEW_DIRECTORY
python tools/cryptid_score_v2.py --registry evaluation/cryptid/mothman/development/registry.json --key evaluation/cryptid/mothman/development/key.json --run NEW_DIRECTORY --output NEW_SCORE.json
python -m unittest tests.test_documentary_date_roles tests.test_event_date_inventory tests.test_pinned_documentary_inspection tests.test_exploration_budget -v
```

All original sources and original dates remain frozen. Existing native caps are unchanged. Scoped committed candidate ZIP testing and once-only transfer are pending at this document freeze. The sixteen-case packet remains sealed; templates were visible to the same operator. Independent historical/semantic adjudication, preparation/blinding, outside-custodian scoring and native OOCC remain **NOT_RUN**. Human onboarding **NOT_RUN**. All work local; no remote publication authorized.

## First transfer retained

Committed scoped ZIP `a439ddc2c9e438863383b90c41d995d274785847`, SHA-256 `e00d606d708a3758b8e7775766d01014fa4e5faf7232800aa6a56d08cb20061e`, reproduced25/28development and41/41focused checks from extraction. Once-only transfer **8/16 decisions;0/8positives,8/8withholds;0false support**. Explicit named-document passive date clauses are unrecognized. This is a failed transfer claim, retained as development material. A fresh24case packet is sealed before the next native repair; same-operator/template exposure limits apply.
