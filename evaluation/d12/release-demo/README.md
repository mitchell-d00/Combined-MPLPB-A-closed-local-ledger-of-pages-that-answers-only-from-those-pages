# D12 documentary language release demo

Last reviewed: 2026-11-23.

From a Git checkout with the pinned baseline in its history, run the following command with Python 3.8 or later, `venv`, pip, setuptools 61 or later, and wheel already installed. Use a fresh output directory. The demo builds and installs two native wheels in separate virtual environments and runs offline.

```sh
python tools/release_demo.py --output /tmp/mplpb-release-demo
```

The runner compares the pinned baseline with the current commit. Use `--candidate <commit>` to repeat a specific run. Each interpreter imports its installed wheel and receives only the question and source packet. The outer runner checks the separate labels, exact citation text and hashes, the witness pages for each claim, and the full, partial, or withheld outcome. [Frozen fixtures](fixtures.json) · [Labels](labels.json) · [Input pins](pins.json) · [Pre-change regression failures](before.log)

Read `report.json` for the comparison, revision and wheel hashes, elapsed build and install time, and p50 and p95 query latency. The `baseline/` and `candidate/` folders retain each wheel, source archive, and native case-level responses with citations. Replay time includes temporary ledger setup and citation readback. To install the candidate wheel alone in your active environment, use `python -m pip install --no-index /tmp/mplpb-release-demo/candidate/wheels/*.whl`.

## Installed-wheel comparison

One local run on Python 3.12.14 on x86-64 Linux. The recorded baseline is `323492d` and the candidate is `6df82ed`. [Full measurements and revision hashes](results.json)

| Measurement | Baseline | Candidate |
|---|---:|---:|
| Expected outcomes matched | 20/40 | 40/40 |
| Full answers | 0 | 10 |
| Cited partial answers | 0 | 10 |
| Abstentions | 40 | 20 |
| False full answers | 0 | 0 |
| Exact citation readbacks | 0 | 70 |
| Query latency p50 / p95 | 9.277 / 10.624 ms | 6.509 / 8.917 ms |
| Wheel build and install | 3.291 s | 3.403 s |

The baseline abstained on all cases. The candidate recovered both receipt forms and reported the sender alone when a receipt was missing or retired. It preserved all 20 abstentions involving mismatched dispatch, parcel, or recipient, or wording that only planned receipt.

A second run reproduced both wheel hashes and all case responses and citations. Elapsed times vary between runs.

## What the rule proves

Given “Parcel BK-18 is listed as the court diary,” a dispatch recording that Ari Long sent the identified parcel to Noel King, and a receipt naming Noel King and the same parcel and dispatch, “They received it” binds to the named recipient and parcel within that receipt. The reader cites the catalog and dispatch for the sender, and all three records for receipt. If the receipt is absent or retired, the reader can report the sender and leave receipt open. Ambiguous or inconsistent packets withhold the combined answer.

## Limits

- The 40 authored cases share five fictional packets. Variations measure one documented class of three-record joins, local references, and several ways to ask about sender and receipt.
- The rule requires explicit dispatch and parcel IDs, one named recipient in the receipt, and finite statement forms. Additional eligible records, longer prose, and statements the rule cannot classify may prevent a match.
- The result establishes what eligible records say. General coreference, arbitrary multi-document synthesis, and independent historical accuracy remain unmeasured by this demo.
- Timings describe a small local, native Python workload. Browser, network, and large-collection latency are outside this measurement.
