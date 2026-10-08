# Patch canned

Combined MPLPB, cloned and run on 8 October 2026 from
https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages

This note records the experiment, the bug it exposed, and the fix. The reader change is in `reader-full-name-before-majority.patch`. It was not applied to the clone. The clone's own tests were left as they shipped.

## Problem

A page owns a question when its `scope` and `when-to-use` fields contain more than half of the question's content words (`mplpb_combined/reader.py`, `owners()`). Two or more owners stop as ambiguous. None means not in the corpus.

That half-rule is not exclusive. Two titles in one question are disjoint sets. The longer title can clear half of the combined question by itself. The shorter title never becomes a second owner, and the subset-drop never fires, because neither match is contained in the other. The reader then returns the longer page.

The fixed wiki kit hides this. Its two-title probe is "Cat Dog". Neither one-word title is more than half of the pair, so the probe refuses and the 19-row smoke test passes. Uneven titles fail.

A second, separate miss is user-focus. The wiki sealer sets both `scope` and `when-to-use` to the page title. A question that does not mostly repeat that title has nothing to own. Paraphrases are reported and not scored.

## Solution

In `decide()`, before the half-threshold may return one page: if the question contains every declared word of two or more current pages, stop as ambiguous.

- One fully named page still returns.
- A fragment still has to clear the existing half-rule.
- No rank, no blend, no new score.
- "Cat" still returns. "Cat Dog" still does not return, so the fixed kit stays green.
- "Phrynomedusa vanzolinii Hyundai Engineering and Construction" becomes ambiguous, which is what the two-title row requires.

User-focus is not fixed by weakening that rule. The capture should set `when-to-use` from the lead sentence, and set `not-for` to the other titles captured beside it, as `open_clone` already does. A relationship question is then set aside. A fixture that only shares the title should not be counted as an answer.

## Experiment

Repo: `/tmp/mplpb`. Package is standard library only. No install.

### 1. Documented studio queries

```
python3 -m mplpb_combined ask examples/studio "how fast should I heat raw clay on its first firing"
python3 -m mplpb_combined ask examples/studio "what is the glaze firing schedule for cone 6"
python3 -m mplpb_combined ask examples/studio "what is the capital of France"
python3 -m mplpb_combined validate examples/studio
python3 -m unittest discover -s tests -t .
```

| Question | Result | Exit |
|---|---|---|
| how fast should I heat raw clay on its first firing | return STUDIO-0002, bisque firing schedule | 0 |
| what is the glaze firing schedule for cone 6 | ambiguous, STUDIO-0003 electric and STUDIO-0004 gas | 2 |
| what is the capital of France | not in the corpus; capital, france on no page | 3 |

Validation: 25 records, 21 current, 4 retired, 0 errors. Unit tests: 220 passed.

### 2. Custom two-topic smoke, not the official entry point

This run called `capture()` with an empty paraphrase list, then `check(live=False)`, then a hand-rolled ask. It is not the official kit. Snapshot: `/tmp/wiki-random-two`.

Random English Wikipedia titles:

- 2026 Taça de Portugal final, revision 1371250509
- Hollies (1965 album), revision 1364510133

Scored rows: 7 pass, 1 fail. Local titles returned. External ask and gate withheld. Absent title `NotARealTopicXYZ` refused. The two titles together returned `WIKI-0001` instead of refusing.

Later user-style questions against that corpus, not part of the scored path:

| Question | Result |
|---|---|
| who won the 2026 Taça de Portugal final | return WIKI-0001, declared scope |
| who played on the Hollies 1965 album | return WIKI-0002, declared scope |
| what songs are on the Hollies 1965 album | return WIKI-0002, declared scope |
| what stadium hosted the 2026 Portuguese cup final | not in corpus |
| is the Hollies album related to the Portuguese cup final | not in corpus |

### 3. Official fixed kit

```
python3 tools/wiki_live_eval.py check --offline
```

Head snapshot `evaluation/wiki/captures/20261008T165537443813Z`. Scored 19/19, 0 failures. Titles Cat, Dog, Moon, Paris, Photosynthesis. Absent Tokyo, Violin, Glacier. "Cat Dog" refused (`not_in_corpus`), so the two-title row passed.

Paraphrases reported, not scored:

| Question | Outcome |
|---|---|
| domestic feline | not_in_corpus |
| earth only natural satellite | not_in_corpus |
| how plants make food from light | return |

Open clone:

```
python3 tools/open_clone.py evaluation/wiki/loose /tmp/wiki-alien Cat Dog "Cat Dog" Tokyo
```

Four loose pages sealed. Cat, Dog, "Cat Dog", and Tokyo all withheld on the external profile.

Live `python3 tools/wiki_live_eval.py run` did not score. Wikipedia returned HTTP 429, Retry-After 37. The checker left it unscored, which is its own rule. Exit 2.

### 4. Official functions, two random topics

`wiki_live_eval.capture(dest, api, spec)` and `check(live=True)`. The CLI `run` command only reads `titles.json`, so the random titles went in through the `spec` argument `capture` already accepts. API: Simple Wikipedia. Snapshot: `/tmp/wiki-official-two`. Live verification scored.

Fetched: Phrynomedusa vanzolinii (revision 9330670), Hyundai Engineering and Construction (revision 9900817). Absent: Robert Axelrod (actor), Ethereum.

Scored 8/9. Failures: 1.

| Mode | Question | Passed | Outcome |
|---|---|---|---|
| local title | Phrynomedusa vanzolinii | yes | return WIKI-0001 |
| external ask withheld | Phrynomedusa vanzolinii | yes | not_in_corpus |
| external gate withheld | Phrynomedusa vanzolinii | yes | not_in_corpus |
| local title | Hyundai Engineering and Construction | yes | return WIKI-0002 |
| external ask withheld | Hyundai Engineering and Construction | yes | not_in_corpus |
| external gate withheld | Hyundai Engineering and Construction | yes | not_in_corpus |
| absent title | Robert Axelrod (actor) | yes | not_in_corpus |
| absent title | Ethereum | yes | not_in_corpus |
| two titles must not choose one | both titles | no | return |

Paraphrases reported, not scored:

| Question | Outcome |
|---|---|
| what should I know about Phrynomedusa vanzolinii | return |
| explain Hyundai Engineering and Construction in plain words | not_in_corpus |

The same guard failed on the custom uneven pair and on this official-function uneven pair. The fixed five-title kit still passes because "Cat Dog" is balanced.

## What this does not claim

Hashes pin the stored revision. They do not authenticate authorship or check the facts. Paraphrase outcomes are observations, not a scored evaluation. The patch is the proposed reader change. It was not committed and was not run against the 220 tests.
