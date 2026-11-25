# Bubble and Wrap: reported content

Last reviewed: 2026-11-25.

Betty implementation step, on PR #103 from head
`5bef945e401f96a6422bb8c468932d330b705fc4`. The existing proposal remains
byte-frozen. This cycle adds execution isolation and contrasting development
controls before changing the shared source-scoped report operation.

The supplied [plan](inputs-received/bubble-wrap-plan.json) and
[PR inventory](inputs-received/mplpb-pr-history.json) remain unchanged design
inputs. They are not a historical-suite rerun. The inventory excludes #15 because
it was not a PR in that retrieved history.

## Frozen inputs and current execution stage

The original twenty inputs, ten primary targets, role obligations and 24-case
transfer seal remain under
[the proposal](../../current-failure-inventory/proposal/freeze.json).
The new [32-case matrix](wrap/matrix.json), [key](wrap/matrix-key.json) and
[seal](wrap/matrix-freeze.json) are separate. Denials and quotations are not
blanket withholds. Conditional source-inspection answers must retain the
condition and cannot establish that reporting or authorship actually occurred.

The [stable registry](registry.json) contains **256 executions**: 111 inventory,
32 Wrap, 96 consumed instruction attribution and seventeen PE-02 preservation
cases. The twenty original proposal cases are memberships within the 111, not
twenty extra independent samples. Each case records origin PR, failure mechanism,
protected rule, frozen packet hashes, budgets, baseline pin, reproduction command,
custody and the join key for later immutable run/score records. Semantic input
hashes expose overlaps independently of case IDs.

The [harness freeze](harness-freeze.json) binds worker, adapter, scorer, key,
generator, registry and guard tests before baseline/candidate comparison. At
this initial freeze the 24 transfer instances and key are unopened/unexecuted;
no candidate or transfer pass is claimed. Current results will append as
immutable records rather than overwrite this freeze.

## Bubble boundary

`tools/bubble_wrap_adapter.py` reuses `tools/study_sandbox.py` command/invoke.
Only the three approved native packages, frozen execution worker and the single
case input are staged. Keys, generator, scorer, Git metadata, credentials and
host network stay outside. Read-only code/inputs, cleared environment, isolated
namespaces, dropped capabilities and disposable bounded scratch remain enforced.
The same-operator host is not isolated from its own keys: isolation is not
independent preparation or adjudication.

Case limits remain 30 CPU seconds, 45 wall seconds, 2 GiB address space, 8 MiB
result and 256 MiB scratch. Reader budgets remain eight records, 200,000 scanned
characters, 1,000 units, twelve passages, 8,000 output characters and existing
phrase limits. No cap increase is a semantic gain.

The first restricted-environment gate failed before any reader case: Linux
could not write its UID map. A host-access invocation then passed all four
required sandbox tests. The fully logged repeated gate is
[BW-ENV-004](gates/BW-ENV-004/record.json), with [raw log](gates/BW-ENV-004/output.log).
Earlier denied/successful attempts and the pre-native reference-path preparation
failure remain in [initial observations](attempts/0001-initial-observations.json).
There is no direct reader fallback after a Bubblewrap failure.

Adapter parity initially checked 123 consumed cases, including all 96 instruction
cases and all seventeen PE-02 contracts/discovery arrays. A final twenty-case
proposal parity pass also completed. Every compared answer/pack matched; only
code fingerprints are ignored. Original Pole admission/projection/profile behavior
is unchanged. Documentary preservation retains its original admission semantics.

PE-02 permission-reprinted source inputs and raw outputs remain privately
retained. Only hashes and complete-contract/discovery comparison results publish
for those seventeen rows. They are not replaced with synthetic reconstructions.
All source inputs visible to the worker are approved case evidence; no scoring
key is mounted. Public reproducibility of those private originals remains limited
by the existing delivery restrictions.

## Wrap and accounting

The matrix is four reporting mechanisms × two question purposes × four contexts:
affirmative reporting, reported denial, denial of reporting, conditional
reporting; source attribution versus independent actual authorship; standalone,
different writer, unrelated balanced quotation with the innocuous noun “reports”,
and a distinct eligible conflicting appearance. Expected answers, conflicts and
withholds derive from the requested layer, polarity and condition. Complete
governors are frozen as witnesses. Every returned claim, including a partial or
conflict claim, is scored; correct totals cannot excuse unsupported propositions.

`BW-GUARD` adds sixteen frozen source-state, scoped-quotation, unresolved
competitor, record/scan/unit/output-budget and final-mutation tests. Its baseline
has thirteen passing guards, two failures and one missing-new-module error; those
remain failures in [the raw baseline log](baseline-native-guards/output.log).
`BW-ACCOUNT` protects duplicate IDs, planned/missing execution and unscored PASS
claims. These supplemental unit tests are separate from the 256 isolated packet
executions and are not counted as independent source cases.

Run receipts separate execution from semantics. Failed launches have
`BLOCKED_EXECUTION`, nonzero command status and `NOT_RUN` semantics; they are
never reader abstentions. Completed outputs initially remain `UNSCORED` in the
immutable execution receipt; a separate immutable score record supplies their
later outcome. Planned = completed + failed + not run; attempted = completed +
failed; completed = scored + unscored at the stated receipt stage.

`tools/publish_bubble_wrap_runs.py` appends hash-linked records. The audit rejects
duplicate IDs, missing/changed seals, broken index links, unledgered run records,
missing outputs and planned/unscored executions presented as passed. Private raw
receipts have explicit delivery restrictions and hashes, never fictitious public
links. See [Test Index](../../../docs/TEST_INDEX.md).

## Reproduction and transfer custody

```sh
MPLPB_REQUIRE_SANDBOX=1 python -m unittest tests.test_study_sandbox -v
python tools/bubble_wrap_trial.py run --implementation BASELINE_OR_EXTRACTED_CANDIDATE --source-commit READER_COMMIT --phase baseline --output NEW_PRIVATE_RUN_DIRECTORY
python tools/bubble_wrap_trial.py score --run NEW_PRIVATE_RUN_DIRECTORY --output NEW_SCORE_FILE
python tools/audit_bubble_wrap_delivery.py
```

Use the actual same frozen harness/key for baseline and candidate. Intended
recoveries may change only the ten declared primary abstentions; all unaffected
contracts, valid propositions, refusals, conflicts, qualifications, missing
obligations and citations remain preserved. Broad-summary FRESH-05 is an explicit
remaining non-target miss. Baseline/candidate raw records, scores and exact pins
will append; this initial-stage guide does not turn planned work into a pass.

Commit and ZIP-freeze a candidate before opening the existing transfer packet.
Run it once, retain failures, and consume it if failures inform a repair. The same
operator previously authored/saw its templates and inspected the existing
generator for schema reconciliation; reserved constructions remain excluded from
supplemental development. No transfer instance/key was opened for that work.
This cannot establish independent blinding or preparation.

Independent historical accuracy, independent semantic adjudication,
outside-custodian scoring, independent preparation, independent blinding and
native OOCC remain **NOT_RUN**. Current deployment remains the completed PR #102
release until a separately tested merge and observed deployment occur.

The initial isolated baseline completed and scored all 256 rows: **230 pass, 26
misses, zero false-supported claim cases**. All 26 failures are retained as
failures, not relabeled. [Baseline score](baseline-score.json),
[baseline execution](runs/baseline-001/run.json). The ten primary targets still
miss; sixteen Wrap source-scoped targets also miss. All preservation rows and
independent-authorship controls retain their expected decisions. Delivery audit
v2 fixes a score/execution record classification error; frozen v1 and that failed
audit attempt remain unchanged in the ledger.
