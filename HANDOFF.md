# Repository handoff

Last reviewed: 2026-11-08.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `3d37fb8f1b9b7ddd4dc3df4328a2e9396950e5f3` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4ee7c844177d05d765cc505ba9c975d18f3e2735e4c19015182779825544e68a`.

## Latest user update instructions

Latest user image reports: “Optional AI unavailable: Program terminated with exit(1)”. Follow-up clarification: “It reached 100% first”. Investigate this reported loading failure and make its handling recoverable. [The investigation scope is inferred from the supplied error image and conversation; the quoted error and follow-up are verbatim.]

Persisting constraint: “this can’t cost me anything, I build very cheap”.

## Implemented scope

- Add a bounded model-load diagnostic report with original stage, progress, GPU/browser capabilities, available runtime logger messages, thrown error/stack/cause and cleanup outcomes. Export it locally without source questions and include it in the broader explicit interaction export.
- Distinguish a 100% download from successful initialization. Keep general-chat requests unsent while loading and label an unloaded model as unavailable rather than question clarification.
- Use the documented constructor/reload equivalent of the same pinned runtime so failure cleanup can be attempted. Bound unload to three seconds; require a user-triggered page reload before another initialization attempt. Do not clear caches or ledger data.
- Preserve all source authority, integrity, collection and delivery rules, model/runtime/license bytes, historical evaluations and frozen probes/labels. Keep the zero-cost, no-paid-provider, no-training scope.
- Keep bounded browser/GPU summaries on each attempt separately from the recent-event ring, so long two-phase parameter loads cannot evict diagnostic context.

## Validation recorded

- Baseline main 0c8199257e23c4030ab8ccb72cb687d399b9b115 had passed 873 Python tests, 45 MCP SDK checks and actual public Chromium deployment in PR #32 / Pages run 42490859108. These are baseline results, not a new-device success.
- The user reported a real iPad attempt completing its download then failing with exit(1). The visible message does not establish memory exhaustion, GPU incompatibility or another specific cause.
- 13 authored loader/state/DOM checks passed, including 100%-then-exit failure, deferred readiness, missing features, changed runtime hash, bounded logs, cleanup error/timeout, blocked repeated initialization, and unchanged real pinned WebLLM constructor/logger/unload API without weights. Runtime/GPU failure scenarios are simulated, not actual neural inference.
- 33 existing helper checks against the actual native source engine and eight focused asset/data Python tests passed. Twelve actual Chromium/WebAssembly workflow checks passed, including visible separate load-stage report, physical report download matching its display without source questions, strict source/citation/conflict paths and saved clarification after reload.
- Compared 877 protected baseline files with Git blobs, unchanged. Documentation, handoff, committed archive and exact-head CI are recorded separately and are not claimed before completion.
- Follow-up baseline 3d37fb8f1b9b7ddd4dc3df4328a2e9396950e5f3 exposed a report-retention defect: progress/log rollover could evict the sole browser/GPU events. The strengthened bounded-events case failed before the fix; actual WebLLM emits download and device-load progress for 66 shards. Store browser/GPU snapshots independently from the event ring. This does not diagnose or resolve physical GPU initialization.
- Context-retention fix: all 13 loader checks, 33 actual native-engine checks and eight focused Python tests pass; 12 actual Chromium/WebAssembly checks pass. Updated bounded-events assertion verifies browser/GPU fields survive rollover. This is not a physical-device or live-model pass.

## Limitations and blocked checks

- The physical iPad failure root cause remains unresolved until device diagnostics are captured. No successful Phi-4 generation, hardware compatibility, independent human evaluation or model training is claimed.
- Reports are local and bounded; they capture the pinned instance logger and thrown errors, not all GPU/console events. They do not measure available RAM and are lost on tab reload/closure unless exported. A process crash can prevent export.
- Unloading is attempted and bounded, not proof that every partial GPU allocation is reclaimed. A new initialization requires page reload after failure; the report should be exported first. Browser eviction can still remove cached model files.
- The public site remains static hosting with visitor-device compute. There is no paid AI API, rental, hosted MCP/inference backend or unlimited free hosting promise.

## Next steps

- Freeze the context-retention follow-up, verify the exact extracted source and wait for required exact-head CI before merging. Verify its public deployment separately. The previous diagnostic release passed all required gates; its metadata-retention follow-up must be tested as its own revision.
- After the new loader is published, reload the site and make one explicit model-load attempt if desired. If it fails, export the model-only report before reloading and inspect the concrete runtime evidence; do not diagnose exit(1) from speculation.
- For future updates, replace this record with the latest task instructions, review affected documentation/result links, stage intended files and regenerate/check the repository-owned handoff. No private personal context belongs in public source/training artifacts.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
