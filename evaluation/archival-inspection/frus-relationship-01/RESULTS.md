# FRUS Relationship 01 — unchanged-reader diagnosis

Last reviewed: 2026-11-28.

Verified main and PR #133 merge
`6942df4670196405797114cbe25317577c3118e1`. Case selection and protocol
were frozen at `bcd689ba54d17a479328bf10a40c75acd12fa0e1`.
The 77-case baseline and its source, runtime, and original grades stay
pinned. This diagnostic uses 11 consumed relationship questions plus
three passing location controls. It changes no reader or effect code.

## Results

The first stop on each relationship question was interpretation. The
documentary plan, named-reference parser and literal relation frame all
returned no route. For each two-link question, link 1, link 2 and the join
were all unrecognized. Strict emitted no relationship claims or citations
and did not enter its ranked relationship path. All **25/25** frozen
relationship anchors were nevertheless exact in projected text, eligible
under the original question, and wholly present in native indexed passages.

In the table, **B/P** counts target spans reached by the separate BM25 and
documentary prose rank probes. They use the unchanged question and
12-passage/8,000-character budget. **Docs** counts target documents in
those two probes. This is later diagnostic evidence, not Strict display.
Strict displayed 0/25 relationship anchors and 3/3 location anchors.
The evidence-supplied kernel returned no requested link certificates,
even where the rank probes located all the anchors. This tested the actual
native documentary relationship and action verifier. It did not supply a
replacement question or fabricate a source identity.

| Case | First stop | B/P spans | B/P docs | Evidence-supplied blocker or control finding |
| --- | --- | --- | --- | --- |
| DIRECT-01 | Interpretation | 2/2 · 2/2 | 2/2 · 2/2 | Eligible complete units still yield no certificate for Connally's response to d157. |
| DIRECT-02 | Interpretation | 2/2 · 2/2 | 2/2 · 2/2 | The subject and original memorandum are located, but the native kernel cannot certify the subject-line identification. |
| DIRECT-03 | Interpretation | 2/2 · 2/2 | 2/2 · 2/2 | Johnston's account and the Connally header are located. No native identification certificate. |
| DIRECT-04 | Interpretation | 1/2 · 1/2 | 2/2 · 2/2 | The edition cross-reference does not certify a link. The other indexed anchor, “135133. Ref: Paris 12595.”, crosses native documentary unit boundaries. |
| DIRECT-05 | Interpretation | 1/1 · 1/1 | 1/1 · 1/1 | Withheld. d156 points to missing d154. A locator does not establish the missing meeting contents. |
| DIRECT-06 | Interpretation | 0/2 · 0/2 | 2/2 · 2/2 | Withheld. Supplying Connally's reported understanding and contrary wording yields no proof of Nixon's agreement. |
| TWO-01 | Interpretation, neither link nor join | 3/3 · 2/3 | 3/3 · 2/3 | Neither link from Johnston through Connally to McCracken certifies, so no joined response chain. |
| TWO-02 | Interpretation, neither link nor join | 1/3 · 2/3 | 3/3 · 3/3 | The edition/response anchors supply no native certificate for either edge or their shared document. |
| TWO-03 | Interpretation, neither link nor join | 1/2 · 2/2 | 2/2 · 2/2 | Withheld. The paired references yield no certified bridge or full text for absent Paris 12595. |
| TWO-04 | Interpretation, neither link nor join | 2/3 · 3/3 | 3/3 · 3/3 | Withheld. Shared Connally mentions and different events do not establish co-reference. |
| TWO-05 | Interpretation, neither link nor join | 1/3 · 2/3 | 3/3 · 3/3 | Withheld. The two possible references and contrary wording establish no adoption or join. |
| LOC-03 | Complete, literal location | 1/1 · 1/1 | 1/1 · 1/1 | Exact citation and supplied literal certificate for the May dateline. |
| LOC-09 | Complete, literal location | 1/1 · 1/1 | 1/1 · 1/1 | Exact citation and supplied literal certificate for the June dateline. |
| LOC-14 | Complete, literal location | 1/1 · 1/1 | 1/1 · 1/1 | Exact citation and supplied literal certificate for the archival header phrase. |

The three controls preserved their exact literal scope. The five
relationship controls demonstrate withholding under the unsupported
interpretation and the tested evidence-supplied verifier. They do not
demonstrate that an admitted relationship path rejects these premises.
The readback supplied 24/25 relationship anchors as complete native
units, exercised the existing action and relationship proposal types,
and returned zero relationship proofs. No reported verifier limit fired.
The rank probes returned 16/25 and 19/25 relationship anchors, showing
further passage-selection omissions after recognition for some cases.
There were zero execution failures across 14 original-question traces
and 14 separate readbacks.

## Scoped repair recommendation

Test one explicitly attributable **document-to-document response**
route first. Use DIRECT-01 as the positive and DIRECT-05 as the
missing-target refusal. Require a relation obligation and an eligible
certificate that binds the complete response statement to one exact
target record, using the source wording, document identification and date.
A cited identifier alone must still withhold the absent meeting's contents.
Also freeze a matched DIRECT-01 refusal under the same question with d157
withdrawn from eligibility. That control must reach the new relation route
and stop at target verification. DIRECT-01 already has both witnesses in
both bounded rank probes, so this repair need not depend on a rank change.
Keep two-link composition, ambiguous identities, and claims of agreement
or execution outside this proposed repair. No repair was applied.

## Recovery and custody

[Native trace](native-first.json.gz) contains unchanged Strict answers,
independent native plans, eligible index passages and both rank probes.
[Evidence-supplied trace](readback-first.json.gz) contains every per-anchor
placement, complete proposed unit and kernel result. Their exact
[checksums](OUTPUT-SHA256SUMS) and [input seals](FREEZE-SHA256SUMS) support
public reassembly. The run used an extracted, hash-checked public runtime
and phase-separated processes. It did not run a new OS-isolation study.
Only these consumed annotations entered the second process. No fresh
question, answer, authoring parameter, or original mixed rubric file was
published. Private evaluator material stayed in the prior restricted
workspace. The original fresh, older-runtime comparison, independent
review and human onboarding statuses remain NOT_RUN.

To reproduce from this branch, retrieve the pinned parent corpus and run
each phase in a fresh output location:

```sh
lab=evaluation/archival-inspection/frus-relationship-01
git show 6942df4670196405797114cbe25317577c3118e1:evaluation/archival-inspection/frus-correspondence-01/corpus.json > corpus.json
(cd "$lab" && sha256sum -c FREEZE-SHA256SUMS)
PYTHONPATH=. python "$lab/run.py" native corpus.json "$lab" new-native.json.gz
PYTHONPATH=. python "$lab/run.py" readback corpus.json "$lab" new-readback.json.gz new-native.json.gz "$lab/consumed-anchors.json"
```
