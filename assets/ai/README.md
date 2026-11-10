# Optional browser model assets

Last reviewed: 2026-11-10.

The core app does not need a language model. These pinned parts reconstruct the
original WebLLM 0.2.87 browser runtime, then apply the explicitly pinned
`webgpu-device-limits-v1` local patch when building the public site. No model
weights are bundled, and no paid inference endpoint or API key is configured.
`tools/build_ai_assets.py` verifies every part and the reconstructed runtime.
The browser checks the active patched-runtime hash before importing it.
The manifest retains upstream and patch/output hashes; patch matching fails closed.
Original compressed runtime parts and all third-party licenses remain unchanged.
The local patch requests buffer limits within the adapter’s supported capacity
instead of dropping intermediate-capacity devices to undersized defaults.
It also checks actual device limits against the host-declared tensor minimum and
records negotiated limits before loading weights. This is a local derivative,
not an assertion that the upstream package contained the repair. Model config and compiled
library pins are also checked by the runtime; immutable model locations identify
the selected snapshot, not its truth or independently authenticated lineage.

The application code remains under the repository license. WebLLM is Apache-2.0;
its original runtime bytes and license are preserved. Bundled loglevel has an MIT
notice. The model catalog includes only Microsoft's MIT-licensed Phi-1.5, Phi-2
and Phi-4-mini instruct; each MLC conversion has a pinned immutable snapshot,
configuration/library integrity hashes, and an included original Microsoft notice.
`models.json` defaults to Phi-1.5; `model.json` retains the earlier Phi-4 record for
compatibility. The builder and browser loader reject non-MIT catalog entries.
The builder also checks license-notice hashes and consistent runtime pins.
Conversion lineage is declared by its publisher, not independently verified here.

| Model | Tensor download | Upstream working-memory estimate |
| --- | ---: | ---: |
| Phi-1.5 (default) | 798,633,984 bytes (0.80 GB) | 1,210.09 MB |
| Phi-2 | 1,564,948,480 bytes (1.56 GB) | 3,053.97 MB |
| Phi-4-mini instruct | 2,158,049,280 bytes (2.16 GB) | 3,437.58 MB |

Estimates exclude other browser/engine overhead; they are not measured free RAM
or guarantees for the configured context. Phi-1.5 and Phi-2 are base models;
instruction-following and JSON proposals may be unreliable. Compatible WebGPU,
shader-f16, sufficient buffer limits, memory and storage are required. These are
not measured guarantees for an iPad. Loading is explicit; it never happens merely
because someone opens the page. Unsupported devices keep the core MPLPB tools.
The selected model ID is saved locally; removed selections revert to the default.
After initialization, selecting another model revokes the old proposal provider
and requires a page reload before loading again. Failed initialization also
requires a reload. Weight caches are not deleted.

This uses a pretrained model. No fine-tuning or training on visitor conversations
runs. Free hosting/CDN usage remains subject to the services' normal limits; the
app does not configure a billable backend or silently fall back to one.
