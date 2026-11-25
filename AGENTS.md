# Repository update and handoff instructions

Last reviewed: 2026-11-25. See [current status and result-to-test index](docs/CURRENT_STATUS.md). Dates and numeric results in historical validation sections retain their original scope; this review is not a rerun or independent certification.

Package role: [how this part fits Combined MPLPB](docs/PACKAGE_GUIDE.md#delivery-and-packaging). This operational guide covers one delivery or maintenance surface of the combined package.

Read `HANDOFF.md`, `handoff/update.json`, README release requirements, and the applicable source contracts before changing this repository. Preserve frozen sources, questions, labels, reports, delivery restrictions and provenance. User instructions in the current session take precedence over this file.

## TeamBuilding role selection

When the maintainer says **“You are Al”** or **“You are Betty”**, use the
[TeamBuilding role guide](docs/TEAMBUILDING.md). Al reviews public evidence,
challenges conclusions, and drafts the next test prompt. Betty owns the
authorized repository and archive work, including frozen tests, scoring,
commits, and publication. Each push carries a current **Betty report for
Al** in the generated `HANDOFF.md`. Betty also posts the report on each PR
she opens or updates. The maintainer starts Betty first and opens a separate
Al chat after Betty leaves the report. Al first inspects the repository in
depth, then reads the report and PR. The maintainer pastes Al’s response
and their direction to Betty, who runs the authorized tests and updates
the same PR. Keep the live PR report current with the last applied change,
checked head, measured outcomes, and next authorized step. Reconcile a stale
report with `HANDOFF.md` at the actual PR head before continuing.

For every implementation/update, and before providing a source ZIP or other delivery:

1. Update `handoff/update.json` from the **latest user update instructions**. Preserve the user's wording in `instruction`; record the implemented scope, validation actually performed, remaining limitations, and concrete next steps. Never claim a check passed before it ran. This file is development coordination, not source-ledger evidence or permission to change imported sources.
2. Stage intended source additions/deletions so the handoff builder sees the complete intended repository. Do not stage personal saves, secrets, caches, generated runtimes or downloaded dependencies.
3. Run `python tools/build_handoff.py`, then `python tools/build_handoff.py --check`. The builder records content hashes, the last instruction, and a human-readable handoff. Regenerate after any further source, test, documentation or update-record change. Commit the handoff and its manifest with the update. The recorded base commit is ancestry; the source inventory digest identifies the actual packaged content without a self-referential commit hash.
4. Freeze and archive a committed candidate; test its extracted content following `docs/ZIP_FIRST_RELEASE_TESTING.md`. Keep tested implementation evidence separate from subsequent evidence-only edits. Run required checks and explicitly report blocked checks. Do not equate source tests or candidate browser checks with deployed-site verification.
5. Include `HANDOFF.md`, `handoff/update.json`, `handoff/manifest.json`, this file, and hidden `.github/` workflows in every full-repository ZIP. Use tracked source packaging, not an indiscriminate directory ZIP. Verify the delivered ZIP and checksum and check its extracted handoff.

`tools/build_release_packages.py` requires a current handoff. The `Repository handoff` Actions workflow checks committed freshness, rebuilds from `handoff/update.json` on every push/PR, and uploads the handoff files as an artifact. It does not invent new instructions, commit changes, publish a site, or modify user sources. A stale committed handoff fails the job even though a rebuilt artifact is retained.

## Documentation and result maintenance

For every update, review affected operational documentation and record its actual
review date in `docs/documentation.json` and its `Last reviewed:` marker. Classify
new documentation explicitly. Keep dated historical reports, original papers,
licenses, byte-pinned resource documentation and frozen evaluation artifacts unchanged; do not refresh their dates.
Add or update `docs/results.json` and `docs/RESULTS_AND_TESTS.md` for new evaluation
families, linking retained tests and reproduction tools with their measurement
scope. A test link does not establish that a historical metric was rerun.

Run `python -m tools.audit_documentation`; use `--as-of YYYY-MM-DD` when performing
a complete review for that date. Never automatically advance review dates based
on a build clock. Record `reviewed_on` explicitly in `handoff/update.json` for the
reviewed update. The handoff builder preserves that date when CI rebuilds it.

> Update 2026-11-16: The [public 52-case evidence suite](docs/PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](docs/HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.

## General class fixes; never benchmark-specific passing

Implement fixes for a general source-understanding or verification failure class, not individual benchmark instances. Runtime rules must not branch on evaluation case IDs, fixture names, generated actors, frozen answers, dataset labels or a published answer key. Do not add language filters that remove hard generated cases. A higher score alone does not justify a rule.

Before changing a rule, state the general failure mechanism and retain a failing regression using independently worded examples. Add contrasting negatives, changed actors/negation/conditions, source-state and budget controls. Preserve attribution, uncertainty and missing links. Only the native deterministic checker may establish source support after independently rereading currently eligible bytes; extractor classes and feature labels never authorize it.

Freeze generator, private key and baseline before engine changes. Keep every old corpus, question, seal, output and failure unchanged. Analyze failure rates by structural feature with denominators and both answer/refuse outcomes; correlated feature cohorts are diagnostic, not causal proof. Rerun identical frozen inputs after a class change and retain new false support, missed answers and unscored cases. Never relabel failures to improve the score. New unseen batches and actual independent assessment remain separate milestones. Update the handoff so another AI instance can resume from pinned files and rules without relying on private session memory.
