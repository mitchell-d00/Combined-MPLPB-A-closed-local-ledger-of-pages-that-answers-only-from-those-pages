# Repository handoff

Last reviewed: 2026-11-22.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `ddde79f55d3fcb46dd3a9d5a445e81f6ad3103aa` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `ca4189defa28cda7f6ad47d52825c2aac7f7b20d29dc7f632e404e54b91bd4c6`.

## Latest user update instructions

And others I forgot can you crawl my full repo and put it all into a path like this so I don’t have to describe all the connections of modules projects and mplpb

## Implemented scope

- Expand the package guide into the connection map for source intake, candidate review, strict reading, application interfaces, work coordination and guarded dispatch.
- Link implementation files and workflow paths from the guide, and make it discoverable from the README and documentation index.
- Map the companion testbench, preserved implementations, credited research projects, data packs, and release tooling to their roles.

## Validation recorded

- Traced native CLI entry points, the shared App used by the browser and MCP, the WorkStore dispatch boundary, and pinned B-Tests workflows.
- Verified that the two diagram edge lists refer to declared nodes and that the documented source paths resolve.
- The documentation audit, infrastructure checks, 248 focused Python tests and the JavaScript API test passed.

## Limitations and blocked checks

- This is an implementation and navigation guide. Its diagrams document supported paths through the local system.

## Next steps

- Update the connection map when a supported entry point, storage boundary, or distribution changes.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
