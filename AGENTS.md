# Repository update and handoff instructions

Read `HANDOFF.md`, `handoff/update.json`, README release requirements, and the applicable source contracts before changing this repository. Preserve frozen sources, questions, labels, reports, delivery restrictions and provenance. User instructions in the current session take precedence over this file.

For every implementation/update, and before providing a source ZIP or other delivery:

1. Update `handoff/update.json` from the **latest user update instructions**. Preserve the user's wording in `instruction`; record the implemented scope, validation actually performed, remaining limitations, and concrete next steps. Never claim a check passed before it ran. This file is development coordination, not source-ledger evidence or permission to change imported sources.
2. Stage intended source additions/deletions so the handoff builder sees the complete intended repository. Do not stage personal saves, secrets, caches, generated runtimes or downloaded dependencies.
3. Run `python tools/build_handoff.py`, then `python tools/build_handoff.py --check`. The builder records content hashes, the last instruction, and a human-readable handoff. Regenerate after any further source, test, documentation or update-record change. Commit the handoff and its manifest with the update. The recorded base commit is ancestry; the source inventory digest identifies the actual packaged content without a self-referential commit hash.
4. Freeze and archive a committed candidate; test its extracted content following `docs/ZIP_FIRST_RELEASE_TESTING.md`. Keep tested implementation evidence separate from subsequent evidence-only edits. Run required checks and explicitly report blocked checks. Do not equate source tests or candidate browser checks with deployed-site verification.
5. Include `HANDOFF.md`, `handoff/update.json`, `handoff/manifest.json`, this file, and hidden `.github/` workflows in every full-repository ZIP. Use tracked source packaging, not an indiscriminate directory ZIP. Verify the delivered ZIP and checksum and check its extracted handoff.

`tools/build_release_packages.py` requires a current handoff. The `Repository handoff` Actions workflow checks committed freshness, rebuilds from `handoff/update.json` on every push/PR, and uploads the handoff files as an artifact. It does not invent new instructions, commit changes, publish a site, or modify user sources. A stale committed handoff fails the job even though a rebuilt artifact is retained.
