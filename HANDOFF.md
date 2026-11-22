# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f6b1d17c7246abdb7c08ee6214c29f464eae938f` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `2fc4346d8f8a457d8829fa19055fd7840e51e54374721d26b392b29554a6cfd6`.

## Latest user update instructions

That gives us separate targets for improving passage discovery and proving an answer from prose. Lets walk that path and devise a pattern rule

## Implemented scope

- Accept a complete natural date inventory form with explicit role and site guardrails. Reuse the existing proof kernel and preserve the full policy question.
- Add a separate bounded named-summary passage probe and a way to refresh the retained graph evaluation baseline against a new native revision.

## Validation recorded

- An independently worded fictional harbour example failed on the old grammar and passed after the repair. Focused regression tests cover scope additions, mismatched targets, reported events, calendar limits and competing sources.
- The unchanged original 22 had identical native contracts except code hashes. Exactly one of the 40 follow-up answers changed. The Fort Sumter paraphrase moved from abstention to supported with all reference anchors. The ten boundary questions kept full support withheld.
- All 52 public evidence controls passed with zero falsely supported bridges. The graph comparison reran on 52 new and follow-up rows. The Apollo 13 explicit-summary probe recovered the reference passage under the ordinary passage and character caps.

## Limitations and blocked checks

- The named-summary lookup is an experimental discovery path with no automatic proof use. Only the explicit section case was recovered in the Apollo pair.
- Retained results cover frozen development questions and known originals. Independent historical semantic review was not run.

## Next steps

- Collect independently written date-role requests and multiple well-formed section fixtures to test transfer. Keep Apollo causal proof separate from section discovery.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
