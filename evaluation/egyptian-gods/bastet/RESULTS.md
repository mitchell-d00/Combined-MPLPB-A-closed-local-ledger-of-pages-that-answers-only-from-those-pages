# Bastet first development baseline

Last reviewed: 2026-11-27.

[Released baseline](baseline.json) · [Frozen cases](development/registry.json) ·
[First receipt](evidence/first-receipt.json) · [Raw archive](evidence/development-first.zip)

The deployed Round 4 reader ran the twelve development cases, representing
four distinct questions. All executions completed, and no unsupported
claim was emitted. There was no verified document selection and no
verified attribution. All six expected answers missed with
interpretation_unsupported, despite discovery finding their expected
witnesses. The generic attribution gain from Round 4 supplies no proof
for a named writer.

| First measurement | Released reader |
|---|---:|
| Complete answers / 6 | 0 |
| Safe claim-free withholds / 6 | 6 |
| Exact I/O withholds / 6 | 5 |
| Verified selections or attributions | 0 |
| Proof-stage controls | 0 |
| Unsupported claim cases | 0 |
| Execution failures | 0 |

The duplicate eligible writer control CRYPT-BASTET-D-0006 gave a claim-free
conflict with retrieval_ambiguous. Its original contract expected an
abstention, so the I/O score retains this as a status miss. The conflict
diagnostic supplies no selected-source receipt and establishes no named
writer proof. All five other negative controls withheld at interpretation.
No wrong-reporter refusal certified selection of the intended document.

The [claim score](evidence/development-claim-score.json) and
[I/O score](evidence/development-io-score.json) preserve these two measures.
The I/O check retains every final status, missing field, citation check and
diagnostic separately from execution. Same-operator fixture preparation and
scoring used evaluator-only key access. The fresh twelve cases were sealed
separately and stay NOT_RUN. No reader or controller code changed in this
batch. Round 4 F05 remains a consumed development lead. The next
implementation decision must address named writer selection before it
claims anything about embedded attribution.

The original incomplete checks, unrun transfers and publication-history
incident retain their recorded status.
