# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3fffe29dc4b43aabb4688072b5c3249f109139cc` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `efc3b2c319b3603ceb8a79685ca3616f044b62176c123d45050297db1683b388`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run a frozen attribution trial from PR #101 head 28b8feb871cd0c2eb29440f2ab46623e410622b6. Preserve all 17 PE-02 cases, the 28 targeted regressions, and earlier applicable evidence controls. Freeze 48 development and 24 separate transfer cases across signed letters, meeting minutes and quoted reports. Keep existing source-state and evidence budgets. Acceptance: all frozen target decisions pass; zero false-supported claims; every document form demonstrates positive coverage; valid earlier behavior remains intact. Publish development and transfer separately, retain failures, test the committed ZIP extraction and update the pinned Betty report.

# Attribution trial — maintainer clarification

Freeze the generator, seed, packet hashes, and scoring key before implementation. Keep transfer inputs unopened until the candidate is frozen. Describe this as **same-operator transfer testing**; independent preparation, blinding, and adjudication remain unmeasured.

Make transfer wording and sentence structure differ from development examples. Changing names and tasks alone tests limited transfer.

**A quotation with a different speaker is not automatically a withhold case.** If the question names the explicitly attributed speaker, a source-attributed answer may be supported. If it incorrectly assigns that instruction to the writer or reporter, withhold that attribution. Set each expectation from the requested actor and evidence, rather than forcing the planned positive/negative counts.

Run the frozen candidate on transfer once. Preserve failures. Any repair informed by those failures makes that packet development material; use a fresh packet for the next transfer evaluation.

Mitchell selected: Use a sealed, program-generated packet; label the custody limits.


### Implemented scope

- Freeze source-attribution development/transfer generator, seed, packets, separate keys, acceptance and native baseline before code changes.
- Preserve the reported PE-02 implementation and permanent seventeen-case corpus with all twenty-eight targeted regressions.
- Add one shared native source-writer/speaker/recipient/instruction representation for bounded letters, minutes and quoted reports. Preserve the old PE-02 path unchanged.

### Validation recorded

- Development baseline at specified PR #101 pin: 24/48 expected decisions; 24 positive misses; all 24 withholds retained; zero false support.
- Transfer baseline executed by worker and sealed without implementer inspection; exact inputs, key and output stay separately held until candidate freeze.
- All 17 preservation cases replayed against baseline; 28 inherited targeted controls passed.
- Final development candidate: 48/48 expected decisions, 24/24 positives and 24/24 withholds, zero false support and zero budget failures.
- All 17 PE-02 answer contracts and discovery arrays match baseline exactly, excluding code fingerprints only. All 56 focused controls pass, including the existing 28.
- Retained rejected first candidate (passive misses and conditional-governor false support) and second candidate (unframed competing-source false support), their source snapshots, outputs and failed control logs.
- Separate frozen-source projection audit verified 48 input bodies and all 56 development citations.

### Limitations and blocked checks

- Development repair is complete; committed candidate/source ZIP, extracted archive validation and once-only transfer acceptance remain pending.
- Same operator prepared the generator, saw all templates and will score both sets. Transfer instance bytes remain unopened. No independent preparation, blinding or adjudication is claimed.
- Independent historical accuracy, independent semantic adjudication, outside-custodian scoring and native OOCC remain NOT_RUN.

### Next steps

- Commit/freeze the complete candidate and source ZIP, validate its extracted content and keep transfer instances unopened until that freeze.
- Run the frozen candidate on transfer once; retain failures without repairing against the same packet.
- Publish separate development/transfer measures, exact source pin/checksum and current Betty report for Al.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
