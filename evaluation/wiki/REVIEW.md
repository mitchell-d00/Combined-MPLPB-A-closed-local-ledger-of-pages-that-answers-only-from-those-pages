# Review status — 2026-10-08

This supplied package is published as an experimental external-text smoke test. It is not independently labeled evaluation or a verified live match. Source files and the supplied manifest were preserved without refetching or replacing them.

## Observed results

The supplied local corpus validates cleanly. At reader revision `3bac10f21a5b74e8aacbf9dada9773cfee25dcb0`, its five exact-title requests return the expected pages; Tokyo, Violin, Glacier, and Cat Dog refuse. The three reported paraphrases also refuse and are not scored. This checks lexical title ownership, not answer quality.

The real `wiki_live_eval.py check` exited 2 and did not score. Cat, Dog, and Paris had matching revision ids but different live extract hashes. On a second diagnostic request, stripping Paris's live extract matched the stored digest; Cat and Dog still differed. Moon and Photosynthesis matched their raw live extract digests. The original mismatched snapshot remains intact. Live page extracts may vary independently of article revision ids, so a revision id alone does not prove the loaded extract matches.

An offline score-path diagnostic with the live-match function mocked reported zero failures. That diagnostic is not live verification and must not be presented as a passing live run.

## Outstanding verification gaps

- The code revision check compares the manifest with a hard-coded constant; it does not verify actual imported module bytes, a clean checkout, or the running revision.
- The local page text being served is not compared with the source extract hash in the manifest. A live-site comparison alone cannot establish that the reader serves the corresponding source bytes.
- The loose-file importer declares every import `human`, including unknown-origin text. This is a formatter assumption, not authenticated authorship. External profile eligibility does not establish human authorship or trustworthy origin.
- Fetched/absent title lists supply labels; they are not independently written realistic questions or blinded human judgments. Do not turn these results into independent validation claims.

Before claiming a pinned evaluation, verify actual code bytes and the local source payload, record raw response snapshots and extraction normalization, and prevent unknown imports from automatically qualifying for external delivery. Preserve existing snapshots and failures when creating a new run. The existing frozen pottery and other evaluation artifacts were not changed.

## Rollback

This addition's parent is `3bac10f21a5b74e8aacbf9dada9773cfee25dcb0`. Find the commit with subject `Add experimental wiki ingestion and live-match tools`, then use `git revert <wiki-addition-sha>`, run tests, and push normally. Reverting removes this experimental package and its menu without undoing the supersession or provenance-gate fixes. Previously generated corpora outside the tracked package are unaffected.
