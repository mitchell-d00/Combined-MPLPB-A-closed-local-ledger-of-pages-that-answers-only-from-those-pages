# Bunyip Round 2 bounded replacement comparison

**Decision: narrow the coverage claim and hold C3.** C3 recovered three distinct
fresh routing questions. The evidence covers two entity yes/no forms and one
opening-time form. The original release and custody gates remain incomplete.

## Pins and execution

| Item | Pin |
|---|---|
| Released reader from PR #105 | `2622813aba9ee1f1880693eeb71ae015cb3da999` |
| Released scoped runtime ZIP SHA-256 | `62231d49f21df9c61bc58d48e5038202158893001214fc197c4b9f4fb0b3d634` |
| C3 reader | `3bf9657c7b956623f07ed4b94765e0edd5cd3f02` |
| C3 scoped runtime ZIP SHA-256 | `73b96b79eed8a116df54dd4f48cce2a116553d4f056204694e1913c5428f38e0` |
| Development freeze before execution | `dcbf222605898d887d21a9ceb72ba63b83a838b9` |
| Both fresh packets frozen before either execution | `491e0e15086b23546407d361344f28698a32c53c` |

Both hosted isolation preflights passed. The existing Cryptid v5 runner ran each
original question once per reader on identical synthetic source bytes, source
order, eligibility and budgets. The ZIPs pin the three native packages. Keys
were committed before execution and excluded from the worker mount. Preparation
and scoring were same-operator. No independent blinding was performed. Raw
outputs and initialization logs are retained after checking publication scope.

[Development freeze](development/freeze.json) · [Routing freeze](R/freeze.json) ·
[Cross-family freeze](X/freeze.json) · [Frozen rules](scoring-v1.md)

## Matched results

| Arm | Executions per reader | Distinct original questions | Targets met by both | C3 only | Released only | Missed by both | Controls meeting key, both |
|---|---:|---:|---:|---:|---:|---:|---:|
| Development P01–P05 | 10 | 7 | 1 | 0 | 0 | 4 | 5/5 |
| Fresh routing R | 20 | 10 | 0 | 3 | 0 | 7 | 10/10 |
| Fresh cross-family X | 20 | 16 | 0 | 0 | 0 | 10 | 6/10 |
| Fresh total | 40 | 26 | 0 | 3 | 0 | 17 | 16/20 |

Development P05-A gave the exact opening time on both readers. Both retained
the competing-owner conflict. Both abstained on the signed-instruction,
named-report, conditional-instruction and checked-partial development targets.

| Fresh language family | Targets | Both | C3 only | Released only | Neither | Controls meeting key, both |
|---|---:|---:|---:|---:|---:|---:|
| Entity and yes/no | 4 | 0 | 2 | 0 | 2 | 4/4 |
| Temporal role and routing | 4 | 0 | 1 | 0 | 3 | 4/4 |
| Ownership wording | 2 | 0 | 0 | 0 | 2 | 2/2 |
| Attribution and negation | 3 | 0 | 0 | 0 | 3 | 3/3 |
| Conditional instruction | 3 | 0 | 0 | 0 | 3 | 3/3 |
| Compound and partial | 4 | 0 | 0 | 0 | 4 | 0/4 |

C3 answered “Is Vale and Sedge a municipal archive?” and “Is Loam Exchange a
public library?” with the exact positive and negative source sentences. For
“At which time does Cairn Desk open?” it cited **07:25**. The relevant unresolved
record blocked the matched contrast, while unrelated unresolved material did
not block the positive.

Both readers withheld on X07-B through X10-B. Their keys expect a checked
opening-time partial with the missing location named. All 16 fresh
full-withhold controls held. Across the 50 cases per reader there were zero
execution failures, unsupported completions or unsupported claims. C3 lost
zero released target outcomes. The fresh packet had zero released full target
answers, so it offers no positive preservation denominator for that reader.

Both C3 yes/no completions met the separately scored readable format.
There were no formatting disagreements on scored completions. The receipts
list source support, attribution, polarity, conditions, citations, original
question strings and the execution memberships separately.

[Development scores](development-score.json) · [Fresh scores](fresh-score.json)

## Retained evidence and release status

| Archive | SHA-256 |
|---|---|
| [Development raw evidence](development-evidence.zip) | `1420fc5a9c68ea48a27f8df2082ed7b5c01896aeefbde6202edf5ee5383c6a48` |
| [Fresh raw evidence](fresh-evidence.zip) | `f0e6da998f224b8f0e58ab99bd2c0b8dd52aca6fe4f9a75ca4f858b856949e68` |

[Development run](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/45909726593) · [Fresh run](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/45909956979)

Reader bytes did not change. The previous 832 public matches and BB's 900
positives, 900 eligible citation readbacks and 200 withholds carry forward.
The original 17 private cases remain incomplete, the original 100 held cases
remain NOT_RUN, and the retired recovery stays INTERRUPTED / UNRECOVERED. The
restricted archive Git-history incident is open. Independent historical
accuracy, independent semantic adjudication, outside-custodian scoring, native
OOCC and human onboarding remain NOT_RUN.

If reader work continues, trace frozen X07-B from discovery through compound
obligation admission. A repair informed by that output consumes the fresh draw
as development and requires a replay of affected protection checks. C3 remains
unmerged and undeployed.
