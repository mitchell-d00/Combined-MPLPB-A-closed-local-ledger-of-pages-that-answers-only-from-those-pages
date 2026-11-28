# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `bcd689ba54d17a479328bf10a40c75acd12fa0e1` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `cff7171294faa8db4975ca0a83f81854206580982839ee90557231ceaddf9fed`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run the next FRUS relationship diagnostic set from merged PR #133 at 6942df4670196405797114cbe25317577c3118e1. Use all 11 relationship cases and a predeclared set of passing location and header controls. Trace interpretation and discovery separately. Run evidence-supplied readback separately and stop at the diagnosis. Verify recoverable public readback and report custody separately.

### Implemented scope

- Frozen 11 consumed relationships and three known passing location controls. Unchanged public reader and effect code.

### Validation recorded

- Freeze bcd689ba. Fourteen native and fourteen separate evidence-supplied traces with zero execution failures. All relationship questions stopped at interpretation. 25/25 anchors eligible/indexed, 16/25 BM25 and 19/25 documentary probe, zero native relationship citations or supplied link certificates. Three location controls preserved.

### Limitations and blocked checks

- Same-operator consumed evidence. Phase separation without new OS isolation. Prior 77-case grades kept. Held fresh, older comparison, independent review and human onboarding stay NOT_RUN. Prior private custody unchanged and off-workspace recovery unverified.

### Next steps

- Verify remote checkpoint readback. Recommend narrow DIRECT-01 response identification with matched missing-target refusal if a separate repair is authorized. Stop this study at diagnosis.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
