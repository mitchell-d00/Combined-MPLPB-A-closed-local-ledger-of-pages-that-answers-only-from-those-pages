# Repository handoff

Last reviewed: 2026-11-21.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `692f72eee2ec743e084a98708737e9ca571be7a3` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `fc19efc44d3a50fb9f3fbba2d96327f99363b9ab8a5839fd926834bfd9365416`.

## Latest user update instructions

Make this explicit in read me

## Implemented scope

- Introduce Combined MPLPB as a deterministic, rule-based AI reader and explain how the strict reader decides source support.
- Describe the test-driven training loop and link to the frozen paraphrase reproduction and the Primary Book Test.

## Validation recorded

- The documentation audit, infrastructure check, and 18 focused tests passed.
- The unchanged public reproduction confirmed 750 of 750 supported paraphrases and all 200 expected refusals on the current engine.

## Limitations and blocked checks

- The comparison describes the published frozen synthetic experiment. Independent semantic review on unfamiliar historical prose remains a separate measurement.

## Next steps

- Use fresh Primary Book Test batches and independent reviewers to measure transfer to unfamiliar sources.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
