# Repository handoff

Last reviewed: 2026-11-27.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `5dfa6b7316c19b8d993c18aaad7774467fd68ec9` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `fb49011c45ac3cc24d09860b3a0b1483f7ae9421a64e30fb9b0300942f421cd9`.

## Betty report for Al

Run the Betty implementation step first, then the Al review step in a separate chat. Both inspect the repository and the public API manifest, confirm their step, then read the last Betty report on the newest PR by creation time. A specific PR link selects that PR. The maintainer pastes Al’s response and direction to Betty, who tests and updates that PR. Resume from the last applied state after a pause.

### Latest user update instructions

Continue rebuilding from the recorded seeds and pinned generator revision, including the original parameters and source-state settings. Compare regenerated inputs and keys against the retained hashes or seals. Exact matches restore those cases to the replay inventory. Record the regeneration receipt and run them under their original IDs and expectations. If any bytes differ or cannot be verified, label that reconstruction separately. Keep original execution statuses unchanged until the restored cases actually run. Revise the proposed retirement list after this check; retire only what remains unrecoverable.

### Implemented scope

- Freeze six development and six fresh cases per set, each with three supported targets and three contrasts. Use the unchanged Cryptid v5 isolation runner.
- Seshat binds an exact reporter and embedded writer before resolving an unambiguous reported object. The printed recorder remains a separate source role.
- Anubis independently binds explicit denial of a report and denial inside the reported writing claim. A missing scoped witness withholds.
- Horus binds an exact if-clause and the instruction or intention modality, or routes the explicit conditions-of-permission question to the existing policy proof. No condition fulfillment or execution authority is inferred.
- Route the bounded subject-before-modal permission request through the existing permission proof. The first Horus score and archive remain retained.
- Prepare the inactive PR110 narrow diagnostic compatibility proposal. Keep active gates and reader bytes unchanged.
- Freeze the full reproducible inventory: 55 registry cohorts, 248 original D% cases via verified original seals, BB, and the overlapping 832 public preservation contracts.
- Restore the original 444-case fully enumerated primary packet to the Cryptid replay inventory. Freeze the exact reconstitution and keep evaluator keys out of the hosted worker and public artifacts.

### Validation recorded

- Remote main is a442c8f0. No Seshat branch or worktree was found. The initial stage diagnosis and all six freezes precede changes to the reader.
- The isolated released development baseline had 9/9 target witnesses discovered, 0/9 targets complete and 9/9 controls withheld, zero unsupported claims or execution failures. The baseline archive and per-set first scores are retained.
- The five existing source-claim, policy, attribution and report suites passed after applying the ordered native changes.
- Isolated intermediate runs preserve the ordered gains: Seshat 3/3 at its stage, Anubis 3/3 at its stage, and first Horus 2/3. All matched controls withheld. Horus permission missed because the embedded question places the subject before the modal.
- The cumulative development pin 426791113 scored 3/3 targets and 3/3 withholds in each set. Its native scoped ZIP matched local and hosted archive bytes. Both readers now run the three fresh arms together.
- Frozen fresh compared the released and cumulative readers once per case. Seshat, Anubis and Horus each moved from 0/3 to 3/3 with 3/3 controls withheld. Zero useful partials, unsupported claims, lost valid targets or execution failures. No fresh-informed repair.
- Capability gate 52/52, public preservation 832/832, BB 900 exact positives and citations and 200 exact withholds. The untouched retained exact check scored 87/96. Readback shows only diagnostic changes on nine unchanged abstentions. All 46 prior claim-bearing contracts matched.
- Raw readback verified 96/96 executions, 87 exact contracts, 46 exact prior claim-bearing contracts and only the nine listed diagnostic changes. Direct source and presentation consumer probes recorded. The prior documentation check found two frozen metadata files not classified; register their unaltered byte hashes.
- All seven registry groups completed. The D% first hosted job stopped at the archive layout assertion before any D% worker ran. Preserve the failure. Retry only the two original public D% packets, staging seal-listed public members with exact original fingerprints from the legacy archives. No evaluator member reaches the worker or the new artifact.
- The primary rebuild matched all 962 archived public files including the seal, as well as the original key, dice, pairing, generator, runner, worker and scorer fingerprints. The 128 other exposed development inputs match their public seals, but no matching original keys were recovered.
- The first two D% replay attempts stopped in setup before any reader ran. The second had valid public packet bytes but lacked the checkout identity D% records. Restore the original host checkout setup while keeping the Bubblewrap worker mounts unchanged.
- The two-lane public 832 job completed. BB matched 900 original positives and citations and 200 withholds per reader. The seven registry groups scored 899 exact contracts, 18 new original-key passes, and 24 diagnostic-only abstention differences across 941 paired memberships.

### Limitations and blocked checks

- Fresh packets and scoring keys stay in separate local custody. Preparation and scoring are same-operator. Independent/human measures NOT_RUN. Original 17 checks incomplete, 100 held cases NOT_RUN and historical publication incident separately OPEN.
- Held: unchanged 96-case exact comparator failed on nine refusal diagnostic differences. An automatic review rejected the proposed preservation workflow and acceptance change. The original acceptance script was run unchanged. Candidate and raw evidence are pinned. The live reader remains the released Thoth pin a442c8f0.
- Archive incidence remains open separately. The 17 original private checks remain incomplete and the original 36 routing and 64 cross-family held cases remain NOT_RUN. The original 128 other exposed development cases have verified input bytes but no verified original keys. No historical status changes from the primary rebuild.

### Next steps

- Replay and privately score the 444 exact restored primary cases and the two unchanged D% draws using the original scorer, then publish verified receipts and update the PR report. Diagnostic compatibility remains inactive.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
