# Current status — November 2, 2026

Last reviewed: 2026-11-02.

Inspected main: `c0eb212b51c41a96e361ae0ceb680a0a5df0d55f` (PR #29).
This review updates navigation, result scopes and maintenance checks. It changes
no source ledger, frozen question, original label or answer-engine rule.
The [result-to-test index](RESULTS_AND_TESTS.md) links every retained evaluation
family to its regression tests and reproduction tools. A mapped test does not
retroactively validate an old metric.

## What is implemented

Strict answers require eligible source-body evidence under bounded rules. Negative
assertions participate in conflict detection, including same-page and cross-page
contradictions. Subject, relation, value and applicable scope remain material;
related words or search rank never prove an answer. Source ownership, ancestry,
revision and delivery rules remain authoritative.

Procedures use complete source-authored JSON blocks or explicit numbered body
lines with required declarations. Natural requests with an identifiable procedure,
step clarification, explicit position corrections, saved-state reload and partial
evidence inspection are implemented. Context cannot prove real-world execution,
resolve ambiguous source identity or supply missing conditions. See
[procedure rules](PROCEDURAL_CONSTRAINTS.md) and the [generated system guide](SYSTEM_GUIDE.md).

An optional native local-model reader remains separately labeled model-assisted;
its semantic quality and calibration have not received independent validation.
New collections work within these finite capabilities, not arbitrary prose.

## Measured results and their limits

| Evidence | Recorded result | Meaning and test route |
|---|---|---|
| PR #29 regression, head `ec5d318e82a79a10d9bb1ae69db3af6174811240` | 828 Python tests passed in 451.954 seconds | Published CI result, not a new local run of this documentation change. [Actions](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/41492475176). |
| Inspected pottery, 106 probes / 59 answerable labels | 12 document-identity returns; 45 answerable refusals; 2 answerable ambiguities | Meaning review: 11 complete source statements plus one conditional quote with unresolved applicability. Original 6/59 report preserved; no independent holdout. [Per-case audit](../evaluation/language-audit/README.md). |
| Four polarity defect reproductions | Ambiguity replaces an unqualified positive return | Same-page and cross-page cases; development examples. [Polarity tests](../tests/test_assertion_polarity.py). |
| Frozen synthetic language set | 6/12 before, 12/12 after | Frozen before execution; model-authored synthetic evaluation, not independent validation. [Audit](../evaluation/language-audit/README.md). |
| Cross-domain relation smoke | 312 cases and 24 metamorphic checks passed | Authored bounded relations across 12 domains; no general language claim. [Runner](../tools/benchmark_relation_graph.py), [tests](../tests/test_relation_graph_generated.py). |
| Procedure recovery | 18/18 authored turns; 9 Chromium checks; 3 CLI checks | Implementation-candidate evidence retained separately from publication; finite source declarations only. [Report/tests](../evaluation/procedure-recovery/README.md). |
| Reference corpus growth | 0, 23, 48, 73 of 73 positives as pages are added; 20/20 controls refuse at every stage | 372 per-stage rows; same reader, growing source data. Unratified lab-only records, absent from default hosted collections. [Reproduction, tests, checksums](../evaluation/reference-corpus-reproduction/README.md). |

Hashes attest consistency with recorded bytes, not truth or authenticated
publisher authorship. Source repetition and shared ancestry are not independent
corroboration. Synthetic or developer-authored tests are not human validation.

## Publication and actual verification

PRs #28 and #29 are merged. All four PR #29 workflows passed: regression/browser,
archive-first (extracted source ZIP), infrastructure synchronization and handoff.
Main revision above passed Pages build, deployment and the postdeploy real-Chromium
smoke test in [run 41495283409](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/41495283409).
That deployment evidence belongs to that revision. This documentation update
requires its own checks; successful source tests alone do not establish deployment.

New checks and their exact outputs are retained under
[evaluation/documentation-audit](../evaluation/documentation-audit/README.md).
The [handoff](../HANDOFF.md) records this update's actual local validation and
remaining release steps. Later CI outcomes belong to their Actions runs rather
than silently rewriting historical reports.

## Documentation policy and remaining work

Current operational guides are reviewed November 2. The machine-readable
[inventory](documentation.json) identifies current guides, original historical
reports/specifications and vendor material. Historical/vendor hashes prevent
accidental redating or rewriting. Copyright, source-publication, introduction and
experiment dates retain their original meaning. The review date is explicit;
future builds cannot automatically pretend someone reviewed the docs that day.

Cross-sentence reasoning, arbitrary procedures, broad paraphrase handling,
independent collection-builder trials, independent human semantic grading and
live assisted-reader calibration remain limited or unverified. Ambiguity and
honest refusal remain required when the available evidence cannot justify a
complete answer. Earlier dated status pages remain historical snapshots.
