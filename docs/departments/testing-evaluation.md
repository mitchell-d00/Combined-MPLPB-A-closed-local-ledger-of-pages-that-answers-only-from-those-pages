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

Measured status: The earlier release evidence remains pinned to its tested source. The [local Cryptid programme](../../evaluation/cryptid/README.md) now records sequential date, wording, modality, identity, correction, link, structure and fixed-cap studies. Its [machine inventory](../../evaluation/cryptid/programme.json) separates executed, failed, consumed-transfer and unperformed work. This branch is LOCAL_ONLY; these experiments have not been published.

Open work: Keep failed attempts, execution accounting, scoring amendments, source pins and custody limits visible.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)
