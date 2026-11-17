# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `bbadcaa9d629b003997d4f780cb218e661cbd54b` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `1639c08a94d1c2f2e945e82661672e05887b1d52eca46799b71edc154e12f93e`.

## Latest user update instructions

Add a local small-language-model frontend strictly subordinated to the existing MPLPB authority rules. Present these five options, then implement Option 5 in full: Constrained Local Narrator. Configuration via MPLPB_NARRATOR_BACKEND=ollama|llamacpp|openai, MPLPB_NARRATOR_MODEL and MPLPB_NARRATOR_BASE_URL. Every generation runs strict answering first, supplies exact eligible spans and authority rules, validates output deterministically, and falls back on failure. Expose narrate(question, corpus_path, profile) and mplpb-combined narrate; keep models optional with --no-model. Do not change ownership rules, hash checks or finite grammar. Begin by scaffolding Option 5 as described above.

Merge it

## Implemented scope

- Implement optional local narrator and CLI using existing strict answer coordinator and bounded loopback transport; Ollama, llama.cpp server and generic OpenAI-compatible server protocols.
- Accept only complete unchanged ledger text in approved layouts; exact quotes alone and model confidence never establish support. Refusal/conflict/partial bypass inference; fresh strict proof and source/policy recheck after model attempt.
- Add18 narrator tests and backend HTTP fixtures; document configuration, labels, exact citations, failure behavior and limits; preserve historical evidence.
- Publish the tested narrator branch through a pull request and merge into main only after all required checks pass on the exact candidate head.

## Validation recorded

- Baseline17 native tests passed with local sockets enabled; initial sandbox failed7 HTTP setups because sockets were denied. Logs retained.
- First new tests had2 fixture errors: agreeing exact-field values were not a conflict in the existing coordinator. Corrected fixtures and added a separate multiple-owner statement control; no core rules changed.
- Focused66 tests passed5.406s. Frozencc49d6e extracted archive passed1219 Python tests and52 public evidence cases, zero observed false-supported bridges, all exit0; full wall362.109s/CPU345.241s, max child RSS299597824bytes.
- JavaScript, crawler, actual Pyodide314.0.7 and real Chromium public-baseline/candidate-preview compatibility tests passed. Initial two Node EPERM failures and missing-browser executable failure are retained with unchanged successful retries after environment fixes.

## Limitations and blocked checks

- Live neural generation and independent semantic review NOT RUN; authored protocol fixtures are not model-quality validation.
- Only complete exact answer formatting is allowed; arbitrary paraphrase, semantic extension, streaming and model-only claims are disabled.
- Loopback cannot attest that a service never forwards remotely; local operators must disable forwarding. Socket timeouts do not establish total wall-time against malicious trickle responses.

## Next steps

- Resume from docs/LOCAL_NARRATOR.md, the dated general-reader narrator REPORT.md and checkpoint.json; verify source hashes before changing implementation.
- No live neural generation or independent semantic review was performed. Test explicitly installed local models separately; retain exact-rendering rejection and final source/policy recheck.
- Merge explicitly authorized. Push branch, open PR, wait for required archive-first/regression checks, then merge without bypassing protection. Inspect deployment separately; retain tested runtimecc49d6e and its evidence.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
