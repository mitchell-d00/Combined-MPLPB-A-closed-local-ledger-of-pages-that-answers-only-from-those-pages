# Instruction Date 01 — bounded native composition

Last reviewed: 2026-11-28.

Acknowledged Al note 0011 at `8df0aeeae765fc21eea4bc0020539ab79f20c74c`.
[The contract and packets](CONTRACT.md) were frozen at
`de0ea9cdd02ddeff2cacd084a10eb81dd56ba613` against verified main
`26621affeb487fb096a08acfc5bcdeb335760ad7`. The candidate was pinned at
`e90226354e509a7f1f3e73ce3845621d11aaf7c4`, tree
`6a2d854d2ded503b6dd34c9ba6991bd5df533c58`. Its extracted native package
and runner archive SHA-256 is
`7b60bd30ff1f0720d281291c7854fb0b5e2d39a22064be1a924aff9d3fcf25d4`.
The committed native package bytes stayed fixed through the first fresh run.

| Measure | Baseline development | Candidate development | Candidate first fresh |
| --- | ---: | ---: | ---: |
| Exact cases | 5/15 | 15/15 | 15/15 |
| Complete attributed instruction and date | 0/3 | 3/3 | 3/3 |
| Checked instruction, date unresolved | 0/6 | 6/6 | 6/6 |
| Expected withholding decisions | 6/6 | 6/6 | 6/6 |
| Withhold including frozen diagnostic | 5/6 | 6/6 | 6/6 |
| Exact eligible citation coordinates | 0 emitted | 18/18 | 18/18 |
| Unsupported completions | 0 | 0 | 0 |
| Reader execution failures | 0 | 0 | 0 |

Each draw contains 15 case instances. Question strings repeat across
source and budget contrasts.
The cases exercised two exact question strings per draw, with the second
substituting the writer for the instructor. Each run called the reader
16 times, including one withdrawal reread. On baseline the withdrawal
case missed its required initial proof. The candidate first proved the
attributed instruction and date, then emitted no claims after withdrawal.
The 114 focused preservation tests cover standalone instructions,
signed letters, advice, documentary assertions, date roles and inventory,
presentation, linked proofs and their control cases.

The maintained instruction proof now recognizes a bounded compound under
the original question and default eligible view. A complete affirmative
instruction explicitly prefixed by a literal valid date can support the
date of that instruction. The same canonical witness establishes the
directive and its date. Separate publication, reporting, receipt,
unrelated dates and another instructor's date leave the date unresolved.
A verified instruction survives as a partial when its date is unbound.
The proof still withholds when its role, reporting layer, relevant competing
instruction, qualification, eligibility or display budget is unresolved.
The change leaves prior standalone grammar in place.

This study stops at native proof. Separate anaphoric dates, independent
blinding, real-world truth, original PR #130 fresh cases and its Git-effect
cases remain NOT_RUN in this study. The original PR #130 grades were
untouched. This result meets the frozen native gate and can motivate a
separately frozen integration study. No effect dispatch was activated.

## Reproduction and custody

The worker ran the frozen [inputs](D-inputs.json) on main and candidate
without an evaluator path, Git on PATH or an effect repository. Retained
[baseline grade](baseline-score.json), [development grade](candidate-dev-score.json)
and [first fresh grade](candidate-fresh-score.json) retain the first scores.
The public [evidence receipt](EVIDENCE-SHA256SUMS) covers raw development
outputs and both candidate grades. Fresh raw outputs, exact fresh inputs,
keys and authoring and scorer code remain in separate local evaluator
custody, with sealed input hashes checked before first fresh execution.
Fresh raw output SHA-256: `ba650fcd7b1306959e510067511a761b5fc6d26136400ceb5e94cd77f8684b02`.
One operator authored, implemented and evaluated. Matching grammar and
contrast mechanisms were known before repair. External private custody
and OS isolation are unverified.

From the repository root, provide a compatible native source path as the
first runner argument:

```sh
lab=evaluation/egyptian-gods/instruction-date-01
env -i PATH=/nonexistent PYTHONDONTWRITEBYTECODE=1 /usr/bin/timeout 45 \
  /usr/bin/python3 "$lab/run.py" "$PWD" "$lab/D-inputs.json" > new-replay.jsonl
(cd "$lab" && sha256sum -c EVIDENCE-SHA256SUMS)
```
