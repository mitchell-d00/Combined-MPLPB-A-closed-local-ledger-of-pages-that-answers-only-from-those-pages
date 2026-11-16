# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `1cc0b83ded9185428b92b1d4f08b8288e97c6d9c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `7df492f5579b8c223875b7fc1b6f168f82c76e9352f9a51d4a89165e1e08191f`.

## Latest user update instructions

CODEX: Repair MPLPB’s Source Conversion, Mapping, and Round-Trip Reconstruction

Investigate why those existing capabilities are not producing useful historical evidence reconstruction when presented with previously unprepared original documents.

Fix the underlying conversion, indexing, mapping, retrieval, or reconstruction problem wherever the evidence shows it occurs.

Do not assume that MPLPB needs an entirely new architecture.

Do not assume the reported 0/14 supported-answer baseline means source conversion failed. Determine the precise failure stage before modifying implementation behavior.

Do not overwrite the baseline or alter the frozen questions, source corpus, answer keys, or scoring criteria.

If a benchmark is currently executing, preserve its completed outputs and let the existing execution reach a documented terminal state before replacing any relevant code.

MPLPB should be able to receive unfamiliar information, preserve the original, organize it into useful native objects, reconstruct the supporting evidence, and distinguish what the source actually establishes from what the system merely proposes.

The goal is to improve MPLPB’s real capabilities, not to change test scores artificially.

Begin by determining whether the historical baseline failed at import, indexing, retrieval, semantic mapping, or verification. Repair the earliest demonstrated bottleneck while preserving the rest of MPLPB’s existing architecture.

## Implemented scope

- Implement the neutral unprepared-original reconstruction challenge in the actual repository using the existing ledger, gate, investigation, sealed-study and work infrastructure. Prepare a focused public PR with evidence, rather than claiming independent validation.
- Freeze five authentic public-domain/authorized source editions and 14 developer questions separately from 24 randomized fictional controls across 12 rare-topic domains. Never rewrite originals into answer fields or pool synthetic scores with historical results.
- Retain the measured profiled pilot, timeout and old harness. Use a versioned checkpoint/RSS harness with unchanged source/question/scoring hashes, unchanged 180-second budget and pinned baseline native code.
- Add opt-in eligible prose context candidates after an observed baseline evidence-discovery failure; never infer historical identity, apply corrections or promote candidate output.
- Generate source-linked review packets and strict separate-human/adjudication scoring, with all actual independent human evaluation marked NOT RUN. Preserve unknown costs/metrics rather than inventing zero.
- Preserve historical artifacts, source authority, fencing and source-change safeguards; add targeted positive, negative and regression tests.
- Trace all 14 original questions through acquisition, import, indexing, actual retrieval and interpretation; preserve all earlier executions.
- Add bounded source-context expansion, reversible lexical candidate structures and exact raw-source reverse coordinates using existing native gates and answer contract.

## Validation recorded

- Baseline source integrity verified; baseline targeted authority regressions: 137 passed.
- Initial implementation full suite: 988 passed; repaired full suite: 994 passed in 453.483 seconds.
- 25 focused protocol, source conversion, fresh-process public-original integration and mapping controls passed in extracted source.
- UI script, JavaScript API, browser transport and crawler fixture checks passed from extracted committed ZIP 1cc0b83.
- Prepared public suite: 52/52; separate randomized finite-contract controls: 24/24 for baseline, initial update and repair. Repair controls are public-key regressions, not a new blind.
- All 14 repaired historical questions completed under the unchanged 180-second budget and frozen v2 conditions. Draft span coverage: baseline expert 0/23, initial prose 5/23, repair 10/23; native support remains 0/14.
- 96/96 returned citations match canonical source text; 865/865 candidate objects and 126 unique raw passages passed post-run fidelity checks. All 23 draft-reference passages round-trip to original bytes.
- Documentation inventory and infrastructure checks passed; exact final-head CI results are available on PR #44 and must be checked before release.

## Limitations and blocked checks

- Independent human historical evaluation, independent unseen question authorship and adjudication NOT RUN. Review packets prepared, no participant identities or times invented.
- All semantic event/relationship/correction precision/recall and false-positive historical judgments remain unknown. Draft-span coverage is retrieval only.
- Lexical candidate rules do not establish unrestricted semantic meaning, event identity, chronology, correction scope, causality or source truth. Native supported coverage remains zero in the authentic study.
- Repeated source reads impose measured processing costs; no efficiency improvement claimed. Compute price and human times unknown.
- Historical corpus editions/OCR, lossy canonical layout projection, incomplete retrieval and unreviewed draft references limit conclusions.
- No deployment or independent external review claimed.

## Next steps

- Review the focused public PR #44, exact-head CI and complete dated research report.
- Obtain two genuinely separate historical reviewers and separately authored sealed questions; adjudicate disagreements explicitly.
- Investigate remaining retrieval omissions and lexical mapping limits against retained failures in a new frozen, dated experiment.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
