# Delivery and Project Operations

Last reviewed: 2026-11-25.

Installation, releases, documentation, handoffs and the manual Al/Betty/Outside loop. Packaging or deployment alone does not establish runtime or semantic correctness.

Implementation: `pyproject.toml, .github/, handoff/, docs/, packaging and audit tools`. See the [component routing map](components.json) for every tracked top-level component and the split ownership within shared packages. Existing paths remain in place.

Run or inspect:

```sh
python tools/build_handoff.py --check
```

Protecting checks:

```sh
python -m tools.audit_documentation
```

Measured status: Exact-head release gates and postdeployment checks must be read from their actual Actions runs and PR report.

Open work: Freeze/test extracted artifacts, verify deployed bytes, and retain every NOT_RUN label.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)
