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

## Replacement verification plan

The 17 original private checks stay incomplete: one recorded startup failure
and 16 NOT_RUN. The 36 original routing and 64 original cross-family cases
remain unavailable and NOT_RUN. Missing data supplies no reader outcome.
The separate publication incident remains open.

| Track | Admissible inputs | What the result can establish |
|---|---|---|
| Exact public replay | Permitted public 832 reference bundle, original authorized inputs, frozen harness and pinned reader. Require original source bytes, questions, keys or complete expected contracts, and budgets to match retained pins. | Same-case preservation for the verified subset. Retained outputs alone support receipt verification. |
| Replacement preservation | Newly authored, explicitly synthetic examples covering signed instructions, reported speech, quotation and polarity, conditions, partials, citations, and competing or ineligible sources. Pair positives with nearby withholds. | A separate comparison between released reader `2622813` and the published C3 native source. The original 17 checks remain incomplete. |
| Replacement transfer | New routing and cross-family packets, with proposed sizes 36 and 64. Vary wording, layout and obligations. Include attribution, modality, references and multi-record evidence plus wrong-owner, missing-witness, withdrawn-source and fixed-budget controls. | Once-only transfer on new cases. The original 100-case packet and its NOT_RUN status remain intact. |

1. Inventory each authorized public case as byte-exact replayable, receipt-only
   or unavailable. Record source IDs and original byte hashes, question hash,
   expected contract or key hash, harness and budget pins. Refetched sources
   qualify only if permitted and byte-identical. Keep exposed incident
   material out of the replacement inputs.
2. Prove required isolation using synthetic controls. Freeze new case IDs,
   source bytes, witness spans, questions, budgets, rule, expectations,
   scorer and separate custody before the first reader run. Give the worker
   only the authorized operator packet. Record who prepared, saw and scored it.
3. Score statuses, claim meanings, qualifications, eligible exact citations and
   preservation of prior valid support. Keep coverage gains, consolidation,
   boundary correctness, and runner outcomes separate. Record execution
   failures without reader labels. Require zero false support and no lost
   valid support under the frozen checks.
4. Freeze the committed candidate ZIP and its SHA-256 before opening either
   new transfer packet. Run each once and retain every outcome. If a packet
   informs a repair, retain it as development material. Replacement results
   cannot satisfy the original missing checks or revise the release gate.

**Next achievable step:** inventory authorized public inputs against the retained
contracts, then freeze independently identified replacement preservation cases
and expectations before a reader run. Human onboarding, independent historical
accuracy, independent preparation and blinding, independent semantic
adjudication, outside-custodian scoring and native OOCC remain NOT_RUN.
