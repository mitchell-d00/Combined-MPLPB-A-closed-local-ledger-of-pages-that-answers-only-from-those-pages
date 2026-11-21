# Bounded field-question normalization

Last reviewed: 2026-11-21.

The strict pipeline accepts additional whole-question structures for literal
body fields. For example, `Tell me the custody location listed on record ARCH-91.`
and `Could you give me ARCH-91's custody location?` reach the existing exact-field
checker. Record-context questions (`In record ARCH-91, what does the custody
location field say?`) and record-labelled imperatives (`Record ARCH-91: report
the custody location.`) are also admitted through whole-question syntax.
This syntax layer does not infer field meanings. A subsequent bounded
[source-field alias layer](SOURCE_FIELD_ALIASES.md) can select eligible declared
labels such as Current Status for current state, with explicit ambiguity and
qualification checks. No semantic model is used; a status does not prove execution.

The original question remains the policy input and output question. An additive
`question_normalization` object records the literal field, record identifier,
canonical question, version and `normalization_is_evidence: false`. Whole-question
matching prevents dropping trailing conditions, time scopes, extra requests or
attribution. Canonical and normalized requests with contradictory explicit
selectors raise `ValueError`. The CLI reports the mismatch as an input error.
Unsupported wording remains unresolved under the existing contract.

The reader grammar and ownership, hash, delivery, retirement, conflict, correction,
budget and final source-state checks remain intact. Syntax recognition only
selects a field; source support still requires eligible source-body evidence.

## Reproduction

The unchanged public reproduction ZIP and before/after results are retained in
[the experiment directory](../evaluation/field-question-normalization/2026-11-20).
The public script generates isolated native ledgers and runs 900 positive plus
200 negative probes. Its CSV contains the 900 positives; negatives are generated
in the script. Its metric is native support, not independent historical truth.

From an extracted source checkout, with the public ZIP extracted to PACKAGE:

```sh
PYTHONPATH=. python PACKAGE/reproduce.py --output /tmp/new-field-run
python -m tools.evaluate_field_questions --package PACKAGE --fixtures /tmp/new-field-run/fixtures --output /tmp/new-field-score
python -m unittest tests.test_field_question_forms -q
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/new-public-evidence.json
```

Output directories must be new for the scorer. Preserve older results. These
fixtures are now known development material, not a hidden or unseen evaluation.
Reported gains apply to tested question structures, not arbitrary paraphrases,
entity resolution, historical reconstruction or independent semantic accuracy.
