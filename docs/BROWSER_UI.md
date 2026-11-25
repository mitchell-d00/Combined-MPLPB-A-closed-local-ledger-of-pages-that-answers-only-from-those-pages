# MPLPB browser front end

Last reviewed: 2026-11-25. See [current status and result-to-test index](CURRENT_STATUS.md). Dates and numeric results in historical validation sections retain their original scope; this review is not a rerun or independent certification.

Package role: [how this part fits Combined MPLPB](PACKAGE_GUIDE.md#delivery-and-packaging). The interface connects the ledger, reader, collections and conversation without merging their authority.

[Documentation index](README.md) · [Live application](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/)

The interface calls the same Python ledger, supported-answer layer, and provenance gate in desktop and standalone modes. The markup/styles/UI script live in root `index.html`; the standalone builder embeds that interface with a Python/WebAssembly worker. It does not implement a second reader in JavaScript or send requests to a model.

## Start

| Mode | Start and storage |
|---|---|
| Hosted standalone | Open the live site. Python runs in the browser; IndexedDB holds normal saved sessions and imported sources for that origin. |
| Downloaded standalone | Extract the browser ZIP and open `MPLPB_Browser.html`, or serve it over static HTTPS. Browser storage/runtime permissions are required. |
| Desktop source | Extract/clone the full repository, install Python 3.8+, then run a launcher below. Python owns the local filesystem save store; the browser retains UI preferences and resume pointers. |

| Desktop system | Launch |
|---|---|
| Windows | Double-click `Launch_MPLPB.bat`, or run `python launch.py`. |
| Mac / Linux | Run `sh Launch_MPLPB.sh` or `python3 launch.py`. |

Desktop mode opens <http://127.0.0.1:8766>. Keep the terminal running; stop with Ctrl+C. If the browser does not open automatically, visit that URL yourself. Opening the unbuilt root `index.html` as a file shows launcher instructions, not a working Python engine. GitHub Pages serves the generated `dist/index.html`, not that source file.

For a different desktop corpus or port:

```sh
python3 launch.py --root /path/to/corpus --port 8767
```

Choose **Your local corpus**. `python3 tools/ledger_ui.py` starts the desktop server without automatically opening a browser. See [installation](INSTALLATION.md) and [runtime requirements](BROWSER_RUNTIME.md).

## Ask about your own document

1. Choose **Use my documents** and create or select a collection.
2. Choose a UTF-8 `.txt` or `.md` file, or paste text. Review the title and text before importing. Leave the URL blank for a local document. The hosted browser can also try fetching a public HTTPS source.
3. Choose **Review imported source** to read the sealed page under the selected delivery profile, then **Continue to Strict Ask** and enter your question.
4. Open a citation to read its source. For a partial or unresolved result, **Next steps** can show matching pages, bring you back to the question, or open the collection inventory. Matching pages are labeled for inspection and appear below the separate Strict decision.

[Local imports, provenance, and collection storage](EXPLORATION_COLLECTIONS.md)

## Controls

Open **How to use** for the in-app path from a sample through importing,
reviewing, and asking about your own material. The [tool directory](TOOL_DIRECTORY.md)
links to examples for the browser, native CLI, specialist work, and integrations.

- **Explore:** filter/search local records and inspect eligibility reasons. Retired, altered, or withheld records remain visible with their reasons; their bodies cannot be opened through this inventory UI.
- **Ask:** request a supported answer. Eligible body statements must satisfy the bounded grammar. Reader decision traces and separate gate-source cards explain the result; gate matches do not turn refusal into support. Help questions can return labeled interface instructions.
- **Chat:** use deterministic conversation and source-bound topic discussion. **Guide me** opens the saved tutor; **Show my MPLPB** lists eligible titles. Suggestions for new questions prepare text for Send; explicit source actions can contact the selected online service.
- **Chat / Serious / Off-the-record free chat:** Chat clears active Serious scope while retaining sources; Serious uses loaded collections, with outside-scope references labeled separately. Free-chat message handling is ephemeral and does not fetch sources or save a transcript.
- **Build and search your MPLPB collections:** create collections, import permitted source text/URLs, configure the optional crawler, or clear selected named collections with confirmation. Bundled corpora are retained.
- **Revision tree:** inspect retained captures, revision slots, hashes, heads, and historical verification dates. Viewing history does not fetch sources or run an evaluation.
- **Source dialog:** show escaped plain text and sealed metadata. Source HTML is not executed. Inspecting a page does not itself establish a supported answer.
- **Journal:** up to twelve recent actions in this tab, separate from persistent chat transcripts.
- **Appearance / Monster helper:** visual palettes, light/dark theme, helper name/identity, and Reason Mode. Reason Mode opens existing decision details; it changes presentation only.

Keyboard: E Explore, A Ask, R Revision tree, J focus journal, Escape close a source dialog. Shortcuts pause in editable fields and while a source dialog is open. Chat Enter sends; Shift+Enter inserts a newline.

## Network and persistence

Local decisions and bundled reference operations need no internet after the complete runtime is available. Wikipedia `search`, `find`, and `import` use the selected service. The UI's automatic Wikipedia setting can acquire missing/exhausted topic material; general-web crawling requires a separately deployed backend and token. See [chat workflow](CHAT_WORKFLOW.md) and [collections](EXPLORATION_COLLECTIONS.md). The JavaScript API has its own explicit per-call network permission; it does not inherit the UI checkbox.

Normal sessions can resume after refresh. **Export transcript** saves conversation/pins, not the whole source ledger. **Restart MPLPB** clears the selected session while retaining sources. Clearing collections archives their retained files locally; it is not a storage purge. Off-the-record free chat has no saved transcript and cannot be resumed/exported.

In desktop mode, clearing browser storage loses resume/preferences but does not delete the server's saved source tree. In standalone mode, browser clearing/eviction can delete the sessions and captures themselves. Export important material and keep the same origin when continuity matters. [Capture compatibility](BROWSER_CAPTURE_COMPATIBILITY.md) is checked separately from storage availability.

## Verification and historical reference

```sh
python3 tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
```

These checks cover element-stub behavior, transport, and API integration; they are not rendered-browser tests. Use the [real Chromium runbook](BROWSER_TESTING_FOR_AGENTS.md) and [ZIP-first release gate](ZIP_FIRST_RELEASE_TESTING.md) for hosted baseline, generated candidate, persistence, and deployment checks. Results belong to the revision/run tested; Windows launcher execution and hardware/browser coverage need separate evidence.

The layout adapts Mitchell's [Give It Back: The RPG](https://github.com/mitchell-d00/Give-It-Back-The-RPG), originally inspected at `d4a2c2945f3894a6cdb11456c7744cd5d06b4c41`. Its MIT notice remains in [GIVE_IT_BACK_UI_LICENSE.txt](GIVE_IT_BACK_UI_LICENSE.txt). Its world generator/story rules are not included. [Publication history](PUBLISH_AND_ROLLBACK.md) documents the original UI delivery; [rollback](ROLLBACK.md) explains current recovery practice.

> Update 2026-11-16: The [public 52-case evidence suite](PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.

## Documentary question parts

Documentary answers show each question part, its existing verification status and
the numbered checked claims supporting it. Citations expose source IDs/hashes
and canonical offsets, with source-inspection buttons. Unanswered parts and
qualifications stay visible. Recorded arrangements describe what letters state,
not actual acceptance, execution or delivery. The outside-world confirmation
notice also appears on ordinary supported answers. See the [solo workflow](SOLO_RESEARCH_WORKFLOW.md)
and [current status](CURRENT_STATUS.md) for measured capabilities and limits.
