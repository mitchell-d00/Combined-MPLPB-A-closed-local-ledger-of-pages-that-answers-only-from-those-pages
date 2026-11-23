# Advanced MPLPB

Last reviewed: 2026-11-23.

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
