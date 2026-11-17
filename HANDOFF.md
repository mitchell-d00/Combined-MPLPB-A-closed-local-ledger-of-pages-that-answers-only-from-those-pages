# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `4d0f4470adfa88e36b736d78f429ee86d003a925` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `775232e20a040bc8a4837d8cfcdf53e031582a0e5f95eb145adf73c0470b1570`.

## Latest user update instructions

CODEX BUILD PROMPT — MPLPB Historical Reconstruction Engine
Build a working, source-grounded historical reconstruction engine inside the existing Combined MPLPB repository.
Build the actual implementation. Do not merely produce a design document or implementation proposal.
Every accepted source-supported claim must have an inspectable, independently checked evidence path. Every unverified historical interpretation must remain explicitly unverified.

Codex, I want you to take Combined MPLPB to a genuine 9/10 research-engineering standard by making it more capable, accurate, independently verifiable, and easy to use.
Proceed with the implementation and make the strongest measurable progress possible in the available environment. Do not claim a target has been met unless actual results demonstrate it.

Build and test rules then code that resolves source identity and historical truth, but don’t break mplpb, build a crawller set it has basic crawllers in repo

Set rules for historical truth to be entered do synthetic historical truth so the method has a test subject

Summarize what all we are doing and then continue

## Implemented scope

- Extend existing source-unit inspection, complete-context discovery, obligation retrieval and independent documentary kernel for literal causal/temporal/resource/passive assertions and exact wording comparisons.
- Expose a reversible candidate graph and reconstruction CLI using existing source/provenance/reader systems; content-only bounded projection cache never caches serving decisions.
- Extend existing crawler with direct public URL seeds, optional source hashes and explicit byte-versus-event identity boundaries. No deployment or paid search requirement for direct seeds.
- Add capability-gated typed historical-review entries through existing WorkStore; synthetic oracle fixture exercises rules without claiming real historical truth or real independent reviewers.
- Add target accounting after existing human-review/adjudication validation; 200 unseen-question independent evaluation and performance targets remain unmeasured.

## Validation recorded

- Clean merged baseline4d0f4470adfa88e36b736d78f429ee86d003a925:1068 tests passed in376.449 seconds;62 focused tests in14.641 seconds;52 public controls passed.
- Expanded focused run passed147 tests in18.179 seconds before final freeze; both crawler suites passed. Full final archive checks and unchanged historical replay pending.
- Preserved first slow source-unit parsing attempt and failed review-schema/crawler-runtime attempts; repaired bounded lexical tail and existing effective_status field usage.

## Limitations and blocked checks

- Independent human review, adjudication, real historical truth validation and >=200 unseen-question evaluation NOT RUN; proposed targets are not achievements.
- New relation proofs retain partial scope; document/event/person identities, execution from requests, correction scope and OCR quotation ambiguity can remain unresolved.
- Final comparative outcomes and resource costs pending at this source freeze; do not infer historical accuracy from tests or candidates.

## Next steps

- Freeze committed source, test extracted archive, replay all22 unchanged questions using original seals/budgets and audit every accepted certificate against original bytes.
- Retain full successful, failed, partial and unresolved outputs, measure resource costs and report unknown metrics as null.
- Obtain real independent custodians/authors/reviewers and sealed unseen materials before target/rating claims.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
