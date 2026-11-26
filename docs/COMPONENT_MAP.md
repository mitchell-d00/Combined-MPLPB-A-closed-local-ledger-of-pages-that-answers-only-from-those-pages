# Components and their homes

Last reviewed: 2026-11-26.

[MPLPB](MPLPB.md) · [Experimental Lab](EXPERIMENTAL_LAB.md)
· [Testing apparatus and evidence](TESTING_APPARATUS.md)

These are navigation homes, not file moves. A released component can also carry
experimental work on a candidate branch. Exact versions and measurements remain
in the **[Test Index](TEST_INDEX.md)** and its linked reports.

| Department / primary area | Components and purpose | Release status / protecting checks |
|---|---|---|
| [Reader](departments/reader.md) / MPLPB | `mplpb_answers/`: interpretation, proof, checked partials and citations | Released finite rules; Bunyip additions are candidate work until release. [Test Index](TEST_INDEX.md), answer/support and documentary suites |
| [Ledger](departments/ledger.md) / MPLPB | `mplpb_combined/`: records, revisions, provenance, eligibility | Released; [Test Index](TEST_INDEX.md), source-state and integrity controls |
| [Intake and Research](departments/intake-research.md) / Experimental Lab | Sorter/source mapping in `mplpb_work/`, `crawler/`, `reference_corpus/`, `training/`: prepare material and propose links | Sorter is shipped; proposed links and research are non-supporting. Cross-link [MPLPB import](MPLPB.md#how-to-add-documents). [Test Index](TEST_INDEX.md), sorter and candidate graph controls |
| [Work Coordination](departments/work-coordination.md) / MPLPB | WorkStore and coordinator modules in `mplpb_work/`: permissions, dispatch, receipts and continuity | Shipped interfaces; authority limited to covered adapters. [Test Index](TEST_INDEX.md), work/dispatch/continuity checks |
| [Applications](departments/applications.md) / MPLPB | `browser/`, launchers, CLI, UI, MCP and JavaScript interfaces | Shipped interfaces; optional models have separate prerequisites. [Test Index](TEST_INDEX.md), JS/HTTP, WASM, Chromium and installed-package checks |
| [Testing and Evaluation](departments/testing-evaluation.md) / Testing apparatus and evidence | `tests/`, `evaluation/`, `killtest/`: frozen studies, regressions and transfer; TeamBuilding/Thespian/onboarding guides | Apparatus, not reader capabilities; human onboarding NOT_RUN. [Test Index](TEST_INDEX.md), seals/schema/isolation/scorer checks |
| [Delivery and Project Operations](departments/delivery-operations.md) / MPLPB, cross-link Testing Apparatus | Packaging tools, workflows, documentation and handoffs | Shipped packaging; coordination is a manual operator process. [Test Index](TEST_INDEX.md), archive/handoff/docs/deployment checks |

The existing [machine-readable department map](departments/components.json)
assigns every tracked path to an owner. Its `entry_areas` and `department_areas`
fields connect the seven departments to these three pages. This map records
ownership and release boundaries; it does not duplicate test results.

Implementation paths, imports, commands, frozen archives and historical links
are preserved. Any future physical move needs a separate proposal with explicit
old-path/new-path entries and import, command, link and preservation checks.
There are no proposed or performed implementation moves in this pass.

## Follow a capability to its evidence

Use [MPLPB product](MPLPB.md) to run it, [Experimental Lab](EXPERIMENTAL_LAB.md)
to develop it, and [Testing apparatus and evidence](TESTING_APPARATUS.md) to inspect it.
Follow capability → implementation → test → result → retained evidence in the
[Test Index](TEST_INDEX.md#capability-to-evidence-map). Its existing machine
inventory records stable family IDs, responsible area/department, per-run pins,
checksums, custody and execution status. Navigation is not a new measurement.
