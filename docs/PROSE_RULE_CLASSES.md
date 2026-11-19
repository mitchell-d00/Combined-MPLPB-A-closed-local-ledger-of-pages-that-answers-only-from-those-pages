# Checked prose rule classes

Last reviewed: 2026-11-19.

These rules extend existing documentary extraction and independent verification. They do not create another answer engine. See [AGENTS.md](../AGENTS.md#general-class-fixes-never-benchmark-specific-passing) for the mandatory prohibition on benchmark-specific runtime branches.

## General failure mechanisms

* Correspondence headers and salutations were being consumed as the grammatical actor of the first sentence. Leading letter/mail layouts now supply **boundaries only**. Every prefix and source coordinate remains intact and available to quotation/conditional checks. The writer named in a header is never substituted for the sentence actor. Only leading recognized layout is handled; nested and incomplete communications remain conservative.
* Polite source-inspection requests and non-factual instructions could become extra factual obligations. A finite question view recognizes classes of request scaffolding and generic documentary attribution. Named speakers, conditions and extra factual questions remain. The complete original question and profile still govern eligibility, final checks and output; this view cannot change permissions or author a new query.
* Active and passive clause forms had asymmetric coverage. Exact positive passive actions, including written-by, now enter the independently reread observation scan. Literal Unicode capitalized actor spellings are allowed without resolving identity. Passive denials remain alternative evidence that blocks complete active acceptance; they are not silently dropped. Pronouns and modal/qualified actors remain unresolved.
* Explicit because-of assertions were checked but could never close even an exact source-scoped why question. A bounded kernel rule now matches the complete question's subject and action against one independently derived explicit cause. Negation, a competing appearance or an unresolved pronoun counterstatement stops closure. A second similar appearance is not merged into the same historical event. Compound requests still require proof of every part; the rule cannot complete a larger question by itself.

Only existing source-attributed support is awarded. Event identity and historical truth remain unverified. No missing dispatch, receipt, cause, correction target or pronoun binding is supplied. Full contrary-evidence scans, provenance, current eligibility and display budgets remain enforced.

## Validation and failure cohorts

[Class tests](../tests/test_prose_rule_classes.py) use separate vocabulary and cover positive forms, named-attribution erasure, unchanged original questions, metadata-only sources, reported/conditional/negated statements, passive conflicts, Unicode actors, explicit causes and missing counterstatement identity. The initial test run and intermediate harness errors are retained in the versioned comparison evidence. The frozen generator/key are not edited to improve performance.

The custodian-only feature analyzer reconstructs the sealed generator draws, verifies every packet and the entire dice trace, then joins outcomes by structural feature. It is never mounted in the runtime and never grants source support:

```sh
python -m tools.dpercent_features --packets /path/public --custodian /path/private --score /path/score.json --out /tmp/new-feature-cohorts.json
python -m unittest -q tests.test_prose_rule_classes tests.test_dpercent_features
```

Family and rolled layout, wrapping, question structure, scope variants, line endings, extensions and distractor counts have separate denominators, missed-answer rates and false-alarm rates. Actor names and answer strings are excluded from feature labels. Some rolled values are inactive or overridden to retain necessary source context; use these as descriptive cohorts, not causal effects or independent accuracy. Comparison results are written to new directories. No general historical reconstruction success is implied.
