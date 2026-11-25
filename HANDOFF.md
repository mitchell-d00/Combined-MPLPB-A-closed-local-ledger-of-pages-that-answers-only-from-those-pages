# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `600b793524bc811d665a5795fdafba9e59c53c85` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `e6747bb99a4927cd56d2a1f8fb0a16c96e216d8912264aaefe9b9349dfea6dd0`.

## Latest user update instructions

Please use the verified record and field to write the caption for this answer route. The regression check should preserve the supported result and working citation in both the pasted-source and blank-URL local-file paths.

## Implemented scope

- Guide users through collection creation, local document import, sealed source review and Strict Ask in the browser.
- Support text and Markdown files or pasted text without a web URL. Seal the submitted text under a local content identifier with external delivery withheld.
- Keep Strict decisions visible when inspecting matches, and offer question editing and collection review after incomplete results.
- Document Thespian, Mitchell D. McPhetridge's multi-agent testing method, in the browser runbook with a configurable role prompt, pinned comparisons and separate custody of the answer key.
- Show the verified field and cited record on supported exact-field answers in the browser. The caption uses the existing Strict answer contract.

## Validation recorded

- Focused browser bridge and desktop API tests passed, including the local import hash, question support, external withholding and zero network calls.
- Chromium passed local file import, sealed source review, a cited Strict answer, partial evidence, separate inspection and a refusal using a developer fixture.
- The UI script, JavaScript API and browser transport checks passed.
- The integrity regression now checks the shipped Strict and Inspect choices, while Chromium checks their behavior. The targeted integrity, ledger, proof and browser suite passed 113 tests.
- The separate evaluator reported 3/3 predeclared answer and citation checks in each lane, 7 to 5 scripted navigation clicks for the paired workflow, and a misleading no-eligible-owner caption on supported field answers.
- The developer Chromium regression reproduced the caption bug on f225d14 and passed after the fix. It opens both a pasted source with an HTTPS label and a blank-URL local file, checks the field caption, source ID and answer text for each, then follows each citation to its reviewed source. The focused integrity and browser tests passed 47 tests, and the JavaScript API and transport checks passed.

## Limitations and blocked checks

- The file picker accepts UTF-8 text and Markdown. Local imports pin submitted text and retain unknown authorship.
- Matching page inspection does not establish documentary links or answer support. The browser follows the existing strict proof rules.
- The separate evaluator tested the original browser candidate on synthetic fixtures. Its report measures scripted path length and bounded answer checks.

## Next steps

- Keep c1e2100 and f225d14 as the original evaluation pins. Check the updated caption separately on the revised PR head before treating its browser artifact as evaluated.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
