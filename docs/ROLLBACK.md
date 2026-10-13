# Rollback and recovery

## Pinned known-good baseline

Before the context behavior update (PR #5), main was:

- Commit: `6a7601b89a927a5cf3445979a512b8f5bf92e0f1`
- Recovery branch: `rollback/pre-context-repairs-2026-10-13`
- Verified live browser build: `a85403e84f9e`
- Successful Pages workflow: `38333994142`

Keep the recovery branch fixed during release cleanup. It preserves source code,
not user saves. Export important sessions before changing versions.

## Local recovery

Keep the current installation and saves intact. In a clone:

```sh
git fetch origin
git worktree add --detach ../mplpb-before-context 6a7601b89a927a5cf3445979a512b8f5bf92e0f1
```

Follow INSTALLATION.md in that separate directory. Use a separate browser profile
for an older browser runtime. Older adapters may reject newer captures; retain
original exports rather than deleting data to force compatibility.

## Deployed recovery

Use a revert commit; do not force-push or destructively reset main.

1. Fetch origin and start a clean recovery branch from `origin/main`.
2. Find PR #5's merge using `git log --first-parent --merges origin/main`.
   Verify its parents and diff. The first parent should be the baseline above
   if no intervening main commits landed before this release.
3. Run `git revert -m 1 <verified-PR-5-merge-commit>` on the recovery branch.
   Review conflicts and dependencies of later work; do not overwrite unrelated
   changes with the entire baseline tree.
4. Run `python -m unittest discover -s tests -q`,
   `python -m tools.evaluate_context_matrix --output rollback-context.json`,
   and `python -m tools.smoke_conversation_architecture`.
5. Review and merge the recovery PR. Confirm both Pages build and deploy succeed;
   verify live module bytes as well as the build footer.

Rebuilding reverted source can produce a different build identifier because
metadata changed. Deployment does not roll back or erase local/browser user data.
Restore the feature later by reverting the recovery commit after testing.
