# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `044ac27e2833341acba9e6ccb4973c304292ea4e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `57f921afa3eb44f9f53a15c235cc8cd3985b228deff6c0f10908edea042e3eb6`.

## Latest user update instructions

Build a generator based on all the errors we know see etc and generate more in more

## Implemented scope

- General whole-question literal field-request syntax in the existing exact parser; additive inspectable normalization; no core authority changes.
- Unchanged public reproduction preserved with baseline at published bbf6690 and pre-change 3483b1a; new tests and exact CSV scoring.
- Separate follow-up branch feature/field-question-normalization based on unmerged PR56; no merge performed.
- Additional instruction: write a response paper to the 19 November public evaluation after tests complete, citing the original paper/package members and reproducible source tests.
- Implement optional expanded D% generator/scorer around existing isolated worker;48 semantic families;1000cases frozen; all dice/keys hash-pinned in separate custody.
- User supplied another parser-only verification account; distinguish that from our completed full engine replay. Do not manufacture independent semantic review.

## Validation recorded

- New regression failed before fix; 37 focused tests passed after syntax change; nine expanded controls pass.
- Public reproduction: baseline 150/150 canonical,0/750 paraphrases; updated150/150 and750/750. All200 negative controls refused. Script runs exit0.
- Full frozen-archive regression and public evidence pending; never infer pass from prior candidate.
- Actual frozen 044ac27 public replay:900/900 exact field/value matches,200/200 negative refusals. Full native regression and frozenD%still running; five new generator tests pass separately.

## Limitations and blocked checks

- Literal field labels only; no semantic aliases or general historical reasoning.
- Public fixture now known development material; independent review NOT RUN.
- Browser/WASM/live-site and current historical/D% reruns not yet performed.

## Next steps

- Finish full native/public suite, original D% and expanded1000-case run; retain errors and unmet obligations.
- Freeze a complete follow-up including generator tests and run final full suite before response-paper claims.
- Write response paper with citations to every external package member via hash inventory; render md/txt/pdf; update docs/evidence/handoff. No merge.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
