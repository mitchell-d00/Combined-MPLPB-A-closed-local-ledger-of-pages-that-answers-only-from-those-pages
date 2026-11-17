# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3df2c6e22f0ef454f3ee67b88d43402a42f63443` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5e9f6fd50561fc202f001b72384e12bfa36ce39f7ebb7d2081070670797517f9`.

## Latest user update instructions

The two modes differ only in the edges they emit. Both compare and not-compared must extract the same source-anchored keys, spans, and provisional statuses from the same input. Confirm this with fixtures: same input, both modes, identical nodes, differing only in edges. The retired-page snapshot is truly withheld under the existing reader under all three delivery profiles without modification. Once these two checks pass, freeze the implementation and document the input/output contract for both modes. Do not claim the sorter completes historical reconstruction. Keep every proposed relationship non-authoritative and inspectable.

## Implemented scope

- Implement offline standard-library raw-text sorter with separate extraction, provisional status assignment, comparison and JSON emission.
- Compare appends only review edges; nodes and source anchors identical between modes. Clusters and correction windows remain edge annotations.
- Reversible original UTF-8 byte/character spans, bounded processing, replay verification and prior assessment preservation.
- Explicit new-ledger retired snapshot export through unchanged native ledger; no grammar, gate or answer support changes.

## Validation recorded

- Pre-edit focused baseline:43 tests passed0.839s.
- Final focused sorter and source/boundary tests:67 tests passed1.308s, including24 sorter tests.
- Direct gate test excludes retired snapshot under all profiles; native answers and past as-of answers remain unsupported.
- One stronger exclusion assertion initially expected retired for external; corrected to reflect existing external=no precedence, with no reader changes. Frozen archive regression checks pending.

## Limitations and blocked checks

- Lexical candidates only; no semantic accuracy or historical reconstruction claim.
- No independent semantic review performed; fictional fixtures do not measure original-record answer coverage.
- Serving eligibility is not inferred from raw input headers. Original source policy must be supplied through normal ingestion.
- Bounded algorithmic work, no hard OS timeout; trusted local filesystem required.

## Next steps

- Freeze committed candidate and run archive-extracted regression/public-evidence checks.
- Retain commands, profile refusals and actual resource costs in versioned sorter evidence.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
