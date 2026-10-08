# MPLPB browser front end

The front end follows the compact map, action controls, journal, modal sheets and
three visual settings of Mitchell's [Give It Back: The RPG](https://github.com/mitchell-d00/Give-It-Back-The-RPG).
The exact inspected reference is recorded below.

The entire front end lives in the root `index.html`: markup, styles and script.
It calls the existing local Python reader and gate. It does not implement a second
reader in JavaScript. Nothing is sent to a model or external service by the UI.

## Start

Extract the full ZIP first. Python 3 must be installed.

| System | Launch |
| --- | --- |
| Windows | Double-click `Launch_MPLPB.bat` |
| Mac / Linux | Run `sh Launch_MPLPB.sh` from the extracted folder |
| Any system | Run `python3 launch.py` (or `python launch.py` on Windows) |

The launcher starts the local server and opens http://127.0.0.1:8766 in your
browser. Keep its terminal running. Close it with Ctrl+C when finished.
If the browser does not open automatically, open that address yourself.

Opening `index.html` directly shows instructions to start the local reader. It
makes no requests in file mode. HTML alone cannot execute the Python ledger or
crawl local folders, so a Python server remains required for real decisions.
Do not publish this file to GitHub Pages expecting the local reader to run there.

For a different corpus or an occupied port:

```sh
python3 launch.py --root /path/to/corpus --port 8767
```

Choose “Your local corpus” in the selector. The launcher opens the selected port.
If you prefer to open the browser manually:

```sh
python3 tools/ledger_ui.py
```

## Controls

- **Explore:** browse actual records as tiles. Search title, ID or scope; filter
  eligible or blocked records. A retired, altered or withheld page stays visible
  with its reason, but its body cannot be opened through the UI.
- **Ask:** query the real reader. Its return, ambiguity or refusal appears above
  the gate's separate source cards. Clarification choices submit a new lexical
  question. They do not change the reader rule.
- **Source dialog:** read plain text and sealed metadata; ask about that scope.
  HTML from a source is not executed.
- **Revision tree:** inspect retained wiki captures, source dates, revision slots,
  hashes and the active local head. Stored verification dates are historical.
  Engine pin mismatches remain visible. The UI does not fetch, score or promote
  wiki revisions; the existing explicit CLI commands do that.
- **Journal:** up to twelve recent actions in this tab. Clear it at any time.
- **Appearance:** Fantasy, Sci-fi and Wasteland palettes, plus light/dark theme.
  These affect appearance only and use local fonts, not downloaded font services.

Keyboard: E Explore, A Ask, R Revision tree, J focus journal, Escape close source.
Shortcuts pause in editable fields and while a source dialog is open.

Only theme, visual setting, corpus key and profile are saved in browser storage.
Questions, results and source bodies are not saved there. UI selection counts
refer to records and eligibility, not truth, accuracy or an evaluation score.

## Validation

- 236 Python package tests passed, including ten HTTP UI tests.
- Front-end script syntax passed Node checking.
- Optional local script checks cover explorer setup, page controls, query results,
  clarification, profile changes, revision history, supplied experiment display,
  escaping, preferences, stale responses and file-mode behavior:

```sh
python3 tools/check_ui_script.py
```

Node is required only for that optional developer check, not to launch the UI.
These checks use a small local element stub and real App fixtures. They do not
render a browser. Visual layout and native browser interactions remain unverified;
cloud preview was previously blocked by automatic approval review over exposing
local repository contents. Windows launcher execution was not tested on Windows.

The reader patch and its tests from the earlier delivery are retained unchanged.
Frozen probe files, stored reports, source captures and papers are untouched.
No fresh live wiki score is claimed. This delivery is committed locally and has
not been published to main.

## Reference and walk back

Reference: Give It Back: The RPG, commit
`d4a2c2945f3894a6cdb11456c7744cd5d06b4c41`.
Adapted appearance tokens and layout patterns retain the upstream MIT notice in
[GIVE_IT_BACK_UI_LICENSE.txt](GIVE_IT_BACK_UI_LICENSE.txt). The RPG's world generator,
story and rules are not part of this front end.

Return to local commit `f08a1b5` for the earlier UI and corrected reader. Return to
published base `b3de809` to remove both UI deliveries and the name guard.
