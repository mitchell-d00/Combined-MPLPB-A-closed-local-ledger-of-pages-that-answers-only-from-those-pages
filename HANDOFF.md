# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f225d142ebad6bb714007374a3f946b3c413202e` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `59eac22b50a63e402f63f48b53c02a30cf070559f28bb6727042ea2b4368bb7e`.

## Latest user update instructions

Do that

## Implemented scope

- Guide users through collection creation, local document import, sealed source review and Strict Ask in the browser.
- Support text and Markdown files or pasted text without a web URL. Seal the submitted text under a local content identifier with external delivery withheld.
- Keep Strict decisions visible when inspecting matches, and offer question editing and collection review after incomplete results.

## Validation recorded

- Focused browser bridge and desktop API tests passed, including the local import hash, question support, external withholding and zero network calls.
- Chromium passed local file import, sealed source review, a cited Strict answer, partial evidence, separate inspection and a refusal using a developer fixture.
- The UI script, JavaScript API and browser transport checks passed.
- The integrity regression now checks the shipped Strict and Inspect choices, while Chromium checks their behavior. The targeted integrity, ledger, proof and browser suite passed 113 tests.

## Limitations and blocked checks

- The file picker accepts UTF-8 text and Markdown. Local imports pin submitted text and retain unknown authorship.
- Matching page inspection does not establish documentary links or answer support. The browser follows the existing strict proof rules.
- Independent evaluator baseline and candidate results are pending.

## Next steps

- Use c1e2100 as the evaluator baseline and rerun the same documents, questions and delivery profile on f225d14. The subsequent regression-test revision has the same browser and engine source.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
