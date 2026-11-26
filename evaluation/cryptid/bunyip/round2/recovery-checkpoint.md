# Bunyip C3 recovery closure

**Recovery attempt: INTERRUPTED / UNRECOVERED.** The retired session is no longer a dependency. Further recovery polling is closed.

2026-11-26. Checked PR #106 head `cc54c4276bb4895c33df46cc782e758f4c8e5a0b`
and released main `515a919df40996e9d1d521dd50474b832a1a599c`. PR #107's
deployment receipt covers the released reader. C3 is still a candidate.

| Measurement | Status |
|---|---|
| Exposed development | Retained 489/572 → 572/572 decisions and 57/128 → 128/128 positives. |
| Coverage | Retained 71 positive recoveries across 34 original question strings. The wording-only diagnostic is 40 executions across 19 strings. No new recovery measured here. |
| Consolidation | No new change or measurement in this checkpoint. |
| Boundary correctness | Retained 832/832 exact public contracts and the original 22 strict-key failures. No private decision accepted. |
| Private preservation | Original Bunyip custody mount and receipt were not found in this attached workspace. One previous attempt failed before reader execution. Sixteen cases remain NOT_RUN. File loss is unverified. |
| Isolated runner | A synthetic no-input Bubblewrap canary failed before worker startup with a NETLINK_ROUTE permission error. A second host-side invocation of the same isolated canary failed setting up the UID map on a read-only filesystem. PID 1 and the supervisor were untouched. |
| Held transfer | 36 routing and 64 cross-family cases remain unopened. No designated transfer ZIP freeze. |

Both existing public replacement archives matched their receipt SHA-256 digests,
byte lengths and file-member counts (867 reference and 1,363 interrupted-run
members). These checks did not read the restricted outputs or verify private
originals. The cancelled source-ZIP run 45870407049 lists zero artifacts.
The original incident report and prior failures remain unchanged.

## Interruption and data loss

- **PR #105** is the last released reader and preserves its earlier storage and
  CI failures separately from reader decisions.
- **PR #106** retains C3's published source and public evidence. The interrupted
  first remote preservation run (45870399223) recorded 321 matching completions
  and 528 execution failures. Its raw artifact upload failed with EACCES, so
  those first-attempt raw outputs are unavailable from Actions. The full job
  log is retained. The later 832 public matches are a separate replay.
- **PR #107** is the completed documentation release. Its verified deployment
  keeps #105's reader. The original #106 workspace was unavailable at handoff.
  This interruption left the private files and custody receipt unavailable
  to this session. Their deletion or permanent loss is unverified. This is a workflow and data-availability failure. Context compaction may have contributed; its involvement is unconfirmed.

No missing raw output is reconstructed. No original private result or held
packet is treated as executed based on a summary.

## Proposed history and artifact cleanup

No destructive step below has been executed. A private source-span inventory
and verified backup are prerequisites. Keep the old workspace and preserve the
incident archives, run records and hash metadata in designated private custody.
Inventory the affected result and log members against their privacy descriptors
and original source spans. Keep the source text and inventory private.

1. The two version-1 archive paths listed in
   [the containment receipt](custody-containment-v2.json) are present at
   `9b4bdf9` and inherited by `1c34dc80`. The paths are absent at the
   current PR head after `bfd41a5`. Main does not descend from the introducing
   commit. Of 122 advertised repository heads/tags and PR #106 refs fetched
   for ancestry inspection, only `refs/heads/local/bunyip-round2`,
   `refs/pull/106/head` and `refs/pull/106/merge` descend from it. This
   identifies known introducing ancestry; it does not clear other copies.
2. Prepare and verify a replacement branch tip based on clean main, carrying
   the reviewed current C3 tree and only permitted evidence. Before replacing
   `refs/heads/local/bunyip-round2`, scan all advertised heads/tags and
   affected PR refs for the two blobs and their introducing ancestry. Verify
   the replacement native tree, handoff and public evidence, and record exactly
   which source pin and status checks must be reissued. Use an exact expected-tip
   lease for the planned replacement after it has been presented and approved.
   Main requires no rewrite for the two known archive objects.
3. Recheck Actions artifact and log scope for the two affected source-tree
   revisions and their PR test-merge runs. Metadata returned 10 artifacts on
   the introducing-head runs and none on the intermediate-head runs. This is
   a metadata inventory, not payload clearance. Compare the producing steps and,
   where necessary, inspect the artifacts privately. Preserve private evidence
   before proposing deletion of any confirmed affected artifact, log or run.
   The cancelled full-source ZIP run had no listed artifact to remove.
4. Coordinate GitHub-side cleanup for affected PR refs, cached commit views
   and unreferenced Git objects. Recheck reachability after cleanup. Report
   separately any forks, clones or caches outside repository control.

## Public replay inventory and executed checks

