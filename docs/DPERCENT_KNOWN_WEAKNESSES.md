# D% known-weakness sampling

Last reviewed: 2026-11-20.

This is a versioned development stress study, not independent historical validation.
It preserves the original D% producer, expanded producer, frozen questions, keys,
source bytes and prior outputs. No native answer or sorter rule is changed by
this tool. Runtime receives source files, the question and the unchanged proof
budget; it receives neither expected outcomes nor dice records.

## What is sampled

`python -m tools.dpercent_weaknesses catalog` lists75 executable classes and15
known gaps requiring another adapter or independent assessment. The executable
classes retain all31 original and17 expanded classes, add19 sorter classes and8
alias controls. The separate unmeasured list includes crash durability, classing
transactions, retired snapshot delivery, as-of correction operations, concurrent
mutation, model quality, cold-instance continuity, shared source ancestry,
unfamiliar event identity, exploration-budget separation and long-document OCR.
Static source corruption is tested; it is not a concurrent-mutation test.
A coherent false original cannot be detected from integrity checks alone.

The original families cover active/passive assertions, reported and negated
statements, instructions versus execution, explicit causes versus chronological
co-occurrence, date roles, exact/changed wording, earliest documentary dates,
explicit chains and missing bridges, pronouns, competing accounts, unsupported
priority, restrictions, withdrawal and absent anchors. Expanded fields cover
synonyms, compound obligations, quoted/reported fields, contradictions, changed
bodies, stacked fields, missing labels and time-qualified questions.

New sorter obligations distinguish primary declarations from quoted, forwarded
and fenced textual appearances; duplicate appearances from independent events;
subject overlap from identity; changed bodies from identical copies; concatenated
records; uniquely targeted, partial, passive, reported, negated and conditional
corrections; missing/ambiguous targets; numbered and punctuated references.
They require legitimate discovery as well as the absence of forbidden links.
An empty graph cannot pass a duplicate-appearance discovery obligation.

Alias controls vary documentary date/time/location roles, unsafe adjective
inversions, ambiguous synonymous labels and geographic State versus status.
Sampling changes question structures, layout, wrapping, source counts, quotation
scope, negation, attribution, line endings, Unicode, fences and target punctuation.
Not every dimension applies to every class; charts and per-case feature records
show actual coverage. There is no question-acceptance or unsupported-word filter.

## Deterministic constraints and scale

A balanced family schedule is shuffled using recorded unbiased D% draws. A fixed
seed reproduces source bytes, questions, expected outcomes, draws and seals.
Structural meaning determines the authored key; the engine never chooses which
cases enter the test. Defaults:4,096 cases,256 per shard,16 independently sealed
shards,54–55 examples per executable class. Preparation supports1–65,536 cases;
actual run/storage cost grows with that count. This is not exhaustive combination
coverage or a guarantee that every known or unknown weakness is represented.

Each shard retains the original worker's45-second case wall limit,30-second CPU
limit,8MiB result limit and256MiB shard result ceiling. Proof budgets remain
12 passages/8,000 characters. Preparation caps global source bytes at128MiB.
The manifest reports the sum of shard result ceilings (4GiB for16 shards);
operators need sufficient storage. The optional batch driver permits1–4 parallel
shards. Concurrency and resource context must be identical for speed comparisons.

## Reproduce without private records

Use new paths, Linux bubblewrap and a Python source checkout:

```sh
python -m tools.dpercent_weaknesses prepare --out /tmp/weakness-public --custodian /tmp/weakness-keys --cases 4096 --seed 2026112003 --shard-size 256
python -m tools.dpercent_weakness_batch --packets /tmp/weakness-public --custodian /tmp/weakness-keys --output /tmp/weakness-run --workers 4
python -m tools.dpercent_weakness_audit --packets /tmp/weakness-public --custodian /tmp/weakness-keys --output /tmp/weakness-run
python -m unittest tests.test_dpercent_weaknesses tests.test_dpercent tests.test_dpercent_expanded tests.test_sorter tests.test_sorter_v2 -q
```

The public directory contains `study.json` plus source-only case packets and
per-shard protocols/seals. The disjoint custodian directory contains keys, dice
and original seal/manifest copies; keep it outside the checkout and worker mount.
Custody hashes detect changed questions, originals, keys and dice. Every runtime
result has its own receipt hash and native code pins.

The sequential runner also supports `--max-shards N`. Rerunning a driver preserves
existing shards and schedules absent ones. An interrupted shard is retained as
partial; it is not silently retried. To repeat it, use a new output directory.
Failed execution, missing result files and unreached shards remain visible.
Neither the parent driver nor scorer writes to a source ledger.

## Read the findings

`summary.json` separates planned, executed and not-run cases, per-family outcomes,
feature cohorts and graph-obligation failures. Shard score files retain detection
E and false-alarm F, missed positives, incorrect positives, unscored support,
quotation fidelity and resource costs. Never substitute null with zero or count
an unexecuted case as a correct refusal. Feature cohorts overlap; their failure
rates are descriptive, not causal attribution.

The post-run audit independently checks every emitted node span against UTF-8
source bytes and hashes, and checks all three candidate authority flags remain
false. It does not measure all internal source reads.

`*-graph-checks.json` records each individual textual obligation. These checks do
not measure semantic event identity precision, relationship recall, independent
corroboration or historical truth. Those metrics and human review effort stay
null. A candidate count is not a success metric. A native partial output is not
a correct partial answer without separate assessment. Graph observations retain
source spans, hashes and provisional assessments; comparison adds review proposals
without promoting them. Unknown obligation schemas fail closed.

A normal driver exit means execution/scoring orchestration finished, not that
all answer or graph obligations passed. Inspect the report. The original source
assertion checker remains the only authority for `answer_supported`.

Study records and limitations are retained under
[evaluation/dpercent-known-weaknesses](../evaluation/dpercent-known-weaknesses/2026-11-20).
Independent semantic review: **NOT RUN**.


The retained synthetic packet ZIP includes public inputs and a separate expected
key/dice directory; it contains no old private evaluation records. Its SHA-256
and internal file manifest permit byte verification. Publicly reproducible keys
make this a development study, not a hidden assessment. For the exact original
producer seal, execute the preserved file with `PYTHONPATH=.`; the current
producer module also contains the post-run legacy-obligation scorer repair.
