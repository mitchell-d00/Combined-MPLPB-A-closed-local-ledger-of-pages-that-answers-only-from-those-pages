# D12 solo post-freeze historical pilot

Last reviewed: 2026-11-23.

Strict Ask completed **0 of 19 answerable questions** on this draw. Native
search and a simple word-overlap baseline each surfaced every required passage
for **12 of those 19**, using three passages and at most 8,000 characters per
question. None of the five missing-evidence questions received a supported
answer. One returned an irrelevant comparison of two draft-stage telegrams.

## What was frozen

The engine was pinned at `c80e546ef6d04296a1c136e9fc4933057d79d071` on November
23, 2026 at 21:16:59 UTC. A seeded draw then selected six pairs of relatively
short cross-referenced historical documents from six different volumes of
*Foreign Relations of the United States*. The seed was
`56323410891661378`. Twelve volumes were attempted. Six contributed a pair,
four had no qualifying pair, and two returned HTTP 503. No pair was swapped
after question writing. [Protocol](protocol.md) · [Draw receipt](draw-receipt.json)

The 24 questions and 36 exact anchors were authored against the selected
documents. They cover six direct facts, five cross-document comparisons,
one change from draft advice to later instructions, five qualifications,
one attributed disagreement, and five evidence gaps. The source packet and key
were sealed at 21:19:49 UTC. The [local custody commit](custody-commit.txt)
commits their digests before execution began at 21:20:34 UTC. The key was
held outside the runner input folder. The same operator drew the sample,
authored and reviewed the key, and ran the test. The local commitment records
the order of operations. Independent custody and human adjudication remain open.
[Hash manifest](pre-run.sha256) · [Questions](inputs/questions.json) ·
[Revealed key](custody/key.json)

The source manifest records publisher URLs, immutable XML volume revisions and
hashes, original byte ranges, and projection hashes. The retained XML
fragments are exact slices of the published volumes. The runner reads prose
projected from those fragments, retaining the title, dateline and document
text, with normalized whitespace and editorial notes omitted. Each source
was sealed as its own ledger page with generic import metadata. No event
identifier, typed correction, answer key, or source link was added to the
native ledger. The draw used publisher cross-references for selection. Those
editorial links were not supplied to the reader as relational evidence.
[Source manifest](inputs/sources.json) · [Publisher's license](LICENSE.source.md)

## Results

| Discovery path | All anchors, answerable / 19 | All anchors, all cases / 24 | Exact anchors / 36 |
|---|---:|---:|---:|
| Simple word overlap | 12 | 17 | 25 |
| Native passage search | 12 | 17 | 23 |
| Sorter-prioritized native search | 12 | 17 | 23 |

All retrieval arms use the same eligible native passage chunks. The word
baseline counts distinct words shared with the question, excluding a fixed
stop list. Its tie-breaks use record ID and source offset. Sorter comparison
suggested both records in eight questions and changed none of the returned
passage sets. Three graphs reached their phrase-token limit. Neither ranking
found every anchor for any of the six cross-document comparison or revision
questions. Native search found every anchor for five of six direct questions
and all five qualification questions.

| Native path | Observed result |
|---|---|
| Strict Ask | 19 answerable misses, four clear withholds, one withhold with a nonresponsive partial. Zero supported-answer assertions. |
| Advanced automatic | Preserved all 24 strict contracts. Routed 23 to lookup and one to investigation. |
| Candidate lookup | Returned one candidate. The corresponding Strict Ask still withheld. |
| Expert investigation | Zero verified observations and zero traversed links. |
| Assisted without a model | Returned `reader_unavailable` for all 24. |

Taken together, 12 answerable cases had their full anchors present in the
native discovery probe, yet Strict Ask completed zero. This points to
question interpretation or proof admission as an additional bottleneck.
The retrieval probe runs alongside Strict Ask and does not establish which
passages reached a particular internal proof rule. On P05-1, lookup found
the source for the half-hour meeting and Strict Ask still withheld. On P06-2,
the native discovery probe found none of the four anchors that connect the
draft and later instructions with the same underlying telegram. On P02-4,
the partial comparison found shared wording in the preliminary telegrams
without providing the requested final wording. These are separate failure
classes to trace before proposing a repair. [Per-case score](score.json) ·
[Native outputs](raw/run.json) · [Sorter graphs](raw/sorter-graphs.json)

The repeat matched the scoring report, sorter graphs, Strict Ask contracts,
and all three discovery outputs exactly. The only raw-output changes were
fresh WorkStore receipt IDs. Both runs used the same packet and software.
There were zero operator interventions during the native runs. Time spent
on authoring and reviewing the key was not timed.

This draw samples two-document English diplomatic packets, with a preference
for relatively short records that already have an editorial cross-reference.
It includes one policy revision and one disagreement. It leaves multi-witness
historical reconstruction, event linkage accuracy, and live model assistance
unmeasured. Zero unsupported full answers came with zero full answers.
The sample measures behavior on these sources and questions. WorkStore notes were not loaded in this run.
A matched notes-on arm could measure how source-pinned notes affect passage
discovery before the same verifier reads the originals. A further post-freeze
draw should follow any repair.

## Replay

Run the archived commands from a clean checkout of the frozen engine, with
this study directory available at an absolute path. Replaying uses only the
retained input files and does not query the web. The seed and archived XML
catalog can reproduce the draw order, while remote availability can change.
The draw receipt supplies the pinned volume URLs and exact byte ranges.

```sh
study=/absolute/path/to/evaluation/d12/solo-post-freeze
(cd "$study" && sha256sum -c protocol.sha256 && sha256sum -c pre-run.sha256 &&
 sha256sum -c runner.sha256 && sha256sum -c inputs.sha256 && sha256sum -c run.sha256)
out=$(mktemp -d)
PYTHONPATH=. python "$study/run.py" "$study/inputs" "$out/replay" \
  --commit "$(cat "$study/engine.txt")"
python "$study/score.py" "$study" --raw "$out/replay/run.json" > "$out/score.json"
cmp "$study/score.json" "$out/score.json"
cmp "$study/raw/sorter-graphs.json" "$out/replay/sorter-graphs.json"
```
