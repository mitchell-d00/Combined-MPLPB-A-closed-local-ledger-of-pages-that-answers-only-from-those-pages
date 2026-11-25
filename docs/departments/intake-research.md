# Intake and Research

Last reviewed: 2026-11-25.

Sorting, source mapping and proposed document relationships. Candidate links and generated tags are proposals until native verification; discovery is separate from proof.

Implementation: `mplpb_work/sorter*.py, source_mapping.py, event_candidates.py; crawler/; reference_corpus/`. See the [component routing map](components.json) for every tracked top-level component and the split ownership within shared packages. Existing paths remain in place.

Run or inspect:

```sh
python -m mplpb_work.sorter_v2 --help
```

Protecting checks:

```sh
python -m unittest tests.test_sorter tests.test_sorter_v2 tests.test_sorter_explorer -q
```

Measured status: Existing frozen sorter and corpus studies retain their own pins; no new historical-coverage result is implied.

Open work: Test source-linked proposals and distinguish discovered witnesses from proved relationships.

[Department directory](README.md) · [Test Index](../TEST_INDEX.md) · [Current evidence](../CURRENT_STATUS.md) · [Full package map](../PACKAGE_GUIDE.md)
