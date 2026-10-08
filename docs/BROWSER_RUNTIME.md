# Standalone browser runtime

`MPLPB_Browser.html` embeds Pyodide 314.0.7 (CPython/WebAssembly), this repository's
actual Python engine, the RPG-style UI, bundled sealed corpora and stored wiki
capture data. No Python installation, local Python server or CDN download is needed
to start the generated build. It does not mount or scan the host filesystem.

Use a current browser with WebAssembly, Web Workers, WebCrypto, IndexedDB, local
storage and Web Locks. Open the generated HTML, or serve it using ordinary static
HTTPS hosting. Some browsers block these features for local `file:` URLs or in
private browsing. Those environments stop with a visible error; they do not quietly
fall back to an unsaved session. This is not an “every browser” guarantee.

Session IDs/preferences use local storage. The worker's dedicated virtual `/mplpb-browser-save-v1` mount, linked as `/app/local`, uses
IndexedDB for session envelopes, raw source captures, revision bundles and heads.
Browser storage is separate from the desktop server's filesystem. Clearing browser
data, origin changes, quota limits or storage eviction can erase saves. Export
important transcripts. The runtime holds a Web Lock so two tabs cannot overwrite
the same save store. A storage failure stops subsequent operations until reload.

Read/query/memory/summary/comparison/rule inference run locally in the worker.
The ordinary Python `App`, reader and provenance gate make those decisions; no
second JavaScript ownership implementation exists. `search` and `import` explicitly
fetch the chosen Simple English or English Wikipedia API with `origin=*` and no
credentials. Raw responses enter the same source-slot pin/capture pipeline. WebAssembly has no git subprocess: the transport records actual engine/checker/renderer bytes, a separate browser-adapter hash, and no invented checkout revision. Adapter hashes are rechecked when serving those captures.
Network/CORS/HTTP failures refuse the operation without inventing an answer or
score. Arbitrary-address imports are not enabled. No links are followed.

The generated HTML is about 20 MB because it includes the runtime and pages.
Browser startup and memory use can be significant on mobile hardware.

## Build

Run `python3 tools/build_browser_runtime.py` to download the pinned core release,
verify its published SHA-256 and generate `dist/MPLPB_Browser.html`.
Alternatively pass `--core-archive /path/to/pyodide-core-314.0.7.tar.bz2`.
The builder packages only named repository folders and excludes user save data.
This build step needs Python; running its HTML output does not.

Core release archive SHA-256:
`2abdcc2e35208af406e07724cffa85bc582ced97e9028383ecf5462541393f95`.
The worker checks bundled source and runtime asset hashes before loading them.
These hashes detect inconsistent bytes, not authenticated authorship.

Upstream: [Pyodide](https://github.com/pyodide/pyodide/releases/tag/314.0.7),
[usage documentation](https://pyodide.org/en/stable/usage/index.html).
Pyodide's MPL 2.0 and CPython's license are included under `browser/licenses/` and
in the generated bundle. MPLPB and RPG-layout notices remain included.

## Verification and limits

Real WebAssembly execution was tested in Node with the same bundled Python files:
name ambiguity, source-gated external withholding, relation proof, extractive
summary, working notes, virtual-save relaunch, fixture source import and transcript continuity passed. The Python browser bridge
has nine tests, including import pin checks, same-revision conflict retention,
network failure, command transport and arbitrary URL/path rejection.

The complete Python suite passed 272 tests. The worker and UI transport have separate JavaScript checks. These do not substitute
for testing browser permissions, IndexedDB persistence or graphical layout in an
actual browser. No live browser Wikipedia score is claimed. Frozen published probe
files and stored evaluation captures were not rewritten.

## Walk back

The root `index.html` and Python launcher retain desktop mode. Remove the generated
standalone build to stop offering browser mode. Browser saves are not desktop saves;
export before clearing browser storage or changing origin. SELF-0003 documents both
modes and retains SELF-0002 and SELF-0001 in the revision tree.
