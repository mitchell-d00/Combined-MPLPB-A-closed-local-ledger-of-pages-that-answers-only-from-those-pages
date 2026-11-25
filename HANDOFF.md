# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `a26ec527e2e3a5bab7883e7892aa00c348ea65dc` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `576dc002f6867f82f7705151d9878df9ef85191dff3815c3075f0d17ecda1c28`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Run Betty. Test and repair report-pin selection, starting from PR #100’s head a26ec527e2e3a5bab7883e7892aa00c348ea65dc.

Freeze six synthetic PR-body fixtures and expected results before changing code. Let H be forty a characters and S forty b characters; actual head.sha is H.

1. Betty report with **Current PR head** and backticked H: match.
2. Historical report with **Public evidence pin** and backticked H: match.
3. Betty report pinned to S: stale, no match.
4. No report or pin: missing, no match.
5. H appears only inside a fenced Markdown example: no match.
6. Fenced example containing H precedes a real Betty report pinned to S: stale, no match.

Run all six through both --al and --betty: twelve executions per revision, mocked HTTP only, thirty-second limit per execution. Retain baseline outputs before implementing a general parsing fix.

Acceptance: all twelve expected decisions pass; zero false-current matches. Preserve newest-PR selection, explicit historical override, fork handoff links, and empty-list behavior. Rerun the existing JavaScript and HTTP checks. Record before/after counts, failures, tested commit, archive checksum, and updated handoff.

Keep independent historical accuracy, independent semantic adjudication, and native OOCC marked NOT_RUN.

Maintainer direction after relaying Al’s PR #97 review and PE-02 proposal: Retain as the next proposal.

Start PE-02 proposal after what you are doing keep it all in pr101 then we will do an al report

### Implemented scope

- Freeze six synthetic PR-body fixtures and expected decisions at PR #100 head a26ec527e2e3a5bab7883e7892aa00c348ea65dc; retain exact baseline outputs before repair.
- Ignore Markdown backtick/tilde fenced examples when selecting the first exact live current-head or historical evidence-pin label. Preserve discovery, explicit override, fork links and empty listings.
- Retain the relayed Al PR #97 proposal and the initial defer decision. The latest maintainer direction authorizes PE-02 after the report-pin repair, with both cycles in PR #101.

### Validation recorded

- Frozen mocked-HTTP replay: baseline 8/12 decisions, four failures and four false-current matches; repaired parser 12/12 decisions, zero failures and zero false-current matches. Each subprocess has a thirty-second limit.
- Existing JavaScript contract passed, including the frozen twelve-case replay, fourteen additional fence controls and inherited discovery/override/fork/empty-list checks.
- The first filtered-checkout HTTP run had two failures out of thirteen from omitted assets/history; after restoring those tracked assets, all thirteen HTTP tests passed. Both logs are retained.

### Limitations and blocked checks

- Independent historical accuracy, independent semantic adjudication and native OOCC remain NOT_RUN.
- Archive validation and full release checks are pending at this candidate preparation stage. No deployed-site verification is claimed.

### Next steps

- Freeze a committed candidate, archive and extract it, rerun the replay and HTTP/JavaScript checks, and record the actual tested commit, ZIP checksum and failures.
- After completing the report-pin archive, start the authorized PE-02 Smith-letter cycle in PR #101 from its separate pin and frozen limits; prepare Al’s report after both cycles.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
