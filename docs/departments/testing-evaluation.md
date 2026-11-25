# Testing and Evaluation

Last reviewed: 2026-11-25.

Stable Test Index, frozen studies, baseline outputs, failures and transfer. Same-operator synthetic tests do not establish independent historical or semantic accuracy.

Implementation: `tests/, test_tools/, evaluation/, killtest/, training/`. See the [component routing map](components.json) for every tracked top-level component and the split ownership within shared packages. Existing paths remain in place.

Run or inspect:

```sh
python tools/bubble_wrap_review.py
```

Protecting checks:

```sh
python -m unittest discover -s tests -q
```

Measured status: Checked source7f6641d ran1,810 tests; first transfer16/24 remains failed, fresh composition24/24 is separately scoped.

Open work: Keep failed attempts, execution accounting, scoring amendments, source pins and custody limits visible.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)
