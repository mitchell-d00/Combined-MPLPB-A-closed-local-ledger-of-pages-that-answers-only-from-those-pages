# Offline candidate preprocessing sorter

Last reviewed: 2026-11-17.

The sorter supplies inspectable textual observations and review proposals. It does
not complete historical reconstruction, authenticate testimony, determine historical
truth, or create supported answers. It runs offline with Python's standard library
and the existing MPLPB date-cue helper. No answer grammar or reader gate is changed.

## Run both modes on identical inputs

From the repository root, use a new output directory outside the source directory:

```bash
mkdir /tmp/sorter-example
python -m mplpb_work.sorter sort tests/fixtures/sorter --mode not-compared --output /tmp/sorter-example/raw.json
python -m mplpb_work.sorter sort tests/fixtures/sorter --mode compare --output /tmp/sorter-example/compare.json
python -m mplpb_work.sorter verify /tmp/sorter-example/compare.json --sources tests/fixtures/sorter
python -m mplpb_work.sorter peruse /tmp/sorter-example/compare.json --sources tests/fixtures/sorter --max-items 8
python -m unittest tests.test_sorter -q
```

`not-compared` (also spelled `not compared`) emits observations only: source
occurrences, statements, identifiers, date expressions, headers, reference mentions,
correction cues, action-word candidates and repeated four-word phrase keys. Its
edges are containment and textual co-occurrence; they assert no event identity or
chronology. Literal dates have documentary roles only when a recognized header
supplies that role. Body dates remain unresolved.

`compare` emits **exactly the same sources, nodes, source spans and provisional
statuses**. It appends review edges: candidate identity clusters for shared explicit
identifiers, shared-header/phrase reviews, explicit-reference candidates, possible
corrections and unresolved-reference reviews. Raw edges remain an identical prefix.
Clusters are hyperedge annotations (`members`), never additional nodes. Different
bodies sharing an identifier are flagged, never merged. A shared subject alone
cannot create an identity cluster. Correction windows retain literal expressions,
claim quotation and `applied: false`; no prior claim is rewritten or retired.

Only edges change as documentary data. The envelope also records the chosen mode,
comparison flag, digest and any comparison-budget exhaustion. Comparison cannot
change extraction statuses. Missing or ambiguous targets stop a documentary hop;
unresolved-reference review edges point back to the occurrence being inspected,
not to an invented intermediate record. No transitive chains or inferred chronology
are emitted. Confidence is null; evidence notes explain the lexical proposal basis.

## Input and graph contract

Inputs are recursively discovered `.txt`, `.text`, `.md`, `.markdown` files, strictly
UTF-8. Newlines, BOM and Unicode remain unchanged. Supply extracted document text;
PDF/HTML conversion, OCR and fetching URLs are outside this tool. Hidden entries,
symlinks and nonregular files are excluded. Markdown quotation/fence and conditional
scope recognition is conservative and incomplete, not semantic verification.

Schema `offline-candidate-sorter-v1` has:

* `sources`: relative paths, exact raw SHA-256 hashes and byte lengths.
* `nodes`: stable content/path-derived IDs, `kind`, `span`, `assessment`, and typed
  lexical attributes. Spans include source ID/hash/path, half-open Unicode character
  offsets and half-open original UTF-8 byte offsets. Statement/feature spans carry
  exact `text`; full source-occurrence spans use the original file instead of
  duplicating its text. Paragraph boundaries and explicit identifier-header splits
  are layout candidates, not proof of complete historical documents or events.
* `edges`: `from`, `to`, `kind`, `evidence_nodes`, assessment and proposal notes.
  Compare-only edges have `comparison_only: true`. Identity-cluster edges also carry
  all occurrence `members`, shared identifier namespace/key and changed-body flag.
* `limits`, `complete`, `limits_or_exclusions`, `source_bytes_read`: explicit bounded
  processing diagnostics. Complete means extraction finished within its rules and
  budget, not that all relevant historical evidence exists or was understood.
* `implementation_sha256`, `graph_sha256`: implementation and canonical JSON pins.
  Replay rejects changed source bytes, source inventory, forged proposals and
  implementation drift. Replay establishes extraction fidelity, not semantic truth.
* `prior_assessment`: optional `--prior OLD.json` snapshot retained literally as
  untrusted historical JSON with its own raw hash. Prior assessments are preserved,
  never reused as current matching evidence or authority.

Every assessment has `answer_supported: false`, `source_support_established: false`,
`historical_truth_independently_verified: false`, and serving eligibility unevaluated.
A literal Status header yields a **provisional** current/retired candidate label only;
it cannot change ledger serving state. Event candidates are lexical action-word
observations with no established occurrence or identity.

Default limits: 64 files, 1 MiB/file, 8 MiB total source bytes per pass, 4096 tree
entries, depth12, 4096 nodes, 8192 edges, 2000 statements, 8000 characters/statement,
20000 comparisons, 4096 phrase keys, 32 phrase groups, 1 MiB prior snapshot and
32 MiB serialized output. `--limits limits.json` may only lower these positive
integer limits. Oversized paragraphs are skipped rather than truncated into false
complete statements. Exclusions/caps mark partial output; integrity changes refuse.
Two source passes are counted in `source_bytes_read`; code/metadata reads are not.
There is no OS-enforced wall timeout. Use a trusted local filesystem; path and regular
file checks do not constitute isolation against a hostile OS. Outputs are new files
with mode0600 and never overwrite inputs or existing outputs. Exit2 means refusal.

## Peruse or seal a withheld snapshot using the existing reader

JSON is a research artifact, not a native supported-answer page. `peruse` verifies
fresh source bytes then shows candidates. To store it as a native sealed page:

```bash
python -m mplpb_work.sorter export-retired /tmp/sorter-example/compare.json --sources tests/fixtures/sorter --ledger /tmp/sorter-example/ledger
python -m mplpb_answers ask /tmp/sorter-example/ledger 'Which record corrects the cargo request?' --profile lab --json
python -m mplpb_answers ask /tmp/sorter-example/ledger 'Which record corrects the cargo request?' --profile internal --json
python -m mplpb_answers ask /tmp/sorter-example/ledger 'Which record corrects the cargo request?' --profile external --json
```

The last three commands refuse (exit3), with `answer_supported: false` and empty
claims. The native `SORTER-CANDIDATES` page is intact, machine-origin, unratified,
external=no and **retired before publication** from private staging. No existing
ledger is overwritten. The unchanged gate withholds retired evidence in lab/internal;
external also enforces external=no before its retirement check. Tests directly
inspect gate exclusions as well as answers, including historical as-of views. A
failed retirement never publishes a current snapshot at the destination.

Do not reactivate the snapshot as factual evidence. Import unchanged originals
through normal source-management workflows with their real restrictions, ownership
and provenance. The sorter does not know or authorize those policies. Exported
hashes authenticate the snapshot bytes, not the proposed relationships. Graphs may
contain sensitive original excerpts; keep their private output permissions and
apply the source's actual access restrictions.

Fixtures in `tests/fixtures/sorter` are fictional development material. They test
repeated appearances, changed bodies, partial corrections and stopped links; they
are not an independent historical accuracy evaluation. The retained 22-question
historical completion measurements are unchanged by this preprocessing tool.