| Original arm | Availability | Executed at this checkpoint |
|---|---|---|
| C3 public consumed preservation | **832 exactly replayable** across 35 cohorts. All 832 authorized packet file maps match the frozen registries and execution receipts. | **832/832** unchanged normalized contracts, zero failures, on the original hosted isolated runner and C3 pin `3bf9657`. |
| Bunyip BB consumed external regression | **1,100 exactly replayable** against the same 100 retained fixture-file hashes. | **900/900** exact positive contracts, **900/900** citation readbacks, and **200/200** unchanged negative withholds. |
| C3 exposed D% development | **572 receipts/outputs only** for the original score. Published inputs and seal hashes exist. The original custody key/dice bytes are absent. | Published packet/member hashes checked. Original scores, including the 22 strict-key failures, are retained. No new scored reader run for these cases. |
| Original private preservation | **17 unavailable**, with one historical startup failure and 16 NOT_RUN. | No private reader execution. |
| Original held transfer | **100 unavailable**, 36 routing plus 64 cross-family. | NOT_RUN. |

[Case inventory](public-replay-inventory.csv) carries original case IDs or BB CSV
composite keys, cohort scope, input fingerprints and available output digests.
Original held cases without a verified complete ID roster are recorded as cohort
rows. Routing's published seal and ID pattern remain in
[routing-freeze.json](routing-freeze.json). Counts are memberships within each arm.

[Pin map](public-replay-inventory-pins.json) records registry and harness digests,
worker profiles, baseline and C3 commit. Each preservation case's registry and
packet retain its budget and input state. The frozen scorer compares the full
answer contract except its existing `code_sha256` exclusion. Retained output
hashes and normalized contracts were checked against the original comparison
archive and the new run. The hosted job passed all four isolation checks before
replaying public packets. Private rows stayed blocked by the original route.
[Rerun receipt](public-replay-rerun-receipt.json) ·
[Hosted run](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/45871569757/attempts/2).

The BB replay used the exported fixture bytes whose 100 hashes match the
matched-source receipt, the unchanged public package and evaluator, and the
recorded profile on each negative. Its initial host-side fixture check stopped
before execution when it included the older unmatched export. That first
comparison remains an original recorded failure. The verified matched inputs
were then used for the replay. A CLI artifact redirect failed with HTTP 403;
the GitHub connector retrieved the same public rerun ZIP and its SHA-256 matched.

The publication incident remains open. Neither known restricted archive blob
is in the current tree. The introducing commit still survives on the PR branch
and GitHub PR refs. This checkpoint does not copy any restricted payload or
execute the proposed destructive cleanup above.

## Replacement verification plan

The original 17 and 100 cases keep their missing statuses. Use distinct
replacement IDs and fresh authorized synthetic fixture bytes. Where materially
relevant, use the same source roles and failure conditions with different
wording; preserve all declared proof and custody boundaries.

| Proposed IDs | Freeze these contrasts before execution | Frozen acceptance |
|---|---|---|
| `C3-REPL-P01+/-` | Signed letter contains a complete instruction; a matched version omits the full-name witness. | Exact instructor, recipient and instruction span on the positive; withhold full attribution on the contrast. Do not admit execution. |
| `C3-REPL-P02+/-` | A named reporter quotes another person's statement; the matched request assigns it to the recorder. | Attribute the claim to the quoted speaker at the reporting layer; withhold the wrong actor. |
| `C3-REPL-P03+/-` | A conditional instruction with its full governor; a matched question asks whether the action happened. | Cite the complete governor and preserve modality. Withhold the completed-event claim. |
| `C3-REPL-P04+/-` | A two-obligation question has one eligible witness; a matched packet withdraws that witness. | Checked partial identifies the unmet obligation; withdrawn source supplies no claim or citation. |
| `C3-REPL-P05+/-` | Same public field in a unique eligible record; a matched packet adds a competing owner. | Exact field/value and source revision on the positive; ambiguity stops a complete answer on the contrast. |
| `C3-REPL-R` and `C3-REPL-X` | Scope later new routing and cross-family contrasts to observed gaps from the replacement preservation run. Vary title/body competition, temporal roles, attribution, conditions and multi-record obligations. | Keep routing and cross-family results separate. Run each frozen packet once, score its original questions, and preserve all negatives and exact citations. |

Before any replacement runs, commit and hash the case IDs, exact questions,
synthetic initial sources, path/hash/span identities, states, eligibility
profiles, expected claims and withholds, runner, scorer and unchanged budgets.
Use the existing operator/custodian split and record actual preparation and
exposure. Require the existing isolation preflight to pass and retain all
initialization failures separately from reader decisions. For previously valid
answers require the full supported contract or its predeclared equivalent.
Require zero false support and zero lost valid support on protected cases.
Check attribution, polarity, modality and missing obligations independently of
coverage. Pin and hash the candidate ZIP before any new transfer is opened.
Any transfer that informs a repair becomes development material.

**Next executable step:** author and freeze the five matched synthetic
preservation pairs above, then use the existing isolated runner to compare
released `2622813` and C3 `3bf9657`. New results will be replacement evidence
and cannot satisfy the missing original gate. No independent blinding is
claimed. Human onboarding, independent historical accuracy, independent
semantic adjudication, outside-custodian scoring and native OOCC remain NOT_RUN.
