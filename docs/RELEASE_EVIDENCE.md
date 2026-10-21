> **2026-10-21 audit:** See the [current retest, defects, repairs and evidence status](SYSTEM_AUDIT_2026-10-21.md). Earlier dated results below remain historical; the October 19 SQuAD correction is included in the retest.

# Candidate release evidence and required repository settings

Status: engineering release procedure, not production certification. Added 2026-10-20.

## What is protected by code

The ZIP-first validation workflow packages the exact PR head commit, records the
Git commit/tree SHA, verifies the source ZIP checksum, and runs the extracted
code's Python, JavaScript, actual WebAssembly and real-browser tests. Only after
those gates pass, it copies the exact Chromium-tested candidate
`dist/index.html` into the downloadable CI artifact as
`mplpb-candidate-preview.html`. The workflow then runs
`tools/release_evidence.py create` followed by `verify`.

The resulting `release-evidence.json` includes:
- the full packaged candidate commit and tree SHA;
- SHA-256 and byte count for `mplpb-repository.zip`;
- SHA-256 and byte count for `mplpb-candidate-preview.html`;
- SHA-256 for the validation report and an explicit list of required checks;
- status `candidate_checks_passed_not_deployed`, never 'production verified.'

A hash checks byte consistency, not source authorship, truth, signatures,
browser safety, or that the current live deployment has the tested bytes.
Anyone who controls the artifact and its manifest can replace both. Fetch
artifacts from the trusted GitHub Actions run for the expected repository and
commit. The SHA-256s are not independently signed attestations.

`tools/release_evidence.py verify --archive-dir DIR --expected-commit SHA`
recalculates the hashes and checks the exact SHA, report gate labels, and
manifest. Tampering with an individual downloaded artifact is detected; a
forged set of artifacts is outside this manifest's trust boundary.

## Repository settings that an owner must enforce

GitHub workflow files do **not** configure branch protection. As inspected
on 2026-10-20, the active repository ruleset `Bear` restricts deletion and
non-fast-forward changes but does not require passing checks; `main` reports
traditional protection disabled. An administrator must configure an active
branch ruleset targeting `main` that:

1. Requires a pull request before merge and limits bypasses.
2. Requires the exact-head `archive-first` job in
   `Verify zipped MPLPB source before merge` to succeed. Select the **actual**
   context reported by GitHub Actions rather than an invented display string.
3. Requires `regression` from `Validate proposed MPLPB changes` to succeed.
4. Requires PR checks to be current for the revision merged, with review
   requirements appropriate to the contributors.
5. For any manual merge/deployment path, forbids describing a release as
   verified until the *deployed* Pages workflow and live Chromium smoke pass.

Required check contexts can be chosen only after they have appeared on a PR.
Confirm the branch ruleset actually targets `main`; a ruleset with no selected
ref conditions may not protect it. Verify enforcement with a disposable PR
that has a deliberately failed required check. Never bypass the gate just to ship.

The available code-writing GitHub connection cannot configure repository
settings; changes to these settings must be made by a repository administrator
or a separately authorized settings tool. Documentation alone does not enforce
them.

## Validation and recovery

`python -m unittest tests.test_release_evidence tests.test_release_answer_contract -v`

`python -m unittest discover -s tests -q`

Open the ZIP-first PR Actions run. Download its output, verify both the inner
ZIP SHA-256 and `release-evidence.json`, and inspect the report. A failed
workflow may still produce an investigation artifact from `if: always()`;
that artifact is never an approved release.

A passing PR candidate is **not** a live deployment. After the merge, require
`Publish MPLPB browser runtime` and its `--live-updated` Chromium step to pass
against the public URL. Record the deployed SHA and run URL separately. Existing
revert/recovery instructions in `ROLLBACK.md` remain in force; this workflow
does not migrate, repair, or overwrite stored browser captures.

## Compatibility and evidence authority

No changes in this hardening change set are intended for ledger decisions,
source hashes, capture format, engine ownership, or historical transcripts.
`mplpb-combined ask` and `python -m mplpb_answers ask` are supported-answer
entry points. `mplpb-combined candidates` and
`python -m mplpb_combined ask` are **legacy lexical inspection**, not verified
factual answer entry points. A candidate, even a unique lexical match, cannot
be promoted to a supported answer by a caller or UI. Tests explicitly enforce
that distinction and competing-source ambiguity.

This work does not replace independent evaluation, browser retention testing,
security review, or the production threat model. See
`PRODUCTION_THREAT_MODEL.md`, `ZIP_FIRST_RELEASE_TESTING.md`, and
`BROWSER_TESTING_FOR_AGENTS.md`.
