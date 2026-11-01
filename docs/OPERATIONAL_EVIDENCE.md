# Source-bound operational relations: the coverage and error-class repair

**Status:** proposed strict-reader extension; not an independent validation of answer accuracy. The original three pottery question files, source pages, sidecar checksums, historical runs and score labels remain unchanged.

## Why the reported 6/59 is historical, not a target to relabel

The dated 2026-10-31 practical-coverage evaluation reported **6/59 answerable pottery questions (10.2%)**: 3/32 original, 2/19 formerly held-out, 1/8 adjacent. The 59 cases are the *answerable* subset of 106 pottery probes, not the whole probe count. Six supported returns were individually inspected, with zero observed wrong returns; 51 false refusals and two answerable ambiguities remained. Its document-identity oracle is not general semantic entailment verification. The nominal "held-out" set was already inspected and is now development data.

**Keep this number and the original artifacts.** A later software update does not revise an earlier measurement. A new measurement must record an exact code revision, unchanged frozen-source/question hashes, detailed before/after result rows, complete answer spans and a human check of each new return; label the reused 59 as development data. There is no new validated percentage merely because more question patterns are implemented.

## Failure classes and their correct dispositions

| Class | Example | Repair strategy | Remains forbidden |
| --- | --- | --- | --- |
| C1: source found, relation not interpreted | "What does it mean if the guard has gone over?" vs. explicit "If the guard has gone over, …" | Match an exact antecedent and copy the **entire original consequent-bearing sentence** | Stripping *not*, elapsed time, conditions, or guessing synonyms |
| C2: a list/conjunction is not one subject | "Which bodies must be kept in separate buckets?" vs. "Keep red and white bodies in separate buckets; …" | Preserve the entire object list and qualification verbatim | Inferring that other bodies must be separated |
| C3: lexical hit mistaken for answer | Kiln-room temperature vs. kiln or pyrometer temperature | Apply a complete source subject/relation check after retrieval | A top-scoring page, scope or heading as proof |
| C4: antecedent/qualifier lost | "if the batch is *not* sealed" vs. "if the batch is sealed" | Exact normalized condition, with negation and time intact | Removing modifiers to make a match |
| C5: competing eligible source declarations | Two pages give the same or different policy or process instruction | Retain all eligible owners; return ambiguity | Selecting top-1, even when the values agree |
| C6: provenance, status or policy bypass | Damaged seal, retired basis, depth or not-for restriction | Reuse the complete-question provenance gate and recheck the servable ledger | Opening a source that the gate excluded |
| C7: unsupported discourse or missing knowledge | "What temperature should this room be?" with only kiln firing records; quoted or hypothetical sources | Refuse, distinguish no interpretation from no eligible source in diagnostics | Completing unknown steps or assuming the corpus proves the world |
| C8: historical result or proxy mistaken for accuracy | 6/59 and a document-ID correctness proxy | Pin the exact evaluated revision and record per-case quotes, review and data provenance | Retroactively revising historical score files or calling developer regression independent |
| C9: reused derivations mistaken for independent validation | Several derived pages repeat one assertion | Retain ancestry and machine-origin depth, mark shared evidential roots | Letting repetitions or human clicks automatically certify truth |
| C10: correction without dependent work review | A source is superseded, but dependent task notes remain active | Preserve supersession history and surface the revision surface for review | Silently converting inherited work state to verified fact |

C9 reflects the epistemic-laundering limitation documented by MPLPB-SWARM-013 and Networked MPLPB; C10 follows the attached *Continuation Must Preserve Revisability, Not Truth*. Neither is solved by a new text matcher. The source's structure, its origin and its reality-checking status remain distinct.

## Implemented bounded contracts

The default strict reader still has **no general-language model**. New code in \`mplpb_answers/operational_evidence.py\` recognizes two *generic* finite families. It is not keyed to the frozen probe IDs, page IDs, fixed amounts or particular pottery terms.

1. **Conditional outcome**: \`What happens if CONDITION?\` or \`What does it mean if CONDITION?\` requires a body sentence \`If CONDITION, OUTCOME.\` The full condition (including negation) must match. It quotes the source's complete sentence rather than synthesizing or treating an instruction as executed.
2. **Separate storage**: \`Which OBJECTS must/should be kept in separate CONTAINERS?\` requires a body sentence \`Keep/Store LIST OBJECTS in separate CONTAINERS …\`. The complete list and any trailing qualification are returned exactly.

Both use source body text only, not titles, metadata or headings; hypotheses, speculative contexts and unrecognized question forms abstain. A changed source value changes the returned quote automatically. A page's authorship, external eligibility, origin depth, ledger hash, current/superseded state and declared exclusions remain enforced by the existing gate. Two eligible pages remain ambiguous, even with identical wording.

The extracted result's authority is **source-declared text**, not an independently verified process recommendation, safe operational instruction, or proof of outcome. It remains a finite grammar: anaphora, general diagnosis, unrestricted conditionals, implicit procedure ordering, temporal inference, synonymous antecedents and semantic interpretation of arbitrary material are not implemented. The original strict contract still returns the legacy \`return\`/\`ambiguous\`/\`not_in_corpus\` kinds; use the shared diagnostic pipeline to distinguish unsupported interpretation from evidence absence.

## Reproduction and release conditions

Run on the proposed exact revision:

\`\`\`sh
python -m unittest tests.test_operational_evidence tests.test_practical_evidence tests.test_policy_evidence -v
python -m tools.evaluate_answer_reliability --output /tmp/mplpb-operational-retest.json
python -m unittest discover -s tests -t .
python tools/check_ui_script.py
node tools/check_browser_transport.cjs
node tests/javascript-api.cjs
node crawler/test_worker.mjs
\`\`\`

Do **not** overwrite \`evaluation/practical-coverage/after.json\`: its score is an immutable historical snapshot. To report a new number, inspect the new retest JSON and publish a **separate** dated evaluation, with SHA-256 of frozen inputs, complete case outcomes, semantic review of each newly returned quotation, wrong-return and false-refusal counts, and the exact commit tested. Recheck the deployed/browser API and required extracted-ZIP tests separately before a release claim. Until those checks run, the change is **code proposed and regression tests authored**, not a measured uplift or live-deployment claim.

## Generalization beyond pottery

This fix addresses a form of error, not a pottery vocabulary. New conditional and separation forms may be reused with laboratory, archival, operations, inventory and fictional source corpora, provided the record is eligible and its **exact body** establishes the relation. Future expansions should be one independently testable relation family at a time: define what counts as an exact answer, invent changed-value positive controls, near-miss negative controls, qualifier retention, conflict/duplicate owner controls, gate/status/provenance controls, then run a separate external and human-scored evaluation. Never treat a larger source collection or more agent roles as a substitute for missing interpretation or evidence.

Related: [historical practical coverage](../evaluation/practical-coverage/README.md), [reliability analysis](ANSWER_RELIABILITY.md), [general assisted pipeline](GENERAL_ANSWER_PIPELINE.md), [user-built collections](USER_BUILT_COLLECTIONS.md), [source supersession](SUPERSESSION_POLICY.md), [evaluation index](../evaluation/README.md).
