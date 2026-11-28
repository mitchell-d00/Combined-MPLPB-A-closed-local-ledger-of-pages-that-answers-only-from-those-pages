# Athena, Hermes and Hephaestus

Last reviewed: 2026-11-28.

[Al note 0004](../../handoff/al-notes/0004-heka-diagnostic-disposition.md)
proposed this follow-up. The [Heka disposition](../egyptian-gods/heka-01/DISPOSITION.md)
preserves the original lab grades and the two diagnostic discrepancies.
This sprint tests the same bridge and release runtime on a newly frozen
[contract](CONTRACT.md). The [freeze](freeze.json) and [candidate pin](candidate.json)
identify the apparatus, input and key digests, and unchanged bridge selection.

| Set | Development exact phases | First fresh exact phases | Writer attempts per draw | Intended updates per draw | Durable completions per draw |
|---|---:|---:|---:|---:|---:|
| Athena | 4/4 | 4/4 | 1 | 1 | 1 |
| Hermes | 5/5 | 5/5 | 0 | 0 | 0 |
| Hephaestus | 6/6 | 7/7 | 3 | 2 | 1 |
| Total | 15/15 | 16/16 | 4 | 3 | 2 |

The [development packet](D-inputs.json) contains 12 scenarios. The
[first fresh packet](F-inputs.json) contains 13. Phases count separate
restart invocations. Each draw includes one failed CAS and one observed
intended effect whose completion remains indeterminate. No blocked phase
reached a writer. The existing bridge passed development, so the candidate
was pinned without an adapter change before the first fresh run.

**Athena.** An unrelated eligible page kept the development withdrawal at
the named-selection stage. In fresh, withdrawal of the only eligible page
stopped at eligibility. An unrelated insertion left the report proof
complete and invalidated the whole-ledger binding. All three withheld.
The wrong-reporter and duplicate-writer controls also withheld.

**Hermes.** Integrated cases checked the exact binding and blocked missing,
advisory, revoked, or mismatched authority or scope. Wrong-action, conflicting
grant/receipt, and stale receipt cases called the unchanged controller
interface with a dry writer and are labeled separately. The integrated
binding readback attests the host namespace. An injected namespace mismatch
was outside this packet.

**Hephaestus.** In each draw the failed CAS left the competing ref and marker
intact. The post-Git interruption left a consumed, pending reservation and
no completion receipt. A fresh process refused the repeated request.
Known completed and failed reservations also blocked a second attempt.

## Evidence and reproduction

[Development score](evidence/development-score.json) ·
[First fresh score](evidence/fresh-score.json) ·
[Raw ledger, proof, Git bundles and store traces](evidence/first-runs.tar.gz) ·
[Raw member SHA-256 inventory](evidence/archive-inventory.json)

From the repo root, use Node 20+, Python 3 and Git. Get the pinned gate
module as described in the [controller replay guide](../comparative-tests/workflow-controller/restart/README.md).
Set `lab=evaluation/greek-gods`, `gate` to that module, and `output` to a
new output directory. Use `python "$lab/generate.py" D "$path"` or `F` to
regenerate the corresponding operator packet exactly. Run:

```sh
node "$lab/run.mjs" "$lab/D-inputs.json" "$gate" "$output"
python "$lab/score.py" "$lab/D-inputs.json" "$held_key" "$output" "$output-score.json"
```

Use the corresponding frozen input and held key for the fresh trace.
Subsequent runs reproduce exposed packets. Check the public package with
`sha256sum -c SHA256SUMS` from this directory. The runner received only the
operator packet. One operator prepared and scored both draws. Both keys and
the generator were read back from private workspace preservation. An
off-workspace private backup has not been verified.

No runtime, controller, reservation, Heka bridge, or production workflow
bytes changed. The prior Bastet, Heka, controller and restart evidence is kept
at its original scope. This lab uses simulated host identity and receipt
provenance. It makes no production activation, independent-evaluation, or
cross-resource atomicity claim.
