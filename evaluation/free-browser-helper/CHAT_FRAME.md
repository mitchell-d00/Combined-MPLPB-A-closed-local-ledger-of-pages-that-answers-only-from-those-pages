# AI chat frame and generation recovery

Last reviewed: 2026-11-10.

The AI helper has a bounded, scrolling conversation window with its prompt and
Send button directly below. The source-import form follows the composer, so
expanding it does not move Send away from the prompt. Enter sends; Shift+Enter
adds a line. Successful messages clear the prompt; failed messages remain editable.
Replies stream into the response window, and recent user/reply rows remain in the
tab. This is separate from the native rule-based Chat with MPLPB panel.

AI chat uses plain-text generation rather than a JSON action plan. It carries
bounded recent conversation, labels model output unverified, and makes no source
tool calls. Build continues to validate structured plans and requires review
before creating a collection or importing a source. Source questions still use
the existing reader and retain its answer/citation rules.

A user-provided model report recorded Phi-1.5 reaching ready on Apple WebGPU.
A later screenshot records `The current Object has already been disposed` after
Send. The screenshot establishes a generation failure, not a GPU-loss or total-RAM
diagnosis. The earlier initialization is not relabeled as a successful reply.
The new text path avoids unnecessary JSON grammar setup and lowers reply budgets;
it is not a claim that the physical-device root cause has been repaired.

Disposed/lost runtime errors revoke the provider, change the diagnostic state to
generation failure, preserve the earlier ready event, retain the error/stack in
the local trace, and offer Reload AI after error. A failed runtime is not reused.
Source tools remain available without AI. Reloading does not clear weight caches
or source collections. Exports remain local unless the user shares them.

Reproduction uses [helper/provider tests](../../tests/browser-ai-helper.cjs),
[loader tests](../../tests/browser-model-loader.cjs), and
[actual Chromium chat/picker workflows](../../tools/browser_model_selection.py)
called by [the browser runner](../../tools/browser_free_helper.py). The Chromium
workflow runs the actual WebAssembly source engine with explicit authored GPU and
model-output fixtures. It covers iPad/narrow layout, source-form expansion,
streaming, Enter/Send, duplicate-send prevention, text escaping, contextual replies,
reviewed model-proposed collection creation and generation-error recovery.

```sh
node tests/browser-ai-helper.cjs
node tests/browser-model-loader.cjs
python -m unittest tests.test_browser_ai_assets -q
python -m tools.browser_free_helper --preview-dir dist --browser-executable /usr/bin/chromium --output NEW_REPORT.json
```

These tests do not generate a real neural response or independently reproduce
the iPad failure. Physical-device generation, model quality, exact tokenizer
capacity and long-lived GPU stability remain unverified. Exact archive/CI and
published-site results belong to their corresponding commit and Actions runs.
