# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `8f4e4bf7345ddb52fe9aa5d7c499682645b2e1b1` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `179c9642ae81ad8068123fedb9be5c30a15a11456fabb97978c79301ab56addc`.

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

### Validation recorded

- Development baseline at specified PR #101 pin: 24/48 expected decisions; 24 positive misses; all 24 withholds retained; zero false support.
- Transfer baseline executed by worker and sealed without implementer inspection; exact inputs, key and output stay separately held until candidate freeze.
- All 17 preservation cases replayed against baseline; 28 inherited targeted controls passed.

### Limitations and blocked checks

- No runtime repair implemented yet. Candidate and transfer acceptance, archive checks and publication are pending.
- Same operator prepared the generator, saw all templates and will score both sets. Transfer instance bytes remain unopened. No independent preparation, blinding or adjudication is claimed.
- Independent historical accuracy, independent semantic adjudication, outside-custodian scoring and native OOCC remain NOT_RUN.

### Next steps

- Implement the smallest shared native source-attribution rule supported by frozen development failures, preserving budget and final-state checks.
- Freeze a committed candidate and source ZIP before opening transfer; run candidate transfer once and retain any failures.
- Publish exact pinned before/after evidence and current handoff for Al after archive validation.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
