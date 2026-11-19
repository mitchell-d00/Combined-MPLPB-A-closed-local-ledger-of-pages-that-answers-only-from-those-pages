# Repository handoff

Last reviewed: 2026-11-19.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `35069e83b016ef1ba707ab0ad425d29cbbc54bb4` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b4665e63ee5a2d36ce6839676ed41533099d83a3f962f4c8e53b78eaaa190eaf`.

## Latest user update instructions

With about 440 failures, you can see patterns instead of individual cases, and class fixes become obvious.
D% records every dice roll, so you can cluster the failures by which structural feature was rolled: passive voice, a stated cause, quoted speech, negation, partial correction, and so on. That gives you each feature’s failure rate. Fix the class with the most failures and rerun the frozen set. Repeat until it’s fixed

## Implemented scope

- Preserve frozen baseline20/600 complete,640/640 refusals;580 incomplete answerable cases,including37 partials.
- Persist mandatory general-class/no benchmark-rigging rules in AGENTS.md.
- Reconstruct and verify exact sealed roll trace and packets;group failures by family and structural choices,not actor names.
- Implement correspondence boundaries,source-scoped request grammar,Unicode/passive actions and exact explicit-cause closure in existing independent kernel.
- Iteration2:repair absolute source offsets,cover irregular passive counterevidence,and add literal-text location as a separate textual-only proof class.
- Final guard class:reject blank/wordless literal requests and verify word boundaries in original source context,not extractor clipping.

## Validation recorded

- Baseline20/600 complete;first class iteration160/600;second200/600 (160 source assertions,40 textual locations). Both full1240 reruns preserve640/640 refusals,zero observed D%false support.
- First candidate rejected:one full-suite failure and two lost historical partials from a doubled absolute source offset;all evidence retained.
- Second candidate restored historical2 complete,2 partial,3 conflicts,15 abstentions;all22 source/question seals unchanged.
- Second archived suite1417 tests passed,exit0;public control receipt pending at this handoff.
- Additional adversarial tests found blank/padded literal queries and clipped-source-word proof gaps outside D%distribution. Final guard patch66 focused tests passed,exit0.
- Generator,key,worker and questions unchanged;feature analyzer verifies all rolls and packets for every comparison.

## Limitations and blocked checks

- Historical complete-answer count remains2/22;broader reconstruction not solved.
- D%200 includes40 word-location questions,not40 additional historical relationships.
- Final guard candidate requires its own full archived regression and1240-case rerun.
- Independent semantic accuracy,candidate precision/recall and human effort remain unmeasured.

## Next steps

- Freeze final guard candidate;run full extracted-source regressions and identical D%packets.
- Rerun unchanged22 original-record questions and verify no partial/complete losses.
- Retain all intermediate failures;report remaining400 answerable gaps by general class rather than adding fixture branches.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
