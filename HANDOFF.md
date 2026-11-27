# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `f52ed384b831c2abb7656dfabc0d4b7632c38457` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `d3e17b370e23d3e3e57fbb1e73350bf3cef4fd1d6b8036c92e8087f2d44f772e`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Betty — prioritize a clean release path for the cumulative Thoth candidate before starting another language sprint.

PR #108’s packaging changes are already merged and deployed. Build the reader release from current clean main, preserving those improvements.

1. Keep the retired recovery closed.
The original 17 private checks remain incomplete and the original 100 held cases remain NOT_RUN. Preserve their records and unavailable status. Do not resume recovery polling or represent replacement tests as completion of those originals.

2. Prepare one clean cumulative candidate.
Carry the reviewed C3 → Wampus → Thoth implementation and permitted evidence onto a clean branch without the incident’s affected ancestry. Verify its reader bytes against the tested Thoth runtime. Preserve the original PR #106 checkpoints and results.

3. Define prospective release acceptance explicitly.
Document what the available preservation and replacement evidence establishes, what remains unverified, and the requirements for this release. Keep the original failed and incomplete gates unchanged in history. Do not silently waive them or claim they passed.
Include the 832 public contracts, BB, protected C3/Wampus outcomes, Thoth’s frozen results, applicable software checks and deployment verification. Existing coverage misses may remain documented backlog under the agreed criteria.

4. Address the publication incident separately.
Prepare the precise cleanup plan for affected branch/PR refs, objects, artifacts and caches. Distinguish current-tree containment, clean release ancestry and remaining historical exposure. Documentation alone is not removal. Present any destructive operation with its exact scope and verified preservation plan before execution.

5. Verify and complete the release where requirements permit.
Pin and hash the clean candidate, run the applicable exact-head checks, and rerun affected preservation if reader bytes change. Existing push, merge and deployment authorization remains in force; no repeat confirmation is needed for already-authorized work.

If requirements pass, merge and verify the deployed reader fingerprint and supported/refusal behavior. If blocked, push the recoverable checkpoint and identify the exact unmet requirement and next executable action.

Update CURRENT_STATUS, HANDOFF and the PR report with the actual date, released main, candidate pin, evidence limits, incident status and release decision. Keep independent and human evaluations marked NOT_RUN.

Finish with a clear released or held result, commit and PR links, completed checks, deployment status and remaining blockers.

### Implemented scope

- Integrate the tested cumulative C3, Wampus and Thoth reader and reviewed refusal copy on current clean main f52ed384. Keep the PR #108 packaging and original PR #106 checkpoints.
- Retain only the selected public evidence and record prospective release acceptance and the separate historical cleanup plan.

### Validation recorded

- All three staged native package trees match tested Thoth 6ec348b31. Its scoped ZIP reproduced SHA-256 4ccdf9b9099192395e41b57cbdf2c2ad61a7e79e5b566ba0bccbd306326a5fe5.
- 42 focused Python tests and the documentary-rendering and museum refusal-copy checks passed. One initial local command named a nonexistent test module; the corrected command completed.
- Retained same-runtime evidence covers 832 public contracts, BB 900 positives and citations/200 withholds, 19 protected contracts and all three C3 routing recoveries. Thoth scored 6 complete, 3 useful partial and 3 expected withholds on each frozen draw, zero unsupported claims.

### Limitations and blocked checks

- Original 17 private cases remain incomplete and 100 held cases NOT_RUN. Recovery is INTERRUPTED / UNRECOVERED. Independent and human evaluations remain NOT_RUN.
- The original Bunyip ref and PR #106 still reach the publication incident. The release omits both known blobs and the introducing ancestry. Private incident preservation and GitHub-side historical remediation are pending.

### Next steps

- Run exact-head archive-first and software gates on the frozen clean release candidate. The clean PR Betty report records exact head, ZIP hash and release decision. Merge after the exact-head gates pass and verify the live runtime, support, partial and refusal and compact ZIP. Keep incident cleanup separate.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
