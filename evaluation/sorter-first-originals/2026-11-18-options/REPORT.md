# Three-arm sorter review trial v1 — 2026-11-18

All66 executions completed on the same22 frozen development questions, original sources, strict reader file pins6350988 and180s/300s/2GiB worker limits. Optional runtime source commit0c488a1ec93a6869df348755c31eb22be81d0d2c. Core sorter and strict reader/authority/proof files are byte-unchanged.

| Arm | Complete strict answers | Draft reference spans returned |
|---|---:|---:|
| Sorter alone, common source-discovery reservation |1/22|26/32|
| With Synonym Ranker |1/22|26/32|
| With both additions v1 |1/22|24/32|

No new complete answer was produced. H02 remains complete; H05 remains partial in all three arms. Reserving native source facets was insufficient to preserve the complete comparison. The original unchanged direct baseline remains2/22, with27/32 draft spans returned; the earlier unreserved sorter retest remains1/22 and25/32. These are separately frozen experiments, not relabeled scores.

Relative to sorter alone, v1 ranker/both options changed no native answer outcome. Adding the relater lost two draft spans forU04. comparison.json records every question and exact original passages for these losses. Source discovery coverage against incomplete developer references is not semantic accuracy, complete historical recall or a new answer.

The relater proposed1033 distinct source-pair/type suggestions across queries:995 neighbor-based possible-related passages and38 literal shared-wording reviews. Its generic vocabulary links were too broad. In a post-run exploratory developer/AI review of16 full short-quote pairs,4 were useful textual reviews,4 misleading candidate connections and8 irrelevant website wording. The sample was biased toward short passages and is not an independent or representative false-link rate. See developer-link-sample.json for every source quote, label, reason and sampling rule;1017 unique suggestions remain unassessed. No global false-link rate is claimed.

The complete v1 regression suite passed1240 tests in393.549s. Separate test and byte-replay fidelity does not certify semantic meaning. All candidate support/truth flags remain false. No eligibility, ownership, correction or proof rule was changed. All source spans, queries, proposed links, costs, incorrect suggestions and refused/partial outcomes are public. Independent human and independently unseen evaluation NOT RUN;22 questions are development data.

These measured failures motivated a separate conservative revision: keep synonyms for ranking, forbid neighbor-only documentary edges, and stop traversing weak wording/subject reviews. The failed trial and its frozen runtime remain preserved; later results require their own dated directory.

Rerun from exact0c488a1 checkout: `python -m tools.sorter_options_study prepare NEW_DIRECTORY`, then `python -m tools.sorter_options_study run NEW_DIRECTORY --arm sorter-alone`, `--arm synonyms`, and `--arm synonyms-relater`. The same12-passage/8000-character strict display budget and12000-character candidate budget apply. Preparation includes both legacy sorter modes under unchanged default limits; original source layout is projected reversibly, without answer-bearing fields. Per-question review generation is counted separately from native phase measurements; whole-worker CPU and parent wall time include setup. Compute prices and human times are unknown.
