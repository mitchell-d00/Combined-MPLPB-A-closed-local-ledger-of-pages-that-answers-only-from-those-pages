# Reader-owned proof-witness admission — 2026-11-18

The routing regression is repaired. H05 remains complete at the original12-passage/8000-character limit in direct and all three sorter arms. H02 also remains complete. This restores the historical2/22 complete-answer baseline; it does not demonstrate broader complete-answer coverage or22/22 correct outcomes.

## Frozen conditions

Runtime: `6aa4ecd4d052af2b554abd0da2fd465f11c9fef6`. Unchanged historical reader baseline: `6350988a2f64d8e5fa53bd187d368f4397bf4f4c`. Earlier admission trial: `4b6b1f67c231df756a3b7eefb13b13cc3a9b9436`. The same22 development questions,8 original documents, source import, original bytes and draft references are retained. All88 final workers completed under180-second wall,300-second CPU and2GiB memory limits. Freeze/protocol files retain source/question/runtime hashes; scoring references are not mounted into isolated workers. The three sorter arms use exactly one reader revision and identical limits. No new answer-bearing source fields or glossary were supplied.

## Actual failure and repair

The sources imported and round-tripped; the original regression was evidence selection. Unreserved truth-word hints from Darwin displaced Declaration content/framing witnesses. A first-discovery reservation retained the wrong source units and failed to restore completeness. Existing kernel recognition already knew how to verify the required source-framed comparison when its complete witness set survived.

`passage_admission.py` now reserves atomic native-rule witness sets by question part, deduplicates exact source spans before charging and shares one budget through final assembly. Native discovery is separately bounded and costed. Sorter classes explain inspection reasons; synonym/shared-wording suggestions receive no automatic slot or traversal. Existing native rules and fresh eligible originals determine proof. `documentary_verify.py` remains byte unchanged (SHA256 `9b01a7370287178552ce17e57337d271b277457e1ba8131f8a4c931ae8064d8a`).

The first admission trial completed88 workers but failed one of1249 regression tests: the legacy adapter tagged every ordinary result as a hint. That failure and its complete outputs are preserved in the sibling `2026-11-18-witness-admission` directory. The compatibility fix uses the index's independent native query retrieval when no ordinary passages remain, without admitting search-only hints. Existing tests were not weakened. This final trial uses a separate code freeze and result directory.

## Measurements

| Arm | Complete strict answers | Draft spans visible | Additional draft spans located only in review | Whole-child CPU seconds | Summed parent worker wall seconds | Peak worker RSS bytes | Logical original HTML bytes read |
|---|---|---|---|---|---|---|---|
| direct | 2/22 | 27/32 | 0 | 308.64 | 388.01 | 51843072 | 9658683974 |
| sorter-alone | 2/22 | 27/32 | 0 | 373.47 | 451.91 | 253206528 | 9749888842 |
| synonyms | 2/22 | 27/32 | 0 | 357.37 | 437.12 | 223502336 | 9704286408 |
| synonyms-relater | 2/22 | 27/32 | 0 | 357.01 | 443.70 | 222973952 | 9704286408 |

Each final arm returns2 supported,1 partial,3 conflict and16 abstain. Only H05 changes native outcome relative to conservative v2. Exact before/after claims, original passages, source URLs and byte coordinates are in `witness-comparison.json`; no newly complete question beyond the original two is established. Draft-span coverage uses32 inspected draft anchors (23 historical,9 government); this is not independent historical recall. Review-only discovery and strict completeness are separate. Synonyms and the relater add no newly located draft anchor or complete answer here. Global relationship precision/recall, false-link rate, missed historical relationships, appropriate-refusal accuracy and correct-outcome score remain unmeasured without defensible complete semantic labels. Generic refusals are not automatically credited as correct.

Costs are measured, but concurrent local execution and differing preprocessing prevent controlled efficiency claims. Raw per-case CPU/wall/peak memory/read measurements, review preprocessing costs and failures remain retained. Logical bytes read are not physical disk traffic. Actual model/API use was zero; compute price and real human labeling/correction/review/adjudication time are unknown, not zero.

H05 admits the same four source spans (native canonical character offsets; raw-byte mappings are recorded separately): rough-draft content1122–2964 and framing259–623; final-transcript content1537–3165 and framing799–1035. Together they cost4070 characters and4 unique slots. Repeated offers avoid14 duplicate charges. `H05-admission-trace.json` retains each arm's admitted passages, reader roles, discovery bounds, blocked spans and final citations. Native proof certification remains separate from admission and original-byte fidelity.

## False links and retained limitations

The earlier v1 review trial proposed1033 unique links, including995 loose neighbor-only pairs. Its biased16-item developer/AI sample labeled4 useful textual reviews,4 misleading links and8 irrelevant wording matches. The final conservative relater retains38 literal-wording reviews; the sampled4 misleading links are absent and4 useful textual cues remain. All8 sampled irrelevant wording matches also remain. `developer-sample-retention.json` preserves every paired judgment. This is a development retention check, not an independently measured general false-positive rate. Candidate identity, causation, chronology and correction remain unresolved; no sorter link becomes a deterministic fact.

## Regression, fidelity and independent review

The extracted frozen ZIP executed1249 tests successfully in479.177 seconds. The public fictional finite-contract suite passed52/52 separately; it is not historical accuracy. The final source audit freshly checked12 native claims and32 original-byte citations, and replayed44 suggestion files. Exact-span admission invariants pass for every reported documentary answer. Neither replay nor finite-rule checks establish unrestricted historical understanding.

The unchanged counterevidence control returns conflict when both eligible statements fit; with one slot it withholds completion and reports `contradictory_passages_pruned`. Generic multi-part and duplicate-span controls also pass. Full logs retain hash, eligibility, supersession, source-change, exclusion, permission, inference, receipt, work-history and other existing regression checks. See `full-regression.json` for exact tested archive SHA. These local checks are not postdeployment validation; the PR's exact-head ZIP/browser CI remains a separate release gate.

`independent-review-packet.json` provides source-linked outputs, two-reviewer instructions, null assessment/time fields and explicit adjudication requirements. Independent human review and genuinely unseen-original evaluation are NOT RUN. The22 questions are development data. The goal remains22 evidence-justified correct outcomes, counting complete cited answers separately from genuine source-backed conflict or abstention.

## Reproduce

Use a clean checkout of the runtime revision above and a new output directory (commands refuse overwrites):

```sh
python -m tools.sorter_options_study prepare evaluation/sorter-first-originals/local-replay
python -m tools.sorter_first_study run evaluation/sorter-first-originals/local-replay --arm direct
python -m tools.sorter_options_study run evaluation/sorter-first-originals/local-replay --arm sorter-alone
python -m tools.sorter_options_study run evaluation/sorter-first-originals/local-replay --arm synonyms
python -m tools.sorter_options_study run evaluation/sorter-first-originals/local-replay --arm synonyms-relater
python -m tools.report_witness_admission evaluation/sorter-first-originals/local-replay
python tools/audit_sorter_options_study.py evaluation/sorter-first-originals/local-replay --implementation . --include-direct --output evaluation/sorter-first-originals/local-replay/fresh-source-audit.json
python -m unittest discover -s tests -q
```

Linux Bubblewrap with permitted namespace creation is required. There is no unsandboxed worker fallback. An initial host namespace denial is retained separately under `2026-11-18-witness-admission/launch-blocked`; those launch failures are not performance outcomes. Historical baselines, questions, originals and failed trials remain unchanged.
