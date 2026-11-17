# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `49b2360934cc2ebb37688414902d68f7b83d2cb8` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `a5a495cd823d046290224c99342384cc75c14e86bc90cb62faa63271285818f9`.

## Latest user update instructions

Rewrite the papers remove that I used Ai to write it “Prepared with AI-assisted implementation and writing.” Folks dismiss ai as sloppy I’m not sloppy did you upload th3 paper to my repo?

## Implemented scope

- Revise the published sorter technical paper in Markdown, text and PDF to remove the requested preparation sentence.
- Update the paper guide, version1.1 metadata, generated-format hashes and documentation catalog; preserve factual evaluation and independent-validation limits.
- Publish the requested paper-only revision through normal protected-main PR checks; no runtime or historical evidence changes.

## Validation recorded

- Prior paper was uploaded and merged to main by PR47, commit49b2360; publication workflow44093727619 succeeded.
- All three v1.1 formats regenerated with existing renderer. Exact editorial-only source diff, whitespace-normalized PDF/text sentence removal, retained validation limitations, nine-page count and all format hashes checked. Focused renderer/handoff/documentation tests12/12 passed0.225s.

## Limitations and blocked checks

- Historical semantic review remains NOT RUN; removing the preparation sentence does not alter the report’s measurements or support boundaries.
- Original historical sources, older papers and evaluation reports remain unchanged.

## Next steps

- Check rendered PDF/text, hashes and exact requested-sentence removal; run focused documentation/renderer tests from a committed archive.
- Push and merge the editorial PR only after exact-head required CI succeeds.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
