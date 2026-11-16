# Original-record evaluation and review workflow

Last reviewed: 2026-11-16.

The next evaluation uses MPLPB's public original papers. It separates preparation,
sealed questions, execution and external review. Passing this protocol's software
tests does not establish independent historical accuracy or close every remaining
capability gap. The existing 52-case development suite and historical reports stay
unchanged.

```sh
python -m tools.historical_study prepare /tmp/new-study
python -m tools.historical_study seal /tmp/new-study /path/to/questions.json
python -m tools.historical_study run /tmp/new-study --sandboxed
python -m tools.historical_study score /tmp/new-study /path/to/reviewer-a.json /path/to/reviewer-b.json
```

Preparation verifies four existing original-paper byte pins and creates an empty
question template. A separate author supplies cases with `id`, `question` and
`required_source_ids`. Source IDs are the prepared `ORIGINAL-0001` style witness
IDs. Empty, duplicate, or invalid questions cannot be sealed. Keep genuinely unseen
questions outside this repository and separate from development work until the
study is complete. No unseen or independently authored questions are invented by
the preparation command.

Sealing pins source content, runtime questions, salted private source expectations,
implementation modules, evaluator bytes, profile, budgets and model settings.
Execution reads no gold labels. Changed source bytes, questions or implementation
are rejected. Strict responses and bounded expert evidence reports are retained
separately with measured CPU/wall time. Original source files are never revised;
the engine receives isolated documentary witness wrappers.

Runtime output and the generated review template are waiting for external review,
not graded successes. Reviewers submit explicit completeness, false-bridge and
source-accuracy judgments, exact pinned-source citations, rationales, and reported
labeling/correction seconds. Completed answers require citations. Blank or duplicate
review identities, missing judgments and fabricated citations are rejected.
Disagreements require adjudication. Source-coverage fractions measure required
witness retrieval, not semantic answer accuracy. Reviewer rates are submitted
judgments and times are self-reported, not independently measured observations.

The private gold file and secret commitment salt are mode 0600 in a private directory.
The public salted commitment avoids exposing small gold-label sets to hash guessing.
Share only the corpus, runtime questions, seal and required code with the execution
operator; distribute review packets separately.

`run --sandboxed` requires Linux, bubblewrap and permitted kernel namespaces. It
fails closed when isolation is unavailable or the worker fails; it never retries
direct execution. The worker receives read-only code and runtime inputs, a private
256 MiB scratch filesystem and a writable output directory. Private gold, reviewer
files, host home, credentials, repository metadata and host temporary directories
are excluded. Network access is isolated; inherited environment and capabilities
are removed, and nested user namespaces are disabled. Limits are 300 CPU seconds,
600 wall seconds, 2 GiB address space per process, 50 MiB per file and 256 open
descriptors per process. These are not aggregate process-tree memory/disk limits.
Only regular output files are accepted. A run-bound `sandbox-receipt.json` records
the configuration; scoring checks its run binding and records its hash.

The dedicated [isolation CI](../.github/workflows/study-sandbox.yml) requires actual
Linux isolation tests and fails if unavailable. Reproduce with bubblewrap installed:
`MPLPB_REQUIRE_SANDBOX=1 python -m unittest tests.test_study_sandbox -v`.
Ordinary test runs on restricted hosts may skip Linux integration checks; skips do
not verify isolation. Ubuntu CI uses a privileged outer test controller to permit
namespace creation; worker capabilities are dropped inside the sandbox.

The trusted host custodian, administrator and kernel remain outside this boundary.
This isolates the worker process; it cannot prevent its human operator or a host
administrator from reading files they already control. Direct `run` remains
available without a sandbox receipt or isolation claim. Neither mode proves the
operator never saw the questions or gold.
Hashes and distinct reviewer IDs do not authenticate people or establish their
independence. Outputs retain `independence_verified:false`; genuine independent
validation requires outside participants and an auditable custody record.

After review, publish source receipts, questions, gold expectations, system output,
review submissions with consent, adjudication and score receipts together. Those
released questions then become public development examples. Do not publish private
material or personal data merely to make an evaluation inspectable.

Remaining technical limits are explicit: arbitrary implicit event reconstruction,
automatic semantic partial-message correction, unrestricted as-of/causal reasoning,
and independent external delivery/read/acknowledgement verification are not added
by this evaluation workflow. Current native expert/correction capabilities remain
bounded by their declared contracts. See [public tests](PUBLIC_EVIDENCE_TESTS.md)
and [expert investigation](HISTORICAL_EXPERT_PATH.md).

Update 2026-11-16: [Scoped evidence extensions](SCOPED_EVIDENCE_EXTENSIONS.md) add precise field/identity/correction diagnostics, exact source routing, distinct event nodes, declared correction windows, quoted relation inspection and non-authoritative receipt/effort metadata. Public focused tests are linked in the guide; historical reports retain their original scope.
