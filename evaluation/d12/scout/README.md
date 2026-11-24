# Scout

Last reviewed: 2026-11-24.

Scout measures how often the current MPLPB paths interpret previously unused
historical material and prove answers across documents. The first run used a
clean engine at `b53b7103b5d4491bc1f7db4bae9f6f50d9cee35e`. A random draw then
selected 12 linked documents from six volumes of *Foreign Relations of the
United States*. The previous D12 pilot's six volumes were excluded before
sampling. Twelve volumes were attempted. Six had no qualifying pair. The
draw kept the exact source fragments, original byte ranges, and projections.
[Protocol](protocol.md) · [Draw and source URLs](draw-receipt.json) ·
[Publisher's license](LICENSE.source.md)

The 24 questions comprise six direct facts, six cross-document relationships
or comparisons, six questions about qualifications, and six missing-evidence
controls. The questions, exact source anchors, key, and runner were committed
to a local custody bundle before the native run. The runner verified the
source packet and loaded the questions without reading the key. The same
AI-assisted solo evaluation prepared and reviewed the cases. [Custody receipt](custody-commit.txt) ·
[Questions](inputs/questions.json) · [Revealed key](custody/key.json)

## Native results

| What was tested | Result |
|---|---:|
| Fully answered direct facts | 0/6 |
| Fully answered qualifications | 0/6 |
| Fully proved cross-document relationships | 0/6 |
| Correct withholds on missing evidence | 6/6 |
| Advanced graph passes matching standalone Strict Ask | 48/48 |
| Second Advanced passes that changed route | 0/24 |
| Expert Investigation verified observations / traversed links | 0 / 0 |

Of the 18 answerable questions, 17 withheld and one returned a nonresponsive
partial. Strict Ask labeled 22 of the 24 requests as unsupported
interpretation. Only two questions produced a documentary plan. One mapped an
actual receipt-date question to temporal evidence and appropriately withheld.
The other mapped a difference in recommendations to a wording comparison.

That comparison is an important presentation miss. Both Melouza memos were
eligible and their wording could be aligned. A shared heading and a local
alignment left the actual policy disagreement open. Advanced preserved the
partial contract, and its presentation described the comparison as a
verified part. Scout gave it no credit for the relationship. A matched graph
certifies correspondence to the current strict result. The original question
still needs the correct proof rule. [Case review](review.json) · [Per-case score](score.json) · [Native outputs](native.json)

## Discovery and the quote probe

These discovery arms used the same eligible passage chunks, a matching
8,000-character limit, and the stated passage count. They run alongside
Strict Ask. Their coverage does not establish which passages entered a
particular native verifier.

| Discovery arm | All anchors on answerable cases | All anchors on cross-document cases |
|---|---:|---:|
| Word overlap, 3 passages | 10/18 | 1/6 |
| Native search, 3 passages | 10/18 | 0/6 |
| Word overlap, 12 passages | 13/18 | 2/6 |
| Native search, 12 passages | 14/18 | 3/6 |

The separate key-assisted probe ran after the original outputs were sealed.
Strict Ask verified 22 of 24 exact quote requests for anchors on the
answerable cases. The two failures both passed as split fragments. Passing
the frozen reference locations as hints yielded zero complete answers to
the original questions. This distinguishes quote readback from interpreting
a question or proving its requested relationship. [Locator outputs](locator-probe.json)

Scout samples only short English diplomatic records with archive
cross-references. It measures one post-freeze draw and used no configured
reader model. A repeat reproduced every result apart from fresh WorkStore
receipt IDs. [Repeat differences](replay-differences.json)

## Replay

From a separate clean checkout of the exact engine above, point to this
study directory by absolute path. Native execution uses the frozen packet
offline. The draw used the existing [D12 source draw](../solo-post-freeze/draw.py)
and the retained filtered catalog and seed.

```sh
scout=/absolute/path/to/evaluation/d12/scout
out=$(mktemp -d)
(cd "$scout" && for manifest in protocol pre-run runner inputs run; do
  sha256sum --quiet -c "$manifest.sha256" || exit
done)
PYTHONPATH=. python "$scout/run.py" "$scout" --output "$out/native.json"
PYTHONPATH=. python "$scout/score.py" "$scout" --raw "$out/native.json" --output "$out/score.json"
cmp "$out/score.json" "$scout/score.json"
```

The score command checks a replay against the revealed key and the recorded
claim review. With no raw replay supplied, it scores the retained original. A future engine run needs a fresh output
path and fresh claim review for any changed answer.
