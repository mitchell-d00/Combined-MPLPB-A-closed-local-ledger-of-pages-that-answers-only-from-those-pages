# User-built collection repair: measured local results

Baseline: `f425a0583e8a69ef17b86009ed40206871808416`.
Tested implementation: `31b2426ef23906a9dea60ed6356e950534057731`.
This work is local and has not been published or deployed.

Both input files and acceptance thresholds were frozen before implementation.
The separate evaluation was first executed after the implementation commit was
fixed, using both the preserved baseline worktree and repaired worktree. One
developer authored the inputs and exact-quote oracle. These are development and
frozen developer evaluation evidence, **not independent human validation**.

| Set | Baseline correct / answerable | Repaired correct / answerable | Wrong returns before / after | Unnecessary refusals before / after |
| --- | --- | --- | --- | --- |
| Development, four tasks | 4/12 (33.3%) | 12/12 (100%) | 0 / 0 | 8 / 0 |
| Separate frozen evaluation, four new tasks | 4/12 (33.3%) | 12/12 (100%) | 0 / 0 | 8 / 0 |
| Existing frozen NPC questions | 12/18 (66.7%) | 13/18 (72.2%) | 0 / 0 under its literal oracle | 6 / 5 |

The original pottery sets remain 3/32, 2/19 and 1/8 supported answers, with zero
wrong returns in this retest. This repair does not solve arbitrary pottery
procedures or general natural-language interpretation.

Each new set has 16 primary queries: 12 answerable and four genuinely absent
fixture answers. The absent-answer refusals do not contribute to correct answers.
All gold passages were retrieved before and after; the primary repair is bounded
interpretation. Returned-answer literal precision and citation accuracy/completeness
are 100% on both versions of these small sets, with a different number of returns.
Matching a quote or passing a workflow alone cannot earn a correct-answer score:
the complete answer text must equal the frozen policy sentence and its current
source citation must validate. This is not a general semantic grader.

Four additional post-revision body-conflict checks per set pass after repair;
the baseline's lexical ambiguity was not counted as a checked body conflict.
Full task completion improves from 0/4 to 4/4 per set under the frozen workflow
criteria. Each repaired set passes all 40 workflow checks, including revision,
retired citation rejection, transcript/notes recovery, external withholding,
quiescent source/lineage/note restore and injected capture-damage rejection.

## Resource observations

These are single small local runs, not stable performance benchmarks or load tests.

| Measurement | Development before / after | Evaluation before / after |
| --- | --- | --- |
| Total native query latency, 16 queries, ms | 139.902 / 143.694 | 135.032 / 159.807 |
| Retrieved characters, summed over queries | 9,856 / 9,856 | 10,236 / 10,236 |
| Saved workspace bytes, four tasks | 127,606 / 128,030 | 128,423 / 128,847 |
| Source-network requests / model calls | 0 / 0 on both versions | 0 / 0 on both versions |

Storage includes deliberately retained revisions and captures. No operating-scale
memory/CPU claim, long-term retention result or hosted-provider price is inferred.

## Retained evidence

- `development.json` and `evaluation.json`, with SHA-256 sidecars and frozen policy.
- `before-development.json`: first observed development baseline, retained with
  its original runner hash before the additional backup-assessment checks.
- `baseline-development-final.json` and `baseline-evaluation.json`: old code run
  with the final study runner, pinned to baseline code and frozen inputs.
- `after-development.json` and `after-evaluation.json`: repaired code against the
  same inputs. Both meet the frozen acceptance thresholds.
- `existing-npc-after.json`: unchanged older NPC inputs, 109 workflow checks and
  13/18 answers. Original NPC reports remain in their original directory.
- `pottery-retest/`: original frozen pottery/development comparisons, with named
  code baseline and current answer-module pins; no historical result overwritten.
- `packaged-wasm.json`: actual built Pyodide runtime, import metadata, exact policy,
  changed values, source hashes, revision, saved-note reopen, conflict, withholding
  and HTTP-fixture acquisition. This is not a Chromium or IndexedDB UI pass.
- `validation.json`: test/package verification, code pins and browser limitation.

The full Python suite passes **772 tests**. The full actual WebAssembly suite,
UI script, browser transport, JavaScript API and crawler fixtures also pass.
An installed 2.1.0rc1 wheel was imported outside the checkout and passed policy,
changed-value/revision, qualifier preservation and CLI checks; packaged modules
match the source bytes.

Chromium 143.0.7499.0 was obtained as a test-only dependency and reported its
version, but terminated with SIGTRAP during launch in this environment. There is
no new actual-browser, visual, live-source-network or human usability pass.
The executable browser reproduction script is supplied for an environment where
Chromium can run. It needs Playwright and an installed browser; use
`--browser-executable /path/to/chrome` when using a system browser.

See [the workflow and authority guide](../../docs/USER_BUILT_COLLECTIONS.md).
No live model or independent participants were available. The next useful product
work is a validated portable collection backup/restore interface, followed by
evaluation with independent builders and their own source material/questions.
