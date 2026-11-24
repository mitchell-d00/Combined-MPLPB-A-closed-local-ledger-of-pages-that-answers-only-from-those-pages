# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `b1200a4fb533c5fe07130614b3e0bcbacfc284ff` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `265ecb1f545bdad92e96426e78a35ba384f67cec5cf21d5402a47ef30c613cc8`.

## Latest user update instructions

Prompt for the bot
Continue the public MPLPB Pole training loop on the current pin.

Goal: close the remaining authentic relational gap (0/6 Strict Ask complete even when discovery finds the anchors). The two existing proof paths only succeed when documents already contain explicit named links. We need a rule that can form or correctly refuse a supported bridge from ordinary prose without inventing links.

Run these four named tests. Freeze every case set before scoring. Keep the same public accounting: pinned commit, archive hash, before/after counts, explicit NOT_RUN labels, and zero false-supported bridges. Do not claim independent historical accuracy or native OOCC.

1. Tacitus (link-establishment from ordinary prose)
   - Draw a small authentic subset where the relation is stated in plain language but not as an explicit request–dispatch–receipt or “see also” chain.
   - Score discovery and Strict Ask separately.
   - Include the usual negative controls.
   - Report: anchors found, bridges formed, bridges withheld, any unsupported bridges.

2. Douglass (authentic partial corrections)
   - Re-run the original 12 Pole miss family using real archive/Federal Register wording instead of the synthetic explicit-reference versions.
   - Measure movement: complete miss → partial → complete.
   - Confirm the sorter no longer exhausts slots when multiple supporting records exist.
   - Keep negative controls.

3. Babbage (multi-document proof under resource caps)
   - Re-test the multi-record cases (Ada Lovelace style) with the current sorter.
   - Force both the eight-slot cap and the phrase-group limit to trigger.
   - Verify that retaining both records does not later produce a false-supported bridge when one record is ineligible.

4. Komnene-Outside (prepared packet)
   - The 22 anonymous paired cases are already prepared.
   - Package them for outside semantic review with concealed keys.
   - Do not score locally; mark independent scoring NOT RUN until the outside judge returns.

After the four tests:
- Write the exact rule that was added or refused for forming links from prose.
- Update the open-items README with before/after counts for each named test.
- Leave independent historical accuracy and native OOCC marked NOT RUN.
- Commit the frozen cases, results, and rule under the public pin.

Return the four result tables, the new rule text, the updated open-item list, and the new commit hash.
Copy and send. The names are Tacitus, Douglass, Babbage, and Komnene-Outside.

Next tests (focused on the remaining gap)
The current pin still fails the authentic relational set (0/6 complete) even though discovery finds the anchors. The two new proof paths only succeed when the documents already explicitly name and link the records. The open work is therefore the step that turns ordinary prose into those links without inventing them.
Immediate next tests
1.  Link-establishment from prose (the actual missing rule)
	•  Freeze a small authentic subset where the relation is stated in plain language but not as an explicit “see also / request–dispatch–receipt” chain.
	•  Score two things separately: (a) did discovery still find the anchors, (b) did Strict Ask produce a supported bridge or correctly withhold.
	•  Keep the same negative controls. Goal: isolate whether the failure is “cannot form the bridge” vs “formed an unsupported bridge.”
2.  Partial-correction families on authentic text
	•  Re-run the Ida B. Wells style cases but using the real Federal Register / archive wording instead of the synthetic “explicit source reference” versions.
	•  Measure how many of the original 12 Pole misses move from complete miss → partial or complete once the link rule is applied.
	•  Record whether the sorter still exhausts slots when multiple supporting records exist.
3.  Multi-document proof under resource caps
	•  Re-test the Zora Neale Hurston / Ada Lovelace style cases with the new sorter behavior, but force the eight-slot and phrase-group limits to trigger.
	•  Confirm that retaining both records does not later produce a false-supported bridge when one of them is ineligible.
4.  Outside-custodian packet for the Anna Komnene set
	•  The 22 anonymous paired cases are already prepared. Ship them with concealed keys and score only after the outside judge returns. This is the cleanest way to check whether the link rule generalizes beyond the local custody rehearsal.

## Implemented scope

- Freeze and replay Tacitus, Douglass, and Babbage against 5ffdca2 using separate development scoring custody.
- Resolve bounded publication corrections from eligible original headings, references, and scoped values.
- Package Komnene-Outside with anonymous arms, exact originals, and a separately verified crosswalk.

## Validation recorded

- Tacitus recovered 3/6 authentic bridges with all 5 negative controls withheld and 4/6 discovery anchor coverage.
- Douglass recovered 6/12 authenticated question variants from miss to complete. Original synthetic focus and related controls were unchanged.
- Babbage retained two distinct occurrences in eight slots and withheld under both eligibility controls and both proof budgets.
- Verified 22 paired questions, 44 anonymous arms, and one matching concealed crosswalk outside the reviewer archive.
- The extracted archive matched all retained candidate test decisions, passed 52 public evidence controls, Pyodide and Chromium, and ran 1,720 Python tests with 2 skips.

## Limitations and blocked checks

- Three authentic relations and all 12 original synthetic focus misses remain unresolved.
- The worker received no custody path and did not run with process isolation.
- The outside packet is ready for delivery. Independent scoring, historical accuracy, and native OOCC remain NOT RUN.

## Next steps

- Build fresh frozen controls for the DHS applicability and partial-correction cases and the B-Tests attribution scope.
- Diagnose the separate sorter phrase limits and incomplete literal lookup at larger corpus scales.
- Collect outside judgments using the anonymous packet and separately held mapping.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
