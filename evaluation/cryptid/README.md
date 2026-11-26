# Cryptid local test programme

Last reviewed: 2026-11-26.

Programme started from verified remote main `c01021c0b9983f9a607fbe782dea7ed5872d1f11`. Family names identify tests, never runtime facts or rules. Mitchell authorized branch/PR publication; PR #105 is open. The final transfer fails 19/24, so merge and deployment remain blocked. See [current review package](revision3/REVIEW_PACKAGE.md).

The ordered series are Mothman (date roles), Jackalope (question wording), Yeti (polarity/conditions/modality), Sasquatch (identity), Chupacabra (comparisons/corrections), Kraken (multipart/document links), Nessie (automatic source-linked representation), and Thunderbird (fixed-cap scale/counterevidence). [Programme state](programme.json) distinguishes planned work from executions.

For each series: freeze inputs, controls, expected claims and withholds, generator, key, harness/scorer hashes; retain current-reader baseline; implement the smallest evidenced shared operation; compare identical inputs and preservation; commit and archive; open fresh transfer once after candidate freeze. Transfer-informed changes consume that packet. Scoped study ZIPs contain the approved runtime, workers and public inputs; the final integration gate requires the complete tracked-source ZIP and clean extraction.

All preparation, implementation and scoring are same-operator. Sealing is custody control, not independent blinding. Historical/semantic adjudication, independent preparation/blinding, outside-custodian scoring and native OOCC remain **NOT_RUN**. Human onboarding remains **NOT_RUN** until Mitchell returns real observations.

## Preservation and accounting

Preserve the unchanged [280-case release comparison](../bubble-wrap/2026-11-25/continuation/development.json), its keys, original source hashes, 17 restricted PE-02 cases, earlier integrity, attribution, reported-content, citation, UI and budget controls. Inventory overlapping content by semantic input hash; cohort membership is not independent evidence. Restricted originals and their raw output remain in existing private custody.

Run records are append-only and separately identify execution status, reader outcome, scoring status, exact reader/harness/scorer versions, budgets, raw hashes, citations and exposure. Failed isolation or missing output is execution failure, never reader abstention. No unsandboxed fallback. Freeze explicitly reviewed target transitions before candidate scoring; all other valid claims, qualifications and citations must remain intact.

No inputs or keys are relabelled to make a run pass. Retain rejected candidates and original scores beside versioned scorer corrections. Recovered positives require full witness, qualification and citation review. Remaining misses stay visible.

## Ownership and rule map

Testing and Evaluation owns the programme; Reader owns shared parsing/proof; Ledger owns current source eligibility; Applications owns UI gates; Delivery and Project Operations owns committed archives/handoff. [Shared rule map](shared-rules.json) links operations to stable case IDs and cross-family preservation.

## Isolation

`MPLPB_REQUIRE_SANDBOX=1 python -m unittest tests.test_study_sandbox -v`

The default nested namespace launch failed two required checks. The same required command on the host passed four checks using real fail-closed Bubblewrap. Both transcripts are retained in [isolation evidence](gates/isolation.json). Workers receive only approved read-only native code and public inputs, bounded scratch/output, no host network, Git, credentials, keys, scorer or generator. The host operator remains trusted.
