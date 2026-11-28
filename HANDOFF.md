# Repository handoff

Last reviewed: 2026-11-28.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `d92fbdd646d51f8feb5268ea1962e886bea74091` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `37cd291c8ed0561a4154fe1033e47ce81bcd7642d554cfd757d7a24623a6802e`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty, start ARIADNE-01 — FRUS subject-line identification. Acknowledge Al note 0014 at dcdcfd93fc4a3017f44b0d976ae7de2aad9f6986. Recheck main against verified #135 at 241bee0f2301e69331db862f3cfd1ab49e59924a. Use a separate reader PR or reconcile an existing sprint branch. You can begin the baseline readback and packet freeze while Al publishes note 0015. Acknowledge its exact commit when supplied. Use DIRECT-02 as consumed evidence. Under the original question and profile, verify the complete subject reference against exactly one eligible original memorandum, binding named writer, date, addressee, and topic to exact witnesses. Leave submission, receipt, agreement, and execution unresolved. Keep ranking unchanged. Freeze the baseline, grammar, source pins, independently worded development and separate held fresh cases, citation spans, scorer, budgets, and expected stopping stages before edits.

### Implemented scope

- ARIADNE-01 native document identification. The reference and unique eligible original must agree on full writer, explicit date, President addressee and exact topic. Rankers, other FRUS paths and controller code are unchanged. Applied Al notes 0014 dcdcfd93 and 0015 265f1f7e.

### Validation recorded

- Baseline all 21 stopped at interpretation. Initial candidate passed original 21 arms and falsely completed supplemental X02, retained with source and raw outcome. Following-prose boundary correction passed 21/21 original and 3/3 supplemental, with zero unsupported completions and zero reader execution failures. 12/12 #135 packet and 154 focused checks passed. 77-case comparison changed DIRECT-02 only. Held fresh is sealed and NOT_RUN at this checkpoint.

### Limitations and blocked checks

- Exact identified document only. Submission, receipt, agreement and execution remain unresolved. Fresh authorship and scoring are same-operator. Public evidence and local private custody are measured separately. Independent historical and human assessments remain NOT_RUN.

### Next steps

- Make an archive of the pinned native candidate, run development from the extraction, run first fresh exactly once, and preserve all raw outcomes and hashes. Then verify remote and exact-head checks before a qualifying merge and verify Pages.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
