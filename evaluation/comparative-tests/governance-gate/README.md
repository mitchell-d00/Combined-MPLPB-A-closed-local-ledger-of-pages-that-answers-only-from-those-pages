# AI proposal to verified report

Last reviewed: 2026-11-23.

This local experiment wraps a governance prompt in a deterministic WorkStore gate. It takes one typed proposal, checks host approval for the exact source, field, and report target, asks the strict reader for the cited fact, and writes one local report. The host reads the artifact back before returning `verified`.

## Try it

```sh
python -m tools.governance_demo --output /tmp/mplpb-governance
python -m unittest tests.test_governance_demo -v
```

Choose a fresh directory. The first command creates its own fixture ledger, executes one approved proposal, and prints the official status, receipt ID, and artifact hash. Open `reports/museum-hours.json` under that directory to see the claim, citation, and receipt ID. The second command checks the public result, WorkStore audit events, calls, and files together.

## Example governance prompt

> Propose one local cited report. Return one JSON object with exactly five fields. Copy the host-provided operation, source ID, source hash, and field. Choose a lowercase report filename under the host-managed report directory and supply it as the target. If any required value is missing or unclear, ask for clarification. Send the proposal for host review. The program supplies the official execution status and receipt after dispatch.

The schema governs the proposal. Only the trusted host can record approval. The approval digest binds the operation version, arguments, and task and evidence revisions. WorkStore checks its allowlist, authority, revision pins, and source eligibility before dispatch. The adapter rereads the pinned source and gets claims from the strict reader. The official status uses WorkStore's receipt and the report readback. Extra proposal fields, including a claimed status or receipt, fail schema validation.

| Tested condition | Expected official outcome | Expected local effect |
|---|---|---|
| Approved proposal that still matches | Verified, with matching receipt and citation | One report |
| Missing approval, invented tool, or claimed receipt | Denied, with zero dispatches and no receipt | No report |
| Target or source pin changed after approval | Denied, with zero dispatches and no receipt | No report |
| Source retired after approval | Denied, with zero dispatches and no receipt | No report |
| Duplicate submission | First verified, second denied | One report total |
| Adapter interrupted after writing | Indeterminate, with no automatic retry | One report may already exist |
| WorkStore reports a pass but the file is gone | Indeterminate | No file available at readback |

The archived candidate produced the cited opening time and passed all **10/10** controls. All six denied inputs produced zero calls, zero execution receipts, and zero report files. [Observed result, report and archive pin](result.json)

## Limits

The experiment scripts model-shaped inputs and uses a trusted Python host with a private output directory, WorkStore credential, adapter, and in-memory approval state. Restarting the demo requires a new run and fresh approval. The demo covers one local operation and a single explicit source field. It measures promotion into official status and citations. Free-form model accuracy, external effects, isolation from other programs on the host, and complete mediation are outside this experiment. A citation establishes the ledger statement. Historical truth requires independent evidence. [WorkStore dispatch controls](../dispatch-enforcement/README.md)
