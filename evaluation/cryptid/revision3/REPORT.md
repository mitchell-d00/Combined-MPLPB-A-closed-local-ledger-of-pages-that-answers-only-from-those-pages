# Local reporting-negation revision

Last reviewed: 2026-11-26.

**Published for review in PR #105. Acceptance FAILED; merge and deployment are blocked.** The tested full-source commit is `d265881fec092afffdda56cd8781438e40ef1cf7`, ZIP SHA-256 `c3ea1c2db6dfa13462c5a300fe060a1e3908cf2f0cc374850fdae9705e9dd282`. The fresh once-only packet completed **19/24 decisions**, with **five semantic positive misses, zero false-support flags, two budget stops and zero unscored cases**. All earlier packets, keys, outputs and original failure classifications remain unchanged. The sections below retain their before-archive scope; the [final review package](REVIEW_PACKAGE.md) gives the current state.

The reporting repair improves the frozen 32-case development comparison from **18/32 to 32/32**, removing two unsupported completion decisions caused by missed competing reporting evidence. Shared verb polarity now reaches that-clause, quoted, postposed and passive reporting forms. A curly-quotation boundary separates a printed byline from its following report. The native checker retains writer/reporter/actor distinctions, the complete reporting witness, unasserted embedded content under an outer denial, conditions, eligibility and final state checks. It establishes no independent authorship or execution.

The **prospective checked-partial policy** is a separate evaluation change. On 12 new fixtures, native contracts are unchanged: five supported partials, two complete answers and five abstentions. The old strict criterion scores 7/12 and rejects the five partials; the new criterion scores 11/12 and exposes one passive-question wording miss. This is not a reader coverage gain. The original temporal-partial strict-key failure is retained.

Before archive freeze, 419 prior Cryptid cases, 20 Thunderbird cases, 12 boundary cases and the first consumed 24-case packet preserve their contracts exactly. The second packet has 15 unchanged contracts plus recovery of the formerly unparsed “did not say” report. Its original key still disagrees with the native contract: the key expects `inner_negative=true`, while an outer reporting denial leaves the embedded assertion unasserted (`inner_negative=null`). The exact quoted payload remains in the source witness. The original failed scores remain failures.

The release comparison's original exact score is **276/280, failed**. All claims, qualifications, citations and answer statuses are preserved; four changes are solely examined-unit counts increasing from two to three, matching the existing three paragraph units. The additional 1,000/1,001-unit controls pass 2/2 and keep the 1,000-unit cap unchanged. The [measurement review](release-semantic-preservation-c1.json) does not erase the original failed exact comparison.

[Reproduced mechanism and frozen baseline](repair-freeze.json), [development](reporting-development/registry.json), [passive/present controls](reporting-shell-wrap/registry.json), [cap controls](reporting-budget-wrap/registry.json), [prospective policy](partial-policy-development/policy-v2.json), [pre-freeze results](pre-freeze-summary.json), [original-case membership and disagreement](development-memberships.json), [recovered source claim review](consumed-reporting-recovery-c1.json), [unchanged earlier final report](../final/summary.json).

A new 24-case cross-family packet is [sealed](fresh/transfer-seal.json) and remains unopened at source freeze. It varies document structures, question purposes, reporting forms and obligations. Preparation, implementation and scoring remain same-operator with visible generator templates. Any transfer-informed repair consumes that packet.

The full source ZIP will be stored losslessly as an unchanged base ZIP plus a small delta because this workspace cannot hold another flat archive. The reconstructed full ZIP must match its frozen SHA-256 before clean extraction and release checks. Existing ZIPs, packets, keys and scores stay intact.

Independent historical accuracy, semantic adjudication, preparation/blinding, outside-custodian scoring and native OOCC remain **NOT_RUN**. The twelve-person onboarding trial remains **NOT_RUN** until Mitchell returns actual observations. No participants are simulated. Required final software checks and the fresh packet are pending at this freeze.

## C1 semantic review

C1 is rejected despite passing its frozen 32 decisions. Same-operator review found that CRYPT-YETI-0121 wrongly expects a conflict between reporting C and denying that not-C was reported. Those statements can coexist. The original key and score remain unchanged. [Compatibility review](compatibility-review.json) explains the reader defect and the next frozen contrasts. Fresh transfer remains unopened; no final semantic acceptance is claimed.

## C2 state before the final archive

The representation now records **literal embedded-content polarity** separately from whether that content was asserted. Outer denial keeps the legacy `inner_negative=null` and `inner_polarity=unasserted` fields. Compatibility compares the literal payload, outer reporting sign and explicit conditions; it does not infer actual authorship or reporting occurrence.

All eight new compatibility controls pass, compared with four correct comparison decisions and no v2 fields in C1. The original 32 reporting keys score **31/32**: their incorrect conflict target remains a failed strict-key result. C1's earlier 32/32 score and rejected source archive are retained. This is a reader repair plus an explicit representation addition, not retroactive relabeling.

All 771 earlier executions pass the frozen semantic-preservation audit: every legacy claim, qualification and citation remains intact, except the predeclared recovery of the old “did not say” abstention. The additive literal fields are checked against exact source witnesses before legacy comparison. Four examined-unit measurements increase, and original exact-comparison failures remain available. The prospective partial-policy fixture still has one passive-question miss; its 12 native contracts remain unchanged.

The fresh 24-case packet remains sealed. C2 was informed by development compatibility controls, not transfer instances. Full committed-ZIP checks and final transfer remain pending at source freeze. [C2 machine state](c2-before-archive.json), [new frozen compatibility controls](reporting-compatibility-wrap/registry.json), [representation and migration policy](reporting-compatibility-wrap/representation-v2.json), [source-checked preservation audit](preservation-semantic-c2/summary.json).
