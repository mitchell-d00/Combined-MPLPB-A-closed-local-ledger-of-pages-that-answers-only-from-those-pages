# Offline candidate preprocessing sorter

Last reviewed: 2026-11-17.

Package role: [how this part fits Combined MPLPB](PACKAGE_GUIDE.md#sort-and-import). Raw-text sorting creates reversible candidates or retired snapshots, never automatic answer evidence.

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
python -m mplpb_answers validate /tmp/sorter-example/ledger --strict
python -m mplpb_answers show /tmp/sorter-example/ledger SORTER-CANDIDATES
python -m mplpb_answers gate /tmp/sorter-example/ledger 'sorter candidate inspection' --profile lab --json
python -m mplpb_answers gate /tmp/sorter-example/ledger 'sorter candidate inspection' --profile internal --json
python -m mplpb_answers gate /tmp/sorter-example/ledger 'sorter candidate inspection' --profile external --json
python -m mplpb_answers ask /tmp/sorter-example/ledger 'What is Owner for record MAIL-001?' --profile lab --json
python -m mplpb_answers ask /tmp/sorter-example/ledger 'What is Owner for record MAIL-001?' --profile internal --json
python -m mplpb_answers ask /tmp/sorter-example/ledger 'What is Owner for record MAIL-001?' --profile external --json
```

`validate --strict` exits0 with zero errors/warnings: the snapshot is a valid
native page. `show` exits0 and displays it for inspection, even though it is
retired. Each `gate` command exits3 with no eligible sources. Storage acceptance
and inspectability do not confer answer eligibility. Native `show` uses the reader’s
existing normalized text display; use the graph JSON, stored HTML payload and
original source spans for exact whitespace/byte inspection.

Before publishing the new directory, export now runs the existing native validator
against its private staging ledger and independently re-reads the sealed page.
Any native error **or warning**, retirement failure, or changed embedded graph
refuses export and leaves the destination unpublished. The native writer adds its
normal heading; the graph inside the escaped `pre` block must round-trip exactly,
including quoted Unicode, HTML delimiters and original CRLF source strings.
The export receipt includes `native_validation` with errors0, warnings0 and
`graph_roundtrip_verified: true`. These are storage/fidelity checks, not support
or truth judgments. A literal original Status header still cannot activate a page.

The last three commands refuse (exit3), with `answer_supported: false` and empty
`answer_contract.claims`. The native `SORTER-CANDIDATES` page is intact, machine-origin, unratified,
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

For a retained graph pair, direct gate exclusions and all three CLI refusal logs,
run `python -m tools.evaluate_sorter --output /tmp/sorter-evidence-new` from the
frozen checkout. This uses fictional fixtures and reports software checks, not
semantic accuracy. Its source/reader code is identical to the frozen implementation.

## Check a plain pre-sorter checkout

The existing reader accepts native pages; it does not need to understand the sorter
JSON schema to withhold a retired page. To reproduce compatibility against the
unchanged revision before the sorter existed, prepare a separate checkout:

```bash
git archive --format=zip --output=/tmp/mplpb-reader-base.zip 3df2c6e22f0ef454f3ee67b88d43402a42f63443
python -m zipfile -e /tmp/mplpb-reader-base.zip /tmp/mplpb-reader-base
python -m tools.evaluate_sorter --output /tmp/sorter-plain-reader-new --reader-checkout /tmp/mplpb-reader-base
```

The runner checks that all Python files in `mplpb_answers` and `mplpb_combined`
are byte-identical between the two checkouts. It sorts and exports using the new
code, then invokes native `validate`, `show`, `gate` and `ask` from the specified
plain checkout, with its working directory recorded in each command receipt.
Neither checkout is modified. This distinguishes storage compatibility from
answer eligibility without adapting the reader's grammar or policy checks.

## Technical report and preserved evidence

[A Dual-Mode Sorter for MPLPB](research/dual-mode-sorter/README.md), by Mitchell D. McPhetridge, is available in Markdown, plain text and PDF. It documents the implemented stages, dual-mode contract, native publication checks, measured development costs, failed attempts and remaining limitations. Its frozen software results are not independent historical validation. Shared-subject pair proposals consider at most the first16 occurrences per subject; graph completeness does not mean every possible review pair was enumerated.

## Header appearances versus primary declarations

Header recognition is an observation, not a declaration of the containing file's
identity. Extraction now classifies layout **before occurrence partitioning**.
Recognized fences (backticks or tildes), Markdown blockquotes, explicitly delimited
quotations, forwarded-message frames and bounded example/quotation cues retain
headers as embedded observations. Nested explicit forward frames remain scoped
until their closing markers; an unclosed frame remains review-scoped. A code-fence
closer must use the same marker family, sufficient length and no trailing text.

Header nodes retain `header_context`, `header_role` and
`primary_identity_eligible`. A top-level declaration candidate has
`header_role: record_declaration_candidate`. An embedded appearance has
`header_role: embedded_text_observation` and cannot be a primary identity key.
These fields are derived layout assessments, not proof that a communication is
genuine. An ordinary top-level header stays eligible even if its paragraph also
contains quoted body prose; paragraph scope warnings alone do not decide its role.

Only primary declaration candidates can delimit record occurrences, enter primary
identity-cluster membership, resolve a documentary reference target, or supply the
outer occurrence's declared-status/date-role candidates. The source occurrence
also records `identity_role`: `declared_record_candidate` or
`textual_appearance_only`. The latter means no primary identifier was recognized,
not that the file or a quoted historical communication ceased to exist.

Both modes preserve the same observations and classifications. Compare may append
`embedded_identifier_review` edges with lexical `matching_primary_occurrences`.
These annotations preserve discovery of copied/forwarded material without merging
it into primary cluster membership. An embedded-only target remains unresolved
with `embedded_only_target`; missing and ambiguous targets retain their existing
refusal/review behavior. Shared subjects and similar wording still cannot establish
historical identity or event independence.

These are finite layout rules. Unmarked quotations, ambiguous forwarded archives,
misleading labels and damaged/OCR delimiters can require manual scope review.
No universal document-boundary or historical-identity resolution is claimed. Earlier
graphs remain preserved; the changed implementation fingerprint requires a fresh
replay rather than accepting an old classification silently.

[Scope regression evidence and resume checkpoint](../evaluation/preprocessing-sorter/2026-11-17-header-scope/REPORT.md)
records the supplied probe, the failing pre-fix tests, before/after cluster members,
source-byte checks and verification commands. The checkpoint allows a fresh process
or future worker to recover the task and rules without relying on this session;
it does not measure a minimum AI context size or prove general historical accuracy.
