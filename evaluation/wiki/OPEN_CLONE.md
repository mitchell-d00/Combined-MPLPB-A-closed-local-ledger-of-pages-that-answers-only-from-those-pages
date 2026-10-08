# Open clone

Loose open-web records go in. An MPLPB folder comes out. One source is one page. The scope is that source's title, not its whole body. Pages loaded together do not gain a parent, and the footer says co-presence is not a relationship.

```
python3 tools/open_clone.py evaluation/wiki/loose evaluation/wiki/alien Cat Dog "Cat Dog" Tokyo
```

JSON, JSONL, and text are accepted. Title may be `title`, `name`, `heading`, or a `Title:` line. Body may be `body`, `text`, `extract`, `blurb`, `content`, or `summary`. A file with none of those is still sealed, as an untitled source, so it cannot claim the folder by scope.

`not-for` is `relationship; other source`. A question that asks for a relationship is set aside instead of answered from whichever page shares a word. Refusal stays inspectable: the reader names the page, or says not in the corpus, and does not merge sources.

This is the not-made-by-me path. The words come from the files you point at. The formatter does not write the corpus. It also does not label a human evaluation.
