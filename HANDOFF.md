# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `2b177c7363d9c25d8a55a4043675150f20941806` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `11ec56e572155c3aafe452b244eeef704160288de290ea5d2c699618546d39e5`.

## Latest user update instructions

Continue the public MPLPB Pole training loop on pin 941511731b6b5af8d767110930aee7b92a1dcc5a.

Prior results (keep frozen):
- FRUS-SingleClass: same four FRUS cases + four negative controls + one same-form wrong-speaker control. Discovery 4/4. Complete Strict Ask 0/4. One checked partial (PE-04 source-reported proposition). PE-01/02/03 misses. All five controls withheld. Zero false-supported bridges.
- PE-04 advice witness: “Mr. Samuels suggested that Secretary Stans stress ‘outwardness’ rather than ‘inwardness’ in trade policy.” Adjacent trip witness present. Separately reported first-person presentation remains unresolved.
- Retained: Tacitus 3/6, Douglass 6/12, both DHS complete, BT-Erratum 1/1, Babbage caps, Komnene packet sealed (scoring NOT_RUN), Focus-12 0/12.
- Independent historical accuracy, outside-custodian scoring, independent semantic adjudication, and native OOCC remain NOT_RUN.

Goal: test whether an exact witness can bind the separately reported first-person presentation in PE-04 to its speaker, or whether the current rule is limited to the source-reported advice form. Freeze any new control before scoring. Do not raise scan or phrase caps. Preserve all previously closed results. Do not claim independent historical accuracy or native OOCC.

Run one named test:

1. FRUS-Presentation
   - Use the same four frozen FRUS cases and the existing five controls from FRUS-SingleClass.
   - Write and freeze one candidate rule that attempts to bind the separately reported first-person presentation to its speaker using only exact witnesses already present in the eligible originals. Require unique resolution, speaker continuity, reporting-layer preservation, and existing budget checks.
   - Add one new negative control that matches the presentation surface form but lacks the required speaker or reporting-layer witness. Freeze it before scoring.
   - Score discovery, proposition admission, and complete Strict Ask separately.
   - Zero false-supported bridges allowed.
   - Report complete, partial, miss, expected withhold, and the exact witness used (or the exact reason for withhold) for the presentation binding.

After the test:
- Write the rule that was added (or the explicit withhold condition).
- Update the open-items README with before/after counts for these four cases only.
- Leave Focus-12, scan/phrase limits, outside scoring, independent historical accuracy, and native OOCC marked NOT_RUN or open as they currently stand.
- Commit the frozen cases, results, and rule under a new public pin.

Return the result table for FRUS-Presentation, the rule text, the updated open-item list, the new commit hash, and the archive SHA-256.
Browser release validation remains the maintainer’s priority until the deployed smoke on PR #93 is cleared. The reader repair above is the next falsifiable step on the Pole track.

Make sure each pr gets the note so handoff because of context is easier

## Implemented scope

- Freeze the nine inherited cases, one absent-presentation-source control and the candidate rule before scoring.
- Bind two source statements in PE-04 using the advice record and the dated editorial account quoting the attributed memorandum.

## Validation recorded

- Discovery stayed 4/4. Complete Strict Ask moved 0/4 to 1/4. Positive partials moved from one to zero.
- Five inherited controls withheld. The new control preserved only the checked advice. No false-supported bridges or execution failures.
- An independent wording regression moved from partial to complete. Role, chronology, quote, list, ambiguity and budget controls passed.
- The first candidate trial withheld on a departmental title. The native readback is retained.
- The extracted source ZIP passed the Python suite with 1,731 tests run and two skips, all 52 public evidence checks, local Chromium and WebAssembly. The bundled engine replayed PE-04 and its new control.
- The retained Tacitus, Douglass, DHS, BT-Erratum, Babbage, and Focus-12 decisions matched. The Komnene delivery archive checksum matched.

## Limitations and blocked checks

- PE-01, PE-02, and PE-03 remain misses. The PE-04 comparison establishes record order and attribution. Event identity, implementation and impact remain unresolved.
- Focus-12 and scan and phrase limits remain open. Outside-custodian scoring, independent semantic adjudication, independent historical accuracy and native OOCC remain NOT_RUN.
- PR #93 stays in its separate browser validation lane. Its TeamBuilding handoff is recorded on the PR.

## Next steps

- Use the pinned evidence and exact witnesses to review the unresolved proposition classes. Keep release and deployment verification tied to the browser PR.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
