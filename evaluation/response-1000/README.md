# Response spelling audit

This development audit uses ten synthetic fixture topics and 100 primary questions
per topic. It is not independent evaluation or a claim of general language
understanding. Every fixture has five exact attribute statements.

Run from the repository root:

```sh
python -m tools.evaluate_response_1000 --output /tmp/mplpb-response-audit.json
python -m unittest discover -s tests -p test_spelling_suggestions.py -v
```

The matrix covers 250 direct questions, 250 phrasing variations, 250 misspellings,
and 250 unsupported or adversarial requests. Topic-selection calls are excluded
from the count. Each spelling suggestion is explicitly resubmitted as an
additional confirmation call. Source hashes and exact quotations are checked;
refusals count toward safety but not toward successful fact retrieval. Confirmed
corrections count as helpful only after an exact source-backed answer. Sessions
are reused for each topic, and their transcript chains are checked.

The spelling regression tests additionally cover social interruptions, reloads,
topic switches, stale suggestions, bare yes/cancellation, missing facts,
conflicting values, duplicate titles, altered/withdrawn/revised pages, delivery
profiles, excluded attributes, and the browser automatic-lookup path.

## User behavior

With a local topic selected, `what is its diamter?` offers a question such as
`What is the diameter of Moon?`. Choose or resend the offered question to run the
normal evidence checks. A bare `yes` does not confirm it. The original user text
remains in the transcript. The suggestion contains no source-backed assertion
and does not fetch new pages.

This is a closed grammar for pronoun attribute questions, including five common
attribute misspellings, `waht`, `whats`, `itt`, and `plz`. It never fuzzy-matches
names or pages. Names, numbers, negation, quotations, comparisons, and conditions
are not repaired by this mechanism. An explicit topic in the suggested question
prevents it from silently following a later topic switch. Other spelling errors
continue through the existing response paths.

## Observed development result

On the working tree based on `c8b073f`, all 1,000 primary cases passed their
category criteria, with 250 additional explicit confirmation calls. Direct and
phrasing questions each returned 250 exact source-backed answers. All 250 known
typo cases offered a correction and then returned the expected source quotation
after confirmation (baseline: zero typo recoveries). All 250 unsupported cases
still refused. This is a development regression set using the known typo grammar,
not a held-out spelling benchmark. See `summary.json` for counts and evaluated
source-file hashes. Full per-response records can be regenerated with the command
above.
