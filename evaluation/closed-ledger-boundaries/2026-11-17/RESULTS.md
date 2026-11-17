# Closed-ledger boundary engineering record

Date: 2026-11-17. Author-run software evidence; independent review NOT RUN.

Baseline: `473048dfa23d07439fef5f636e287b23b50b1e27`.
Tested implementation: `6a4230399b83ed259bc1aec1bc9c0d02fedc0f75`.
Later report/handoff changes do not change the tested runtime, tests or reproduction runner.

This update tightens inspection and operational boundaries. It does not increase
historical answer coverage or detect a coherent false original. The earlier
retained original-record result remains 1 complete source-scoped comparison and
2 checked partial answers across22 questions; those historical runs were not
repeated for this interface/observation update. Independent historical precision,
recall, truth and human effort remain unmeasured.

## Before and after

The baseline's63 focused tests passed in4.050s. Its runtime/tests/tools are
byte-equivalent to previously archive-tested63cea982 (1124 tests); that old full
suite result is retained evidence, not a new baseline full run in this update.
Fresh public control runs use unchanged published52 cases and identical budgets.

Six retained identical-input examples in `before.json` and `after.json` have
identical source-byte hashes, claims, citations, kinds, support booleans and
verification states. They are fictional developer fixtures, not historical cases:

| Case | Source support before/after | New category |
| --- | --- | --- |
| Coherent single original | true/true | source_support_established |
| Opposed source fields | false/false | known_source_conflict |
| Conflict exceeds display budget | false/false | known_source_conflict |
| Existing record lacks requested field | false/false | insufficient_evidence |
| No eligible record | false/false | absent_eligible_source |
| Nonconflicting evidence exceeds budget | false/false | index_exhaustion |

All results now require outside-world confirmation. The single original reports
one declared root; multiple declared roots do not waive confirmation or establish
independence. Source-state changes clear old quotes and root counts. Restricted
pages do not count as corroboration. Existing codes and proof rules remain intact.

## Operational receipts

The existing host-only receipt hook now checks predecessor ordering for STORE,
DISPATCH, DELIVERY, READ, ACK and COMPLETION. Every linked transition carries its
own artifact digest and matching execution pin. Missing stages, foreign execution
predecessors and legacy standalone acknowledgments cannot bridge a checked chain.
Existing standalone READ/ACK observations remain compatible but explicitly unchained.

These observations are host declarations. The checked chain is not independently
authenticated operational reality. Answer support and external-world truth remain
false; this stream does not satisfy task acceptance or supply claim support.
Independent receipt adapters/authentication remain an integration gap.

## Commands and resource scope

Run the source archive experiment with a NEW output directory:

```sh
python -m tools.reproduce_boundaries --revision 6a4230399b83ed259bc1aec1bc9c0d02fedc0f75 --output /tmp/mplpb-reproduce-new
```

The runner retains command outcomes, failures/timeouts, exact archive SHA and
revision in `reproduction.json`. It tests extracted source, not a moving checkout.
Interface commands and pinned runtime hashes are in `interfaces.json`;
`browser_check.py` is retained and runs with extracted source as its working directory.
Use the repository's pinned browser-runtime setup before running it.

`metrics.json` distinguishes process costs from public per-fixture measurements.
Logical source-text reads include repeated calls; they are not physical disk I/O.
Fixture output source coverage is not retrieval recall or historical relevance.
No performance speedup is asserted. Unknown human labeling/correction and
independently judged semantic error metrics are null. Shared x86_64 Linux host,
Python3.12.14,5 exposed CPUs; Chromium156.0.8078.79 and Pyodide314.0.7.
No hardware isolation or independent measurement is claimed.

## Failures and remaining limits

Two initial new tests failed: a missing exact-route record was labeled insufficient
evidence, and a model-reported conflict was grouped with reader failure. Fixed by
using the zero-eligible-page fact and an explicit unverified-reported-conflict
category. These were diagnostic changes, not answer-support changes.
The first baseline timing invocation failed because `/usr/bin/time` is absent;
`failed-time-attempt.log` preserves it. The successful replacement uses Python
resource counters. No failed historical cases were removed.

No exact legacy887-case revision/fixture package or critique text was established
by the inspected documentation. This package reproduces the actual current suite;
it does not authenticate B-Tests, reproduce a private setup or validate Gelhaus's
paper. Identify and pin those artifacts before claiming that specific reproduction.
A third party can rerun these public checks; no third party has been claimed to do so.
The deployed live site was not retested or updated. This candidate is locally
committed, not pushed or merged by this update. Existing frozen corpora and prior
historical reports remain unchanged.

## Recorded results

Extracted candidate:1134 tests passed in396.640s (process wall397.903s, CPU377.961s).
Focused extracted checks:51 passed0.589s. Public controls:52/52 before and after;
0/3 false supported bridge probes before and after. These authored probes are not
a representative random sample and cannot establish a general false-bridge rate.
Actual WebAssembly, JavaScript API, transport, crawler fixtures, candidate Chromium
smoke/eight scripted researcher steps and visible confirmation notice all passed.
No deployed-site or human usability result is inferred.

| Public fixture metric | Baseline | Updated |
| --- | ---: | ---: |
| fixture_cpu_seconds | 29.708939649999998 | 26.407760648999993 |
| fixture_wall_seconds | 31.285158373000286 | 26.978539585997623 |
| logical_source_text_read_bytes | 10704298 | 10704298 |
| source_text_read_calls | 16928 | 16928 |
| fixture_source_appearances | 89 | 89 |
| output_source_appearances | 48 | 48 |
| max_fixture_peak_python_allocated_bytes | 2491278 | 1227483 |

Runner process-lifetime maximum child RSS:308064256 bytes, including archive and all test commands; not process-tree memory.
The baseline standalone public process peak RSS was27,070,464 bytes; it is not
comparable to that whole-run maximum. Fixture Python allocation peaks are separately
reported above. No speedup or reduced memory claim is made.
