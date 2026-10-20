# ZIP-first release testing for humans and AI agents

This is the release order for Combined MPLPB. **Test the artifact you intend to ship**, not merely the Git checkout that created it. GitHub Actions is the execution environment; the ZIP and report are downloadable artifacts from its completed run.

## Six gates, in order

1. **Freeze the candidate revision.** Record its full `git rev-parse HEAD` commit and tree hashes. Keep all changes on a feature branch and open a PR. Do not modify `main` until the candidate passes.
2. **Make the repo ZIP.** In CI, `git archive --format=zip --output="$RUNNER_TEMP/mplpb-zipped/mplpb-repository.zip" HEAD` includes the source tree from exactly that commit, not untracked caches or a partly modified workspace. Write `commit.sha`, `tree.sha`, and `mplpb-repository.zip.sha256` alongside it.
3. **Inspect and extract the ZIP.** Require `unzip -tq` to pass, then extract to a new isolated `$RUNNER_TEMP/mplpb-unpacked` directory. All test commands **must change directory into that extraction** and use the files there. If a test edits a source file or the archive checksum changes, rebuild and restart the process.
4. **Test the extracted content completely.** Execute adversarial regression tests, the full Python suite, JavaScript API/transport/crawler checks, and actual pinned Pyodide/WebAssembly integration. Build `dist/index.html` from the extracted copy only.
5. **Browser-test BOTH contexts.** Use real Playwright Chromium, not a simulated DOM. First test the **currently deployed live GitHub Pages site as a baseline** in a fresh isolated browser context. Second, host the ZIP-built `dist/` on temporary localhost and use another isolated Chromium context to test the proposed behavior. Both must initialize their embedded Python engine. The running code under test and the historical published site are different until merge.
6. **Merge, deploy, and browser-test live again.** Merge to `main` only after the ZIP-validation job has completed **successfully for that exact PR head SHA**. GitHub Pages then runs its own complete build, deploys the new site, and runs `tools/browser_release_smoke.py --live-updated` against the **actual public URL**. Do not call the release verified until this postdeployment check passes.

## Download the evidence

Open GitHub Actions for the completed `Verify zipped MPLPB source before merge` PR workflow. The **Artifacts** section contains:

- `mplpb-repository.zip` — the actual tested source ZIP.
- `mplpb-repository.zip.sha256` — content checksum.
- `commit.sha` and `tree.sha` — candidate identity.
- `validation-report.txt` — gate results written only after every test and browser check succeeds.
- `mplpb-candidate-preview.html` — the exact ZIP-built HTML run through candidate Chromium smoke.
- `release-evidence.json` — exact candidate commit/tree, tested ZIP and preview hashes, report hash and passed gate labels.

GitHub wraps these files in its own downloadable Actions artifact archive, which is not the same as the inner tested repository ZIP. Extract the outer wrapper, then verify the inner ZIP's SHA-256 against `mplpb-repository.zip.sha256` before using it. Artifacts are retained for 30 days by the current workflow.

The workflow creates and verifies the evidence manifest **after** all test gates pass;
`release-evidence.json` always says `candidate_checks_passed_not_deployed`.
A candidate manifest is not a signed provenance attestation or post-deploy evidence.
An owner must separately require the `archive-first` and `regression` GitHub checks
on `main` in repository branch rulesets; workflow text alone cannot prevent bypass.
See [release evidence and branch settings](RELEASE_EVIDENCE.md).

**Important:** An artifact produced by `if: always()` from a failed run is for investigation only. It is **not validated for release**. The summary report exists only after all tests complete.

## Exact CI and local commands

The authoritative executable pipeline is `.github/workflows/zip-release-validation.yml`. If you have a local clone and internet access, its main steps are:

```sh
mkdir -p /tmp/mplpb-zip /tmp/mplpb-extract
git rev-parse HEAD > /tmp/mplpb-zip/commit.sha
git rev-parse 'HEAD^{tree}' > /tmp/mplpb-zip/tree.sha
git archive --format=zip --output=/tmp/mplpb-zip/mplpb-repository.zip HEAD
cd /tmp/mplpb-zip
sha256sum mplpb-repository.zip > mplpb-repository.zip.sha256
unzip -tq mplpb-repository.zip
unzip -q mplpb-repository.zip -d /tmp/mplpb-extract
cd /tmp/mplpb-extract
python -m unittest tests.test_integrity_hunt tests.test_record tests.test_ledger tests.test_literal_evidence tests.test_answer_reliability tests.test_answer_support -q
python -m unittest discover -s tests -q
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
node crawler/test_worker.mjs
```

For the Pyodide, browser, and live URL steps, use the workflow itself and [BROWSER_TESTING_FOR_AGENTS.md](BROWSER_TESTING_FOR_AGENTS.md). The runtime tarball is pinned to its published SHA-256 in `tools/build_browser_runtime.py`. Browser automation uses fresh contexts; never overwrite a visitor's IndexedDB.

## What AI agents must not claim

- A green checkout-only test is **not** a green ZIP test.
- A successful HTML build is **not** a working WebAssembly/browser test.
- Opening a URL with an HTTP fetch is **not** clicking and testing the running site.
- A live-site **premerge** pass is a baseline; it does not mean the candidate is already deployed.
- An archive ZIP created **after testing** is not automatically the tested ZIP.
- Merging before the tested SHA is green defeats the gate.
- A successful Pages upload, by itself, is **not** a passing postdeployment Chromium smoke test.
- Scripted smoke testing is limited; manual iPad/Safari, real network Wikipedia captures, and long-term IndexedDB upgrades remain separate checks.

## Related files

- `.github/workflows/zip-release-validation.yml` — ZIP-first premerge release gate.
- `.github/workflows/pr-validation.yml` — conventional PR regression.
- `.github/workflows/pages.yml` — actual production deployment and postdeploy Chromium smoke.
- `tools/browser_release_smoke.py` — real Chromium interaction against published and candidate pages.
- `tools/check_browser_wasm.mjs` — direct Python engine in the real WebAssembly runtime.
- `docs/BROWSER_TESTING_FOR_AGENTS.md` — detailed browser reproduction guide.

If internet access is unavailable locally, **do not imply** the local ZIP was built or tested; rely on the actual GitHub Actions ZIP artifacts and the recorded checksums and run status.
