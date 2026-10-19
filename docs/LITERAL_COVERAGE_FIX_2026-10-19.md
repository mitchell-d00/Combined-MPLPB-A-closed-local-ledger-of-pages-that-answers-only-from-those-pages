# Literal evidence coverage and external-profile regression — 2026-10-19

## Scope

The default supported-answer path retains the existing sealed MPLPB core, source provenance, hash checks, ambiguity behavior and abstention requirements. This change adds three *bounded* question forms to the separate `mplpb_answers.literal_evidence` layer. It does not add an LLM, rewrite archived sources or convert unsupported lexical candidates into answers.

## What changed

1. **Classification branch**: Recognize questions asking which branch of a named discipline classifies named problems by difficulty and relationships among classes. Require one affirmative body sentence that names the branch and explicitly describes *both* the classification and class relationship. The matching branch is quoted from the original source sentence.
2. **Population center**: Recognize questions asking where a named country's named population was largely/mainly centered. Require an affirmative body sentence that ties the named population to concentration in the stated country's regions. Do not infer geographic answers from neighboring sentences or another group.
3. **Legal framework definition**: Recognize explicitly defined law bodies supported by a directly matched sentence. A concrete example clause may use ordinary `or` wording; this narrowly scoped rule does not relax the legacy general disjunction filter.
4. **External-profile test**: Fix a previously incorrect expectation. An eligible depth-zero page with no restriction is allowed for external delivery; `external="no"` must be refused. Tests now cover both restricted and permitted cases, plus depth constraints.
5. **Regression check**: Re-run the already-inspected 20-item SQuAD excerpt (10 answerable, 10 unanswerable) as developer-regression material; assert 10 supported returns, 10 correct non-returns and zero wrong returns. Include negative near-matches for mismatched topics, groups and countries.

## Reproduce

```sh
python3 -m unittest tests.test_literal_evidence tests.test_answer_reliability tests.test_answer_support -q
python3 -m tools.evaluate_literal_coverage
python3 -m unittest discover -s tests -q
```

The test data are from an *inspected development excerpt*, not untouched external validation. A pass proves these exact source/question combinations are handled, **not** general semantic understanding or arbitrary-corpus accuracy. Full GitHub Actions also checks the JavaScript API, browser transport, source boundaries and the actual Python/WebAssembly build.

## Boundaries and migration

- Matching requires directly eligible source-page bodies, not the title or scope as evidence.
- Negated, hypothetical, quoted-instruction and nonmatching relations must not be promoted to answers.
- Multiple or conflicting supported pages remain ambiguous; unknown forms abstain.
- No sealed historical core files, pinned reference artifacts, saved browser state formats, API contracts or network permissions are changed.
- This note is the change record. Historical evaluation files are preserved unmodified.
