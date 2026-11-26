# Delivery and Project Operations

Last reviewed: 2026-11-26.

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

Current local source archives use [lossless ZIP storage](../../tools/cryptid_zip_delta.py) when space requires it: the unchanged base plus delta must reconstruct the exact tested full-ZIP SHA-256. This changes archive storage, not source content or publication permission.

[Three entry areas](../COMPONENT_MAP.md) lead to usable MPLPB, the Experimental Lab and the Testing and Training Apparatus. [Verified clean-install instructions](../../evaluation/newcomer-navigation/README.md) retain exact output and failures separately from human onboarding NOT_RUN.
