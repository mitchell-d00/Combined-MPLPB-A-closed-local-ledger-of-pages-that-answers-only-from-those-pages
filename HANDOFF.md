# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f9e71b9e124eb1843dc9d412628faf192f0ba6bf` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `74043445e8d247c2f51f458ecd01d5a319572b8d7e7fad6836bc2303ff631363`.

## Latest user update instructions

Let’s expand it the test that generated the 22 and see if we can find the patterns

## Implemented scope

- Add a separate frozen 40-question extension on the exact source bytes from the historical 22, with ten matched quote, direct, paraphrase and boundary groups.
- Record native outcome, cited reference anchors, and bounded passage visibility for the focused question pairs.

## Validation recorded

- All 40 cases ran at the f9e71b9 engine state. The independent passage probe replay preserved all 40 native contracts.
- The native reader fully supported 4/10 exact quote controls, 1/10 direct questions and 0/10 paraphrases. Nine quote controls cited their anchor. All 10 boundary controls withheld full support.
- The passage probe surfaced all selected anchors for 7/10 direct and 7/10 paraphrased queries. Three focused test harness checks passed.

## Limitations and blocked checks

- The extension uses authored follow-up questions and selective source anchors. These results measure retrieval and native proof behavior under frozen conditions. Historical accuracy and independent semantic grading remain unmeasured.
- The passage probe uses a separate entry point. Visibility there does not establish the strict reader's causal failure mechanism.

## Next steps

- Vary documentary date-role wording around the Fort Sumter case without weakening rupture and scope guards. Test contingency, attribution and permission-plus-limit classes separately. Inspect Apollo 13 passage discovery before changing a causal proof rule.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
