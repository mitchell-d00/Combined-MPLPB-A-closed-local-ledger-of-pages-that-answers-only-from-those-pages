# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `614b18cc34f5270d4cb7dfbbf8239391a9f83b31` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `624decfc6224ecc255a2cb56b1b52b598809e2eaa3ce99e4004e46dbc82b1b84`.

## Latest user update instructions

Continue with both evaluation arms.

Preserve the authentic historical corpus separately from the randomized synthetic controls.

Freeze and hash the source records, questions, scoring rules, and baseline code revision before evaluating performance. Run the unchanged baseline first, then evaluate any implementation improvements against the same frozen conditions.

Do not allow synthetic records or generated answer keys to contaminate the authentic-source evaluation.

Retain all correct answers, incorrect answers, missed relationships, false causal relationships, refusals, costs, and regression results.

Clearly label synthetic withheld-answer controls as distinct from independently blinded human evaluation. If external reviewers are unavailable, mark that evaluation NOT RUN.

Proceed with implementation and automated testing. Do not stop solely because independent human reviewers are unavailable.

## Implemented scope

- Implement the neutral unprepared-original reconstruction challenge in the actual repository using the existing ledger, gate, investigation, sealed-study and work infrastructure. Prepare a focused public PR with evidence, rather than claiming independent validation.
- Freeze five authentic public-domain/authorized source editions and 14 developer questions separately from 24 randomized fictional controls across 12 rare-topic domains. Never rewrite originals into answer fields or pool synthetic scores with historical results.
- Retain the measured profiled pilot, timeout and old harness. Use a versioned checkpoint/RSS harness with unchanged source/question/scoring hashes, unchanged 180-second budget and pinned baseline native code.
- Add opt-in eligible prose context candidates after an observed baseline evidence-discovery failure; never infer historical identity, apply corrections or promote candidate output.
- Generate source-linked review packets and strict separate-human/adjudication scoring, with all actual independent human evaluation marked NOT RUN. Preserve unknown costs/metrics rather than inventing zero.
- Preserve historical artifacts, source authority, fencing and source-change safeguards; add targeted positive, negative and regression tests.

## Validation recorded

- 19 challenge/prose unit controls pass. The unchanged baseline authority/contract suite passes 137 tests; logs and exact source revision are retained.
- Both frozen baseline arms are executing in real Linux namespaces. Synthetic baseline cases completed; authentic baseline is still running. No final performance conclusion is claimed yet.

## Limitations and blocked checks

- Independent question authorship, separate human review and adjudication are NOT RUN. Developer-authored historical questions and randomized synthetic controls do not establish independent blinding.
- Candidate context discovery is not historical reconstruction. Semantic precision/recall, false relationships, chronological accuracy and human effort remain unassessed until actual reviewers provide defensible references.
- Peak RSS is measured, allocation peaks are unknown in primary v2 runs. Host load and profiling changes preclude treating pilot versus v2 timings as implementation efficiency gains.

## Next steps

- Finish unchanged authentic baseline, then execute the modified implementation under the identical frozen primary conditions. Run actual search comparators and separate synthetic controls; publish complete outputs and failures.
- Complete frozen-candidate regression/archive checks, source-linked report and human packets. Prepare a focused PR with actual CI/publication receipts; no independent review or deployment is asserted without evidence.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
