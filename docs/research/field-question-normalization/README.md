# Field-access response paper

Last reviewed: 2026-11-20.

**Mitchell D. McPhetridge**, *From Paraphrase Refusal to Bounded Field Access:
A Reproduction and Engineering Response to Guarded Retrieval, Paraphrase
Blindness, and Evidence-Grounded Answering*, 20 November 2026, version 1.0.

[Markdown](response.md) · [Plain text](response.txt) · [PDF](response.pdf)
· [Hashes and renderer](manifest.json)

The paper reproduces the published pin's 150/150 canonical support and 0/750
paraphrase support, documents 900/900 corrected field-value matches with 200/200
negative refusals, and retains a harder frozen 1000-case comparison: 156 to 168
complete key-matched answers out of 420; 580/580 refusals; 252 positives still
incomplete. Native regression passed 1,482 tests and 52 public controls at the
recorded source pin. These are development measurements, not independent
historical validation or a deployed-release guarantee.

Attribution is explicit: McPhetridge's MPLPB implementation and pre-existing
native test/evaluation infrastructure, B-Tests wrappers and generators, and the
external evaluator's additional benchmark are separate contributions. The
supplied public package **does not include M6**, so M6 was unavailable for
inspection or execution. No M6 capability or private harness use is inferred.

[Full experiment and commands](../../../evaluation/field-question-normalization/2026-11-20/REPORT.md)
· [Expanded stress results](../../../evaluation/dpercent-expanded/2026-11-20/REPORT.md)
· [Usage](../../FIELD_QUESTION_NORMALIZATION.md)

Regenerate the formats from the source checkout:

```sh
python tools/make_paper.py --source docs/research/field-question-normalization/response.md --title 'From Paraphrase Refusal to Bounded Field Access' --author 'Mitchell D. McPhetridge' --subject 'Reproduction, attribution and bounded question normalization' --footer 'MPLPB field access | 20 November 2026 | Research engineering report' --invariant
```

The PDF renderer uses reportlab as a documentation-only dependency. The paper's
measured implementation is 9b5ff0c; later evidence/docs commits do not establish
a new independent experiment. Original papers, source documents and old reports
remain unchanged. The new paper itself is a dated report, not a current manual.
