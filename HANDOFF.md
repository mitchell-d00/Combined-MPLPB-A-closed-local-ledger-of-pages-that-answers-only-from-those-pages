# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6a4230399b83ed259bc1aec1bc9c0d02fedc0f75` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `48caebbcb6026071683ef0e98bd4e07f17c470648ad9bf0e06c1bc7b98769f96`.

## Latest user update instructions

, the improvements should close the residual gaps the comparative experiments and Gelhaus’s critique already identified, without relaxing the closed-ledger guarantees that make it strong.
Highest-leverage changes
1.  Precise refusal diagnostics
Separate the current refusal into labeled cases: unsupported question grammar, absent eligible source, known source conflict, insufficient evidence, index exhaustion. The experiments showed that exact-wording and identifier mismatches produced strict FAILs even when the factual answer was correct. Explicit diagnostic codes would make those failures actionable instead of opaque.
2.  Distinct event identity and time-scoped correction
Treat multiple appearances of the same message as distinguishable source occurrences. A later partial correction should update only the specified claim while retaining the original statement, its provenance, and the prior assessment. This directly addresses the coherent-false-original problem: history stays recoverable even when a current page is later shown to be wrong.
3.  Evidence-gated candidate relations
Allow exploratory relation proposals, but keep them explicitly marked as candidates. Missing intermediate evidence must stop the proposed relation; candidates must never appear as deterministic supported answers. This matches the acceptance criteria in Beyond Guarded Retrieval and prevents the system from silently promoting unsupported bridges.
4.  Independent operational receipts
Store, dispatch, delivery, read, acknowledgment, and completion as distinct, evidence-gated transitions. A stored completion statement currently does not independently establish completed work. Making each transition require its own receipt closes that gap without adding generation outside the ledger.
5.  External verification hooks for high-stakes claims
When a current owner is coherent but thin (single root, no contrary page inside the ledger), surface an explicit “outside-world confirmation required” flag rather than a clean return. The paper already states that source integrity, proposition support, and outside-world truth are distinct; making that distinction visible at the interface prevents the “map becomes authority” failure mode you flagged.
Supporting changes that raise the ceiling
•  Public, version-pinned reproducibility package. The B-Tests fixtures and scoring already exist. Packaging them so a third party can re-run the exact 887-test suite plus the boundary probes without private setup would move the evidence from author-authored to independently confirmable.
•  Exact-field routing without false pruning. Improve source location for held-out cases while guaranteeing that contradictory eligible passages are never dropped. Test zero-, one-, and multi-match behavior explicitly.
•  Operator-burden metrics. Report human labeling time, bytes scanned, source-count coverage, and false-bridge rates alongside the existing pass/fail counts. This makes the cost of the stronger guarantees measurable.
•  Clear non-claims in the runtime. Document at the point of answer that MPLPB does not detect a coherent false original lacking internal contradiction, does not authenticate arbitrary testimony, and does not reconstruct unprepared historical events. The comparative paper already draws these lines; surfacing them prevents over-trust.
What not to change
Do not add open-ended generation, external retrieval that bypasses ownership rules, or automatic promotion of candidates. Those would trade the determinism and refusal properties that currently differentiate MPLPB for capabilities it is not designed to provide. The 9+ path is tighter enforcement, clearer diagnostics, recoverable history, and explicit boundaries—not a broader answerer.
The residual limit remains: if the ledger itself contains only a coherent false current page, the system will still return it. The improvements above make that case diagnosable, historically recoverable, and harder to act on without an external check.

## Implemented scope

- Add refusal categories without changing legacy diagnostic codes or answer proof rules.
- Expose source-only assurance and outside-world confirmation requirement in JSON, CLI and both answer renderers, with fresh declared root counts.
- Extend host-only receipt observations with explicit predecessor-gated operational stages; preserve standalone legacy READ/ACK without allowing chain promotion.
- Add version-pinned source ZIP/extraction regression runner retaining failures and honest unknown cost/accuracy metrics.

## Validation recorded

- Baseline473048d:63 focused tests passed4.050s; fresh unchanged public52/52. Existing full1124-test result is retained on byte-equivalent63cea982 runtime, not newly rerun baseline full suite.
- Tested ZIP-extracted6a4230399b83ed259bc1aec1bc9c0d02fedc0f75:1134 tests passed396.640s (process CPU377.961s/wall397.903s),51 focused passed0.589s, public52/52;0/3 authored supported-bridge probes before/after.
- Actual pinned WebAssembly, JavaScript API, browser transport, crawler fixture checks and Chromium candidate smoke/researcher workflow/new confirmation notice passed.
- Six unchanged fictional inputs preserve exact source-byte pins, claims, citations, kinds, support booleans and verification states while adding diagnostics/assurance. Frozen corpora/prior reports unchanged.
- Costs and failed initial diagnostic checks/timing invocation retained in evaluation/closed-ledger-boundaries/2026-11-17; independent semantic review/human effort NOT RUN/null.
- Final evidence-only documentation/infrastructure/handoff audits passed;10 handoff/documentation tests passed0.151s. Tested runtime/tests/tools remain byte-identical to6a42303.

## Limitations and blocked checks

- Source support cannot detect a coherent false original; declared roots do not authenticate testimony or independence.
- Host observations are not independent external-world proof; full independent receipt adapters remain deployment-specific.
- No exact legacy887-test revision or external critique text established in inspected documentation. Independent historical review and semantic accuracy remain NOT RUN; unknown metrics null.

## Next steps

- Identify original legacy experiment revision/fixtures before claiming exact887-test reproduction.
- Obtain independently authenticated operational adapters and independent historical reviews; source integrity/host observations never auto-promote outside-world truth.
- Review and publish local candidate through exact-head archive/release workflow; live deployment was not tested in this update.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
