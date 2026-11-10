# Public builder and chat helper with no AI server bill

Last reviewed: 2026-11-10.

The product remains a public website at the existing MPLPB address. Everyone can
open it. GitHub Pages serves the interface; the MPLPB engine runs in each visitor's
browser. An optional pretrained MIT-licensed model can run in a compatible browser,
so no shared AI server, paid API, account, subscription or local Python setup is
required by a visitor. This does not promise unlimited free hosting/bandwidth or
support for every device. The core app continues to work without the model.

## Use the helper

Open **Builder and chat helper** near the bottom of the page. Choose the collection
and task, then send a request. The delivery profile is the profile chosen in the
existing MPLPB controls; the model cannot override it.

- **Ask sources** sends the original question to the strict reader. A model may
  propose the action but cannot substitute a simpler question or supply its answer.
- **Chat with MPLPB** uses its existing conversational and source-follow-up rules.
  Saved engine session identifiers allow a pending clarification to continue after
  reload; source changes still require reselection.
- **Build** proposes a collection name or source draft. Review it before choosing
  Save. Change the request or provided text and send again to replace a proposal.
- **General chat** produces clearly labeled, unverified model conversation when a
  model is loaded. Without it, the helper explains how to use the
  native source conversation mode. General model context is limited to recent turns and held in this tab.

Provided source text is saved exactly through the existing import API after
review. A model cannot invent an external citation URL. An unsourced model draft
gets an explicitly invalid local placeholder and an AI-generated/unverified label.
Saving does not establish truth, authenticated authorship or human ratification.
Existing origin/depth, ancestry, delivery and source-ownership rules still apply.
The helper performs no autonomous web acquisition, revisions, deletion or ratification.

## Optional model and device limits

Choose **AI model · MIT licenses only**, then press **Load**. Phi-1.5 is the
smaller default (0.80 GB weights, estimated 1.21 GB working memory); Phi-2
(1.56 GB, estimated 3.05 GB memory) and Phi-4-mini instruct (2.16 GB, estimated
3.44 GB memory) are also available. These upstream estimates exclude browser
overhead and do not measure free memory or certify the configured context.
WebGPU, shader-f16 and adequate buffer/memory limits are
required. The runtime and model locations are pinned. The app checks compatibility
before starting the large download and shows failures instead of enabling a paid
fallback. Browser caching/storage eviction can require another download later.

Every selectable model is MIT-licensed by Microsoft and converted to MLC format.
Original MIT notices, immutable model revisions, config/library integrity pins
and per-model tensor minima are included. Phi-1.5 and Phi-2 are base models;
their instruction-following and structured JSON planning may be unreliable.
The runtime is WebLLM 0.2.87, Apache-2.0, with notices
retained under `assets/ai`. No claim is made that every iPad can run it. The
execution environment's software GPU lacks shader-f16, so live Phi-4 generation
has **not** been validated here. The actual browser tests validate source/builder
behavior, native fallback and the unavailable-model path; simulated model plans
validate orchestration boundaries, not neural answer quality.

Only the selected model is initialized. Changing the choice after initialization
disables its old proposal provider and changes the button to **Reload page to
load selection**. The choice is saved locally and survives reload; an unavailable
saved choice falls back to Phi-1.5. Reloading avoids accumulating two engines.
Initialization failure also requires a reload before retrying; choose a smaller
model first if needed. Model caches and source collections are not deleted.
The default is a smaller option to test on iPad, not a confirmed iPad repair.

## When the model fails to initialize

A visitor reported an iPad download reaching 100%, followed by
`Program terminated with exit(1)`. This is evidence of a failed attempt, not a
confirmed memory diagnosis or a working iPad model. Download progress and model
readiness are separate: only successful engine initialization enables AI chat.

**Model loading details** records the stage, preflight browser/GPU capabilities,
last progress, thrown error/stack/cause and available TVM runtime logger messages.
Use **Export model load report** before reloading to retain this information.
This report is local and excludes source questions; it is not uploaded or used for
training. The broader interaction trace can include questions/source text.

Capture is bounded to three attempts and 120 recent events per attempt, with
omission counts and declared text/stack limits. Browser/GPU summaries are kept
separately from recent events so long downloads cannot evict those summaries.
It does not capture every console
or GPU message, determine available RAM, survive closing/reloading the tab, or
establish a hardware root cause by itself. A browser-process crash may lose it.
The loader uses the documented `MLCEngine` constructor/reload equivalent and the
logger hook inspected in pinned WebLLM 0.2.87. An unexpected logger-hook change fails visibly. The later device-limit repair
is an explicit pinned local derivative of that runtime; original upstream bytes,
model weights/library pins and cache identity are preserved.

Failed initialization attempts runtime unload with a three-second bound; its
outcome is recorded, without claiming all partial GPU allocations were reclaimed.
The retry control then explicitly reloads the page, rather than repeatedly
allocating another model in the same page. No cache or ledger deletion is
requested. The same model/cache identity is reused; browser eviction can still
require another download. Source tools remain usable without AI. An unloaded AI
is labeled **AI not loaded**, not a request to clarify the user's question.

