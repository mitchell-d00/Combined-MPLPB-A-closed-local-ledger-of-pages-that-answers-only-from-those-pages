# Walk-back and rollback notes

This change adds the separate-source provenance gate, six topic corpora and their frozen probes, supplied papers, an upload review, and a dated documentation archive. The existing single-owner `ask` command remains available.

## Walk back behavior without reverting files

Use `python3 -m mplpb_combined ask <root> "<question>"` to retain the original majority-scope/prose-containment ownership and refusal rule. Stop the local query bench with Ctrl-C. The gate and bench do not modify a selected source corpus.

The gate returns lexical source bundles, not a synthesized answer. A game source and a budget source do not establish a historical D&D budget. Declared authorship and intact hashes are not verified identity or truth. The gate's 29 tests and the 90 topic probes are controlled regression fixtures; they do not establish independent validation.

## Revert the complete addition on main

The last main commit before this addition is:

`6734fa4a74a2886ab335d30559d07e65d04d5aeb`

Find the published addition by its exact commit subject:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git log --oneline --grep="Add provenance gate, topic corpora, papers and rollback notes" -n 1
```

After reviewing the shown commit, substitute its SHA below:

```bash
git revert <addition-commit-sha>
python3 -m unittest discover -s tests -t .
git push origin main
```

This creates a new reversal commit and preserves shared history. Resolve any conflicts against subsequent changes before pushing; do not reset or force-push main. The original baseline had 122 tests. Later unrelated changes may alter that count.

The revert removes files introduced by this addition, including the copied papers and archive on the branch, and restores the prior CLI and README changes. Git history retains those files. Downloaded kits, other working copies, published caches, and already delivered source text are unaffected.

## Restore after a rollback

Review the reversal commit, then use `git revert <reversal-commit-sha>`, run the tests, and push normally. The addition was verified with 151 tests and live local-interface checks for all five scenarios. Paper bytes are pinned by `papers/manifest.json`; pre-gate documentation by its dated manifest.

See [the gate specification](PROVENANCE_GATE.md), [upload review](UPLOAD_REVIEW.md), and [past documentation](past-documentation/README.md) for scope and preserved failure results.

## Walk back the supersession policy fix only

The last main commit before this fix is `c665337492a4aa5c3619c57c439a0583732c68bd`. Find the subsequent commit with subject `Enforce supersession restoration and derivative serving policy`, then run `git revert <policy-fix-commit-sha>`, run the tests, and push normally. Do not revert the earlier provenance-gate addition to undo only this fix.

Reverting restores the earlier serving and write behavior, including its permissive handling of invalid successor pages, stale derivatives, and the inability to write a restoration pinning a withdrawn head. Existing source files written after publication remain in their corpora; inspect them with the restored reader before relying on rollback behavior. Original probe files remain frozen. The policy fix passes 165 tests; that is regression evidence, not independent validation.
