# Fix Log

Errors found by running the kill test, what caused each, what was changed, and what the rerun
showed. Nothing is overwritten: each earlier reader is kept at `killtest/v1/reader_v1.py` and
`killtest/v2/reader_v2.py`, its results beside it, and each earlier paper under
`docs/superseded/`.

## Summary

| | First probe set (56) | Held-out set (30) |
|---|---|---|
| Reader v1: correct / wrong return / wrong refusal | 41 / 0 / 15 | 12 / 4 / 14 |
| Reader v2: correct / wrong return / wrong refusal | 50 / 0 / 6 | 20 / 3 / 7 |
| Reader v3, with `not-for` (E6) | 50 / 0 / 6 | 22 / 1 / 7 |

A third set of 20 questions was written for E6 and run once: 15 / 3 / 2 with the field,
12 / 4 / 4 with the field ignored.

The fixes below were developed against the first probe set, so its numbers are no longer
evidence. The held-out set was written after the fixes and before the fixed reader was run on
it, frozen by hash, and run once.

## E1. Pages could not be found by their own words

**Error.** All 8 questions phrased from a page's prose were refused. "How long do I candle the
burners" has an answer in the corpus and the reader said it did not.

**Cause.** Ownership looked only at the `scope` and `when-to-use` fields. A word that appeared
on a page but not in those two fields did not exist as far as the reader was concerned.

**Fix.** A second step. When no page owns a question by declared scope, a page owns it if
every content word of the question appears on that page. Scope still goes first and still
wins. A return decided this way says so in its citation: `matched on prose, not on declared
scope`. The `external` profile leaves the step off.

**Rerun.** First set: 7 of 8. Held-out set: 3 of 8.

## E2. One stray word broke ownership

**Error.** Seven misplaced refusals. An ordinary word in the question ("long", "room", "load",
"bottom") sat in some other page's `when-to-use` phrase, that page claimed part of the
question, and the reader stopped.

**Cause.** A page owned a question only if it declared every word that any page declared.
I had also added a case the formula does not have: when several pages each declared part of
a question, the reader said "ambiguous". The formula says that when none own it, it is not
in the corpus.

**Fix.** A page owns a question when it declares more than half of the question's content
words. When two pages own it and one's matched words strictly contain the other's, the more
specific one wins. The added "split" case is gone: none own it, not in corpus.

**Rerun.** The four misplaced "ambiguous" answers on uncovered questions became two.

## E3. Firing, fired and fire were three words

**Error.** "Can I recycle my trimmings" did not match a page declaring "recycling trimmings".
"Did the firing reach temperature" did not match "reached temperature".

**Cause.** The only normalisation was a trailing plural *s*.

**Fix.** A light suffix stripper: plural, *-ing*, *-ed*, a doubled final consonant, a final
*e*. No word list, no synonyms.

## E4. Question words counted as content

**Error.** "How **long**", "how **much**", "how **many**", "how **often**" put a word into the
question that matched unrelated pages. A possessive *'s* was counted as a word of its own.

**Fix.** The four words joined the stop list. Possessives are stripped before tokenising.

## E5. Two constants removed

The rule that ignored words declared by more than half the pages, and the per-profile coverage
dial, are both gone. The first run showed the dial moving two answers across its whole range.
The one remaining constant is "more than half".

## What is still wrong, and why the fixing stopped

On the first probe set the reader still misses 6 of 56:

| Probe | Question | Why |
|---|---|---|
| op02 | what does it mean if the guard has gone over | "mean" is on no page, so no page has every word |
| om03 | the coils are sagging badly near the bottom of the chamber | the right page declares 2 of 6 words |
| om04 | can I recycle my trimmings from yesterday's session | 2 of 4; not more than half |
| om08 | should I be covering my teapot with plastic over the weekend | 2 of 4 |
| ot04 | can I fire glass in the kiln | several pages declare "firing" and "kiln"; ambiguous where not in corpus was right |
| ot07 | what cone does porcelain fire to | the same |

Each of these can be made to pass. Lower the threshold to "at least half" and om04 and om08
pass. Put "mean" on the stop list and op02 passes. I stopped here because the held-out set
shows what that kind of fixing buys.

On the held-out set the fixed reader is right 20 times in 30 and returns the wrong page 3
times:

