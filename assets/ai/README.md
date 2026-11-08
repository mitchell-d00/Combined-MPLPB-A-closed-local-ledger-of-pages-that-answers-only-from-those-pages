# Optional browser model assets

Last reviewed: 2026-11-08.

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
notice. The selected Microsoft Phi-4-mini model is MIT-licensed; the MLC-converted
weights are fetched from the separately identified immutable repository snapshot.
The Microsoft notice is included. Conversion lineage is declared by its publisher,
not independently verified by this project. See the three retained license files.

Tensor files total about 2.16 GB; the upstream model record estimates about
3.44 GB device working memory before browser/engine overhead. Compatible WebGPU,
shader-f16, sufficient buffer limits, memory and storage are required. These are
not measured guarantees for an iPad. Loading is explicit; it never happens merely
because someone opens the page. Unsupported devices keep the core MPLPB tools.

This uses a pretrained model. No fine-tuning or training on visitor conversations
runs. Free hosting/CDN usage remains subject to the services' normal limits; the
app does not configure a billable backend or silently fall back to one.
