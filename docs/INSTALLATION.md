# Installation and release packages

Last reviewed: 2026-11-17.

[Package guide](PACKAGE_GUIDE.md#delivery-and-packaging) · [Documentation index](README.md)

Choose a delivery mode for the part you need. A native wheel, full source checkout
and standalone browser are related distributions, not interchangeable installations.
All retain the same distinction between source inspection and strict answer support.

## Choose a distribution

| Delivery | Use it for | Requirements |
|---|---|---|
| [Hosted application](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/) | Browser source inspection, collections and bounded conversation | Modern browser, WebAssembly/workers, WebCrypto, IndexedDB and storage permissions |
| `mplpb-monster-browser.zip` | Downloaded standalone core application | Extract and open `MPLPB_Browser.html`, or serve it over static HTTPS; optional site sidecars/model weights are separate |
| `mplpb-monster.zip` / source checkout | Desktop App, sorter, native source tools, MCP and full retained repository | Python 3.8+ declared; CI exercises Python 3.12; core runtime uses standard library |
| `combined_mplpb-*.whl` | Installed ledger/answer/library/work/evaluation CLIs and sorter module | Python and a wheel installer; bring your own ledger/raw files; full App/resources/examples are not installed |

The successful main-branch **Publish MPLPB browser runtime** Actions run provides
an artifact named `mplpb-monster`. It includes the two ZIPs, wheel and
`SHA256.json`. A running Pages site does not mean that an optional general-web
crawler or remote model service has been configured.

## Full source and desktop application

Clone/extract the full repository, then run from its root:

```bash
python3 launch.py
```

Windows can use `python launch.py` or `Launch_MPLPB.bat`; Mac/Linux can use
`sh Launch_MPLPB.sh`. The launcher opens <http://127.0.0.1:8766>. Keep the Python
process running. The root `index.html` alone does not run the native engine.
`python3 tools/ledger_ui.py` starts the server without opening a browser.
See [browser/desktop controls](BROWSER_UI.md) for a custom ledger or port.

The full checkout includes the three core Python packages, App/tools, source
sorter, resources, examples, preserved parts, tests, documentation and evaluation
records. It does not include your private local collections or Git history when
obtained as the release source ZIP. Installing the wheel is not required to run
Python modules from this checkout.

## Wheel and command-line tools

```bash
python -m pip install PATH_TO_WHEEL
mplpb-combined --help
mplpb-library --help
mplpb-work --help
mplpb-evaluate --help
python -m mplpb_work.sorter --help
```

From a checkout, `python -m pip install .` installs the same three packages and
entry points. Package-build tools may need installation separately; the installed
runtime itself declares no application dependencies.

`mplpb-combined ask` and `python -m mplpb_answers ask` use supported answering.
`mplpb-combined candidates` and legacy `python -m mplpb_combined ask` are lexical
inspection, not strict answers. A retrieved page and a supported answer are not
the same result. [Result contracts](PAGE_RETRIEVAL.md).

The package version is 2.1.0rc1. Legacy core 1.0.0, JavaScript API 1.0.0, paper
versions and content-derived browser build IDs are separately scoped identifiers.

## Sort raw files offline

```bash
python -m mplpb_work.sorter sort RAW_DIRECTORY \
  --mode not-compared --output NEW_OBSERVATIONS.json
python -m mplpb_work.sorter sort RAW_DIRECTORY \
  --mode compare --output NEW_COMPARISON.json
python -m mplpb_work.sorter peruse NEW_COMPARISON.json --sources RAW_DIRECTORY
python -m mplpb_work.sorter export-retired NEW_COMPARISON.json \
  --sources RAW_DIRECTORY --ledger NEW_SNAPSHOT_DIRECTORY
```

Both modes preserve identical nodes and source spans; compare adds only review
edges. Output paths must be new and outside the input tree. No model, network or
hidden source fields are needed. Originals stay unchanged. Native snapshot
validation/inspection succeeds while serving and supported answering withhold
it under every profile. Import originals separately under their real source policy;
never activate the candidate graph as factual evidence.
[Sorter contract and native commands](PREPROCESSING_SORTER.md).

## Browser runtime and storage

The hosted and standalone application run the Python engine locally through
WebAssembly. Their ordinary source queries and deterministic conversation need
no Python server, model or inference account. Browser saves belong to the current
origin. The native App uses filesystem stores. These stores are not automatically
shared, and transcript export is not a complete source-ledger backup.

The browser ZIP contains the standalone HTML and instructions. Pages additionally
publishes configured public sidecars, discovery files and an externally eligible
bundled-source snapshot. Optional helper/model assets are not all in the one-file
ZIP. File-origin storage permissions vary by browser; static HTTPS is an alternative.
[Runtime](BROWSER_RUNTIME.md) · [Storage/recovery](PACKAGE_GUIDE.md#storage-and-recovery).

## Optional components

| Component | Separate setup | Boundary |
|---|---|---|
| Native MCP | Full checkout, local stdio-capable client, explicitly authorized corpus roots/profile | No source-writing tools or access to another browser's IndexedDB |
| Wikipedia/source acquisition | Existing App setting/caller network permission | Captures/imports still require source checks; supplied text is not a verified site download |
| General-web crawling | Hosted Worker, authentication and appropriate provider setup for search | Pages does not deploy it; explicit seeds and provider-backed search have different requirements |
| Native assisted reader | Explicitly installed local model and loopback reader service | Model-only interpretations remain unsupported |
| Browser model/helper | Explicit opt-in, compatible WebGPU device, model download and sidecars | Initialization, generation and semantic quality are separate; no production device guarantee |
| Paper PDF rebuild | Optional ReportLab documentation dependency | Not required by the ledger, reader, sorter or core application |

[MCP](MCP_AGENT.md) · [Crawler](../crawler/README.md) · [Native reader](GENERAL_ANSWER_PIPELINE.md)
· [Public helper](FREE_PUBLIC_HELPER.md) · [Sorter paper formats](research/dual-mode-sorter/README.md).

## Package reproduction and source preservation

After building the browser from the intended committed source revision:

```bash
python tools/build_release_packages.py
python -m pip wheel --no-deps --wheel-dir release .
```

Source packaging uses `git archive HEAD` and a current handoff. Local/untracked
sessions are excluded. `SHA256.json` pins the two ZIPs and source commit; it does
not certify every artifact, installed wheel or current live site. Reproduce and
inspect the same committed candidate rather than packaging uncommitted edits.
[ZIP-first procedure](ZIP_FIRST_RELEASE_TESTING.md) · [Release evidence](RELEASE_EVIDENCE.md).

Keep the actual source ledgers, capture originals, receipts, work databases and
private credentials backed up separately. A source release ZIP contains the
application, not a backup of your user data or Git history. Preserve existing
workspaces when updating code. [Rollback](ROLLBACK.md) · [Capture compatibility](BROWSER_CAPTURE_COMPATIBILITY.md).
