# Conservative candidate relater v2 — 2026-11-18

All66 executions completed on frozen runtime4785b13c25c4cd88c3365d2524c4ff1624d786b4. Strict reader source files remain those of6350988; all three arms use identical22 questions, originals and180s/300s/2GiB worker limits,12 strict passages/8000 characters and12000 candidate characters.

| Arm | Complete strict answers | Draft reference span discovery |
|---|---:|---:|
| Sorter alone |1/22|26/32|
| Synonym Ranker |1/22|26/32|
| Both additions v2 |1/22|26/32|

H02 remains complete. H05 remains partial in all three arms, versus2/22 complete in the unchanged direct baseline. No new complete answer or discovery gain over sorter-only is established. Removing weak relationship traversal recovers the twoU04 draft spans lost in v1; this returns to26/32 rather than establishing new recall. The995 neighbor-only pair suggestions from v1 are removed; the38 literal shared-wording reviews remain inspectable, including irrelevant navigation wording. Four reviewed misleading neighbor links disappear and four reviewed useful textual cues remain; the16-item sample is post-run, biased and not a global false-link rate. Identity and historical relationships remain unverified.

The full regression suite passed1242 tests in408.304s. Default core sorter and strict reader/proof/eligibility files remain unchanged. Detailed case results, original passages, suggestion classes as then implemented, scores, links, failed controls and costs are retained. Fresh mechanical replay and proof/source-byte auditing are separate from semantic assessment. Independent human/unseen evaluation NOT RUN.

The later request to protect reader-assigned proof witnesses is a new experiment. Reserving source-discovery passages alone did not repairH05: the partial answer compares navigation/framing and the wrong draft paragraph instead of retaining the required truth-wording witnesses. This failure is preserved; later routing code must not relabel these results. The subsequent goal is22/22 correct outcomes (complete cited answers or evidence-justified conflict/abstention), with the complete-answer count separate. Generic implementation refusals cannot automatically count as correct source-gap outcomes.

Rerun from exact4785b13 checkout: `python -m tools.sorter_options_study prepare NEW_DIRECTORY`, followed by `python -m tools.sorter_options_study run NEW_DIRECTORY --arm sorter-alone`, `--arm synonyms`, and `--arm synonyms-relater`. Existing outputs refuse overwrite. Source corpus/question/rule hashes and per-worker checkpoints, measurements and logs are frozen in this directory.
