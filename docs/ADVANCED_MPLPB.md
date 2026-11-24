# Advanced MPLPB

Last reviewed: 2026-11-24.

Advanced MPLPB coordinates the existing answer and inspection paths through a
single Python interface and CLI. It starts with Strict Ask and keeps that
result visible, including its citations and remaining obligations.

```sh
mplpb-combined advanced /path/to/ledger "What does the record establish?"
```

| Strict result | Automatic follow-up |
|---|---|
| Full answer | Return the strict answer and its citations. |
| Partial answer | Run a bounded investigation with one hop and up to four sources. |
| Unsupported wording or unresolved evidence | Run an eligible-record lookup and suggest investigation for declared links. |
| Conflict, unclear scope, exhausted evidence budget, or unavailable sources | Show the reason and suggest how to proceed. |

Use `--follow-up none` to see the strict result and a suggestion without
running an inspection. Use `lookup` or `investigate` to run that inspection
explicitly. Use `--follow-up assisted --reader-model NAME --reader-digest SHA256`
to permit a pinned, installed local Ollama reader. Assisted inspection runs
only when strict proof is incomplete and there is no conflict or request for
clarification. The output keeps the strict status and labels the follow-up
as inspection. Top-level `answer_supported` comes from Strict Ask. The
coordinator discards the combined output if the source snapshot changes
between paths. Use `--json` for the complete result, including inspection
details and native receipts.

## Training from one command

Run this as the trusted person holding the evaluation key.

```sh
set_dir=evaluation/d12/coordinator
mplpb-combined advanced-train "$set_dir/fixtures.json" "$set_dir/key.json" \
  "$set_dir/baseline-rule.json" /tmp/mplpb-training.json --objective elapsed_days
```

Omit `--objective` to freeze the inputs, run the baseline, and group
development misses. Use `--candidate PATH` to compare one authored rule.
A registered objective uses the existing bounded calendar repair. Each
report retains the baseline and any tested candidate and verdict.
The existing coordinator checks repeated gains, holdout cases, and refusal
controls. A passing candidate remains a training artifact with
`promoted=false`. The WorkStore capability API remains available for
separate operator and coordinator seats. [Scoped training workflow](../evaluation/d12/coordinator/README.md)

On the archived historical 22 the automatic path preserved every strict
contract. It ran 12 lookups and three investigations and stopped after the
strict result on seven cases. The archived training checks selected the
elapsed-days repair, which recovered two development cases and one holdout
while preserving both refusal controls. Inclusive-day counting failed the
protected holdout and returned `review_needed`.
[Per-case routing and training evidence](../evaluation/d12/mode-replay/advanced-results.json)

Assisted evaluation still requires live-model and independent human validation.
[Historical mode results](../evaluation/d12/mode-replay/README.md)


## Live experience graph and strict flag matching

Use an explicit local SQLite path to record passes and require a matching
graph path before presenting source proof.

```sh
mplpb-combined ask /path/to/ledger "What does the record establish?" \
  --experience-graph ./experience.sqlite --json
mplpb-combined advanced /path/to/ledger "What does the record establish?" \
  --experience-graph ./experience.sqlite --follow-up auto --json
mplpb-combined experience-pass ./experience.sqlite 1
```

Strict Ask derives its answer from eligible ledger bodies using its existing
proof rules. It builds the required graph path from that checked result.
A path contains the question's current seam, warning or unresolved boundary,
checked relations and claims, and each cited source ID, hash, and offset.
Nodes and directed edges use one exact flag vocabulary. Advanced uses the
same `auto`, `none`, `lookup`, `investigate`, and `assisted` flags for its
inspection pass. The database stores pins and tags, with separate timestamps
and a link to an earlier pass or version.

On the first ask, or when the active sources, policy, or proof decision
change, MPLPB records a new path from the fresh strict result. For a
recorded path in the same state, it requires an exact match on every node,
edge, flag set, eligibility snapshot, and source pin. A mismatch returns
`FLAG_MISMATCH` and the diff, with the answer and citations withheld.
The separate read command exposes the stored pass and its version metadata.
Historical passes describe their own snapshot.

In Advanced, a successful lookup can seed a later `investigate` pass for
the same question, collection, delivery profile and proof state. The later
pass rechecks the prior candidates against current eligible sources.
Automatic routing can choose a local inspection, and explicit flags retain
their meaning. The graph path and source state are checked again before
the combined result is presented.

J/Opass turns native outcomes into presentation warnings alongside the
strict result. An **Educated guess · what to check next** helper can suggest
a proof step and repeat previously checked citations. Its output has
`answer_supported: false`. Explicitly selecting assisted mode can show a
model's cited interpretation as a separate inspection. If there is no
eligible source, the presentation says so and skips the guess.

The graph and warnings are opt-in through native Ask and Advanced. Existing
calls without a graph keep their ordinary contract. [J/Opass](../evaluation/d12/j-opass/README.md) ·
[Experience graph controls](../tests/test_experience_graph.py)

### Recorded checks

On native candidate `da9418a`, the historical 22 matched the ordinary strict
contract case by case with the graph gate enabled. The totals were four
full answers, three partials, three conflicts, and twelve abstentions.
On the three 4score20 cases, Lodge's second pass moved from lookup to
investigation. Both telegram and communiqué requests stayed on lookup.
All three kept their original refusals.

The focused source ZIP passed 54 checks. The full native suite ran 1,699
tests with two skips and zero failures, and the test command recorded
exit zero. The execution wrapper reported exit 1 after the test command
completed.
