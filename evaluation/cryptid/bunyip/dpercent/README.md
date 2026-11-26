# Bunyip through D%, Dice Bag and D20

Last reviewed: 2026-11-26.

The development target is broader ordinary-language understanding. The shared
question binder proposes the requested relation and arguments; eligible source
bytes and the existing native checker must still establish each claim. Memory,
provenance, admission, qualifications and citations are preservation requirements.

This extension reuses the unchanged `tools/dpercent.py` runner,
`tools/dpercent_worker.py`, Bubblewrap and `tools/dpercent_expanded.py` scorer.
`tools/bunyip_dpercent_packets.py` only authors packets; it is not another harness.
Dice Bag's public-packet/separate-key/seal/replay/reveal procedure is retained.
D20 supplies matched unique, competing, missing and retired-source conditions.

Every proposition has a canonical question and several ordinary forms on identical
source bytes. Both line-contiguous and paragraph-separated text are tested inside
the unchanged worker's preformatted import. This is not a structured-HTML gain.
The original question remains the scored target. Canonical probes, synonyms and
proof after revealed confirmation are diagnostics, never original-question gains.

| Development family | Released main | Before extension C5 | C6 | Controls withheld |
|---|---:|---:|---:|---:|
| Ownership | 2/8 | 2/8 | 8/8 | 27/27 |
| Classification | 2/8 | 4/8 | 8/8 | 27/27 |
| Opening time | 0/8 | 2/8 | 8/8 | 27/27 |
| Instruction | 0/8 | 4/8 | 8/8 | 27/27 |

C6 recovers **10 distinct original question strings /20 executions** versus C5.
There are no lost positive answers, unsupported additions or citation failures.
All 849 earlier answer contracts match the current PR baseline exactly; these
memberships represent 825 unique earlier inputs, not independent evaluations.
Conflict summaries remain conflicts, and instruction answers retain the explicit
instruction-only qualification. An instruction does not establish execution.

[Frozen baseline](baseline-freeze.json), [source audit](candidate-source-audit.json),
[candidate summary](candidate-development-summary.json),
[raw development/preservation](candidate-development-and-preservation.tar.xz).
The original D% base scores are retained alongside expanded literal-field scores.

The fresh packet uses separately written question structures, not new seeds in old
templates. Its authoring code is visible to the same operator: independent
preparation, blinding and semantic adjudication remain NOT_RUN. Open only after
the committed candidate ZIP is frozen, execute once, and retain every miss.
The initial preparation accidentally repeated development without `--transfer`;
that packet is retained and explicitly excluded from transfer evidence.

Reproduce using new paths, with the key outside the worker:

```sh
python -m tools.bunyip_dpercent_packets --out /tmp/bunyip-public --custody /tmp/bunyip-private
python -m tools.dpercent run --packets /tmp/bunyip-public --out /tmp/bunyip-run --implementation .
```

Score using the existing `tools.dpercent_expanded.score(public, custody, run,
output)` function. Before replay, verify the public seal, worker and key hashes.
The worker never receives the generator, pairing map, key, Git or host network.

[Tool-approval rejection](tool-approval-rejection.json) is an unexecuted storage
action, not a reader failure. The broad deletion was rejected; a later narrowly
scoped alternative verified exact committed duplicates before reclaiming scratch.
No frozen repository evidence or unique run was removed.

[Bunyip BB](../bb/README.md) is a separate consumed external benchmark.
[Test Index](../../../../docs/TEST_INDEX.md) remains authoritative.


## Once-only fresh result and remaining coverage

Candidate `7e272e5d9742931feef05fc004a84d6846a55f39` was frozen before opening.
Full source ZIP SHA-256:
`93dc3e10895c2670f1952b74840c9d187f5bcc3c942e0d9a0b6870c03fa15b89`.
Native bytes in the worker were extracted from that ZIP and match development.

| Fresh family | Main positives | C5 positives | C6 positives | Controls withheld |
|---|---:|---:|---:|---:|
| Ownership | 2/6 | 2/6 | 4/6 | 21/21 |
| Classification | 2/6 | 2/6 | 2/6 | 21/21 |
| Opening time | 0/6 | 2/6 | 4/6 | 21/21 |
| Instruction | 0/6 | 2/6 | 4/6 | 21/21 |

The candidate answers **three newly answerable original ordinary question strings**
versus C5, repeated across six executions, with zero lost support or unsupported
additions. Against released main, one ordinary question string/two executions is
a wording-only gain on an already-supported canonical proposition; eight other
new positive executions require source/proof reach and are reported separately.
No canonical rewrite or proof after revealed confirmation is credited to an
original question. [Original scores, per-case audit and wording list](fresh-summary.json).

All108executions completed and scored once on the frozen candidate:14/24positives,
84/84withholds,10positive misses,zero execution failures/budget stops/unscored
cases/citation errors. All-target perfect acceptance is **not** claimed. The ten
misses cover medial attribution wording, new category syntax, “at which time”,
and instructions lacking an explicit requested object. They remain backlog; no
repair followed opening. [Raw results and matched baselines](fresh-once-and-baselines.tar.xz).

Overlap is explicit: development140memberships represent88unique public inputs;
fresh108represent69. One-line sources are identical under lines/paragraphs labels
for ownership, classification and instruction. Actual field-line spacing varies
for opening-time sources. Thus the six new wording executions versus C5 represent
three question strings and four unique source–question inputs, not six independent
examples. Original inputs and labels remain unchanged; no tag/layout gain claimed.
[Development overlap](development-overlap.json) · [fresh overlap](fresh-overlap.json).

Independent preparation/blinding/history/semantics, outside-custodian scoring,
native OOCC and human onboarding remain NOT_RUN. Existing coverage gaps may remain
backlog for an incremental release; lost valid support/new unsupported claims
require investigation. Required exact-head software gates must pass before merge.
