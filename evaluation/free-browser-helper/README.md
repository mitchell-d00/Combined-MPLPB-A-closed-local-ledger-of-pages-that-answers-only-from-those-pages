# Free public browser helper — development evidence

Last reviewed: 2026-11-08.

Baseline: `9f03116d32bba20b69f0ec9cddf58eb799ab8f17`, the merged local MCP update.
This update adds an optional browser model/builder layer using the existing public
JavaScript API. It does not change source-language rules or train a model.

Authored tests cover real-engine query parity, original-question preservation,
profile restrictions, reviewed writes/cancellation, supplied-text fidelity,
contradictions, model/general labels, blocked cross-mode actions and trace isolation.
The Chromium workflow exercises actual WebAssembly, source creation, exact citations,
conflict handling and a saved clarification after a real page reload. Model plans
in contract tests are synthetic; live Phi-4 generation is not represented as tested.

`native-contract.json`, `focused-tests.json`, `browser.json` and `gpu-probe.json`
retain actual outcomes. `validation.json` identifies source content. `extracted-zip.json` pins the
implementation revision/tree and exact ZIP with focused native/Chromium evidence.
A later socket-enabled test found a single-script packaging mismatch in that
preliminary revision. The embedding repair and successful 66-test rerun are
recorded separately in `validation.json`, with all failure logs retained.
`candidate-browser-after-embedding-fix.json` is the revised nine-check browser
result. Exact-head required CI and public deployment are separate gates. No independent human quality or iPad pass
is claimed. The software test GPU lacks shader-f16, so the selected neural format
cannot be validated there. Source/builder/native conversation remain usable.

The owner's public README material was separately prepared with attribution and
benchmark-overlap screening. Raw candidate material is a separate review artifact;
metadata and reproducible preparation code are in `training/owner-work/`. It is not
an approved conversation dataset and no visitor data or model training was used.

```sh
node tests/browser-ai-helper.cjs
python -m unittest tests.test_browser_ai_assets tests.test_owner_corpus -v
python -m tools.browser_free_helper --preview-dir PREVIEW --browser-executable CHROME --output NEW_REPORT.json
```

See [public helper scope and zero-cost tradeoffs](../../docs/FREE_PUBLIC_HELPER.md).

## Initialization-failure follow-up

An iPad user reported a 100% download followed by `exit(1)` after baseline main
`0c8199257e23c4030ab8ccb72cb687d399b9b115`. `model-load-diagnostics.json` records
the observed communication/diagnostic defect and exact scope. New reports named
`loader-*` are separate from the original release evidence above. The loader
cases use authored GPU/runtime stubs, plus construction/unload of the actual
pinned WebLLM module without model weights. They do not reproduce physical GPU
initialization or establish why that user's device stopped.

```sh
node tests/browser-model-loader.cjs
```
