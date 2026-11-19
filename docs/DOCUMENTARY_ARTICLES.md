# Documentary article dossiers

Last reviewed: 2026-11-19.

The `article` command assembles the existing single-question reconstruction
reports into a read-only research dossier. It does not author a historical
narrative or add a proof rule. **One owner returns; two stop; none refuses.**
Each section still passes its original question through the existing ownership,
source eligibility and strict evidence checks.

## Usage

Import original documents through the existing collection/source workflow first.
An article plan is UTF-8 JSON with exactly two fields:

```json
{
  "title": "Appointments and correspondence",
  "questions": [
    "Who appointed Ellis Marsh?",
    "Who wrote the harbour report?",
    "Did the appointment cause the delivery?"
  ]
}
```

These are fictional example questions, not specially prepared source fields.
The title is a user-supplied topic label, never evidence. Plans cannot supply
answers, article prose, relationship labels or source-support decisions.

```sh
python -m mplpb_answers article LEDGER --plan plan.json --format text
python -m mplpb_answers article LEDGER --plan plan.json --profile external > dossier.json
```

The default format is JSON. Exit 0 means a dossier was assembled, including when
every section abstains. Exit 3 means assembly was withheld, and exit 2 indicates
an invalid plan/configuration or an input error. No model or network is used.

## What is preserved

`documentary-article-v1` contains the original plan and profile, ordered sections,
question-specific eligible source references, and complete existing
`historical-reconstruction-report-v1` objects. Each native answer retains its
kind, support scope, exact citations and canonical coordinates, typed claims,
negations, date roles, conditions, alternative evidence and diagnostic codes.
Candidate mappings and graphs remain in `candidate_analysis`, with their existing
non-authority labels and reversible evidence anchors. Original-byte mapping uses
the existing import receipt and `tools.source_roundtrip`; the article does not
claim that mapping has been independently reviewed.

The assembler adds no transitions such as “therefore,” no causal or temporal
bridge, no cross-section edges and no actor/event merges. `coverage` counts
complete native *question sections*, not complete historical articles. A textual
word-location proof keeps its textual-only scope. Even if every section is
answered, article-level `answer_supported`, `source_support_established` and
`historical_truth_independently_verified` remain false.

## Conflicts and source dependence

Competing checked documentary accounts remain visible, including their exact
wording and the native `conflict` status. The assembler refuses the conclusion
that one account wins; it does not refuse to display the disputed evidence.
Unsupported or missing connections remain unresolved sections.

`provenance.sources` retains the union of question-eligible source identities and
declared ancestry. This is a source inventory, **not a set of supporting
witnesses**. Section-local source references preserve which question each source
was eligible for. Eligibility for one question never grants eligibility for
another.

`shared_declared_roots` groups appearances with a common hash-pinned ledger root,
including appearances retrieved for different questions. It reuses the gate's
structural ancestry meaning. Three pages deriving from one root are not counted
as three independent witnesses. A root that is false can still have intact
provenance: the software does not discover that falsity by hashing it. Declared
derivation and supersession are not proof of historical transmission.

When ancestry is absent, witness independence remains unknown. The result always
sets `independent_witness_count` to null and `independence_verified` to false.
Undeclared copying, shared informants and testimony authenticity are unresolved.

## Bounds and invalidation

Plans allow 1–8 distinct questions of at most 4,000 characters, one title of at
most 240 characters, and no extra fields. The CLI reads at most 64 KiB of plan
input and rejects duplicate JSON fields. Per-section defaults are 12 passages
and 12,000 context characters; the accepted ranges remain 1–64 and 1,000–64,000.
The assembler withholds output above 256 eligible sources per section. These are
admission/output limits, not a hard CPU timeout or a total source-read limit.
Existing gate/index scans and reconstruction graph/unit caps still apply;
article sections repeat those operations. No speed improvement is claimed.

The source/policy state for every question is captured before assembly and
rechecked after the last section. A changed state discards the entire dossier,
including earlier claims, candidate quotes and provenance lists. This optimistic
recheck is not an atomic filesystem snapshot. Sources can change after return.
Every export is labelled a snapshot: rerun the command for current eligibility.
A `snapshot_pin` checks content identity, not truth, authorship or current policy;
the text renderer is not a verifier for imported or edited JSON.

## Evidence and next milestone

```sh
python -m unittest tests.test_documentary_article -q
python -m tools.article_study --output /tmp/new-article-study
```

The study uses the unchanged 22 original-record questions and frozen source
seals, compares each assembled native contract with the standalone checker under
the same 12-passage/8,000-character budget, and preserves raw packets, citations,
import receipts, costs and failures. It loads no expected-answer file. This is a
developer preservation experiment, not a blinded semantic evaluation.

See the [recorded study](../evaluation/documentary-articles/2026-11-19/REPORT.md).
The next capability milestone is a finite, independently checked cross-document
connection with a witness for each link and contrasting missing-link/conflict
controls. This assembler does not claim to deliver that milestone or improve
historical answer coverage. Independent historical accuracy remains unmeasured.
