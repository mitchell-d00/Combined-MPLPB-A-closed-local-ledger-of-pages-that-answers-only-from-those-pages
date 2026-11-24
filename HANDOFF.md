# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6c3b51023bc350cfdf9341694406f0cded191893` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5e1ac74313ed498b2eecfe463c95414bc907590a1bcbc38adb7b2594a03dde0d`.

## Latest user update instructions

Next prompt
Continue the public MPLPB Pole training loop on pin 53408cdb452cda5aadf10cc42a4d9e50a388c4e2.

Prior results (keep frozen):
- Tacitus: 0/6 → 3/6 authentic bridges (zero false-supported). Venue change, filing-deadline, and two amended instructions now complete. Two DHS cases and B-Tests attribution remain open.
- Douglass: 6 of 12 authentic wording variants moved from miss to complete. Original 12 synthetic misses unchanged.
- Babbage: sorter retains both records under the 8-slot cap; bridges complete only when both eligible.
- Komnene-Outside: package ready; independent scoring still NOT_RUN.

Goal: close or correctly diagnose the remaining open cases without inventing links or producing false-supported bridges. Freeze every new case set before scoring. Preserve the same public accounting (pinned commit, archive hash, before/after counts, explicit NOT_RUN labels). Do not claim independent historical accuracy or native OOCC.

Run these four named tests:

1. Herodotus-DHS (remaining authentic Federal Register cases)
   - Isolate the two open DHS cases and the B-Tests attribution case from Tacitus.
   - Apply the existing Federal Register correction-form rule and any minimal extension required for these specific forms.
   - Score discovery and Strict Ask separately. Keep negative controls.
   - Report whether each moves to complete, partial, or correct withhold, and the exact reason for any remaining withhold.

2. Polybius (relations without explicit publication references)
   - Draw a small authentic set where the relation is implied by ordinary prose (dates, docket language, agency action, or sequential amendments) but lacks an explicit volume/page/document-number citation.
   - Measure whether a supported bridge can be formed or is correctly withheld.
   - Include negative controls that look similar but lack a verifiable chain.
   - Zero false-supported bridges allowed.

3. Lovelace-Limit (phrase-token / phrase-group and corpus-size behavior)
   - Re-run the multi-record cases while forcing the phrase-group limit and while increasing corpus size past the point where complete literal lookup previously degraded (31–34 pages).
   - Record exactly which budget or limit causes the drop from complete to partial or withhold.
   - Confirm the sorter still retains both records when both are eligible.

4. Komnene-Ship (outside packet delivery)
   - Confirm the existing 22-question / 44-arm Komnene-Outside package is still sealed and matches the concealed mapping.
   - Produce a delivery-ready archive and checksum. Leave independent scoring marked NOT_RUN.

After the tests:
- Write any new or refined rule that was added.
- Update the open-items README with before/after counts.
- Leave independent historical accuracy and native OOCC marked NOT_RUN.
- Commit the frozen cases, results, and rules under a new public pin.

Return the four result tables, any new rule text, the updated open-item list, the new commit hash, and the archive SHA-256.
Send that. The names are Herodotus-DHS, Polybius, Lovelace-Limit, and Komnene-Ship.

Booster for the agent
You are operating inside a public, pinned, constraint-first loop on MPLPB Pole.

Governing rules (non-negotiable):

1. Generate → Constrain → Kill → Select → Recurse.
   A proposal is only a candidate. It must be frozen against the current pin before scoring.

2. No ledger → inadmissible.
   Every change must produce: frozen cases, before/after counts, explicit withhold conditions, and a commit hash. Missing any of these = invalid.

3. Hard kills (immediate rejection):
   - Narrative immunity (“it failed because it’s deeper”)
   - Constraint retrofitting after a miss
   - False-supported bridges
   - Claiming independent historical accuracy or native OOCC
   - Authority drift (“the model said so”)
   - Decorative recursion once host-domain closure is reached

4. Straight-Line Boundary:
   When the remaining open cases are either complete under an explicit rule or correctly withheld, and no further falsifiable work remains at this resolution, terminate. Mark everything else NOT_RUN.

5. Bridge discipline:
   Every new rule must cash out into host primitives (exact witnesses, unique publication resolution, chronological order, budget limits). If it only works when the documents already contain the answer in the form the rule expects, or only on synthetic cases, it fails.

6. Public stress is an operator, not governance.
   Outside judges and negative controls increase pressure. They do not replace the ledger.

Current open items on pin 53408cdb452cda5aadf10cc42a4d9e50a388c4e2:
- Two DHS cases
- B-Tests attribution case
- Original 12 synthetic misses
- Relations without explicit publication references
- Phrase-token / phrase-group limits and corpus-size degradation
- Komnene-Outside independent scoring (NOT_RUN)
- Independent historical accuracy and native OOCC (NOT_RUN)

Zero false-supported bridges is a hard invariant. Preserve all previously closed cases (Tacitus 3/6, Douglass 6/12, Babbage caps).

Return only: result tables, any new rule text, updated open-item list, new commit hash, and archive SHA-256.
It is the extract of my past stack applied to the current pin.

## Implemented scope

- Freeze Herodotus-DHS, Polybius, and Lovelace-Limit with separate development reference custody.
- Verify successive publication corrections, scope attribution, and the distinction between applicability and effective dates.
- Instrument the existing literal scan and verify the byte-identical Komnene-Ship delivery archive without scoring.

## Validation recorded

- Herodotus-DHS recovered 2/3 complete answers with 2/3 discovery coverage, 4/4 expected withholds, and no false support. All three previously complete Tacitus claims matched.
- Polybius preserved 0/6 complete, one partial, five misses, and 6/6 expected withholds. Native discovery found all anchors in three cases.
- Lovelace-Limit identified the 200,000-character and 1,000-unit caps independently at 40 pages. The authentic ladder became partial at 31 pages and remained partial through 42.
- Komnene-Ship preserved 22 paired questions and 44 arms and matched all 22 packet hashes to the separately held mapping.
- All four additional frozen dependency controls withheld despite unchanged follow-up wording. The retained Douglass 6/12 decisions and Babbage cap and eligibility outcomes reproduced.
- The exact extracted source archive passed 52 public evidence controls, Pyodide and Chromium, and ran 1,722 Python tests with two skips.

## Limitations and blocked checks

- BT-01 still abstains under unsupported interpretation. Ordinary-prose relation assembly and literal uniqueness under bounded scans remain open.
- Development workers had no custody path and were not OS-isolated.
- Independent historical accuracy, native OOCC, and outside scoring remain NOT_RUN.

## Next steps

- Build a reported-erratum proof that preserves scope and the distinction between withdrawal and a prior verification-limited statement.
- Freeze further ordinary-prose relations and investigate bounded literal scan behavior.
- Provide the delivery archive and checksum to the outside judge through a separately authorized destination.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
