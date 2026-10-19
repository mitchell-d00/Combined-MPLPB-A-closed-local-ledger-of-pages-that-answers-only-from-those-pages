# Monster release and rollback runbook (2026-10-19)

## Recovery checkpoint

Before merging the Monster and bounded-answer extension, the last verified
main revision was:

- Commit: aeb4896ff177c432d79851baa4ae5a54a81e2c32
- Recovery branch: rollback/pre-monster-2026-10-19
- Earlier successful Pages workflow: 39275301670

The recovery branch is immutable by release procedure, not by GitHub branch
protection. Do not amend or force-push it.

## Checks before the release

- Review PR #8 and its changed-file list. Never treat changed code hashes as
  source tampering or silently rewrite archived captures.
- Run the new pull-request validation workflow: full Python tests, JS API and
  UI transport, crawler fixtures, bounded coverage report and actual WebAssembly.
- Confirm invalid/missing/ambiguous questions are not converted to supported
  answers, and the previously inspected external questions are development only.
- Confirm helper name and Reason Mode settings change display only.
- Check save/resume, transcript pins, exported chats and old-capture compatibility.

## How to roll back after a merge

Preferred method: create a **new revert commit**. Never force-reset main, because
that destroys the visible merge history and can obscure published references.

1. Identify the exact merge commit with:
   git log --first-parent --oneline main
2. Create a revert branch:
   git checkout main && git pull --ff-only
   git checkout -b rollback/revert-monster
3. If PR #8 was merged with a merge commit:
   git revert -m 1 <MERGE_COMMIT_SHA>
   For a squash merge, instead run:
   git revert <SQUASH_COMMIT_SHA>
4. Review the revert and run all checks, open a PR into main and merge it.
5. GitHub Pages will redeploy the known prior implementation after the revert.
   Confirm the generated site, query contract, and browser state after deployment.

Emergency recovery when the commit graph is difficult to revert: compare the
recovery branch to main and restore the prior files in a forward commit, keeping
the deployed build and archived evidence separately tracked.

## Browser storage and pin compatibility

GitHub Pages is a static single-page delivery, not a remote query database.
Pre-existing IndexedDB records remain local to the visitor/browser profile.
Release changes can invalidate capture code pins even when page bytes are intact.
A compatibility warning is **not** permission to reseal or edit historical pins.
Export important transcripts first; retain captures for offline forensic review.

Rollback of JavaScript/Python code does not erase already-imported visitor data.
If an old capture is refused, instruct the user to re-import under the reviewed
runtime rather than rewriting old manifests.

## Deployment verification

The existing main-branch Pages workflow runs a full test suite and WebAssembly
smoke before deploy. A failed run should not be described as published.
Verify Pages run is green, the URL serves the new build, a previously supported
question stays supported, a wrong-entity question stays refused, Monster settings
persist on reload, Reason Mode toggles only trace visibility, and saved chat
resumes. If any essential invariant fails, initiate the revert sequence above.
