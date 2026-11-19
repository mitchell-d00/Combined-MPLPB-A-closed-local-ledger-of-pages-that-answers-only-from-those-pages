# Checked prose rule classes

Last reviewed: 2026-11-19.

These rules extend existing documentary extraction and independent verification. They do not create another answer engine. See [AGENTS.md](../AGENTS.md#general-class-fixes-never-benchmark-specific-passing) for the mandatory prohibition on benchmark-specific runtime branches.

## General failure mechanisms

* Correspondence headers and salutations were being consumed as the grammatical actor of the first sentence. Leading letter/mail layouts now supply **boundaries only**. Every prefix and source coordinate remains intact and available to quotation/conditional checks. The writer named in a header is never substituted for the sentence actor. Only leading recognized layout is handled; nested and incomplete communications remain conservative.
* Polite source-inspection requests and non-factual instructions could become extra factual obligations. A finite question view recognizes classes of request scaffolding and generic documentary attribution. Named speakers, conditions and extra factual questions remain. The complete original question and profile still govern eligibility, final checks and output; this view cannot change permissions or author a new query.
* Active and passive clause forms had asymmetric coverage. Exact positive passive actions, including written-by, now enter the independently reread observation scan. Literal Unicode capitalized actor spellings are allowed without resolving identity. Passive denials remain alternative evidence that blocks complete active acceptance; they are not silently dropped. Pronouns and modal/qualified actors remain unresolved.
* Explicit because-of assertions were checked but could never close even an exact source-scoped why question. A bounded kernel rule now matches the complete question's subject and action against one independently derived explicit cause. Negation, a competing appearance or an unresolved pronoun counterstatement stops closure. A second similar appearance is not merged into the same historical event. Compound requests still require proof of every part; the rule cannot complete a larger question by itself.

Only existing source-attributed support is awarded. Event identity and historical truth remain unverified. No missing dispatch, receipt, cause, correction target or pronoun binding is supplied. Full contrary-evidence scans, provenance, current eligibility and display budgets remain enforced.

* Literal source-location questions now have their own finite rule. A question asking which source contains quoted words can establish **textual occurrence only**, including words inside a denial or quotation. The independent checker searches current eligible bodies, enforces code points and word boundaries with explicit whitespace wrapping, and requires a unique source owner plus a complete bounded search. It cannot answer an execution or causal question. Titles, metadata-only matches, multiple owners and over-budget evidence cannot establish a complete answer.
* Absolute source coordinates are retained when a retrieved passage begins partway through a document. A sentence position must not receive the passage offset twice. A separate long-document test covers this class without naming a historical benchmark case.
* Alternative-action detection uses the same finite active/passive form vocabulary, including irregular participles. Unparsed denials, reported wording and unresolved pronouns cannot be hidden because one spelling differs from the affirmative verb.

## Validation and failure cohorts

[Class tests](../tests/test_prose_rule_classes.py) use separate vocabulary and cover positive forms, named-attribution erasure, unchanged original questions, metadata-only sources, reported/conditional/negated statements, passive conflicts, Unicode actors, explicit causes and missing counterstatement identity. The initial test run and intermediate harness errors are retained in the versioned comparison evidence. The frozen generator/key are not edited to improve performance.

The custodian-only feature analyzer reconstructs the sealed generator draws, verifies every packet and the entire dice trace, then joins outcomes by structural feature. It is never mounted in the runtime and never grants source support:

```sh
python -m tools.dpercent_features --packets /path/public --custodian /path/private --score /path/score.json --out /tmp/new-feature-cohorts.json
python -m unittest -q tests.test_prose_rule_classes tests.test_dpercent_features
```

Family and rolled layout, wrapping, question structure, scope variants, line endings, extensions and distractor counts have separate denominators, missed-answer rates and false-alarm rates. Actor names and answer strings are excluded from feature labels. Some rolled values are inactive or overridden to retain necessary source context; use these as descriptive cohorts, not causal effects or independent accuracy. Comparison results are written to new directories. No general historical reconstruction success is implied.

The [versioned comparison](../evaluation/dpercent/2026-11-19-class-rules) preserves a rejected first iteration, including its lost historical partials and full-suite failure. A second candidate repairs source coordinates and expands literal-location and qualification checks. Never silently replace the failed iteration.

Literal matching must reject blank or wordless requests and enforce token boundaries against characters surrounding the **original source span**. Checking a clipped proposal alone is insufficient, even if the same requested word appears elsewhere in that source. Independent adversarial controls exercise padded requests, word prefixes, punctuation endings and forged clipped citations.

Header boundaries do not cancel header scope. The checker independently examines body-printed plan/draft/reported/quoted qualifiers and a bounded original preformatted prefix (2,001 characters; at most 17 physical lines). Folded fields, unknown field syntax, missing required header roles, unmapped layout and exhausted header context remain unresolved for semantic action proofs. An explicit physical separator allows indented body prose. Header spelling/BOM/CRLF variations do not erase qualifications. Literal word-location remains separately available because it establishes no execution.

Header role words such as `Date written` are not action predicates or second event appearances. Their values remain available to counterevidence checks. Explicit self-ascribed plan/example scope and HTML/Markdown quotation structure remain attached to the source. Unresolved self-refutations are shown as alternative evidence with unresolved targets; they neither establish historical corrections nor retire a ledger claim. Conservative scope attachment can withhold later prose in mixed records until its layer is established.

Neutral header topics are not additional event appearances in a causal scan. Metadata values containing relevant action or refutation wording remain reviewable; field labels alone do not supply predicates. Unresolved self-refutations block causal as well as actor-answer closure and are retained as alternatives. Markdown backtick/tilde fences, uncertain quote continuations and explicit structural example/plan annotations never authorize bare action claims. Textual location remains available in those layers.
