# WorkStore rule-training coordinator

Last reviewed: 2026-11-23.

A user can train a named D6 rule by editing a data-only plan and replaying it against a sealed fixture packet. The sub-coordinator groups repeated development failures and retains the computed step and exact citations. The coordinator tests the proposed rule against the identical packet, checks holdouts and refusals, and files the result against the same baseline digest. WorkStore keeps those reports as training records.

## Run a complete example

```sh
demo=evaluation/d12/coordinator
run_dir=$(mktemp -d)
python -m mplpb_work.training freeze "$demo/fixtures.json" "$demo/key.json" "$run_dir/seal.json"
python -m mplpb_work.training repair "$run_dir/seal.json" "$demo/fixtures.json" \
  "$demo/key.json" "$demo/baseline-rule.json" "$run_dir/automatic.json" --objective elapsed_days
```

The baseline mistakes a difference of calendar year numbers for elapsed days. The sub-coordinator groups two wrong-value development cases. The automatic sprint replaces the calculation with the explicit Gregorian elapsed-day operation and tests it against the same packet. The selected candidate recovers both development cases and the held-out reverse interval. The two controls retain their refusals when a date is incomplete or the closing date is absent.

Use `--objective inclusive_days` with this packet and a new output path to see the wrong objective fail safely. Run the selected elapsed-day plan against the same packet again to see `baseline_healthy`. For failure classes outside the registered calendar transformation, the result is `review_needed` with the baseline and findings retained. A selected candidate is available in the result. The ordinary strict reader and repository keep their existing behavior.

The public example key is for demonstration. For a blind sprint, a custodian keeps the key and adjudication calls separate from the operator. Freeze the raw fixture and key files before running either arm. The runner receives only the fixture and rule files. Each named rule contains one D6 step, which may contain an allowed nested plan. Use `"$record"` in selectors so the same rule runs on every fixture. Use only explicit source fields. The coordinator judges the requested completion and any declared scalar result using the sealed key.

### Set and test your own rule

```sh
python -m mplpb_work.training run "$demo/fixtures.json" "$demo/baseline-rule.json" "$run_dir/baseline.json"
python -m mplpb_work.training tag "$run_dir/seal.json" "$demo/fixtures.json" \
  "$demo/key.json" "$run_dir/baseline.json" "$run_dir/findings.json"
python -m mplpb_work.training run "$demo/fixtures.json" "$demo/elapsed-days-rule.json" "$run_dir/candidate.json"
python -m mplpb_work.training compare "$run_dir/seal.json" "$demo/fixtures.json" \
  "$demo/key.json" "$run_dir/baseline.json" "$run_dir/candidate.json" "$run_dir/verdict.json"
```

The comparison needs the same engine, name, sealed inputs and case coverage. A passing candidate recovers at least two development cases in one tagged class, passes every holdout and control, and introduces zero regressions or unexpected full support. Keep the baseline, candidate, key and verdict in their appropriate work areas when preparing the next sprint.

## Let an AI seat drive the same API

The existing WorkStore seat API accepts these operations. A host grants the corresponding capabilities and visibility on an open task. The same JSON can run locally using `python -m mplpb_work request WORK_DIR --credential-file SEAT.json --input REQUEST.json`. For fixture, rule and key arguments, send the exact JSON file contents as JSON strings.

| API operation | Seat capability | Inputs beyond `op` and `task` |
| --- | --- | --- |
| `training_replay` | `training:run` | `fixtures`, `rule` |
| `training_evaluate` with `mode: "tag"` | `training:tag` | `seal`, `fixtures`, `key`, `baseline` |
| `training_evaluate` with `mode: "compare"` | `training:compare` | Same inputs plus `candidate` |
| `training_sprint` | `training:repair` | `seal`, `fixtures`, `key`, `rule`, `objective` |
| `training_record` | `create:training_finding` or `create:rule_sprint` | `id`, `artifact`, optional `group` or `finding_id`, and explicit `share_with` |

Use an operator seat for model-proposed rule runs and a custodian seat for the grading key. Give the sub-coordinator the tag and finding rights and the coordinator the comparison, optional automatic sprint, and verdict-filing rights. The filing API checks that the verdict points to a visible finding from the same task and baseline. Receipts support review and replay. They carry no source-support or execution authority.

## Repository benchmark triage

The fixed bench runner replays the historical 22, D20 seed 20, and an already generated Primary Book packet, then tags observable stages. Results remain separate because source support, owner/refusal behavior, and exact quote fidelity answer different questions.

```sh
python -m test_tools.primary_book_test generate --output "$run_dir/books"
python -m test_tools.training_benchmarks replay \
  --book-inputs "$run_dir/books/engine-inputs" --book-key "$run_dir/books/custodian/answer-key.json" \
  --output "$run_dir/benches"
```

| Replayed bench | Observed result |
| --- | --- |
| Historical 22 | 4 full, 3 partial, 3 conflicts and 12 abstentions, with identical native contracts to the preceding revision. The trace marked 11 absent documentary plans for inspection. |
| D20 frozen seed 20 | 2 supported owner answers and 15 withholds. All three missed positive cases involved alias forms. |
| Fresh Primary Book packet | 3 correct source and quote pairs and 3 altered quotes withheld. |

The [retained benchmark report](benchmark-observations.json) includes input hashes and diagnostic tags. The Book packet drew from pinned editions; use the [seed and source pins](primary-book-pins.json) to replay that draw. See the [passing auto sprint](auto-repair.json), [blocked proposal](auto-blocked.json), and [healthy replay](healthy-replay-summary.json) for the worked training case.

The bench runner is fixed repository test tooling. The live seat API executes bounded D6 plan data. Historical tags indicate where to inspect a case. They preserve conflicts and uncertainty pending independent review. [Historical seam method](../pattern-sprints/historical-seams/README.md)