## Adapter capacity and actual device capacity

The user's report showed a 512 MiB adapter, successful runtime integrity and a
cached parameter load stopping after its first shard with `Object has already
been disposed`. Inspection and execution of the upstream negotiation function
confirmed it requests only 256 MiB buffers / 128 MiB bindings on that adapter,
although the selected model's largest tensor requires 307,298,304 bytes. This is
a confirmed undersized-device configuration; the disposed-object error may be a
secondary effect of a GPU loss. No total-RAM diagnosis is inferred from it.

The versioned local runtime patch requests the smaller of the upstream 1 GiB
target and the actual supported capacity for each buffer limit. Other feature,
compute and storage-count requirements remain unchanged. The loader passes the
same declared tensor minimum used by its adapter preflight into a documented
local runtime extension, `mplpb_minimum_tensor_buffer_bytes`. The runtime checks
actual negotiated device limits against it before uploading parameters. Those
limits are retained separately in the load report. A sufficient single-buffer
limit does not prove sufficient total memory or successful inference.

The original upstream parts/licenses are retained. Patch context, patch bytes and
output hash/size are verified during reconstruction, and the browser verifies the
new active-runtime hash. This is an explicitly identified local derivative of
WebLLM 0.2.87. Model weights, compiled-library/config pins and cache identity stay
the same; no cache clearing or paid fallback is introduced. A physical iPad retest
is required; production-function tests using authored adapters do not establish
that its full model initialization or generation will complete.

## What transparency means

The interface separates the original user input, a model's unverified proposal,
the selected scope/profile, human approval, actual tool arguments/results and final
rendering. Model transport records include the visible request/response and
sampling configuration when inference runs. They do not expose or claim a faithful
account of a neural model's hidden internal reasoning.

Source-backed words come from MPLPB unchanged, with its citations and qualifications.
General model text stays labeled separately. A failed/unsupported request shows
the engine's diagnostic rather than treating grammar failure as proof that the
fact is absent. Inspect the original engine result and event trace, or export the
trace. An export can contain private questions/source text: it is not uploaded or
used for training automatically. Trace events are a tab-local interaction record,
not signed evidence, permanent audit storage or a claim that sources are true.

The browser's private ledger is not shared with other visitors by the address.
A third-party AI given only that URL does not acquire the visitor's IndexedDB.
This helper uses the page's existing JavaScript API. The separately launched local
MCP stdio server remains available to capable desktop clients; GitHub Pages does
not become a hosted MCP or AI inference service.

## Your work and training

The owner authorized their own public work at the supplied GitHub, PhilPeople,
Academia and Medium profiles as initial material. The current preparation pass
captured 46 public repository root READMEs from 48 repositories, yielding 1,131
candidate prose passages after screening against 1,394 stored evaluation questions.
Other supplied profiles were used as indexes; their full papers/blogs were not
bulk-ingested. No login/paywall was bypassed. Attribution, source hashes, declared
permission, observed licenses and limitations are retained.

Raw prose is not an approved conversation dataset. The separate candidate archive
is for review; it is not automatically redistributed in the app or imported as
source authority. Mixed third-party material still needs review. Exact overlap
screening does not prove absence of paraphrase contamination. OpenAssistant/oasst1
is listed separately as a possible Apache-2.0 conversation source and was not
used for training. Visitor chats and private notes are excluded.

No model has been fine-tuned. Training Phi-4 reliably cannot be promised at zero
cost with the available hardware. A useful first step is to put reviewed work in
MPLPB pages and retrieve it while retaining the pretrained model's conversational
skills. Data preparation can run manually through the free standard public-repo
Actions workflow and produce a downloadable artifact; there is no GPU-training
job or paid service hidden in that workflow. Standard public-repository runners
are free under GitHub’s current terms; hosting, artifact storage and upstream
downloads still have service limits. The preparation artifact expires after one
day. No spending limit or billing setting is changed by this implementation.

## Packages and validation

The published site contains optional runtime sidecars under `ai/`; model weights
remain at their identified external source. The one-file browser ZIP retains the
core offline engine but does not include these optional sidecars or model weights.
Use the public site or serve the complete generated site folder for the optional
model. The source package includes the pinned reconstruction parts and notices.

Run `node tests/browser-ai-helper.cjs`, `node tests/browser-model-loader.cjs`,
`python -m unittest tests.test_browser_ai_assets tests.test_owner_corpus -v`, and
`python -m tools.browser_free_helper --preview-dir PREVIEW --browser-executable CHROME --output NEW_REPORT.json`.
See [retained evidence](../evaluation/free-browser-helper/README.md). Source tests,
extracted-ZIP checks, candidate Chromium, live neural inference and deployed/iPad
verification are distinct; none is silently inferred from another.
