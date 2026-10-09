# Installation and release packages

The successful main-branch Pages workflow provides an artifact named `mplpb-monster` on its GitHub Actions run.

* `mplpb-monster.zip`: committed repository source. Extract it, install Python 3.8 or newer, then run `python launch.py` or the supplied platform launcher. This includes the chat application and its bundled resources.
* `mplpb-monster-browser.zip`: extract and open `MPLPB_Browser.html` in a current browser, or serve it over static HTTPS. No Python server or AI account is needed. Browser storage permissions affect persistence. Explicit or enabled automatic Wikipedia lookup uses the network.
* `combined_mplpb-*.whl`: the core ledger command-line package. Install with `python -m pip install PATH_TO_WHEEL`, then run `mplpb-combined --help`. This wheel does not include the browser chat application; use the source or browser ZIP for chat.
* `SHA256.json`: source commit, sizes and SHA-256 digests for both ZIPs.

The source ZIP is built with `git archive HEAD`, so local collections, transcripts and temporary files cannot accidentally enter it. The browser ZIP packages the browser runtime that passed the WebAssembly checks. The workflow installs the wheel in a fresh virtual environment and exercises its command entry point before publishing the site.

To reproduce from the desired clean committed checkout after building and testing `dist/index.html`:

```
python tools/build_release_packages.py
python -m pip wheel --no-deps --wheel-dir release .
```

Chat adaptation is session-local data: explicit personal details, corrections and user-defined meanings. It does not install executable code or modify the MPLPB evidence reader. See `CONTEXT_INDEX.md` and `CHAT_EVALUATION.md` for grammar and limitations.
