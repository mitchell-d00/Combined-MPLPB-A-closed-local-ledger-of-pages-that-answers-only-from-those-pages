# Applications

Last reviewed: 2026-11-25.

Browser, desktop, command-line, MCP and JavaScript interfaces. A candidate preview is separate from deployed-site verification; automated journeys are not human usability results.

Implementation: `index.html, browser/, launch.py, tools/ledger_ui.py and interface tools`. See the [component routing map](components.json) for every tracked top-level component and the split ownership within shared packages. Existing paths remain in place.

Run or inspect:

```sh
python -m tools.ledger_ui --help
```

Protecting checks:

```sh
python -m unittest tests.test_ledger_ui tests.test_browser_bridge -q
```

Measured status: Checked source7f6641d passes JavaScript/HTTP, actual WASM and Chromium local-document import/review/Strict/inspection.

Open work: Twelve-person onboarding trial prepared separately; no human result yet.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)
