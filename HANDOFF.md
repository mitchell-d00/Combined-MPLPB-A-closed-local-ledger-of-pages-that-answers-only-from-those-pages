# Repository handoff

Last reviewed: 2026-11-20.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `27f6fe9ed9be1ed39ddb7721deeb82cf9e2ad4de` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `362a996a3b33152ec1e66dd10658057c9a09e9a87955911193e1b3dd959e170b`.

## Latest user update instructions

Do do search update call it adaptive search   Is that aproprate

Once we are done we will rewrite the paper is A search works

## Implemented scope

- Add optional Adaptive Search to the native documentary investigate CLI and Python API.
- Preserve seed order and breadth-first hop boundaries. Prioritize declared supersession targets and question terms not yet encountered within a hop.
- Report the deepest visited hop and deepest completed hop. Preserve checked findings under existing evidence and source-state verification.

## Validation recorded

- The authored paired test first failed because the requested mode was unavailable. After implementation, the same three-source budget reached the authorization document while discovery order reached a duplicate.
- Thirty-nine focused investigation, verifier, reference identity and D4 test cases passed. Documentation and repository infrastructure audits passed.
- Both the unchanged main baseline and candidate each passed all 52 public-evidence controls on replay. An earlier candidate run returned one intermittent invalid_budget outcome in a completion-receipt control; it did not recur in the isolated probe or paired replay.

## Limitations and blocked checks

- Adaptive Search is opt-in. The ranking uses lexical coverage and declared links as scheduling signals. It does not grant answer support, discover undeclared links, or establish historical truth.
- Authored comparisons establish the specific scheduling behavior. Broad retrieval benefit, latency and independently checked historical accuracy have not been measured.

## Next steps

- Validate the frozen candidate ZIP and its release checks before merge.
- After successful verification, update the research paper with the observed bounded result and remaining research questions.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
