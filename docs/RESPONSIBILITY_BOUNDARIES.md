# Product, project and evidence boundaries

Last reviewed: 2026-11-27.

[Use MPLPB](MPLPB.md) · [Develop MPLPB](EXPERIMENTAL_LAB.md) ·
[Inspect the evidence](TESTING_APPARATUS.md)

These responsibilities share one repository. The [component map](COMPONENT_MAP.md)
shows ownership by department. The [Test Index](TEST_INDEX.md) links a capability
to its code, checks and measured evidence. The maps do not change existing
paths, published case IDs, hashes or history.

| Responsibility | Needed by | Dependencies in the current tree |
|---|---|---|
| Product | Someone using a ledger, asking a question or opening a citation | The three core packages supply the CLI, reader and work commands. Browser uses `index.html`, `browser/`, the pinned WebAssembly core, runtime Python and the configured demos/resources. Desktop launches `tools/ledger_ui.py` via `launch.py` or a platform script and serves the same UI locally. A user supplies a plain-text body or imports a supported document, reviews the source, then asks. |
| Project / Experimental Lab | Someone changing the engine or delivering the app | The product runtime plus build tools, browser and desktop integration, developer documentation, workflows, test machinery and its fixtures. Some modules in `tools/` are runtime dependencies for the UI, while others build or evaluate it. Directory placement alone does not determine delivery. Candidate-only work is linked at its exact pin. |
| Evidence / Data | Someone inspecting evidence or reproducing a measurement | Public corpora and receipts in `evaluation/`, fixtures and tests, `killtest/`, dated docs and original records. A receipt can be read alone. Exact replay additionally needs its pinned runtime, complete authorized packet, harness, budgets, and key or expected contract. Historic results keep their original scope. |

The wheel also ships the existing evaluation and synonym CLI entry points.
These are shared interfaces supplied by the core packages. Evaluation corpora,
the separate test harness, development-only tools and private custody are
outside the wheel. Browser and desktop share the UI, demo ledgers and several
`tools/` imports. The archive bundle has both usable demo data and unrelated
historical material elsewhere in the same repository.

## Build audit against the product manifest

The [machine-readable distribution manifest](PRODUCT_DISTRIBUTION.json) records
the supported packages and the smallest current product deliveries.

| Delivery | Actual boundary | Audit finding |
|---|---|---|
| Compact native download | One wheel with the three runtime package roots and its metadata | Historically Pages zipped every wheel in the release directory. The build now stages the current wheel in a fresh directory and uses the packager to check its members before the ZIP is built. |
| Standalone or hosted browser | Rendered HTML with embedded runtime and data, plus optional hosted API/helper sidecars | The standalone outer ZIP is already scoped. Its inner builder recursively includes `tools/` and `evaluation/wiki/`. The build now leaves 16 offline Wiki reports and five study notes in source/evidence only, removing 425,963 input bytes from the embedded file set. Wiki heads, manifests and captures still back the configured corpus and history view. Shared runtime tools and resources need use-by-use checks before a further split. |
| Desktop | Full source checkout or `mplpb-monster.zip`, Python and local browser | Desktop therefore downloads tests, frozen evaluation files and papers along with its actual UI dependencies. A minimal desktop bundle is proposed work, pending an explicit import and runtime data manifest plus validation. |
| Full source and evidence | `git archive` of the full committed revision | Deliberately preserves review/recovery material and workflows. Use only an approved source checkout; this is not the compact product install. |

**Physical separation** exists for core package directories and retained
evaluation trees. **Packaging separation** exists for the native ZIP and the
standalone browser wrapper. **Navigation separation** exists for product,
lab and evidence. Desktop packaging and the browser's embedded developer/data
trees remain intertwined. No source or evidence was moved here.

[Candidate package verification](PRODUCT_DISTRIBUTION_VERIFICATION.json) records the tested archive checksums, clean-environment quick start and exact browser manifest difference.

## Publication and custody

Publish only approved inputs and outputs. A public receipt may give a stable
case ID, custody owner, hash, availability and execution status. Private
originals, held packet contents and held keys stay in designated custody,
outside build staging, Git and public artifacts. Browser-delivered bytes are
downloadable; delivery-profile checks govern answer admission and are not a
secrecy boundary for embedded bytes. Bundled public demos and previously
published wiki material have their documented source policies.

The older PR #106 restricted archive incident remains open. Current-tree
removal does not erase Git history. This packaging work starts from clean
main and does not take the affected ancestry. It leaves the Cryptid and
Egyptian-series checkpoints and their release gates on the reader track.
