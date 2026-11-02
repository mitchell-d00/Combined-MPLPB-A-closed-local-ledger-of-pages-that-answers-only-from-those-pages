# Browser capture compatibility

Last reviewed: 2026-11-02. See [current status and result-to-test index](CURRENT_STATUS_2026-11-02.md). Dates and numeric results in historical validation sections retain their original scope; this review is not a rerun or independent certification.

Saved Wikipedia collections from reviewed browser releases can reopen after a chat-adapter update. Previously every change to browser/bridge.py invalidated the capture adapter hash, even when source capture semantics were unchanged.

The browser accepts only its current adapter hash or an explicit reviewed SHA-256 allowlist for browser-pyfetch-v1. Four historical revisions are currently listed in `COMPATIBLE_CAPTURE_ADAPTERS` in `browser/bridge.py`; that code is the authoritative compatibility list. Unknown adapters remain blocked. Future adapter releases need compatibility review before adding their hashes.

No capture, manifest, history, or source pin is rewritten. Engine, checker, renderer, raw response, revision-slot, served page, inventory and conflict checks still apply. This is compatibility, not authentication or proof that a source is true.

After deployment, reload the site to load the new runtime; compatible saved collections are checked again automatically. Do not clear browser storage. Collections with other provenance failures still need investigation or restoration from a valid backup. This cannot recover missing local data.
