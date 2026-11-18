# Candidate review workspace

Last reviewed: 2026-11-18.

The opt-in offline workspace compares sorter passages with currently eligible native MPLPB originals. It is available through `mplpb_work.candidate_workspace`; default sorter modes and strict-reader entry points are unchanged.

> Sorter suggestions for review. MPLPB has not verified these links or answers.

Every processed passage and proposed conclusion has status **candidate for review**, with **Exploratory · outside MPLPB-approved evidence.** Eligible-original endpoints carry their own citation and profile status. An exact copy, synonym, reference or correction candidate never transfers approval to processed material.

```sh
python -m mplpb_work.sorter sort PROCESSED --mode compare --output SORTER.json
python -m mplpb_work.candidate_workspace build SORTER.json --processed PROCESSED --originals LEDGER --question 'Who wrote the Redwood memorandum?' --output REVIEW.json
python -m mplpb_work.candidate_workspace peruse SORTER.json --processed PROCESSED --originals LEDGER --workspace REVIEW.json
```

Use `--topic 'lunar lichens'` for exploration without a question, or alongside a question to explore a different topic. Use `--profile internal`, `lab` or `external`; optional `--as-of` reuses the native serving view. The ledger must be a directly resolved collection of native originals. The workspace does not import, revise, retire or approve any source, follow external links or invoke a model. Outputs must be new files outside processed sources and the original ledger.

## Two visible statuses and two budgets

The ownership panel uses the existing ownership algorithm after intersecting its pages with the reader's current evidence gate. Gate exclusions, hashes, lineage, permissions, depth, not-for declarations, supersession and field scope govern eligibility. A small private optional path filter in the native ownership reader avoids duplicating that algorithm; default callers behave identically. Sorter candidates and synonyms never enter the owner set.

| Eligible owners | Workspace behavior |
|---|---|
| One | Return its page with eligible-source status. Call the existing strict pipeline on originals, without any processed hints; body evidence must independently establish support. |
| Two or more | Keep eligible competitors visible and ask for disambiguation; withhold the workspace strict answer. |
| None | Report that no supported answer is returned by this ownership route; retain labeled processed-document exploration. |

The single-page owner route and multi-source evidence proof are distinct existing capabilities. H05's native comparison is complete through the multi-source strict pipeline even though the legacy page-ownership router finds no owner. The optional workspace applies the requested owner-disambiguation policy; it does not replace or relabel the standalone historical reader experiment. Its H05 regression checks the full standalone answer before and after workspace exploration at12 passages/8000 characters. Workspace ownership refusal is not a lost witness or a strict-budget failure.

`--strict-passages` and `--strict-chars` configure the unchanged strict call. `--exploration-passages` (default24) and `--exploration-chars` (default16000) charge distinct processed and original review spans separately from strict proof. The same span is charged once within its own source domain; a processed copy and its eligible original are distinct. No exploration hint consumes a strict slot. Both budgets report truncation, and the ownership panel can withhold a strict answer while processed exploration remains available.

Exploration uses the existing native retrieval on eligible originals, with an explicitly bounded discovery pool (at most64 passages/64000 characters). `--scan-passages` bounds processed hits and the original pool; `--pair-checks` bounds comparisons. Output is capped at32MiB. Search truncation, display truncation and core sorter extraction limits are explicit. Unshown material remains in the separately pinned sorter graph; missing matches do not establish historical absence.

## Source-linked candidate kinds

Exact wording, literal record references, possible corrections, opposing polarity recognized by the existing small action grammar, and literal four-word phrase review are distinct. Quoted or qualified references retain a separate unresolved-scope label. References name documents; a shown target context does not resolve the intended earlier claim or the correction's field/time. Synonyms and shared topic words rank processed search hits only; they never generate a source link. Four-word phrase matches are lexical review cues, not relationships. Identity, chronology, causation, correction applicability and historical truth remain unresolved.

Processed statements retain sorter occurrence/node IDs, raw source hashes, exact UTF-8 byte spans and review annotations. Original endpoints retain the eligible native revision, canonical body coordinates and a reversible raw UTF-8 excerpt. The existing round-trip projection maps HTML entities/layout without pretending canonical characters are raw bytes. Native-page byte coordinates are explicitly distinguished from external acquisition coordinates. Processed-only topics, unmatched statements, unresolved references and processed disagreements remain explorable under their non-authoritative labels.

Perusal reloads sources and replays the whole workspace, including eligibility, ownership and strict decision. Changed/corrupt sources, revoked permissions, altered decisions, even resealed authority promotion refuse replay. This establishes source/decision fidelity, not semantic correctness of a proposed relationship.

## Validation scope

[Workspace controls](../tests/test_candidate_workspace.py) cover all three owner outcomes, missing body support, processed contradictions, processed-only topics, quoted/conditional corrections, unresolved targets, Unicode/entity byte mapping, permission/integrity changes, forged promotion, separate budgets, CLI replay and H05 preservation. The initial workspace completed22 native replays unchanged and five public-source demonstrations, and passed1265 extracted-ZIP tests. A later disconnected-word control reproduced an unwanted broad lexical suggestion; its outputs and failure are retained. The conservative version uses existing four-word phrase observations. Its full regression and same-source demonstration remain pending at this freeze. The earlier [four-arm study](../evaluation/sorter-first-originals/2026-11-18-witness-admission-final/REPORT.md) remains frozen at2/22 complete answers. Independent human and unseen-original evaluation remain NOT RUN.
