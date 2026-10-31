# Installation and release packages

[Open the live application](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/) for a hosted start, or choose a package below. See the [documentation index](README.md) for runtime modes and source-interface contracts. Python 3.8+ is the declared desktop/package minimum; CI tests Python 3.12, not every supported Python/platform combination.

The successful main-branch Pages workflow provides an artifact named `mplpb-monster` on its GitHub Actions run.

* `mplpb-monster.zip`: committed repository source. Extract it, install Python 3.8 or newer, then run `python launch.py` or the supplied platform launcher. This includes the chat application and its bundled resources.
* `mplpb-monster-browser.zip`: extract and open `MPLPB_Browser.html` in a current browser, or serve it over static HTTPS. No Python server or AI account is needed. Browser storage permissions affect persistence. Explicit or enabled automatic Wikipedia lookup uses the network.
* `combined_mplpb-*.whl`: the ledger, supported-answer, specialist-work and evaluation command-line packages. Install with `python -m pip install PATH_TO_WHEEL`, then run `mplpb-combined --help`. This wheel does not include the browser chat application; use the source or browser ZIP for chat.
* `SHA256.json`: source commit, sizes and SHA-256 digests for both ZIPs.

The source ZIP is built with `git archive HEAD`, so local collections, transcripts and temporary files cannot accidentally enter it. The browser ZIP packages the browser runtime that passed the WebAssembly checks. The workflow installs the wheel in a fresh virtual environment and exercises its command entry point before publishing the site.

To reproduce from the desired clean committed checkout after building and testing `dist/index.html`:

```
python tools/build_release_packages.py
python -m pip wheel --no-deps --wheel-dir release .
```

Chat adaptation is session-local data: explicit personal details, corrections and user-defined meanings. It does not install executable code or modify the MPLPB evidence reader. See [context](CONTEXT_INDEX.md) and [chat evaluation](CHAT_EVALUATION.md) for grammar and limitations.

The browser ZIP contains `MPLPB_Browser.html` and instructions. The static Pages
deployment additionally includes the generated public-ledger snapshot and
discovery files; those sidecar files are not inside the one-file runtime ZIP.
The build/packaging commands use committed `HEAD` for source packaging. Rebuild
and test the browser from that same revision before packaging; uncommitted edits
are not included in the source ZIP. `SHA256.json` covers the two ZIPs, not the wheel
or a claim that the site currently runs those bytes. PR candidate evidence uses
the separately named [ZIP-first artifact](ZIP_FIRST_RELEASE_TESTING.md).

## Full repository snapshot and recovery

The full source ZIP contains every tracked file at its named commit, including
application, parts, resources, tests, evaluation data and documentation. It
excludes `.git`, untracked build outputs and private local sessions. It is not
a Git history backup or a prebuilt standalone browser runtime. Use the browser
package for compiled standalone HTML. Verify the supplied SHA-256 and extract
into a new directory. Keep session exports separate. See [ROLLBACK.md](ROLLBACK.md).

## Answer CLI migration

The 2.1.0rc1 wheel includes `mplpb_answers`, `mplpb_work`, and the separately
versioned legacy core. It installs `mplpb-combined`, `mplpb-library`, `mplpb-work`,
and `mplpb-evaluate`; it does not package the source-checkout NPC runner or full UI.
`mplpb-combined ask` and `python -m mplpb_answers ask` require body support.
`mplpb-combined candidates` labels legacy page retrieval explicitly.
`python -m mplpb_combined ask` remains the old archival retrieval interface;
use the new entry point for user-facing answers. Optional assisted Ask requires an
explicitly configured native local reader and installed weights; strict mode and
the standalone browser need no model. See [local-reader setup](GENERAL_ANSWER_PIPELINE.md),
[specialist work](SPECIALIST_CONTINUITY_API.md), and [the review](ANSWER_RELIABILITY.md).
