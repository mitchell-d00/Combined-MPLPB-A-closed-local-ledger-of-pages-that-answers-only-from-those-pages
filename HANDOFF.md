# Repository handoff

Last reviewed: 2026-11-24.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `16a1f9f883bd5c1d6e366cb139272a997a41765a` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `5b54b37da064bf341eeea927e07514cb42ba41c3129bd07c06449c7a5c371b73`.

## Latest user update instructions

Continue the public MPLPB Pole training loop on pin 16a1f9f883bd5c1d6e366cb139272a997a41765a.

Prior results (keep frozen):
- BT-Erratum: 1/1 complete. Zero false-supported bridges.
- Both tested DHS relations: complete development proofs.
- Focus-12: 0/12 complete. Two partials, ten abstentions. 20/20 controls preserved.
- Polybius-Extend (fresh FRUS): native discovery 4/4 after whitespace projection. Strict Ask 0/4 complete. 4/4 controls withheld. Zero false-supported bridges.
- Cap diagnostics and Komnene 22/22 mapping checks reproduced. Outside scoring, independent historical accuracy, and native OOCC remain NOT_RUN.

Goal: force a decision on the four fresh FRUS cases that already have both anchors available. Freeze those four cases (plus their existing negative controls) before scoring. Do not add new cases. Do not raise scan or phrase caps. Preserve all previously closed results. Do not claim independent historical accuracy or native OOCC.

Run one named test:

1. FRUS-Boundary
   - Isolate the four fresh FRUS cases where native discovery now finds all required anchors after publisher-layout whitespace folding.
   - Write and freeze one candidate rule that either:
     (a) forms a supported bridge from the ordinary prose already present in those documents, with exact witnesses, unique resolution, chronological order where applicable, and existing budget checks, or
     (b) correctly withholds because a necessary link cannot be established under the current witness and budget rules.
   - Score discovery and Strict Ask separately.
   - Keep the existing negative controls.
   - Zero false-supported bridges allowed.
   - Report complete, partial, or correct withhold for each case, and the exact reason for any remaining withhold.

After the test:
- Write the rule that was added (or the explicit withhold condition).
- Update the open-items README with before/after counts for these four cases only.
- Leave the original 12 focus cases, the scan/phrase limits, outside scoring, independent historical accuracy, and native OOCC marked NOT_RUN or open as they currently stand.
- Commit the frozen cases, results, and rule under a new public pin.

Return the result table for FRUS-Boundary, the rule text, the updated open-item list, the new commit hash, and the archive SHA-256.

## Implemented scope

- Refreeze the four FRUS comparisons and four existing controls against the requested baseline.
- Use exact source-byte, projected-span and native evidence readbacks to test the explicit withhold condition.

## Validation recorded

- All four comparisons retained both discovery anchors. All eight anchors had unique projected locations and valid raw source coordinates.
- Strict Ask stayed at 0/4 complete and zero partials with four answerable abstentions. All four controls correctly withheld. Zero false-supported bridges.
- The native runtime and case readbacks matched the prior rendered-layout run exactly. Existing source proof and limit code stayed byte-identical.

## Limitations and blocked checks

- The withhold condition is an evaluation boundary over the current native checker. The four answerable reference labels remain misses.
- The operator bundle pins two permission-reprinted originals by URL and hash and uses the previously retained local captures for exact replay.
- Independent historical accuracy, outside-custodian scoring, independent semantic adjudication and native OOCC remain NOT_RUN.

## Next steps

- The open work is certification of independently attributed assertions and their comparison across eligible originals.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
