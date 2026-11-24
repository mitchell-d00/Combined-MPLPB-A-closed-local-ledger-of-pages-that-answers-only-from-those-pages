# Pole · the Frederick Douglass experiment

Last reviewed: 2026-11-24.

Pole is a seeded test for working up from simple questions to difficult
documentary proof. The experiment takes its name from Frederick Douglass,
whose autobiographies make a natural reference point for work on identifying
the speaker, attributing claims, and comparing documentary versions. The
generated cases use fictional records.

## Draw, freeze, replay, score

Run from an MPLPB source checkout on Linux. Pole uses the existing D% dice,
case generators and scorers. Its process receives a copy of one packet and
builds a disposable ledger. Keep custody in a separate location. The local
runner passes no key to the worker and records `os_isolated: false`. Run trusted
native implementations. Use the D% sandbox for its separately isolated studies.

```sh
python -m tools.pole catalog
python -m tools.pole prepare --packets /tmp/pole-packets --custody /tmp/pole-keys --seed 1818 --cases-per-level 16
python -m tools.pole run --packets /tmp/pole-packets --implementation /path/to/baseline --out /tmp/pole-baseline
python -m tools.pole score --packets /tmp/pole-packets --custody /tmp/pole-keys --run /tmp/pole-baseline --out /tmp/pole-baseline.json
python -m tools.pole run --packets /tmp/pole-packets --out /tmp/pole-candidate
python -m tools.pole score --packets /tmp/pole-packets --custody /tmp/pole-keys --run /tmp/pole-candidate --out /tmp/pole-candidate.json
python -m tools.pole compare --before /tmp/pole-baseline.json --after /tmp/pole-candidate.json --out /tmp/pole-comparison.json
```

The focus suite starts with single-field wording and scope controls, adds
distractors and source-role questions, then adds conflict, compound fields
and cross-document proof. The catalog suite covers all 75 executable D%
weakness classes at assigned levels. Use `--suite catalog --cases-per-level 40`
for a full catalog sweep. Select a single level with `--level hard`, or narrow a
sweep with repeatable flags such as `--family explicit_chain --family missing_bridge`.
Difficulty is a design choice based on the evidence obligation. Case counts,
expected answers and refusals are reported per family and level. The 15 documented
adapter and review gaps remain visible in the catalog.

Pin cases by adding `--pin-from PRIOR_PACKETS --pin-custody PRIOR_KEYS` and a
repeatable `--pin-case CASE_ID` to a new draw. Pole verifies the prior public
seal and custody, copies the selected original question and source files,
preserves the scoring key, and records the parent seal. Use a different seed
when the new draw would duplicate a pinned ID. The score groups fresh and
pinned outcomes separately. A fixed seed and configuration reproduce the
draw with the same generator. For exact replay across revisions, keep the
packet, key, dice and seal. `compare` checks the same case coverage and worker,
records changes in strict status, and flags new false support, lost correct
outcomes, new sorter failures and incomplete candidate execution.

Follow Dice Bag's draw/replay/reveal procedure, the D% balanced family
schedule, B-Tests' before/after accounting, and D12's requirement to keep
proof separate from discovery. Existing test inventories retain references
to the other research paths and their measurements. [Dice Bag](../dice-bag/README.md) ·
[D% weaknesses](../../docs/DPERCENT_KNOWN_WEAKNESSES.md) ·
[D12](../d12/README.md) · [Scout](../d12/scout/README.md) ·
[Combined MPLPB test index](../../docs/TEST_INDEX.md) ·
[B-Tests index](https://github.com/mitchell-d00/B-Tests/blob/e3a544b2e8ac37f5a23323025b264c18a15678f7/docs/TEST_INDEX.md)

## First rule repair

The reader could find an identified record but stopped at
`exact_field_missing` on requests that ask for the value recorded for a
named field. Both word orders express the same operation. One finite parser
rule reads the field and record selectors from the complete request, then
hands them to the existing exact-field verifier. The independently worded
regression also tests competing source values and changes in source
eligibility. The strict verifier continues to decide citation eligibility,
conflict and support. [Baseline regression failures](independent-wording-before.log) ·
[Rule implementation](../../mplpb_answers/relation_graph.py) ·
[Regression tests](../../tests/test_pole.py)

| Sealed development draw | Complete checked answers | Expected withholds | Other findings |
|---|---:|---:|---|
| Focus, seed 1818, 48 cases | 5/28 → 16/28 | 20/20 in both runs | All 11 targeted misses recovered. Two generic withholds became cited conflicts. |
| Catalog, seed 1852, 120 cases | 24/41 → 24/41 | 79/79 in both runs | All 75 inherited classes ran. No scored outcome or graph obligation changed. |
| Transfer, seed 1845, 25 cases | 8/15 | 10/10 | Five fresh target cases answered. The pinned conflict retained both source values. |

The matched runs retain zero new false alarms and zero execution failures.
Twelve focus positives still miss, covering date roles, reported statements,
partial corrections, wording changes and explicit request–dispatch–receipt
chains. The transfer draw also found an explicit-chain packet where repeated
phrase grouping hit the sorter budget. Keep that example for a targeted
replay before changing the sorter limit. Treat discovery, native proof,
reported conflicts, and independent historical accuracy as distinct measures.
The key is authored for synthetic development records. [Focus comparison](focus-comparison.json) ·
[Catalog comparison](catalog-comparison.json) · [Transfer score](transfer.json)

The exact operator packets, published development keys and raw outputs are
archived separately. Verify the hashes from the repository root with
`sha256sum -c evaluation/pole/evidence.sha256`. Extract to a new workspace
before replay. Each run receipt includes its native source hashes. The
candidate runs were made against a local working tree with the parser change
over `e3990bf`. Their working-tree hashes identify the tested code.
[Packets](packets.tar.gz) · [Development custody](development-custody.tar.gz) ·
[Raw replays](raw-replays.tar.gz) · [Checksums](evidence.sha256)

The committed source archive matched the retained comparison byte for byte.
The validation receipt records the historical replays, public controls,
Pyodide and Chromium checks, and the loopback retry for the full Python suite.
[Archive validation](validation.json)
