# Repository handoff

Last reviewed: 2026-11-25.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `e787bded7d2c99ddcc5b91228a76575aa8b90e61` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `144c2753b59b743ef0666fe60ae2adfba6dd852f341a745048fa9c7dabc98407`.

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
- Execute the frozen committed candidate on the transfer packet exactly once, preserve reporting layers, publish the consumed inputs and distinguish same-operator testing from independent assessment.
- Add recipient-fronted nominal and possessive instruction argument-order forms to the same native role parser, after fresh packet freeze and before opening its instances. No new-structure development examples were run.

### Validation recorded

- Development baseline at specified PR #101 pin: 24/48 expected decisions; 24 positive misses; all 24 withholds retained; zero false support.
- Transfer baseline executed by worker and sealed without implementer inspection; exact inputs, key and output stay separately held until candidate freeze.
- All 17 preservation cases replayed against baseline; 28 inherited targeted controls passed.
- Final development candidate: 48/48 expected decisions, 24/24 positives and 24/24 withholds, zero false support and zero budget failures.
- All 17 PE-02 answer contracts and discovery arrays match baseline exactly, excluding code fingerprints only. All 56 focused controls pass, including the existing 28.
- Retained rejected first candidate (passive misses and conditional-governor false support) and second candidate (unframed competing-source false support), their source snapshots, outputs and failed control logs.
- Separate frozen-source projection audit verified 48 input bodies and all 56 development citations.
- Once-only transfer on committed ZIP d0f6c67e0684d952afc47c13b83963ca7976d2bb: 12/24 to 24/24 expected decisions, 12/12 positive targets and 12/12 withholds, zero false support and zero budget failures. Each form has four positive targets passing.
- Separate transfer source-byte audit verifies all 24 source bodies and 28 exact citations; no source repair followed transfer inspection.
- Source ZIP SHA-256 0f3148b4a3ef061388a990ef0d0fc306838077ddde18f004285ac404faeee155 passed integrity and tracked-content comparison after restoring one executable bit from ZIP metadata. Extracted development 48/48, permanent 17 contracts/discovery identical, all 56 focused controls, all 52 public controls, all fifteen software checks including HTTP/JavaScript and report pins, WebAssembly and both Chromium contexts passed. Candidate embedded reader hashes match source. Installed wheel and 45 official MCP SDK checks passed.
- First candidate d0f6c67 ZIP completed all 1,779 native tests (two skipped), all 52 public controls, software/WebAssembly/browser/installation/SDK gates. Its first-transfer 24/24 decisions remain retained, but overlap with inspected development controls limits structural novelty.
- Fresh 24-case generator, new seed, packet/key hashes and rule frozen before any further native edits; baseline privately replayed at original PR #101 pin. Instance bytes/key/output remain unopened.
- Fresh candidate preserves original 48/48, consumed-first-packet 24/24, all 56 focused controls and all 17 complete PE-02 contracts/discovery arrays.

### Limitations and blocked checks

- New candidate source ZIP, once-only fresh structural transfer, exact-head archive-first full regression and deployment validation remain pending. The first candidate full 1779-test run is retained with its own source pin and is not a rerun of the new native bytes.
- Same operator authored and saw all generator templates, prepared packets and scored outputs. Exact transfer instances/key stayed unopened until the committed ZIP freeze. This is not independent preparation or blinding. The consumed transfer packet now becomes preservation material.
- Independent historical accuracy, independent semantic adjudication, independent preparation, blinding, outside-custodian scoring and native OOCC remain NOT_RUN.
- No historical answer-coverage gain: historical completion stays 1/4, historical partials stay 1/4, and all five source propositions across seventeen cases remain unchanged. The new gain is bounded synthetic source-attribution coverage.
- Protocol correction: supplemental development controls overlap the first transfer sentence structures. Retain its 24/24 result but classify it as consumed development material; it does not establish unfamiliar structural transfer.

### Next steps

- Freeze a fresh 24-case transfer generator, seed, keys and baseline before further native edits; use constructions absent from all inspected development controls and run a new frozen candidate once.
- Finish full native validation of the frozen ZIP and publish its retained result. Do not change the frozen native candidate after inspecting transfer.
- Push a new PR for this cycle (PR #101 is already merged), keep current head/checked archive and separate development/transfer results at the top. Complete required exact-head archive-first/regression gates before merging within the maintainer’s standing authorization.
- Verify deployed reader bytes after merge. Al reviews the general failure mechanism and transfer limits, then proposes one next falsifiable test. No new reasoning cycle is authorized by a proposal alone.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
