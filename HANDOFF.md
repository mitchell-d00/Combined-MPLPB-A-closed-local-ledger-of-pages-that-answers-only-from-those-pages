# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `937b15712714f5155807b2478ef51592a14fc0d7` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `2bbebf325f08696563def9d01d45f4cdd3401989dc94d7cc9f257b736158957f`.

## Latest user update instructions

Add a local small-language-model frontend strictly subordinated to the existing MPLPB authority rules. Present these five options, then implement Option 5 in full: Constrained Local Narrator. Configuration via MPLPB_NARRATOR_BACKEND=ollama|llamacpp|openai, MPLPB_NARRATOR_MODEL and MPLPB_NARRATOR_BASE_URL. Every generation runs strict answering first, supplies exact eligible spans and authority rules, validates output deterministically, and falls back on failure. Expose narrate(question, corpus_path, profile) and mplpb-combined narrate; keep models optional with --no-model. Do not change ownership rules, hash checks or finite grammar. Begin by scaffolding Option 5 as described above.

## Implemented scope

- Implement optional local narrator and CLI using existing strict answer coordinator and bounded loopback transport; Ollama, llama.cpp server and generic OpenAI-compatible server protocols.
- Accept only complete unchanged ledger text in approved layouts; exact quotes alone and model confidence never establish support. Refusal/conflict/partial bypass inference; fresh strict proof and source/policy recheck after model attempt.
- Add18 narrator tests and backend HTTP fixtures; document configuration, labels, exact citations, failure behavior and limits; preserve historical evidence.

## Validation recorded

- Baseline17 native tests passed with local sockets enabled; initial sandbox failed7 HTTP setups because sockets were denied. Logs retained.
- First new tests had2 fixture errors: agreeing exact-field values were not a conflict in the existing coordinator. Corrected fixtures and added a separate multiple-owner statement control; no core rules changed.
- Focused66 narrator/native/documentary tests passed5.406s exit0. Full archive regressions pending.

## Limitations and blocked checks

- Live neural generation and independent semantic review NOT RUN; authored protocol fixtures are not model-quality validation.
- Only complete exact answer formatting is allowed; arbitrary paraphrase, semantic extension, streaming and model-only claims are disabled.
- Loopback cannot attest that a service never forwards remotely; local operators must disable forwarding. Socket timeouts do not establish total wall-time against malicious trickle responses.

## Next steps

- Freeze committed source, archive it and run full Python and public-evidence checks from extracted content. Record actual outcomes and resource costs separately without changing tested runtime.
- Resume by reading docs/LOCAL_NARRATOR.md and evaluation/general-reader/2026-11-17-local-narrator/REPORT.md; preserve the strict coordinator as sole answer authority.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
