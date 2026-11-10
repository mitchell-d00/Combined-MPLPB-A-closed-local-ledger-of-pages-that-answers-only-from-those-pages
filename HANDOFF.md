# Repository handoff

Last reviewed: 2026-11-10.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `639f449070028616334295b8a3c38753535367fc` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `9cabc973b7ce46234986104b00099bc1071a932c2d1ad984b707ec043a6d08b8`.

## Latest user update instructions

I don’t seem to hav3 a send and makesend and prompt line under the window th3 ai will respond to  in the ai chat frame so it can help build MPLPB

Persisting instructions: use only MIT-licensed selectable models; publish to main for live-site testing.

## Implemented scope

- Add a scrolling AI conversation frame with the prompt and Send immediately beneath it, before the expandable source-import form. Support Enter/Send, Shift+Enter, streamed replies, bounded tab-local transcript rows, duplicate-send prevention, and visible in-frame errors. Default the helper task to AI chat while retaining source tasks and reviewed Build.
- Use a separate plain-text streaming provider for general AI chat instead of requiring a structured JSON action plan. Bound recent context and output; keep original user messages unchanged. Keep structured-plan validation and human approval for Build, and unchanged reader/citation rules for source questions.
- Capture generation request/response errors and stack in the local interaction trace. On disposed/lost runtime errors, revoke the provider, invalidate readiness with a generation-phase diagnostic retaining the earlier ready event, prevent reuse and offer Reload AI after error. Do not clear source collections or weight caches.
- Preserve the MIT-only model catalog, all model/compiled-library/runtime pins and notices, native source rules, imported sources, frozen evaluations and the zero-paid-provider constraint. Do not publish private uploaded device reports or screenshots.
- Extend actual Chromium iPad/narrow-layout and provider/loader tests, update affected guides/result indexes and regenerate the repository handoff. Publish through the existing exact-head archive/regression and Pages checks under the user’s existing main-publication instruction.

## Validation recorded

- Inspected the user-provided Phi-1.5 report reaching ready on Apple WebGPU and the screenshot showing a disposed-object error after Send. This is successful initialization plus failed generation evidence, not a reproduced GPU-loss or total-memory diagnosis.
- 45 helper/provider/native-engine checks pass, including plain streamed text without JSON planning, original prompt/history, short output budgets, oversize rejection before generation, structured Build, diagnostic stack capture, provider revocation and invalid-runtime reuse prevention.
- 18 loader/state/DOM/runtime API checks, 12 actual pinned GPU-negotiation-function checks, and 8 Python asset tests pass. UI script, browser transport, JavaScript API and crawler checks pass. Authored GPU/model responses do not establish neural inference quality or device compatibility.
- 13 focused Python asset/documentation tests pass. Exact archive, CI and actual deployed-site checks belong to their corresponding revision/run and must not be inferred from these focused checkout results.
- Actual Chromium/WebAssembly source-helper workflow passes 12 checks; the extended picker/chat workflow passes 11 checks with explicit runtime/GPU fixtures. It covers 810×1080 and 375×812 composer geometry, expanded source fields, plain streamed replies, Enter/Send, duplicate prevention, escaped user text, previous-turn context, reviewed model-proposed collection creation and disposed-generation reload recovery. No model weights or neural inference were used.

## Limitations and blocked checks

- The text generation path removes unnecessary JSON grammar setup and reduces reply budgets, but does not prove the physical iPad disposed-object root cause is fixed. Successful actual iPad generation and long-lived GPU stability require retesting.
- Browser/provider tests use an authored model/GPU fixture with the real source engine. They validate layout, streaming orchestration, review and recovery, not an actual neural response. Base-model quality and exact tokenizer capacity remain unverified.
- Chat input/context uses conservative character budgets and bounded recent turns; character counts are not exact token counts. Model output remains unverified and cannot substitute for MPLPB source evidence.
- Existing runtime and selectable model bytes/licenses remain unchanged; no paid API, telemetry, training, automatic cache deletion or hidden fallback is added.

## Next steps

- Complete the exact-head archive/regression gates, merge to main under the persistent publication instruction, and verify the actual deployed conversation frame and source workflow separately. Keep release evidence outside the frozen implementation candidate.
- Reload the published page on iPad, load Phi-1.5 from its existing cache and send a short AI-chat message. Confirm an actual reply; if generation fails, export the interaction trace before using Reload AI after error.
- Future updates must preserve source/vendor/history bytes, review affected docs, stage intended files and regenerate/check this handoff from the latest user instructions.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
