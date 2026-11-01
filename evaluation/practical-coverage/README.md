# Practical answer coverage: 2026-10-31

> **Later experimental work (2026-11-01):** The [source-evidence graph proposal](../../docs/DETERMINISTIC_EVIDENCE_GRAPH.md) adds generic, provenance-gated relation types and scripted synthetic-user exercises. It does **not** overwrite the historical 6/59 or turn the old questions into an independent holdout. A new exact-head retest and review are required to report an updated score.


> **Historical evaluation snapshot.** The 6/59 (10.2%) result belongs to the 2026-10-31 exact implementation. The proposed [operational evidence extension](../../docs/OPERATIONAL_EVIDENCE.md) adds generic bounded relation forms, but does not alter this report, the frozen inputs or any historic result. Only a separately pinned, reviewed rerun can establish a later coverage figure.

This is a focused coverage repair, compared with current main at
`251e918340c8cfe700b1157d5367e4af0a02bec6`. Historical reliability reports are
preserved. The original, held-out and adjacent question sets have already been
inspected and are **development data**. “Held-out” here is the frozen filename,
not a claim of an uninspected evaluation.

## Observed supported-answer results

| Frozen set | Before supported returns | After correct returns / answerable | Coverage | Wrong returns | False refusals | Answerable ambiguities |
| --- | --- | --- | --- | --- | --- | --- |
| Original | 0 | 3 / 32 | 9.4% | 0 | 29 | 0 |
| Held-out | 0 | 2 / 19 | 10.5% | 0 | 15 | 2 |
| Adjacent | 0 | 1 / 8 | 12.5% | 0 | 7 | 0 |

The zero-return failure is repaired on each set, but coverage remains low:
6/59 answerable questions return (10.2%). Return precision is 6/6 on these
inspected cases; this small development result is not a general accuracy claim.
Before precision is undefined. Refusals and ambiguities are never counted as
correct answers. There are no newly wrong returns across the complete 154-case
evaluation (106 pottery, 28 adversarial development, 20 inspected SQuAD cases).
The existing adversarial and inspected SQuAD outcomes are unchanged, 28/28 and
20/20 respectively. SQuAD coverage was already repaired on current main before
this change; that improvement must not be attributed to this patch.

The shared evaluator's frozen correctness proxy checks returned document identity.
It does not prove semantic support. The six new quoted statements were additionally
reviewed against their questions:

| Case | Requested relation | Verbatim returned statement |
| --- | --- | --- |
| op01 | Burner candling duration | Light both burners on low and candle for an hour. |
| op03 | Resistance measurement interval | Measure each circuit with a multimeter twice a year and replace the set when resistance has risen by ten percent. |
| od08 | Clay maturing at cone 6 | White stoneware, bag code WS, matures at cone 6 and shrinks twelve percent. |
| h09 | Sieve mesh | Pass twice through an 80 mesh sieve. |
| h12 | Slurry spreading depth | Spread the slurry two fingers deep on a plaster batt and turn it when the underside peels away clean. |
| c04 | Clay suitability for sculpture | Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying. |

These are local source declarations, not externally verified pottery guidance.
The shelf-post grammar also recognizes h10, but both the loading page and the
eligible derived checklist support it. It correctly remains ambiguous rather
than choosing the frozen gold document. Equal values do not erase multiple owners.

## Implementation boundaries

`mplpb_answers/practical_evidence.py` adds seven bounded relation grammars. Values
are extracted from complete body sentences; no document IDs, benchmark IDs, fixed
answer values, headings, or scope declarations supply an answer. Variants beyond
the declared grammar abstain. Tests change source values to exercise extraction
rather than merely replaying the corpus's answers.

The extension uses the existing candidate/provenance pipeline, including current
status, sealed external-delivery policy, origin depth, not-for restrictions, source
hashes and ancestry. The full practical question reaches the gate so declared
exclusions are not discarded. Existing literal retrieval queries are unchanged.
The preexisting strict path, procedures and archived core retain their contracts.

This is deliberately finite grammar coverage, not general procedure understanding.
Unknown paraphrases and diagnosis still abstain. No medical instruction grammar,
implicit heading-to-body inference, automatic corpus rewriting, relaxed gate, top-one
winner selection, or broad lexical answer shortcut is introduced. General coverage
needs additional relation grammars or reviewed source-authored structured evidence,
followed by a new sealed evaluation. Five more specialists cannot manufacture
missing source support.

## Reproduce

From a git checkout with the baseline commit available:

```sh
python -m tools.evaluate_practical_coverage
python -m unittest tests.test_practical_evidence tests.test_literal_evidence tests.test_answer_reliability tests.test_answer_support tests.test_procedure_constraints -q
python -m unittest discover -s tests -q
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
node crawler/test_worker.mjs
```

The evaluator compares the baseline support implementation using unchanged statement/procedure/literal runtime
helpers and refuses if those helpers differ. CLI registration may evolve independently. `before.json` and `after.json`
include code SHA-256 pins, frozen input hashes, metrics, individual outcomes,
reasons and support spans. Source pages and labels are not rewritten. The [specialist work coordinator](../../docs/SPECIALIST_CONTINUITY.md) is now
implemented separately. Its deterministic development fixtures do not establish
multi-agent performance. Adding the `work` CLI changes the recorded CLI module
hash; answer results remain unchanged.

Validation: all 678 Python regression tests pass; the 36-test focused run also
passes. UI script, browser transport, JavaScript API and fixture crawler checks
pass. A new practical query returns the identical supported quote through the
desktop and browser bridge. No live deployed browser/runtime validation has been
performed for this patch; the required PR release checks remain separate.
