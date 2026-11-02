# Documentation and evidence coverage audit

Last reviewed: 2026-11-02.

Inspected baseline: `c0eb212b51c41a96e361ae0ceb680a0a5df0d55f`.
This is a repository/documentation audit, not a new source-language accuracy run.
See [current status](../../docs/CURRENT_STATUS_2026-11-02.md), the
[result/test index](../../docs/RESULTS_AND_TESTS.md), and the
[classification inventory](../../docs/documentation.json).

`inventory.json` records checked classifications and evaluation-family coverage.
`tests.txt` retains the focused documentation, generated-guide and handoff checks.
`reference-replay.json` separately records replay of the already-published 372
reference cases. `infrastructure.txt` records the synchronization check.
`preservation.json` compares all preexisting evaluation artifacts, frozen source
inputs, benchmark inputs and historical/vendor documents against the inspected
baseline; only explicitly current guide text is excluded from the byte comparison.

Run the check from the repository or extracted tracked-source ZIP:

```sh
python -m tools.audit_documentation --as-of 2026-11-02
python -m unittest tests.test_documentation_audit tests.test_handoff tests.test_self_knowledge -v
python -m tools.verify_reference_evidence
python tools/check_repository_infrastructure.py
```

A retained runner/test path does not prove every old result was reproduced today.
Historical exact reproduction still requires the report's original revision and
configuration. Old wiki observations with missing pins remain unscorable, and
independent human semantic and usability validation remain outstanding. New CI
and deployment outcomes belong to their exact Actions runs; this directory does
not claim them before they execute.

## Initial CI correction

The first PR #30 browser build failed the existing resource byte check because a
review banner had been added to the byte-pinned `resources/README.md`. The file
was restored exactly from the inspected baseline and classified as preserved
vendor material. No resource hash or verification rule was relaxed. The failure
and correction are retained in `initial-ci-correction.json`; final CI must run
on the corrected head. The initial extracted-source checks above did not exercise
the resource verifier, so they did not detect this issue.
