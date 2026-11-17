# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `473048dfa23d07439fef5f636e287b23b50b1e27` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `cdd1168805fc6281678838605b0f284d2fe78a54993ef27ffedd8062a4087d29`.

## Latest user update instructions

The improvements should close the residual gaps the comparative experiments and Gelhaus’s critique already identified, without relaxing the closed-ledger guarantees that make it strong.
Precise refusal diagnostics; distinct event identity and time-scoped correction; evidence-gated candidate relations; independent operational receipts; external verification hooks for high-stakes claims.
Public, version-pinned reproducibility package; exact-field routing without false pruning; operator-burden metrics; clear non-claims in the runtime.
Do not add open-ended generation, external retrieval that bypasses ownership rules, or automatic promotion of candidates.
The residual limit remains: if the ledger itself contains only a coherent false current page, the system will still return it.

## Implemented scope

- Add refusal categories without changing legacy diagnostic codes or answer proof rules.
- Expose source-only assurance and outside-world confirmation requirement in JSON, CLI and both answer renderers, with fresh declared root counts.
- Extend host-only receipt observations with explicit predecessor-gated operational stages; preserve standalone legacy READ/ACK without allowing chain promotion.
- Add version-pinned source ZIP/extraction regression runner retaining failures and honest unknown cost/accuracy metrics.

## Validation recorded

- Baseline473048d: 63 focused source/answer/scoped-correction/handoff tests passed in4.050s.
- Development: 40 focused answer/scoped tests passed3.754s; 37 boundary/scoped tests passed0.517s. UI script check passed. Two initial category failures corrected; full archive validation pending.

## Limitations and blocked checks

- Source support cannot detect a coherent false original; declared roots do not authenticate testimony or independence.
- Host observations are not independent external-world proof; full independent receipt adapters remain deployment-specific.
- No exact legacy887-test revision or external critique text established in inspected documentation. Independent historical review and semantic accuracy remain NOT RUN; unknown metrics null.

## Next steps

- Freeze candidate and test extracted archive; record exact results and failures.
- Identify original legacy experiment revision/fixtures before claiming exact887-test reproduction.
- Obtain independently authenticated external observations and independent historical reviews; no auto truth promotion.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
