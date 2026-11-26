# Testing and Evaluation

Last reviewed: 2026-11-26.

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

Measured status: The earlier release evidence remains pinned to its tested source. The [local Cryptid programme](../../evaluation/cryptid/README.md) now records sequential date, wording, modality, identity, correction, link, structure and fixed-cap studies. Its [machine inventory](../../evaluation/cryptid/programme.json) separates executed, failed, consumed-transfer and unperformed work. Mitchell authorized publication in PR #105; final acceptance is failed (19/24), so merge and deployment are blocked.

Open work: Keep failed attempts, execution accounting, scoring amendments, source pins and custody limits visible.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)

Current local work: [reporting negation and prospective partial policy](../../evaluation/cryptid/revision3/REPORT.md). Keep reader gains, evaluation-policy decisions, unit-accounting changes and original strict-key failures separate. [The publication review package](../../evaluation/cryptid/revision3/REVIEW_PACKAGE.md) separates the tested source ZIP, evidence-only publication head, original strict-key failures and required remote gates.

[Bunyip](../../evaluation/cryptid/bunyip/README.md) preserves development, consumed and fresh transfer separately. Byte-identical raw-result storage recipes retain failed native/API attempts; protected exact-head CI determines final software readiness.
