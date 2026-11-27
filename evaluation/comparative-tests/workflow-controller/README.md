# Bounded workflow controller study

Last reviewed: 2026-11-27.

[Released main](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/commit/a7d572067dbf68077ea306584b067e457bd7a3a4) is the base for this lab-only study.
[Policy and fixtures](POLICY.md) were frozen at
`5e30c9b8844d03257cab81de34ab15bb00b5f950`. Candidate
`5111ebba9f6bab653b93d1f61dd73965eeb43583` was committed before the held
run. The extracted test ZIP SHA-256 was
`0d9797fbbf0ce03339104f5ebf10f32e98f7c24c26995f9a0b43c323ec01b95e`.
Reader, browser, native runtime and existing workflow source bytes match
released main. This study measures workflow decisions.

## First results

| Suite | Matches | Correct admissions | False admissions | False denials | Protected withholds or missing evidence | Execution failures | Ref writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Retained shadow | 7/7 | 3 | 0 | 0 | 4 | 0 | 0 |
| Development | 15/15 | 3 | 0 | 0 | 12 | 0 | 0 |
| Disposable Git canary | 8/8 | 1 | 0 | 0 | 7 | 0 | 1 |
| Held combinations | 10/10 | 1 | 0 | 0 | 9 | 0 | 0 |

All 40 cases have a classified outcome. [Raw results and preflights](results/)
include the first completed canary and held runs. The first working-tree
shadow and development outputs matched the extracted-candidate results byte
for byte. The setup errors in the preflight record ran zero canary cases.
The pinned upstream action suite passed 14/14. Existing governance, specialist continuity and handoff tests passed 63/63. The documentation audit passed.

Shadow fixtures translate the cited histories into the declared host schema.
They do not reconstruct the full operational state. Six shadow rows have
exact proposal/state overlap with development. In S04 the original
withdrawal from the replay remains a hold, with unavailable custody
identified as the reason. In S06 the old-revision test receipt still blocks
deployment, with a current action-specific receipt identified as missing.
The original labels stay visible beside each verdict. None of the seven
shadow cases changed its admission decision.

The held file has zero exact proposal/state overlap with either earlier
packet. It exercises cross-action receipts, current/stale/advisory report
mixtures, revoked/active grant conflicts, and contradictory execution and
semantic states. The same implementer authored the frozen inputs and could
inspect them. Independent or blinded transfer remains unmeasured.

## Report for Al

The strongest demonstrated boundary is the no-write result when a previously
allowable canary grant is revoked between evaluation and the ref update.
The test inspects the actual ref and its marker independently, and the same
host executes exactly one later authorized update. Reusing that request is
withheld. The policy shares B-Tests grant and receipt selection and leaves the
existing WorkStore and production release paths untouched.

Identity and provenance are simulated host inputs. Revocation and reservation
are serialized in one trusted Node process and are memory-only. Git enforces
an old-value check on the disposable `refs/heads/canary` ref. Direct Git, shell, hooks, GitHub, and
other processes with write authority remain routes outside this controller.
Production authentication, durable replay protection, cross-process
revocation, and other operations remain unhandled by the prototype. It is
never selected by the public API or release workflows.

One bounded next test for Al is to insert a second local writer between
authorization and the ref update. Verify that the compare-and-swap rejects
the stale write and preserves the other writer’s marker. This study exercised
the in-process revocation boundary.

## Reproduce

Use Node 20 or newer, Git, and a clean checkout. This replay needs no network
after obtaining and checking the upstream module. Execute only in a
disposable local development environment.

```sh
lab=evaluation/comparative-tests/workflow-controller
staging="$(mktemp -d)"
curl -fsSL https://raw.githubusercontent.com/mitchell-d00/B-Tests/c8f5b90a3560a0c0a916955719cef76074abebf8/gate-js/index.mjs -o "$staging/gate.mjs"
git archive --format=zip -o "$staging/controller.zip" 5111ebba9f6bab653b93d1f61dd73965eeb43583 "$lab"
sha256sum "$staging/controller.zip"
unzip -q "$staging/controller.zip" -d "$staging/unpacked"
cd "$staging/unpacked/$lab"
sha256sum -c INPUTS.sha256
for suite in shadow development canary held; do
  node replay.mjs "$staging/gate.mjs" "$suite" "$staging/$suite.json"
done
```

The controller verifies the upstream module hash before importing it. Each
canary replay creates fresh Git revisions in a temporary repository. The
verdicts and marker transitions reproduce; the fresh Git IDs may differ.

## Competing-writer follow-up

Two matched [scenarios](competing-writer.json) were frozen at
`6ff09a241` before harness changes. The only intervening action in the
contrast is a subprocess Git write to the same canary ref from the existing
`beforeWrite` hook. Grants, receipts and target HEAD stay current.
The controller's expected-old-value ref update still uses the initial ref.

| Scenario | Admission | Execution | Ref after attempt and duplicate |
|---|---|---|---|
| CW01, unchanged ref | Allow | Completed | Intended commit and marker |
| CW02, intervening process | Allow | Failed CAS | Competing commit and distinct marker |

The intended update occurred exactly once overall. In CW02 Git rejected the
stale CAS and the readback matched the competing commit and marker. Both
duplicates returned `duplicate_request` and attempted no write. The failed
CAS is a matching execution outcome and remains visible as `failed`.
This controlled interleaving covers one ref and an in-memory reservation.
Durable deduplication, external authorization and enforcement over other
writers remain unestablished. Production dispatch stays inactive.

The [tested lab ZIP](results/follow-up/tested-lab.zip) is from
`32dd7469a1e3ac1d575b355f604d2b1ec8d92e7a`. SHA-256
`af684b0541491ed2352ac1b86b6b5c9f9759aed8ec9ece727fc53c6e77a3b511`.
The old 40 cases were replayed from the extraction and passed again. Original
outputs and overlap disclosures are retained above. The new
[raw per-scenario results](results/follow-up/competing-writer.json) include
all ref snapshots, the CAS exit code, and duplicate outcomes.

The first isolation attempt stopped during apt setup with an HTTP 403 from
Microsoft's Ubuntu repository. It executed zero isolation tests. The
unchanged retry passed all four mandatory isolation tests and executed all
75 frozen D% classes. The [evidence ZIP](results/follow-up/verification-evidence.zip)
retains both exact CI logs, the verified aggregate artifact, and local logs.
This was a setup failure, separate from the controller outcomes.
The source policy, production workflows and reader bytes were unchanged.

To replay the follow-up, unpack the tested lab ZIP, verify `INPUTS.sha256`
and `COMPETING_WRITER.sha256`, and run the documented command with suite
`competing-writer` and a fresh output path. Both fixture sets use fixed
parameters, with no random seed. The
[original fixture authoring script](reproduction/freeze-original-cases.py)
retains its original bytes. Run it from disposable staging if regeneration
is needed. The matched pair was authored directly in the frozen JSON.
