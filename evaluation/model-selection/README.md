# MIT-only browser model selection

Last reviewed: 2026-11-10.

The picker offers Phi-1.5 (default), Phi-2 and Phi-4-mini instruct. All three
models are MIT-licensed by Microsoft; original notices are bundled and hashed.
WebLLM retains its existing Apache-2.0 notice. Conversion lineage is declared by
MLC, not independently authenticated. Model locations, configuration and compiled
libraries are pinned; no weights are bundled or fetched merely by choosing a model.

[Asset verification](asset-verification.json) records actual downloads and hashes
of the two added model configurations, tensor metadata, compiled libraries and
upstream MIT notices. It does not establish neural quality or iPad compatibility.
Phi-1.5 and Phi-2 are base models; structured planning may be unreliable.

The authored [loader tests](../../tests/browser-model-loader.cjs) exercise selected
identity/resource records, unknown choices, non-MIT rejection, duplicate IDs,
missing defaults and prevention of a second live engine, alongside existing error
and integrity behavior. [Asset tests](../../tests/test_browser_ai_assets.py)
check the smallest default, immutable locations, packaging and non-MIT/modified
license rejection.

[Chromium picker checks](../../tools/browser_model_selection.py), invoked by
[the existing browser runner](../../tools/browser_free_helper.py), use a real
WebAssembly source engine with an explicitly authored GPU/runtime/hash fixture.
They exercise choice/size display, selection propagation, locked loading controls,
diagnostic export, provider revocation, reload/persistence, unavailable saved IDs
and catalog failure while source tools remain available. They never download
weights and are not a physical GPU or neural-inference test.

Reproduce from a built site:

```sh
python -m unittest tests.test_browser_ai_assets -q
node tests/browser-model-loader.cjs
node tests/browser-webgpu-limits.cjs
python -m tools.browser_free_helper --preview-dir dist --browser-executable /usr/bin/chromium --output NEW_REPORT.json
```

The supplied private device reports are not published. They showed the patched
512 MiB per-buffer limits and a later cached-weight initialization failure. This
motivates a smaller choice but does not prove total-memory exhaustion. A later user-provided report records Phi-1.5 initializing successfully on Apple
WebGPU; a screenshot then records a disposed-object error on generation. Successful
generation and independent physical iPad reproduction remain unverified. Candidate,
archive, CI and deployed-site results apply only to their respective revisions;
see the PR/Actions runs for exact release outcomes.
