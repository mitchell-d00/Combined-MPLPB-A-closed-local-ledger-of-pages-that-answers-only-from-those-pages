# Instruction Evidence 01 — native prerequisite held

Last reviewed: 2026-11-28.

Betty acknowledged Al note 0010 at
`805f8263f54fa8069f02d48e898705411ccdedf0`. The unchanged Ares reader is
`fe56551c752bd8df3f1728ac8b11e0cb256c5cdc`; the [contract](CONTRACT.md)
and exact inputs and evaluator digests were frozen at
`0e71f835f5fc053cfeb6ca97f9682476466d7c8e`. The first checksum
[preflight](preflight.log) stopped before starting the reader. The corrected
preflight verified all nine seals, then read eight distinct questions in eight
initial probes and one withdrawal reread. There were zero reader execution
failures. The native worker ran without Git on PATH or any effect adapter,
target repository, key, scorer, or oracle argument.

| Case | Native initial | Exact cited spans | First frozen grade | Boundary |
| --- | --- | ---: | --- | --- |
| D01 | Abstain | 0 | Miss | Compound request established neither the instruction nor the instruction date. |
| D02 | Abstain | 0 | Miss | Compound request returned no instruction and no checked partial naming the missing date. |
| D03 | Supported | 2 | Witness mismatch | Source-attributed instruction only; the authored oracle disagrees independently. |
| D04 | Abstain | 0 | Expected | Unsupported grammar; no verified writer/reporter substitution. |
| D05 | Abstain | 0 | Expected | Unsupported grammar; no verified connecting edge. |
| D06 | Supported | 2 | Witness mismatch initially; expected claim-free reread | After withdrawal, `restricted_or_unavailable`. |
| D07 | Supported | 2 | Witness mismatch | Source claim observed. Authority was not exercised. |
| D08 | Supported | 2 | Witness mismatch | Source claim observed. Resource binding was not exercised. |

The unchanged native documentary verifier returned
`documentary_assertion_not_established` for both date cases. Each original
question returned zero propositions. The read-only diagnostic graph retrieved
one candidate per initial case and emitted zero relationship edges. Neither
retrieval nor an eligible date mention can establish the missing date-role
claim. D04/D05 abstained at interpretation, so these controls establish that
no claim was emitted on these questions and leave deeper proof untested.

The [first grade](D-first-score-public.json) is retained with the held oracle
payload removed. Its strict witness comparison expected a byline-only span.
The four standalone claims use the exact enclosing `Report.\nWritten by Mina
Vale.` span and a separate instruction sentence span. The raw outputs locate
all eight citations against the corresponding record path, hash, and
canonical coordinates; the frozen comparison still rejects the larger
byline span. No expectation or first score was changed. This scorer limitation
is independent of the two dates, which emitted no claims or citations.

**Held at the native prerequisite.** No effect adapter, candidate, admission,
writer attempts, Git effects, or durable completion was exercised. The
expected three receipts and five zero-attempt control outcomes remain
NOT_RUN. Both fresh inputs and their held comparison material remain sealed
and fresh execution is NOT_RUN. Production dispatch remains inactive. The next
executable step is a separately authorized native-reader study of exact
instruction/date composition that can retain a checked partial when the date
is absent. Its new expectations should pin the entire native byline span.

Retained prior results remain consumed evidence, with no composition or rerun
claimed here. See [Ares](../../greek-gods/ares-01/README.md),
[Heka](../heka-01/README.md), and the
[restart study](../../comparative-tests/workflow-controller/restart/).

## Reproduce

Use the frozen development inputs from this directory with the unchanged
Ares runtime. From the repository root, run:

```sh
lab=evaluation/egyptian-gods/instruction-evidence-01
env -i PATH=/nonexistent PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  "$lab/reader.py" "$PWD" "$lab/D-inputs.json" > new-development-replay.jsonl
(cd "$lab" && sha256sum -c EVIDENCE-SHA256SUMS)
```

Only synthetic development material was authorized for raw publication.
Evaluator files are under `/workspace/instruction-evidence-01-custody`.
Six private artifacts passed frozen hash readback before the native run.
External persistent private custody has not been verified. Preserve original
results when reproducing, and do not open fresh for a blocked candidate.
