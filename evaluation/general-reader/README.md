# General-reader evaluation and shipping evidence

This directory distinguishes implementation validation from general answer
accuracy. The frozen eight-case suite spans software, library policy, office
procedures, image archives and equipment instructions. It is **developer-authored
and inspected development data**, with explicit absent/conflicting cases. It is
not a held-out or independent model evaluation.

The local-reader adapter has been exercised using bounded loopback HTTP fixtures,
including an end-to-end query/read/review request. No local inference runtime or
model weights are installed in the build environment. No assisted accuracy result
is claimed. The included strict report deliberately leaves semantic correctness
unscored and the release assessment blocked.

## Run and review

Both the source compatibility entry point and the installed command use the same
packaged runner:

```sh
python -m mplpb_answers.evaluate run evaluation/general-reader/development.json --output local/reader-run.json
```

With an explicitly installed local model, an assisted run can use:

```sh
mplpb-evaluate run /path/to/frozen-suite.json --mode assisted --reader-model YOUR_INSTALLED_MODEL --output local/reader-run.json
```

The suite needs a neighboring `.json.sha256` file matching its exact bytes. Inline
source documents have safe IDs and a closed field allowlist; a suite cannot supply
filesystem destinations. The runner writes isolated temporary corpora, passes only
the original question and eligible source context to the reader, and records exact
results, retrieval selection, model/code pins, threshold, policy and latency. Gold
answerability and gold passages are never included in model prompts.

A `<report>.review.json` template is emitted separately. Output reports and existing
human review files are never overwritten; choose a new output name for each run. Human reviewers fill in
`correct`, `citation_complete`, `complete` and a concise `reason` for each returned
answer, and identify themselves under `reviewers`. Null fields remain unreviewed;
matching quotations and high model confidence cannot fill these fields automatically.
Partial answers can have correct claims without counting as complete question answers.
Judgments must identify the exact `run_sha256`.

```sh
mplpb-evaluate score local/reader-run.json local/reader-run.review.json --output local/reader-score.json
```

Reports include all outcomes, reviewed precision, assisted error bounds, complete
answerable coverage, partial/clarification/conflict counts, gold-passage retrieval
recall where supplied, per-domain breakdowns and diagnostic risk/coverage curves.
Strict returns cannot inflate the sample size for evaluating assisted-reader risk.
The original answerable denominator is retained when a threshold filters answers.

Use separate calibration data to choose thresholds. Freeze a new test suite before
running it, with a `calibration_run_sha256` reference to the earlier calibration run.
The reference checks this declaration's presence; freshness, chronology and human
review independence still require an external review process. Renaming inspected
fixtures to `test` does not make them independent.

## Declared release policy

A default policy is frozen into each run. `run --policy PATH` can declare a
justified alternative before seeing answers; scoring rejects a different policy.
The default requires at least 200 reviewed assisted returns, at least three domains,
at least 60% complete answerable coverage per domain, and an assisted error-rate
Wilson 95% upper bound at most 2% per domain. A zero-error domain needs substantially
more than six reviewed returns to meet that bound. Also required are live inference,
a frozen test role, a calibration reference and attributed complete human review.

These thresholds are candidate product targets, not measured achievements or
universal safety guarantees. Wilson intervals require suitable sampling assumptions;
correlated questions, dependent errors, label mistakes and domain shift limit their
interpretation. The scorer always reports `independence_verified:false`. A passing
statistical report is `eligible_for_human_release_review`, never automatic publication.

`strict-release-assessment.json` is blocked because the current data are development
fixtures, no live assisted run or calibration is recorded, and human review is absent.
The existing pottery result is still six strict supported answers out of 59; that
historical limitation has not been hidden by treating assisted output as support.

## Reproduce implementation checks

```sh
python -m unittest tests.test_general_answers tests.test_local_reader tests.test_general_evaluation -q
python -m unittest discover -s tests -q
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
node crawler/test_worker.mjs
```

Final validation: **755 Python tests** pass, including the new general-reader,
local HTTP protocol and human-scoring regressions. The focused compatibility run
passes **62 tests**. UI rendering/escaping, transport, JavaScript API and fixture
crawler checks pass. The installed 2.1.0rc1 wheel passes module-byte parity and
CLI/pipeline/evaluator checks outside the checkout. Configured native UI and shared
bridge payloads match. Exact pins and scope are recorded in `validation.json`.
Live-model accuracy remains unmeasured; exact-head WebAssembly and Chromium release
checks remain for CI. Frozen
pottery questions, source pages, supplied papers and the legacy engine are unchanged.
Original reports elsewhere remain historical. See the [operation guide](../../docs/GENERAL_ANSWER_PIPELINE.md)
and [release capability matrix](../../docs/RELEASE_2_1_RC1.md).
