# Deterministic evidence graph — frozen pottery and synthetic-user retest

> **Later unscored extension:** The [Mitchell-Tech-style 12-domain unique question smoke benchmark](DIVERSE_SMOKE.md) adds seven source-bound relation types, explicit phrasing variants, 312 planned distinct questions, and 24 metamorphic checks. Its pass count and browser capture behavior require separate candidate CI. This dated 12/59 report remains pinned to the earlier graph revision.


**Measured candidate:** `01a41a9c644872b82ffb1c7774d70a9337252a1b` on PR #26, at GitHub Actions run [41340452091](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/41340452091). The focused source-graph and synthetic-user step passed and retained full `frozen-retest.json` / `synthetic-users.json` as artifact `source-evidence-graph-41340452091` (artifact ID 13096543186). **Full Python, ZIP-first, WebAssembly and complete deployment checks are separate and must be inspected before merge.**

## Pottery coverage — unchanged frozen questions

| Inspected set | 2026-10-31 historical strict result | Graph candidate correct-document returns | Newly returned | Wrong returns (candidate) |
| --- | ---: | ---: | ---: | ---: |
| Original | 3/32 | 7/32 | 4 | 0 |
| Held-out-named | 2/19 | 4/19 | 2 | 0 |
| Adjacent | 1/8 | 1/8 | 0 | 0 |
| **Total** | **6/59 (10.2%)** | **12/59 (20.3%)** | **6** | **0** |

The 59 are the answerable questions within 106 pottery probes. The old `6/59` and its machine-readable results remain unchanged. The old held-out filename no longer establishes a truly held-out sample: all three files have been inspected for development. The automated correctness proxy verifies that the returned document matches the frozen gold ID. It does **not** establish unrestricted semantic entailment or source truth. Refusals and ambiguities are not counted as correct returns. The adjacent unanswerable case `a03` changed from ambiguity to refusal, matching its negative label; this does not add to the numerator.

### Six newly returned source statements

| Frozen case | Source | Question and exact returned quote |
| --- | --- | --- |
| `op02` | `STUDIO-0006` | **What does it mean if the guard has gone over?** — “If the guard has gone over, the load ran hot: shorten the soak next time rather than lowering the set point.” |
| `op05` | `STUDIO-0013` | **How much Epsom salt solution?** — “If it has hard-panned, add a teaspoon of Epsom salt solution and sieve again.” |
| `op06` | `STUDIO-0015` | **Ram's head or spiral?** — “Ram's head for small amounts, spiral for anything over two kilos.” |
| `op07` | `STUDIO-0017` | **What is bag code CR for?** — “Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.” |
| `h13` | `STUDIO-0010` | **How do I check the coat with a pin?** — “The coat should be the thickness of a postcard: scratch through with a pin to check.” |
| `h16` | `STUDIO-0014` | **Which bodies must be kept in separate buckets?** — “Keep red and white bodies in separate buckets; a mixed batch cannot be sorted afterwards.” |

These quotes were examined against the displayed questions and source pages while writing this report. The `op05` answer is explicitly *conditional*; showing it as unconditional dosing advice would be incorrect. The `op06` answer preserves both options rather than claiming one technique is always best. The `h13` source describes a check, not verified successful execution. This is one development inspection, **not independent human blind scoring**; the rest of the frozen questions and other languages remain outside the finite guarantee.

## Six synthetic users

The `synthetic-users.json` development fixture replays six isolated local ledgers through `supported_answer` with the full provenance gate:

| Scenario | Representative check |
| --- | --- |
| Pottery apprentice | Code, quantity, slaking duration, explicit cause, clay alternative and pin method |
| Archivist | Coded purpose, drying duration, additive quantity and frame comparison |
| Laboratory assistant | Conditional intake, separation, inspection tool mismatch and absent evidence |
| Warehouse clerk | Identified packing code and barcode condition |
| Plant operator | Distinct positive/negative antecedents, separate containers and absent synonym |
| Duplicate-source reviewer | Two eligible pages with identical claims must remain ambiguous |

**Results on the CI-produced developer-scripted suite:** 36/36 expected outcomes: 21 correct returns (exact full quote and record ID), 14 correct refusals, one correct ambiguity, zero wrong returns. These are authored finite controls; they are neither real user sessions nor evidence of calibrated production answer quality. A synthetic user persona does not substitute for a human usability study.

## Why graph evidence is safer than a loose lexical fix

A statement is counted only when the requested subject, typed predicate and complete source sentence form one provenance-gated path. Every returned value retains its original entire sentence, conditions and contrasts. Alternate options require *both* options explicitly present in a source comparison; an inspection requires the exact requested tool and action. An unrelated procedure, wrong entity, missing negation or merely similar scope cannot create a graph proof. There is no top-1 winner, unrestricted multi-hop inference, synonym rewrite, medical instruction inference or page-to-page fact synthesis.

The resulting graph is inspectable in `answer_support.graph` on a strict return and carries source record ID/hash. The existing chat-language and user-declaration graphs remain separate contracts.

## Reproduce and audit

```sh
python -m unittest tests.test_relation_graph tests.test_relation_graph_synthetic_users tests.test_operational_evidence -v
python -m tools.simulate_relation_graph_users --output /tmp/synthetic-users.json
python -m tools.evaluate_relation_graph --output /tmp/frozen-retest.json
python -m unittest discover -s tests -q
```

The exact-head comparison also runs the pre-existing 28 adversarial development and 20 inspected SQuAD questions, preserving their frozen hashes, retaining changed-case rows, and blocking newly wrong returns. Do **not** overwrite the historical reports; new experiments must have new revision pins and artifacts. Check CI, source pins, actual browser/WebAssembly validation, and post-merge deployment separately.

**Unfinished:** 47/59 answerable pottery questions still lack a supported return under this candidate. Many need audited question normalization, cross-sentence references, explicit author-reviewed procedure tags, scoped time/quantity comparisons, or missing source facts. Some original gold answers measure page ownership rather than proof of a complete requested relation. Do not mark these as solved by generating more synthetic users or pretending source overlap is entailment.

See [architecture](../../docs/DETERMINISTIC_EVIDENCE_GRAPH.md), [historic practical evaluation](../practical-coverage/README.md), and [error classes](../../docs/OPERATIONAL_EVIDENCE.md).
