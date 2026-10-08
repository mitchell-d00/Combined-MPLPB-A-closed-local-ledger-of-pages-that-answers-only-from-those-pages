# Wiki live match

This is a clone-time check, not the pottery probes and not a human-labeled evaluation.

Simple English Wikipedia writes the pages. `evaluation/wiki/titles.json` names five fetched titles and three titles that must not be fetched. Those lists are the labels. They are fixed before the reader runs.

```
python3 tools/wiki_live_eval.py fetch
python3 tools/wiki_live_eval.py check
```

`fetch` loads the intro of each fetched title into `evaluation/wiki/corpus` and pins the live revision id and extract hash. `check` reads the live site again. If a revision or extract hash differs, it stops and does not score. If they match, it asks the frozen reader.

A fetched title should return that page. An absent title should be refused. A question that names two fetched titles must not return one page: shared words are not a relationship. Paraphrases are printed and do not count. Passing this check does not mean the system helps another person. It means the refusal and source pin still match the wiki that was loaded.

Text is CC BY-SA 4.0, Simple English Wikipedia contributors. Code pin: `3bac10f21a5b74e8aacbf9dada9773cfee25dcb0`.

## Current review status

The supplied snapshot failed the live extract hash check on 2026-10-08 and was not scored. Actual code and local-source verification remain incomplete. Loose imports declare human origin without authenticating it. Read [REVIEW.md](REVIEW.md) before interpreting results or using external delivery.
