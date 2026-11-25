# Ledger

Last reviewed: 2026-11-25.

Records, revisions, provenance and eligibility. Integrity and source eligibility do not authenticate source claims.

Implementation: `mplpb_combined/`. See the [component routing map](components.json) for every tracked top-level component and the split ownership within shared packages. Existing paths remain in place.

Run or inspect:

```sh
python -m mplpb_combined --help
```

Protecting checks:

```sh
python -m unittest tests.test_ledger tests.test_record tests.test_integrity_hunt -q
```

Measured status: Included in1,810 passing native tests at source7f6641d; specific withdrawal/corruption controls retained.

Open work: Keep authority prerequisites, profile restrictions and final state checks intact.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)
