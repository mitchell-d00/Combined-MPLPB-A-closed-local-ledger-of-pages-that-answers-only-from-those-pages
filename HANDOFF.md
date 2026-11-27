# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `515a919df40996e9d1d521dd50474b832a1a599c` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `eaf38515c16b852a1903bbe6c512b09e34b2cb429af73834d598868ef7b9951e`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Make the product / project / evidence boundaries explicit as a bounded organization task.

PR #107 established navigation. Now document and verify what belongs to each responsibility:

- Product: supported runtime, CLI, browser/desktop delivery, installation requirements and concise user instructions.
- Project / Experimental Lab: development tools, experimental candidates, methodology and reusable test machinery.
- Evidence / Data: corpora, fixtures, frozen packets, results, failures and historical records, with explicit publication and custody rules.

Start with a dependency and packaging map against the actual repository. Identify what users need to run MPLPB, what developers need to change it, and what reviewers need to inspect its evidence. Record shared dependencies rather than forcing files into arbitrary categories.

Use the existing three entry pages, component map and Test Index. Explain that these are responsibility boundaries within one repository; distinguish completed separation from proposed work.

Define a minimal product distribution manifest. Check the existing build process against it and identify which research or evidence material is included unnecessarily. If a packaging change is straightforward, implement it and verify installation and the documented quick start from a clean environment.

Preserve frozen evidence paths, IDs, hashes and historical records. Prefer manifests and links before moving files. Keep private payloads and held keys outside public distributions; public inventories may identify their custody and availability without including their contents.

Keep the root README concise and give regular users three obvious routes: use MPLPB, develop MPLPB, inspect the evidence. Explain document input requirements directly.

Do not create another framework or new test suite. Use existing packaging and navigation checks. Keep this task separate from reader changes, and preserve every Cryptid and Egyptian-series checkpoint.

Push the concrete map, any verified packaging improvement, and an updated HANDOFF. Report what is physically separated, what is separated through packaging or navigation, and what remains intertwined. Existing publication authorization continues; retain the open incident and release requirements.

### Implemented scope

- Map responsibilities and real shared dependencies from clean main 515a919. Put the existing use, develop and evidence entry points first and state supported source input directly.
- Constrain native download staging to exactly one wheel and its three runtime module roots plus metadata. Reuse the clean-environment README verifier in Pages. Exclude offline Wiki reports and study notes from the standalone browser payload. Preserve every tracked evidence path and native reader byte.

### Validation recorded

- Clean-environment quick start passed 11/11 on the candidate wheel, with exact citation, partial, owner and conflict checks. A second staged wheel and non-runtime package file were rejected.
- Browser manifest removed exactly 21 offline Wiki files and 571,830 standalone HTML bytes; every retained file digest, core Pyodide asset and worker matched the baseline comparison. Existing real WebAssembly checks passed, including the configured Wiki corpus.
- Existing documentation audit passed on 1,374 classified documents and 66 evaluation families. Infrastructure check passed. Clean branch excludes the introducing incident commit.
- The existing real Chromium candidate preview passed after enabling loopback and materializing the existing researcher fixture. First local setup failures are recorded separately in the package receipt.

### Limitations and blocked checks

- Desktop still uses the full source distribution. Browser retains shared UI tools, configured public demo/capture data and resources. Scope and packaging separation are separate from physical file moves.
- Release is subject to protected checks and post-deployment verification. PR106 reader checkpoints, original unavailable cases, independent and human NOT_RUN labels, and Git-history incident remain on their separate track.

### Next steps

- Run exact-head protected checks for the clean packaging PR. Deploy and verify the compact download and browser only after an eligible merge. No reader candidate ancestry is part of this delivery.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
