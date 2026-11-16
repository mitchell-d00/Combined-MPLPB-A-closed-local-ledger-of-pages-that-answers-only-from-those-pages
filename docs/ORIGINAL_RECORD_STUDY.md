# Original-record evaluation and review workflow

Last reviewed: 2026-11-16.

The next evaluation uses MPLPB's public original papers. It separates preparation,
sealed questions, execution and external review. Passing this protocol's software
tests does not establish independent historical accuracy or close every remaining
capability gap. The existing 52-case development suite and historical reports stay
unchanged.

```sh
python -m tools.historical_study prepare /tmp/new-study
python -m tools.historical_study seal /tmp/new-study /path/to/questions.json
python -m tools.historical_study run /tmp/new-study
python -m tools.historical_study score /tmp/new-study /path/to/reviewer-a.json /path/to/reviewer-b.json
```

Preparation verifies four existing original-paper byte pins and creates an empty
question template. A separate author supplies cases with `id`, `question` and
`required_source_ids`. Source IDs are the prepared `ORIGINAL-0001` style witness
IDs. Empty, duplicate, or invalid questions cannot be sealed. Keep genuinely unseen
questions outside this repository and separate from development work until the
study is complete. No unseen or independently authored questions are invented by
the preparation command.

Sealing pins source content, runtime questions, salted private source expectations,
implementation modules, evaluator bytes, profile, budgets and model settings.
Execution reads no gold labels. Changed source bytes, questions or implementation
are rejected. Strict responses and bounded expert evidence reports are retained
separately with measured CPU/wall time. Original source files are never revised;
the engine receives isolated documentary witness wrappers.

Runtime output and the generated review template are waiting for external review,
not graded successes. Reviewers submit explicit completeness, false-bridge and
source-accuracy judgments, exact pinned-source citations, rationales, and reported
labeling/correction seconds. Completed answers require citations. Blank or duplicate
review identities, missing judgments and fabricated citations are rejected.
Disagreements require adjudication. Source-coverage fractions measure required
witness retrieval, not semantic answer accuracy. Reviewer rates are submitted
judgments and times are self-reported, not independently measured observations.

The private gold file and secret commitment salt are mode 0600 in a private directory.
The public salted commitment avoids exposing small gold-label sets to hash guessing.
Share only the corpus,
runtime questions, seal and required code with the execution operator; distribute
review packets separately. This is payload separation and tamper detection, not
a filesystem sandbox or proof that the operator never saw the questions or gold.
Hashes and distinct reviewer IDs do not authenticate people or establish their
independence. Outputs retain `independence_verified:false`; genuine independent
validation requires outside participants and an auditable custody record.

After review, publish source receipts, questions, gold expectations, system output,
review submissions with consent, adjudication and score receipts together. Those
released questions then become public development examples. Do not publish private
material or personal data merely to make an evaluation inspectable.

Remaining technical limits are explicit: arbitrary implicit event reconstruction,
automatic semantic partial-message correction, unrestricted as-of/causal reasoning,
and independent external delivery/read/acknowledgement verification are not added
by this evaluation workflow. Current native expert/correction capabilities remain
bounded by their declared contracts. See [public tests](PUBLIC_EVIDENCE_TESTS.md)
and [expert investigation](HISTORICAL_EXPERT_PATH.md).
