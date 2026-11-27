# Bounded workflow controller v1

Last reviewed: 2026-11-27.

Released starting revision `a7d572067dbf68077ea306584b067e457bd7a3a4`.
This lab covers workflow authority. Merge, deploy, and test dispatch are
shadow decisions. The only executor is a disposable local Git canary.

## Input and output schema

The untrusted proposal is exactly `{action, revision}`, with one of the four
actions below and a full lowercase Git SHA-1. No model field supplies host
state. The host provides this JSON data independently:

| Field | Format |
|---|---|
| `revision` | Full SHA of current target |
| `session` | `{id, role, capabilities}` with an opaque ID, role string and array of action labels |
| `grants` | Array of `{id, issuer, session, action, revision, status}`. Status is active or revoked. The trusted maintainer issuer is `maintainer`. |
| `reports` | Array of `{id, kind, revision}`. An `applied` report can establish current state when its revision matches. `advice` is informational. |
| `receipts` | Array of `{id, action, revision, kind, availability, execution, semantic}`. Availability is available/unavailable, execution is completed/failed/not_run, semantic is passed/failed/not_run. |
| `custody` | `public`, `restricted`, or `unavailable` |
| `release` | `prepared`, `tested`, `merged`, or `deployed` |
| `used` | Array of host-owned `action:revision` keys already reserved for an effect |

IDs and role labels use printable ASCII token syntax: first character alphanumeric,
then up to 127 alphanumerics, dots, underscores, or hyphens. Required host
collections are arrays. Individual IDs within each collection are unique.
Receipts and grants use known actions; capabilities may label a subset.
The controller treats malformed required host state as missing evidence.

Every verdict has `decision` (allow, withhold, or missing_evidence), `code`,
`selected` (report and grant IDs, or null), `receiptIds`, `missing` (the
first unmet prerequisite), and `scope` (exact action, revision and mode
on allow, or null). Effects have a separate execution result: completed,
not_run, or failed. A successful decision alone records no effect.

| Action | Release phase | Action- and revision-specific receipt kinds, in order | Mode |
|---|---|---|---|
| run-tests | prepared | input-freeze | shadow |
| merge | tested | candidate-tests, release-acceptance | shadow |
| deploy | merged | merge-event, deployment-package | shadow |
| record-canary | prepared | canary-ready | local-canary |

Evaluation order fixes diagnostic precedence:

1. Reject malformed/unknown proposals, absent or invalid host state, and wrong
   revisions (`invalid_proposal`, `state_unavailable`, `invalid_state`,
   `revision_mismatch`). Require host role Betty and an explicit capability
   for this action (`capability_denied`). Completion of any named role adds
   no capability. Reject used action/revision pairs (`duplicate_request`).
2. Require exactly one current applied report (`report_missing`,
   `report_conflict`). Stale and advisory records never count as current.
3. Select grants from trusted maintainer records for the exact session,
   action and revision. Multiple matching records conflict, including an
   active/revoked pair. Revocation withholds. Missing authorization, conflict,
   and revocation use `not_authorized`, `ambiguous_authorization`,
   `grant_revoked`.
4. Require the applicable phase and public custody. Phase conflict or
   restriction withholds (`release_phase_mismatch`, `custody_restricted`).
   Unavailable custody is missing evidence (`custody_unavailable`).
5. Select only receipts for the exact action and revision; request the first
   required kind in listed order. A single receipt must have available evidence,
   completed execution, and a passing semantic result. Missing, conflicting,
   unavailable, failed execution, unexecuted, failed semantics and no semantic
   judgment use `missing_check`, `ambiguous_check`, `receipt_unavailable`,
   `execution_failed`, `execution_not_run`, `semantic_failed`,
   `semantic_not_run`. Conflicting evidence never allows. An allow returns
   `allowed`.

The pinned B-Tests action evaluator supplies exact revision, grant cardinality,
and receipt selection/status checks. This adapter filters records by session,
issuer and action, projects statuses into the core, and reads back the selected
records for richer diagnostics. No upstream dependency is copied into the
repository. The runner verifies its SHA-256 before importing it.

## Canary and limits

The test host owns one in-memory state, serializes its mutations in one Node
event loop, and supplies a synchronous fixed Git writer. It checks the exact
proposal again after the between-check-and-write test hook and immediately
before reservation and dispatch. Reservation consumes the action/revision
even on failure. The writer compares the expected ref revision with
`git update-ref`'s old-value check. The proposed action cannot supply
repository path, ref, commit content or commands. Readback inspects the actual
ref and marker, separately from the verdict. Stale grants after a successful
linearization cannot roll back an effect.

Authentication, grant issuance, trustworthy action-specific receipt production,
and authority over the host process are simulated. Another process with Git
write permissions can bypass this prototype, including via direct ref writes,
hooks, shell commands and hosted GitHub routes. External revocation stores,
process crashes, durable deduplication, privilege isolation, aliases that
refer to the same resource, and all production dispatch are outside scope.

## Freeze protocol

Commit this policy, development, shadow, canary scenarios and held inputs
plus their expected verdicts before implementation. The separately named held
file adds state combinations and failure structures. Its author is also the
implementer and can access the file. The development runner will exclude it
until the candidate commit. Preserve the first result and report all case
counts. No independent or blinded evaluation is claimed.

Pinned B-Tests source SHA-256:
`5e71d0b7fc3f64294b726e8108a08d9ff0e79552a8975ee379aaa2546e988291`.
[Upstream JavaScript gate](https://github.com/mitchell-d00/B-Tests/tree/c8f5b90a3560a0c0a916955719cef76074abebf8/gate-js) ·
[WorkStore dispatch controls](../dispatch-enforcement/README.md) ·
[Governance experiment](../governance-gate/README.md)
