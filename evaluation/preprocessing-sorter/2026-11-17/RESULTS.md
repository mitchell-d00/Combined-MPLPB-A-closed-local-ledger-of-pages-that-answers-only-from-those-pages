# Offline sorter contract checks — 2026-11-17

Frozen implementation: `d528b65d6b00f4777f6224591eaed81b4ee25ad1`.
Parent baseline: `3df2c6e22f0ef454f3ee67b88d43402a42f63443`.
Sorter source SHA-256: `7624c4c690e2975f0e9ec49d1347e0a4b578b722f1580b704cece286227c4e4e`.
The evaluation harness was added in the evidence follow-up; its literal source
hash is recorded in `report.json`. No sorter or reader runtime bytes changed after
this freeze. The evidence commit and extracted-source checks identify the final
packaging separately.

## Required checks

Both modes consume the same eight fictional UTF-8 fixtures. Both emit exactly
176 identical nodes, source hashes, spans and provisional statuses. There are264
raw containment/co-occurrence edges. Compare retains that exact edge prefix and
appends77 review edges, including cluster hyperedge annotations and correction
windows. No cluster nodes are added. The graph envelope records mode and digest
separately. See `not-compared.json`, `compare.json` and `report.json:mode_audit`.

The native export is an intact, retired, machine-origin, unratified sealed page,
created through existing ledger write/withdraw functions. The current unmodified
provenance gate returns zero eligible sources for all three profiles:

| Profile | Native exclusion |
|---|---|
| lab | retired |
| internal | retired |
| external | external delivery denied by sealed page policy |

External delivery policy precedes retirement in the existing gate. No gate order,
finite grammar or eligibility rule was changed. The direct gate inspection avoids
mistaking an unsupported question grammar for retirement enforcement. All three
CLI asks also exit3 with `answer_supported=false` and empty
`answer_contract.claims`. Exact command arguments and outputs are retained in
`report.json` and `reader-*.log`. The native fixture additionally tests all profiles
with `as_of=None` and `as_of=1841-06-01` and verifies an interrupted retirement
cannot publish a current snapshot.

## Reproduction

Use a new output path for every run:

```bash
python -m tools.evaluate_sorter --output /tmp/sorter-reproduction-new
python -m unittest tests.test_sorter -q
python -m tools.reproduce_boundaries --revision d528b65d6b00f4777f6224591eaed81b4ee25ad1 --output /tmp/sorter-archive-new --suite full
```

The first command regenerates both graphs, asserts exact node/source equality and
raw-edge prefix equality, replays source fidelity, exports a retired native ledger,
checks each native gate, and invokes the unchanged CLI under all profiles. Its
outputs include failed return codes before raising. Graph verification intentionally
fails after implementation or source drift; rerun from the pinned checkout.

Specific fixtures:

```bash
python -m unittest tests.test_sorter.SorterTests.test_both_modes_keep_identical_sources_keys_and_distinct_occurrences tests.test_sorter.SorterTests.test_sealed_snapshot_is_retired_and_reader_refuses_every_profile -v
```

## Scope and costs

Before changes the sorter did not exist; the focused native/source baseline passed
43 tests in0.839s. The final focused set passed67 tests in1.308s, including24 sorter
tests. This is a software capability addition, not a historical answer-completion
gain. The existing22-question corpus, originals, questions and past measurements
were not modified or rescored for this preprocessing contract.

The retained single-run development measurements are in `report.json`. On this
shared Linux x86_64 environment (Python3.12.14, five visible CPUs), not-compared
used0.166s wall/0.166s child CPU; compare used0.137s wall/0.136s child CPU.
Source bytes read were2804 per mode (1402 original bytes, read twice). Recorded
child maximum RSS was19,111,936 and19,537,920 bytes respectively. These are
process-lifetime maximum child RSS readings, not incremental or process-tree memory;
measurements include Python startup and cannot establish a speed advantage.
Hardware model and host allocation are not pinned. Other measurements are retained
at their actual scope in the archive report and logs.

## Boundaries and failed attempts

All candidate support and historical-truth flags remain false. Similar headers,
repeated phrases and matching identifiers never merge events. Missing/ambiguous
intermediates stop documentary links. Partial corrections retain the prior wording
and scope; no ledger state changes during sort/compare/peruse. Exact quotations
and source replay establish textual fidelity only. Lexical action, qualification
and date recognition are incomplete and require inspection. Limits may yield partial
output. No hard OS time limit or hostile-filesystem isolation is claimed.

A stronger gate assertion initially expected `retired` for external, overlooking
its existing external=no precedence; the assertion was corrected, not the gate.
An early ad-hoc CLI audit looked for `claims` at the top level; the existing CLI
uses `answer_contract.claims`. The retained runner uses that established shape and
a supported field-question syntax. An initial browser launch lacked Playwright's
bundled executable (`browser-first-attempt.log`); the rerun used installed system
Chromium via a temporary executable-path symlink, with both published-live and
candidate-preview passes. No user browser profile or stored collections were used.

Independent review: **NOT RUN**. Historical relationship precision/recall, supported
historical answer gains and human review time remain unknown/null. These fixtures
are authored software controls. The sorter does not complete historical
reconstruction or verify historical truth.

## Frozen archive regression outcome

The tracked ZIP at the frozen implementation revision has SHA-256
`05de06fba66c95a0db30fcf94400c71970083036e0d71d1871b03dde146179ab`.
Its extracted contents passed:

* Full Python suite:1181 tests,342.822s reported test time;344.196s wall and
  328.048s child CPU measured by the reproduction runner.
* Public evidence with required capabilities:52/52; zero false supported bridges
  on these authored controls.20.625s wall,20.015s child CPU.
* Focused source/supersession boundary suite:51 tests passed.
* JavaScript API, serialized browser transport and fixture crawler checks.
* Actual pinned Pyodide314.0.7 WebAssembly engine checks.
* Actual Chromium published-live and frozen candidate-preview checks.

Archive reproduction peak child RSS was300,969,984 bytes (process-lifetime
maximum, not whole process-tree memory). See `archive-report.json` and exact
command logs. Documentation/handoff tests passed10/10; the two specifically
requested fixtures passed2/2. Infrastructure synchronization and classified
documentation audits passed. Prior historical-expert and unprepared-original
evaluation trees are byte-unchanged from the parent revision. No deployed update
or merge is claimed for this sorter branch.
