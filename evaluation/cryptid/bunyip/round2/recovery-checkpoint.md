# Bunyip C3 recovery checkpoint

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
   commit. The PR branch and GitHub PR #106 head and test-merge history do.
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

Once original custody and isolated execution are available, run the 17 unchanged
private cases sequentially. Publish permitted comparisons only. Complete custody
and preservation before freezing the committed candidate and running either
held packet. Human onboarding, independent historical accuracy, independent
preparation and blinding, independent semantic adjudication, outside-custodian
scoring, and native OOCC remain NOT_RUN.
