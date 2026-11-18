# Reader-owned passage admission

Last reviewed: 2026-11-18.

`mplpb_answers/passage_admission.py` assigns atomic source-witness sets to existing native question parts. The existing `documentary_verify.py` remains byte unchanged and independently checks admitted proposals against eligible originals. Admission does not establish truth, event identity or a relationship.

All admitted exact source ID/path/hash/half-open spans share the original passage and character limits. Repeated identical spans are charged once. Distinct nested spans and different revisions remain distinct. Multi-passage proofs must fit together; final assembly uses the same ledger. An independent final citation guard applies to other answer paths as well.

Sorter classes explain inspection priority. Exact source ID/field/quote hints and explicit references/corrections can be considered for a relevant native question part. Shared wording and synonyms remain review-only; they receive no automatic slot or relationship traversal. Neither a class nor a ranking score bypasses source eligibility or verification. Optional API `source_hints` require exact pinned original locations and are non-authoritative.

Source-framed literal comparisons use a bounded reader discovery pass (at most32 records,6000-character prefix each,32 candidate pairs) and the existing comparison recognition rule to reserve content and framing witnesses. Fresh kernel verification remains required. This is a bounded existing grammar, not general historical semantic understanding. Native action and letter rules also reserve their multi-span dependencies by question part.

Relevant contrary evidence remains subject to the existing independent scan. If a necessary competing witness cannot fit, completion is withheld and the budget limitation is reported. Admission metadata includes exact admitted passages, reader roles, deduplication, blocked locators and review-only hints. Unadmitted candidates are explicitly unverified.

H05 is a development regression fixture, not a production routing exception. Its pilot recovered the same four Declaration source spans (4070 characters) at the original12-passage/8000-character limit despite high Darwin search hints. Generic two-part proofs, duplicate charging and over-budget counterevidence have separate controls in `tests/test_witness_admission.py`.

The frozen historical baseline remains2 complete answers out of22. The goal is22 correct outcomes: complete cited answers when established, or well-supported conflict/refusal where justified by originals. Generic retrieval, grammar and budget failures are not automatically correct. Complete-answer counts remain separate. Full rerun outcomes are pending at this implementation freeze; independent human and unseen-original evaluation are NOT RUN.

Reproduce focused controls with:

```sh
python -m unittest tests.test_witness_admission tests.test_sorter_suggestions -q
```
