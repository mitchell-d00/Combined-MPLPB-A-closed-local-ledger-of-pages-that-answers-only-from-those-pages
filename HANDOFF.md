# Repository handoff

Last reviewed: 2026-11-16.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `257e54a51edac272eb6b2441457f38a40485ee4d` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `fb3399fc04b63f9bf411bef87f0d3c00d2ea2e08f4ae21d58658aae15e1a5bfb`.

## Latest user update instructions

MPLPB’s coordinator does not independently check its meaning against the source. Fix this https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages

a contradictory inference can persist as supported_under_scope until someone challenges it. MPLPB’s coordinator does not independently check its meaning against the source

Once you fix it test it then merge it to main

## Implemented scope

- Independently recompute effective claim support against directly pinned source evidence and complete cited bodies. Fail closed outside a finite unconditional status grammar; preserve authored assessments and history.
- Apply source checks to existing claims, handoffs, dependencies and dispatch; contradictory component inference is contested before challenge. Preserve source, frozen evaluation and historical report bytes.
- Add adversarial regressions, update operational documentation and the continuation demo, and merge to main after successful candidate testing and required exact-head CI, as explicitly authorized by the user.

## Validation recorded

- 48 final focused coordinator tests pass, including pre-challenge blocking, legacy supported claims, review bypass, downstream decision blocking, unknown inference chains, partial quotes, negation, opposing statuses and conditional or hypothetical context.
- Updated five-instance demo completes with pre-challenge contested status and final receipt-backed completion. Documentation inventory (230 documents, 26 evaluation families), infrastructure synchronization, UI script, JavaScript API, browser transport and crawler fixture checks pass.
- Full regression and exact committed archive/browser CI validation remain pending at candidate freeze; subsequent results must be recorded separately from this implementation candidate.

## Limitations and blocked checks

- Finite unconditional source-status grammar only; not unrestricted semantic entailment or factual truth. Unsupported language, assumptions and claim chains require rechecking. Full cited source bodies must stay within the grammar; unrecognized surrounding prose requires rechecking.
- Contradiction checks cover cited source bodies, not unrelated or uncited pages. Browser, WebAssembly and release CI checks remain pending.

## Next steps

- Freeze, archive, extract and test this committed candidate; open a PR and require successful archive-first/regression checks for the exact head.
- Merge the tested candidate to main under the latest user authorization, then separately observe deployment and postdeployment browser verification.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
