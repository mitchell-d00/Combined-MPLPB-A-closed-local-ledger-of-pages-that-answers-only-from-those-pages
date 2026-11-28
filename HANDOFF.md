# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `15ed32bd585644d7a640406a20193e5397e9c529` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d28e22857ab0987e787465bde451827071f7b7a2a216b96cf30ef635f985f418`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Let’s give her a new note

### Implemented scope

- Al review step: publish note 0005 against merged main 15ed32bd and index the next bounded Hermes namespace experiment.
- Review the specific missing namespace contrast and distinguish the worker's internal binding from an absent public receipt-import API.
- Advice and map/coordination metadata only; no reader, bridge, controller, key, scorer, runtime or workflow changes.

### Validation recorded

- Read PR 122 and its Greek contract/results, Heka bridge worker, current handoff and Gremlin open work. The report records 15/15 development and 16/16 first fresh phases on the unchanged bridge.
- The results explicitly say an injected namespace mismatch was outside the packet; direct controller dry-writer probes are not integrated bridge evidence.
- No new experiment was run for this review.

### Limitations and blocked checks

- Hermes-02 is proposed. Host identity/provenance, malicious-host resistance, path alias equivalence, distributed recovery and cross-resource atomicity remain outside the measured boundary.
- Greek draws are now consumed preservation; existing Heka diagnostic grades remain unchanged. Same-operator preparation and workspace custody do not establish independent evaluation or an off-workspace backup.

### Next steps

- Betty acknowledges the published note revision and freezes the lab seam, matched development/fresh packets, expectations and scorer before execution.
- Use real reader proof and Git readback at both targets; record authority, binding, effects and reservation state separately.
- Push recoverable checkpoints and merge qualifying lab work after applicable checks under existing maintainer authorization; keep production dispatch inactive.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