| Probe | Question | Returned |
|---|---|---|
| h24 | who is allowed to use the gas kiln | the gas kiln firing schedule |
| h25 | how do I center clay on the wheel | the wedging page |
| h29 | how do I pull a handle | the drying page |

All three are decided by declared scope, not by the new prose step. Each asks about something
the corpus covers (the gas kiln, clay on the wheel, handles) from an angle it does not. The
page that declares the subject owns the question. The first reader does the same thing on the
same questions, and makes a fourth wrong return besides. So the first run's "no wrong page on
56 questions" was a property of those 56 questions, and the first paper should not have
leaned on it as hard as it did.

This is not a bug with a fix inside the rule. A rule that matches words cannot tell "the gas
kiln firing schedule" from "who may use the gas kiln". Loosening the rule to pass the six
remaining probes would add more returns of this kind, and tightening it to remove these three
would bring back the refusals that E1 and E2 removed. Continuing to adjust until one probe set
reads 100% would produce a reader fitted to that set and a number that means nothing.

## What would actually move it

1. Probes written by someone who has not read the corpus or the rule.
2. Refused and returned questions logged from real use, and read.
3. A `not-for` field: a page declaring what it does not cover. That is authoring, not matching,
   and it is the only one of the three that stays inside the formula. **Built: see E6.**

## E6. A page was returned for a question beside its subject

**Error.** Three wrong returns in the 30 held-out questions. "Who is allowed to use the gas
kiln" returned the gas kiln firing schedule. Each question was about a subject the corpus
covers, from an angle it does not, and the page declaring the subject owned it.

**Cause.** A page could say what it covers and had no way to say what it does not. Ownership
by declared words cannot tell a schedule for the gas kiln from a rota for it.

**Fix.** A new optional field, `mplpb:not-for`. A page lists a few words for subjects next to
its own that it does not cover. Before ownership is decided, a page is set aside for any
question containing one of those words, at the scope step and the prose step alike. The
refusal names the page and the word. Details that had to be settled:

- A word the page also declares in its scope is ignored in `not-for`, and the validator
  reports it (check C15). Scope wins over its own exclusion.
- The field enters the hash only when a page uses it. Every page written before the field
  existed keeps the hash it had.
- A revision inherits it. `write`, `revise` and `derive` take `--not-for`.
- `--ignore-not-for` reads as if the field were absent. It exists so the two can be compared.

Fifteen of the studio pages were given a `not-for` line.

**Rerun.**

| Set | Field ignored | Field honoured |
|---|---|---|
| First set, 56 | 50 / 0 / 6 | 50 / 0 / 6 |
| Held-out set, 30 | 20 / 3 / 7 | 22 / 1 / 7 |
| Adjacent set, 20, written for this fix and run once | 12 / 4 / 4 | 15 / 3 / 2 |

The field cost nothing: no question that had been answered correctly was lost, and all 8
covered questions in the new set were still returned.

The held-out set's failures were known when the `not-for` words were written, so its
improvement shows the mechanism works and nothing about how often an author will predict the
right words. The adjacent set is the measure of that, and there the field stopped two
wrong returns of four and caused one, leaving three.

**What is still wrong.**

| Probe | Question | Returned | Why the field did not stop it |
|---|---|---|---|
| h29 | how do I pull a handle | drying | Both words are in the page's own scope ("handles pulling away"). A word cannot be scope and not-for at once |
| a04 | how do I throw a cylinder on the wheel | wedging | The page declares "throwing" and "wheel". Its not-for said "centering" and "pulling walls", not "cylinder" |
| a07 | what glaze recipes do we use for cone 6 | gas kiln schedule | The electric schedule said not-for "recipes" and the gas schedule did not. Setting one aside left the other as sole owner. Without the field this was a harmless "ambiguous" |
| a10 | how hot does the kiln room get | ventilation | Not-for said "heating" and "winter". The question said "hot" |

Two things follow.

The field has the same weakness as the fields it sits beside. It works when the author
predicts the asker's words, this time the words of questions the page should *not* get.

And a07 is a new failure the field itself created. When two pages share a scope and only one
of them carries an exclusion, the exclusion hands the question to the other. Near-duplicate
pages need the same `not-for`. Recorded as FM-C9. A validator check for it is not built.

**Why the fixing stopped here.** Adding "recipes" to the gas page, "cylinder" to wedging and
"hot" to ventilation would pass a04, a07 and a10 and would prove only that I can read my own
results. The four rows above are left as they came out.
