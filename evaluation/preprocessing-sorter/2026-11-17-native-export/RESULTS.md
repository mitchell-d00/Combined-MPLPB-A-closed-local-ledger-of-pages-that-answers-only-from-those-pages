# Native sorter export refinement — 2026-11-17

Baseline: `27b2a6cf0ad023c14703f8202c3f25ff3627ecf5`.
Frozen sorter implementation: `30f0d89c5954b1f1226d0e30c78dc671011849e1`.
Plain pre-sorter reader: `3df2c6e22f0ef454f3ee67b88d43402a42f63443`.
The compatibility runner's literal source hash is recorded in `report.json`.

## Implemented change

The existing sorter already converted raw UTF-8 text/markdown into a source-anchored
candidate graph and a sealed retired native snapshot. Its pre-edit suite passed24
sorter tests in0.490s; an actual baseline `validate --strict` reported one retired
record with zero errors/warnings. The gap addressed here was enforcing and retaining
that format acceptance before publishing the export, rather than checking retirement
alone.

The refined exporter re-reads its private staging ledger, requires zero existing
native validation findings (errors or warnings), checks a single intact retired
page, and checks exact embedded graph serialization and JSON recovery. Only then
is the destination published. Failed validation, changed body or interrupted
retirement leaves the requested destination absent. Receipt `native_validation`
is a format/byte-fidelity check; all candidate support/truth flags remain false.
No native ledger, reader, provenance gate, finite grammar or source policy code changed.

Three additional tests cover both-mode native validate/show acceptance, Unicode,
CRLF and HTML-delimiter roundtrip, injected native errors/warnings, and a validly
sealed wrong graph. The27-test sorter suite passed0.878s; combined focused and
documentation checks passed37 tests in1.147s. Earlier fixtures and reports remain
byte-unchanged. Both modes' source arrays, nodes and edges are also identical to
their pre-refinement fixture output: only export validation was refined.

## Plain checkout acceptance and withholding

The independent directory used for the native CLI was extracted from the tracked
pre-sorter revision, where `mplpb_work/sorter.py` does not exist. All Python files
in its `mplpb_answers` and `mplpb_combined` packages were byte-compared with the
frozen candidate and are identical. This is software compatibility evidence, not
independent semantic review. Per-file hashes, archive pin and exact commands are
retained in `plain-reader-report.json`; the reusable runner also records checkout,
package hashes and command working directories in `report.json`.

| Existing native command | Result |
|---|---|
| validate --strict | exit0;1 retired record,0 current,0 errors,0 warnings |
| show SORTER-CANDIDATES | exit0; snapshot inspectable |
| gate, lab/internal/external | exit3; zero eligible sources |
| ask, lab/internal/external | exit3; answer_supported=false; no claims |

The native gate directly excludes the page, independently of question grammar.
Lab/internal report retired. External applies its sealed external=no restriction
before retirement. The native show display normalizes text as it always did;
exact source strings remain in the stored escaped graph, JSON and original files.
The fixture tests additionally check historical as-of views. A separate deliberately
changed reader-package probe was refused before any sort/native commands ran
(`mismatched-reader.log`), rather than being adapted to pass.

Both modes emit176 identical nodes with exact source spans and provisional statuses.
Not-compared has264 containment/co-occurrence edges; compare preserves that prefix
and appends77 non-authoritative review edges (341 total). No identity or chronology
is forced. Missing/ambiguous intermediate links remain stopped. The original
statements, source IDs/hashes/byte and character coordinates, and optional literal
prior-assessment snapshot remain preserved by the existing contract.

## Reproduction

From the final checkout, use fresh output paths:

```bash
python -m unittest tests.test_sorter -q
python -m tools.evaluate_sorter --output /tmp/sorter-native-new

git archive --format=zip --output=/tmp/mplpb-reader-base.zip 3df2c6e22f0ef454f3ee67b88d43402a42f63443
python -m zipfile -e /tmp/mplpb-reader-base.zip /tmp/mplpb-reader-base
python -m tools.evaluate_sorter --output /tmp/sorter-plain-new --reader-checkout /tmp/mplpb-reader-base
```

The runner produces both graphs, verifies current source fidelity, exports the
retired snapshot, invokes validate/show/gate/ask, records failures/timeouts and
runs sorter tests. Its command logs show the exact acceptance/refusal calls. Outputs
must be outside both checkouts and cannot overwrite a prior run. For the explicit
input/output schema and individual conversion commands, see
[the sorter guide](../../../docs/PREPROCESSING_SORTER.md).

## Costs and remaining limits

Retained `report.json` is a single shared-host development run, Python3.12.14 on
Linux x86_64 with five visible CPUs. Not-compared:0.142s wall/0.142s child CPU;
compare:0.149s wall/0.148s CPU; snapshot export:0.192s wall/0.191s CPU. Cumulative
maximum child RSS readings were19,116,032;19,542,016;24,961,024 bytes respectively.
They are not isolated incremental or aggregate process-tree memory measurements.
Source processing reads2804 bytes per sort invocation (1402 fixture bytes twice);
this excludes implementation/ledger reads and subsequent export verification.
These tiny fictional fixtures do not establish large-pile performance or speedup.
Hardware allocation is not pinned. Historical precision/recall, relationship
accuracy, human review effort and historical supported-answer gain remain null.

An initial new assertion omitted the native writer's standard h1 heading, causing
two export tests to fail. The expected snapshot serialization was corrected to
include that existing heading (`first-roundtrip-attempt.log`); no writer or reader
change was made. A validly sealed wrong-body mutation and injected validator
findings continue to fail closed intentionally.

The sorter is an offline preprocessing/inspection tool. It does not authenticate
original testimony, resolve historical truth, complete historical reconstruction,
or create authoritative answers. Lexical recognition is incomplete; limits may
produce explicit partial graphs. Raw headers cannot authorize serving or access
policy. Independent historical semantic review: **NOT RUN**. All past historical
corpora, questions, expected results and reports are preserved, with no claim that
the22-question historical completion metric improved.

## Frozen archive regression

Tracked source ZIP SHA-256: `33694aceb3bbe525c6ae65edf60affee988e3738d7aa073dcf2e1ce2917aa59b`.
The extracted candidate passed1184 Python tests in353.340s reported test time
and52/52 public-evidence cases with required capabilities; zero false supported
bridges on these authored controls. Exact wall/CPU and cumulative child maximum
RSS readings are retained in `archive-report.json`. The focused boundary suite
also passed51 tests. JavaScript API, browser transport, fixture crawler, actual
pinned Pyodide WebAssembly and actual Chromium published-live/candidate-preview
checks passed. Infrastructure and documentation audits passed. The evidence
follow-up changes the compatibility runner and documentation; sorter/native
runtime and test bytes remain frozen. No merge or new deployment is claimed.
