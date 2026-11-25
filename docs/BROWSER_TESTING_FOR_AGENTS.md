# Browser testing runbook for humans and AI agents

Last reviewed: 2026-11-25. See the [current status and result-to-test index](CURRENT_STATUS.md). Historical results retain the scope of their original runs.

Package role: [how this part fits Combined MPLPB](PACKAGE_GUIDE.md#evidence-and-limits). This guide covers evidence or operation limits; dated results keep the revision and scope they measured.

**Purpose.** This is the repeatable release-gate procedure for the actual hosted MPLPB browser application and the proposed build. Do not describe an HTTP fetch, a static HTML inspection, or a Python-only test as **live-browser testing**. The hosted page embeds Pyodide/WebAssembly, runs the same Python application locally inside the browser, and stores user state in that browser's IndexedDB.

**Production site (do not overwrite data):**

https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/

**Automated browser harness:** `tools/browser_release_smoke.py` (Playwright Chromium).  
**CI gate:** `.github/workflows/pr-validation.yml`; the published-site validation in `.github/workflows/pages.yml` runs after deployment.  
**WASM engine test:** `tools/check_browser_wasm.mjs` exercises source routing, collections, provenance, dictionary, and chat in actual Pyodide, not in a simulated Python environment.

## 1. Prerequisites

From the root of a fresh checkout or PR branch:

- Python 3.12+, Node.js 24, and a Chromium/Google Chrome executable for headless Playwright.
- `python -m pip install "playwright==1.58.0"`. In a local environment without Google Chrome, also run `python -m playwright install chromium` (and install its OS dependencies if requested).
- Internet access to the live GitHub Pages site and to the pinned Pyodide release **during build**. The engine itself has no required network at query time.
- A pristine, **separate test browser context**; never use an individual's actual browser profile, cookies, or IndexedDB.

The GitHub Actions runner uses headless Google Chrome when available, with a Playwright Chromium fallback. The harness requires that the embedded app has initialized and populated the corpus selector before it starts assertions; loading the HTML alone is **not** a pass.

## 2. Run the PR premerge browser gate

Fetch the pinned Pyodide tarball and generate the candidate app exactly as the release pipeline does:

```sh
python -m unittest tests.test_integrity_hunt tests.test_record tests.test_ledger tests.test_literal_evidence tests.test_answer_reliability tests.test_answer_support -q
python -m unittest discover -s tests -q
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
node crawler/test_worker.mjs

curl --fail --location --retry 2 \
  https://github.com/pyodide/pyodide/releases/download/314.0.7/pyodide-core-314.0.7.tar.bz2 \
  --output /tmp/mplpb-pyodide-core.tar.bz2
python tools/build_browser_runtime.py \
  --core-archive /tmp/mplpb-pyodide-core.tar.bz2 --output dist/index.html
mkdir -p /tmp/mplpb-pyodide
tar -xjf /tmp/mplpb-pyodide-core.tar.bz2 -C /tmp/mplpb-pyodide
node tools/check_browser_wasm.mjs /tmp/mplpb-pyodide/pyodide dist/index.html

python -m pip install "playwright==1.58.0"
python tools/browser_release_smoke.py \
  --live-url https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/ \
  --preview-dir dist
```

The `tar` distribution must extract to `/tmp/mplpb-pyodide/pyodide`; don't invent a different location without changing the command.

**Expected assertions (two fresh browser contexts):**

| Surface | Expected observation |
|---|---|
| Current published site, as a historical baseline | `#workspace` visibly initialized, 3+ corpus options, `window.MPLPB` exposed; strict cone 04 test must **not** show `SUPPORTED ANSWER` |
| Candidate local `dist/index.html` served over `http://127.0.0.1:<random port>/` | Same real browser/Pyodide initialization, with the proposed fixes |
| Candidate Strict Ask | Cone 04 must be refused as unsupported, not answered using cone 6 |
| Candidate Inspect Ask | User sees `CANDIDATE ONLY` or an appropriately qualified result, never a supported-answer claim for inspection |
| Candidate sample button | Explicitly switches Ask to the Inspect setting; it does not pretend the finite answer grammar understands everything |
| Candidate Chat and Explore | Chat, Serious, selection controls and page map are present; no JavaScript page errors |

The harness prints `BROWSER PASS published-live` and `BROWSER PASS candidate-preview` only after its assertions. An exception or missing PASS indicates a failed gate. Don't suppress failures, silently skip live checks, or substitute mock API responses. The premerge test **does not** claim the candidate was already deployed.

## 3. After merge: test the deployed candidate

Wait for `Publish MPLPB browser runtime` to finish its GitHub Pages deployment, then check the **newly live** site itself:

**GitHub Actions detail:** The `build` and `deploy` jobs are separate, isolated runners. A deploy job that invokes `tools/browser_release_smoke.py` must first run `actions/checkout@v4` in that **deploy** job, even when the earlier build job already checked out the repository. Otherwise Python fails with `No such file or directory`; repeating the browser check cannot fix a missing checkout. The published Pages artifact may still deploy successfully while the workflow correctly reports a failing final browser gate.

```sh
python tools/browser_release_smoke.py \
  --live-url https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/ \
  --live-updated
```

This command expects the new `#ask-reader-mode` element and the updated behavior **on the public URL**, and fails if the page still serves the old deployment. It doesn't require a local `dist` directory. GitHub Pages propagation or caching may require waiting and retrying; a failed smoke run must never be reclassified as success.

Record the GitHub Actions URL, commit SHA, deployment URL, run time and failure logs in the change record. If the published site is stale, report **deployment pending**, not **browser passed**. Deployment success is not equivalent to a browser smoke pass.

## 4. Drill the underlying source boundary separately

The two UI modes deliberately have different contracts:

- **Strict Ask / Serious:** A source-backed answer must pass current eligibility, unique ownership, and the supported-statement grammar. A refusal is often correct, even when lexical page candidates exist.
- **Inspect / loose Chat:** Finding saved or eligible pages for inspection does **not** prove they answer the question. Preserve labels, source pins, and collection isolation.
- **Dictionary and thesaurus:** Have separate lexical reference authority. Their entries must not become ledger ownership evidence.
- **Retirement/metadata:** Test `tests/test_integrity_hunt.py` using disposable scratch ledgers; NEVER deliberately corrupt the browser's real saved collections.

For deeper deterministic engine checks, use `tools/check_browser_wasm.mjs` and the Python regressions. Run both before attributing an Ask refusal to the UI.

## 5. Interactive browser examination (not covered by this smoke)

The automated gate does **not** establish the following, and an AI must say they are untested unless it performs them explicitly:

- Actual third-party Wikipedia searches, permissions, API responses, and source captures.
- IndexedDB continuity across a reload and a new browser session; recovery of pre-upgrade saved chats.
- iOS Safari/iPad touch input, accessibility, responsive layout, and slow-device memory pressure.
- Cross-corpus follow-up ambiguity in real user-created collections, including duplicate titles.
- Browser-specific caching, blocked scripts, storage quotas or offline failure modes.

To test these with browser automation or manual device testing: create disposable collections, use synthetic source text, verify the displayed source ID/hash/scope on each selection, switch loose/Serious/Strict/Inspect, reload and verify persistence, then explicitly clean only the test collections. For real Wikipedia acquisition, mark it **external network test** and keep it separate from offline source-only contract tests.

## 6. What to report

Include these five facts in a bug report or AI assessment:

1. Exact Git commit SHA and whether testing was against live GitHub Pages or the PR-built local preview.
2. Browser/channel/version and whether real Pyodide initialized.
3. Commands, query, selected collection, delivery profile, and mode.
4. Expected versus actual UI text, reader kind, source/identity pin, and any console/page errors.
5. Proof: completed workflow URL, exit status, traces/screenshots where available, plus which checks were **not** performed.

Do not say **green** until the *same commit* passes the full Python suite, JavaScript/API checks, WASM integration, and actual Chromium UI checks. Do not call the live deployment verified before the postdeploy run passes. Never edit source hashes, fixed historical benchmark outputs, or logs solely to make a test pass.

## Thespian multi-agent testing method

**Thespian** is Mitchell D. McPhetridge's method for running tests with AI agents in separate roles. One agent asks, one answers, and one evaluates. A fourth agent can write the role instructions and coordinate however many agents the test needs. The human sets the goal and decides how to handle disputes.

The local document workflow in [PR #93](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/93) provided the example. The product agent reported its starting commit, files, existing fixtures, and launch steps. A separate evaluator was asked to prepare fresh documents, questions, citations, and refusal cases, then run a pinned baseline in a separate checkout. The product agent could keep building while the evaluator prepared the baseline. The paired test plan pinned `c1e2100` and `f225d14` and specified the same pasted source, source label, questions, and delivery profile. Local file upload and import without a URL were defined as candidate-only checks.

For a blind test, use **three agents** as the asker, answerer, and evaluator. Use **four** to give instruction writing and coordination to a separate agent. Add agent slots only for a specific job, such as operating a second browser or independently adjudicating contested cases. Count the product builder separately when implementation is also underway.

| Role | Access and deliverable |
|---|---|
| Coordinator | Takes the human's test goal and agent count. Writes a short prompt per role, names who gets each artifact, and asks the product lead for commit, ownership, existing test coverage, and launch instructions. Tracks the pins, handoffs, and run status. |
| Asker | Creates fresh synthetic documents and questions. Freezes a separate key with expected outcomes, supporting passages, and any missing evidence before running the suite. Gives the answerer only the sources, prompts, and run instructions. |
| Answerer | Runs MPLPB through the normal interface and records its answer, citations, and refusal or partial result as displayed. If the aim is to test an AI's own answers, specify that in the brief and record that output separately. |
| Evaluator | Scores the submitted results against the frozen key after the answerer finishes. Checks the original eligible passages and source pins. Records unsupported answers, missed supported answers, correct partials, and correct refusals separately. Flags unclear expectations for human review. |

### Copyable starter prompt

> Set up a **Thespian** test of **[feature or question class]** with **[number of agents]**. My success criteria are **[expected answers, citations, refusals, and any workflow checks]**. Write a prompt for each role and say what it may see, what it must return, and who receives it. With three agents, have the asker draft the instructions and keep the key. With four or more, assign a separate coordinator and give every extra agent a named job. If there is a product lead, ask for the starting commit, owned files and issues, existing tests, and exact launch steps. Freeze fresh synthetic sources, questions, and grading rules before the baseline. Give the answerer the sources and questions. Send the key directly to the evaluator after the answerer submits. Replay the same inputs and settings against each pinned revision in a separate clean context. Exercise candidate-only steps separately. Report the commits, counts per outcome, citations, failures, and steps that did not run. Flag disagreements between the evidence and the key for human review.

Use separate conversations or access-controlled files for the key. If a shared workspace exposes it to the answerer, report that the run was unblinded. Preserve actual baseline and candidate outputs, including failures. Use fresh cases after changing a rule based on the first set. Record role separation as an AI-assisted evaluation and track independent human semantic review separately. Use only fixtures approved for the run in any shared report.

## Additional 2026-10-21 audit

`python -m tools.browser_audit_20261021 --preview-dir dist --output browser-results`
runs disposable real-browser checks for supplied-source import, transcript export,
source citation preservation, saved-session reload/new-page continuity, offline
querying, denied-by-default network calls, responsive viewport dimensions, explicit
Wikipedia acquisition, and deliberate session-save corruption. Online failures are
recorded separately. With `--live-url URL`, it also examines the deployed baseline;
known historical error-code behavior is recorded without relaxing the candidate's
`NETWORK_DISABLED` assertion. This does not test actual iPad Safari or certify
accessibility, long-term storage retention, or malicious arbitrary JavaScript.

> Update 2026-11-16: The [public 52-case evidence suite](PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.
