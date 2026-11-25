# Work Coordination

Last reviewed: 2026-11-25.

Tasks, permissions, guarded dispatch and retained receipts. A receipt proves only its checked host event; it does not prove historical truth or unobserved execution.

Implementation: `mplpb_work/store.py, model.py, api.py, training.py and coordinator modules`. See the [component routing map](components.json) for every tracked top-level component and the split ownership within shared packages. Existing paths remain in place.

Run or inspect:

```sh
python -m mplpb_work --help
```

Protecting checks:

```sh
python -m unittest tests.test_training_coordinator -q
```

Measured status: Existing WorkStore/coordinator tests are included in the checked native suite; frozen experiments retain their original scope.

Open work: Retain manual authority, explicit permissions and verified readback.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)
