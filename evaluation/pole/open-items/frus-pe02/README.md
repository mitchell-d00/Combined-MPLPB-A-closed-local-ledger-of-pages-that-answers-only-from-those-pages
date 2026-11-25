# FRUS-PE02: signed-letter instruction partial

Last reviewed: 2026-11-25.

This cycle starts from PR #97 evidence pin
`7618be370c334b082cb91c50eaf665f979ce5c1e`, after the separate
[report-pin repair](../../../report-pins/2026-11-25/README.md). Both cycles belong
to PR #101. PR #97's prerequisite reader modules, tests and evidence were absent
from main; they were imported byte-for-byte before applying this repair. The
PE-02 gain is measured against that pinned reader, not the older main reader.

## Freeze and custody

[freeze.json](freeze.json) binds the exact eleven inherited questions and eight
originals, six independently worded synthetic cases, the baseline runtime,
[candidate rule](candidate-rule.md), harness and separate local key. Inputs,
rule and key were sealed before implementation. The two permission-reprinted
originals were restored locally from their publisher URLs and matched their
existing hashes. All eleven baseline answer contracts reproduced the retained
FRUS-PE01 outputs. The worker receives no key path; the same operator prepared
the key and scored the retained outputs. OS isolation, independent custody and
blinded adjudication were not used.

The six new cases cover a signed instruction, wrong signer, initials-only
signature, quoted directive, negated directive and withdrawn source. The public
operator packet omits FRUS-D2 and FRUS-D3 bodies; its seal still requires the
matching originals before replay. No original, question or expected label was
changed to improve the result.

## Measured result

| Measure | Before | After |
|---|---:|---:|
| Historical positives complete | 1/4 | 1/4 |
| Historical positives with checked partials | 0/4 | 1/4 |
| Historical positives still missed | 3/4 | 2/4 |
| Inherited full-withhold controls | 6/6 | 6/6 |
| Inherited advice-only partial control | retained | retained |
| New standalone instruction positive complete | 0/1 | 1/1 |
| New negative controls with no claims | 5/5 | 5/5 |
| Total source propositions across 17 cases | 3 | 5 |

All 17 discovery passage arrays are unchanged. This is a verification gain;
the earlier 4/4 authored-anchor discovery measurement retains its original
scope. The new scorer verifies exact canonical citations and source identities
separately from the support classification. The final frozen comparison has
zero failed expected decisions and zero false-support decisions.

PE-02 retains one instruction proposition from FRUS-D16. The source displays
`Dear Ambassador Smith:`, a full Richard Nixon signature, a first-person instruction declaration,
the two explicit governing objectives and the complete delegation task. The
claim preserves instruction status and prospective wording. It does not certify
an agreement or execution. The exact first question about the separate Laird
letter remains in `missing`; the `RN` signature has no accepted full-name binding.

PE-04 stays complete with the same advice and presentation claims. Its missing-
presentation control retains exactly the same checked advice. PE-01's assessment
and forecast remain withheld at the same attribution boundary. The other ten
inherited contracts preserve all claim meanings, citations, qualifications and
diagnostics, apart from the expected new code fingerprint.

## General repair and retained failures

The reusable [source attribution checker](../../../../mplpb_answers/source_attribution.py)
binds a printed salutation and full signature in one eligible original letter.
The [instruction checker](../../../../mplpb_answers/documentary_instruction.py)
independently rereads canonical source bytes through the native checker, checks
complete paragraph predicates and resolves the explicit objectives reference.
The new claim carries actor, action, object, source voice, polarity, modality,
conditions, literal time qualifications and exact witnesses. It records an
instruction, never an accomplished event. Initials, competing letters, quoted
or denied declarations, unresolved conditions and insufficient budgets withhold.
This finite letter grammar is a starting class, not general attribution across
speeches, minutes or testimony.

Every attempted candidate is retained with its source delta, output and score:

- First candidate missed both targets because its unit filter excluded a lead
  grouped with the salutation. It made no new false-support decisions.
- Second candidate passed the frozen 17, but 16 additional developmental tests
  exposed two false voice bindings and one missed valid instruction. Their
  source and failing log remain retained; that candidate was rejected.
- Third candidate passed 17 developmental tests but again missed PE-02 because
  a bare reporting-verb filter mistook a capitalized institution name for a verb.
- Fourth candidate checks positive declaration grammar and reporting predicates,
  with complete native paragraph witnesses. It passes the frozen 17 and all 28
  targeted regression tests, including the prior advice, presentation and erratum
  controls. Noun/verb contrasts, changed actors, source mutation, ambiguity,
  execution questions and unchanged scan/output budgets remain covered.

No failed result was overwritten or relabeled. The added adversarial examples
are developer-inspected regression material, not unseen or independent transfer.

## Reproduce and inspect

Restore the two omitted originals following the
[original restoration instructions](../focus-extend/README.md#replay), require
their existing hashes at `PACKET/sources/FRUS-D2.html` and `PACKET/sources/FRUS-D3.html`, and use a separate custodian-held key directory. Run the
same sealed packet against clean baseline and candidate Git checkouts. Only the
scorer receives custody. Public receipts retain the complete private receipt
hash and omit permission-reprinted bodies and excerpts.

```sh
python tools/pole_frus_pe02.py run --packet PACKET --implementation CHECKOUT --output native.json
python tools/pole_frus_pe02.py score --custody CUSTODY --freeze evaluation/pole/open-items/frus-pe02/freeze.json --rule evaluation/pole/open-items/frus-pe02/candidate-rule.md --before before.json --after after.json --output scored.json
python -m unittest tests.test_signed_instructions tests.test_documentary_named_advice tests.test_documentary_presentation tests.test_documentary_errata tests.test_pole_focus_extend -q
```

[Sanitized native readbacks and failed attempts](native-readbacks.tar.gz) · [Original baseline score](baseline-score.json) · [Final development score](fourth-candidate-score.json)
· [Archive validation](validation.json) · [Standing direction and next cycle](maintainer-direction.md)

The archive receipt distinguishes the tested implementation commit/ZIP from
later evidence-only edits and deployment checks. Independent historical
accuracy, independent semantic adjudication, outside-custodian scoring and
native OOCC remain **NOT_RUN**. Broader wording, unfamiliar collections and
shared cross-document attribution still need separate frozen evaluations.
