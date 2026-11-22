# Historical 22 pattern expansion

Last reviewed: 2026-11-22.

The original 22 are two frozen, authored sets. Fourteen questions came from
the authentic-source challenge, and eight came from the government source
follow-up. The questions and evidence drafts were written during development.
The [article replay](../../tools/article_study.py) runs those existing
questions. [Original challenge](../unprepared-originals/2026-11-16/REPORT.md) ·
[Government follow-up](../unprepared-originals/2026-11-16-followup/REPORT.md)

This expansion uses the same source bytes, importer, delivery profile, and
12-passage and 8,000-character budgets. It adds ten groups drawn from the
old question topics. Each contains an exact-quote location request, a focused
direct question, a paraphrase of that question, and a boundary question that
requests an additional fact the selected evidence has not established.
The focused direct questions can ask a narrower question than their original
parent. The frozen parent set and its reports remain separate. The corpus
seals and the new question digest are checked before use, and the imported
ledger files are checked for changes after querying.

## Run

```sh
python -m test_tools.historical_patterns --output /tmp/new-historical-patterns
```

The runner records strict native output and any cited reference anchors. For
the two focused question arms it separately queries the bounded passage index
and records how many full anchors appeared. This probe measures passage
visibility under that query. The strict reader may consult sources through
other paths. Quote and boundary arms have no passage probe. A supported
result requires the native support flag and every drafted citation anchor
for that case to count here. The draft references are selective and authored.
Matching these anchors does not certify answer completeness or the correctness
of every additional claim.

## First run on main f9e71b9

| Arm | Native full support with all selected anchors | Other outcomes |
|---|---:|---|
| Exact quote location | 4/10 | 5 cited partial answers and 1 abstention |
| Focused direct questions | 1/10 | 2 partial answers, 1 conflict, 6 abstentions |
| Paired paraphrases | 0/10 | 10 abstentions |
| Extra claim and source-scope controls | 0/10 | 1 conflict and 9 abstentions |

Nine quote requests cited their designated anchor, including the five partials.
The standalone passage probe found all selected anchors for **7/10 direct
questions and 7/10 paraphrases**. The same ten groups produced one complete
direct answer and no complete paraphrase answers.

- **Fort Sumter date roles isolated a wording gap.** Both forms exposed all
  three anchors in the passage probe. The direct form supported a date
  inventory. Its paraphrase abstained.
- **The government records exposed several post-discovery gaps.** The probe
  surfaced the relevant excerpts for the direct contingency-note,
  Emancipation exceptions, Hayden survey, and Yellowstone lease questions.
  The strict reader abstained on each. These cases suggest testing separate
  rules for condition, source attribution, and permission with a limit.
- **Apollo 13 has a different diagnostic pattern.** The exact-quote request
  cited the anchor in a partial result. Neither normal wording surfaced it in
  the passage probe. This case calls for checking passage discovery separately
  from causal proof.
- **Declaration comparison illustrates a separate proof path.** Its direct
  variant cited both anchors in a partial answer even though the standalone
  probe surfaced neither full anchor under that wording.

The first execution and the execution with the passage probe returned
identical native contracts on all 40 cases. The extension measures development
behavior on known originals with authored questions. Independent historical
semantic review remains outstanding. [Frozen panel](questions.json) ·
[Per-case report](report.json) · [Raw answers and probes](native.json.gz)
