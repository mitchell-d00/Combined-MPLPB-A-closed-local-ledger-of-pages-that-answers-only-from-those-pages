# D% frozen current-main baseline

Recorded 2026-11-19. Developer-authored synthetic source-assertion evaluation; independent semantic review **NOT RUN**.

## Result

The challenge fails complete-answer coverage: **20/600 complete checked answers (E = 3.33%)**, **580 incomplete/refused answerable cases**, **640/640 expected refusals**, **0/640 false alarms (F = 0%)**. All 1,240 executions completed. The capability command intentionally exited **1**. This is evidence of a coverage gap, not a successful reconstruction benchmark or an engine improvement. Expected outcomes are generator-author judgments about fictional source assertions, not independently established historical truth.

Native outputs comprise 20 supported answers, 37 checked partial answers and 1,183 abstentions. All 37 partials belong to expected-answer cases: 23 wording comparisons and 14 explicit-cause questions. They remain incomplete and receive no complete-answer credit. No supported output required an unimplemented semantic matcher in this run. E_output also equals 3.33%. The 580 over-refusals include those 37 partials; the other 543 answerable cases abstained. These are coverage gaps relative to fixture answerability, not automatic violations of the existing finite grammar.

All accepted complete answers are explicit writing assertions: 16 in direct_action and four with competing editorial commentary excluded from strict evidence. The other thirteen answerable families each have zero complete answers. All sixteen unsupported families retain 40/40 refusals each. No aggregate pass percentage is used to hide the low detection rate. Zero observed false alarms on 640 stratified synthetic cases is not universal zero-error reliability or a population-accuracy estimate.

## Freeze and authority boundaries

* Baseline native main: `6334e1b3a08db10984de637adbd5e5a6021b381c`.
* Generator/worker/tests frozen: `0b2c5c834a87262b1cc4853a30f88e3f9252c6a5`.
* Packet/key commitments committed **before execution**: `a58beb46bdf1e578dc320074204c43d521bb1e8f`.
* Archived software checks ran on **a58beb4**. No native package changed from main, and no generator, worker or test was edited after the official seal. Subsequent edits add documentation and retained evidence only.
* [Freeze receipt](freeze.json), [public seal](seal.json), [raw-output freeze](raw-output-freeze.json), [run hashes](run.json) and [score](score.json) retain the chain. Key SHA-256: `676699792759afb2a6cf7ff359a184cd6e04daf08007e0cf022c39e64334de8d`.
* The runtime mounts only one read-only case and three native Python packages. No generator, scorer, key, dice, host workspace or network is available. Each worker checks the expected mount boundary. The administrator/custodian is trusted; this is isolation, not independent authorship.
* All 1,240 cases preserve original inputs, the post-setup ledger, identical nodes and labels across sorter modes, and non-authoritative sorter labels. Observed guard failures: zero. Sorting never feeds strict proof slots. Source receipts and offline graphs are operator artifacts, **not** profile-filtered public delivery.

The private key/dice remain outside Git in `/tmp/dpercent-frozen-private`; the operator custody archive is `/workspace/dpercent-private-custody-2026-11-19.tar.gz`. It is not mounted by execution. Public scoring reveals development labels; a future unseen evaluation needs a new frozen batch. This generator and its typed matcher share developer authorship. The preliminary pilot informed harness development; it is retained separately and is not independent or part of the official baseline.

## Discovery and costs

Both retrieval methods use the same eligible sources and 12-passage/8,000-character budgets. Over 1,080 cases with eligible reference sources:

| Retrieval method | Source recall@1 | @5 | @10 | Full-statement coverage |
|---|---:|---:|---:|---:|
| Native obligation facets | 76.48% | 89.57% | 89.85% | 89.85% |
| Simple BM25 | 77.61% | 98.12% | 100% | 100% |

These are macro-averaged developer reference-coverage measures, not semantic correctness. Packets are small; BM25 can fit every source inside its budget. Protected, withdrawn, corrupt and absent references do not become retrieval misses. The results expose native discovery losses as well as finite-checker gaps. Search completeness remains the engine's own bounded diagnostic; no global absence claim is established.

Observed costs for all 1,240 cases: **147.676 CPU seconds**, **153.136 post-import worker wall seconds**, **586.222 summed parent per-case wall seconds**, **28,516,352 bytes maximum individual worker RSS**, **6,488 explicit original-ingest reads / 795,751 bytes**. These include strict answering plus two retrieval methods and both sorter modes. Import/startup, parent orchestration, sealing/hash verification and concurrent software checks explain why the wall measures differ. See [environment](environment.json): Python 3.12.14, Linux x86_64, Xeon Platinum 8573C, five visible CPUs with a four-CPU cgroup quota and 16 GiB memory limit. These are observed shared-container costs, not isolated latency measurements. Total pipeline source bytes, aggregate process-tree memory and human effort are unmeasured. The container init retained defunct sandbox helper processes; use an orphan-reaping init for long repeated batches. Maximum case count bounds an individual batch, but full process-tree accounting is outstanding.

## Source-linked examples and remaining stops

[Examples](examples.json) include verbatim raw source text, source receipts/hashes, canonical citations, questions and native responses. [Every case](case-results.csv) and [full outputs](raw-execution.tar.gz) retain negative and incomplete cases.

* **DP00125**, supported: “May Reed wrote the copper survey report.” Native SOURCE-0001, canonical `[0,40)`, hash `sha256:db1c6fef3c203a53907d050c90ee008cb4b0206cf5d5df52bdc9ab8d15da19fd`. The checked action is source-attributed writing, not independently verified authorship or historical truth.
* **DP00001**, over-refusal: “Nora Wells wrote the coastal dispatch.” The question asks “According to the record, who wrote the coastal dispatch?” The checker reports the requested argument/qualification or contrary-evidence search unestablished despite explicit source wording. This is an actionable phrasing/context gap; no source alteration is needed.
* **DP00007**, over-refusal: “The harbor report was written by Nora Wells.” Passive prose and a question wrapper remain unsupported.
* **DP00011**, over-refusal: an explicitly dated earlier six-crate statement and a later same-writer correction to nine crates, retaining the east depot, remain unresolved. Both originals are preserved; nothing retires automatically.
* **DP00013**, over-refusal: “The inspection was canceled because of damage to the bridge.” The native checker does not complete the wrapped causal question and treats the request to keep unknown matters unresolved as a separate obligation. No causal inference from mere chronology is required here.
* **DP00006**, correct refusal: “Edda Marén did not send the harbor report” cannot establish that she sent it. **DP00031**, correct refusal: a request plus an unattributed receipt cannot supply the missing dispatch link. **DP00008** preserves external withholding.

General next-fix targets are scoped question wrappers, active/passive statement coverage, preservation of reported/negative meaning, complete explicit-cause answers, exact comparisons and documentary date/reference composition. Each change needs independent native re-reading, unchanged packets and no new false support. This frozen baseline phase contains **no engine fixes**. Later rule changes must be recorded as a separate comparison. The retained 22-question historical corpus was not rerun or changed, and no gain on it is claimed.

## Family breakdown

| Family | Expected | Complete checked | Refused / incomplete | False support |
|---|---|---:|---:|---:|
| absent_anchor | refuse | 0 | 40 | 0 |
| ambiguous_correction | refuse | 0 | 40 | 0 |
| ambiguous_pronoun | refuse | 0 | 40 | 0 |
| chronology_causation | refuse | 0 | 40 | 0 |
| competing_accounts | refuse | 0 | 40 | 0 |
| conditional_execution | refuse | 0 | 40 | 0 |
| corrupted_source | refuse | 0 | 40 | 0 |
| date_roles | answer | 0 | 40 | 0 |
| direct_action | answer | 16 | 24 | 0 |
| earliest_observed | answer | 0 | 40 | 0 |
| editorial_competition | answer | 4 | 36 | 0 |
| embedded_identifier | refuse | 0 | 40 | 0 |
| exact_anchor | answer | 0 | 40 | 0 |
| explicit_cause | answer | 0 | 40 | 0 |
| explicit_chain | answer | 0 | 40 | 0 |
| header_location | answer | 0 | 40 | 0 |
| historical_priority | refuse | 0 | 40 | 0 |
| identical_wording | answer | 0 | 40 | 0 |
| instruction_statement | answer | 0 | 40 | 0 |
| intention_execution | refuse | 0 | 40 | 0 |
| missing_bridge | refuse | 0 | 40 | 0 |
| negated_execution | refuse | 0 | 40 | 0 |
| negated_statement | answer | 0 | 40 | 0 |
| partial_correction | answer | 0 | 40 | 0 |
| passive_action | answer | 0 | 40 | 0 |
| reported_execution | refuse | 0 | 40 | 0 |
| reported_statement | answer | 0 | 40 | 0 |
| restricted_source | refuse | 0 | 40 | 0 |
| subject_identity | refuse | 0 | 40 | 0 |
| withdrawn_source | refuse | 0 | 40 | 0 |
| wording_change | answer | 0 | 40 | 0 |

## Reproduction and software results

See [D% usage](../../../docs/DPERCENT.md) for all limits and the key separation contract. On a checkout of the frozen generator, extract `public-packets.tar.gz`, then run against the pinned main implementation:

```sh
python -m tools.dpercent run --packets /tmp/replay/public --out /tmp/replay-run --implementation /path/to/main-checkout
python -m tools.dpercent score --packets /tmp/replay/public --custodian /path/to/private/custodian --run /tmp/replay-run --out /tmp/replay-score.json --require-perfect
```

Use a checkout with the recorded native hashes; do not run against a silently changed main. Exact scoring requires the custodian key matching the sealed hash. A fresh generated batch is a different sample. Raw archives are data-only; extract into new directories. Expected exits: execution **0**, capability scoring **1** for this baseline.

Actual software commands on the frozen archived source:

```sh
python -m unittest -q tests.test_dpercent
python -m unittest tests.test_answer_boundaries tests.test_scoped_extensions tests.test_supersession_policy -q
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/dpercent-archived-software/public-evidence.json
python -m tools.reproduce_boundaries --revision a58beb4 --output /tmp/dpercent-archived-software --suite full
```

Generator/scorer controls: **15 tests, exit 0**. Full archived suite: **1,394 tests, exit 0**. Native boundary subset: exit 0. Public evidence: **52/52 controls, exit 0**. [Software receipt/logs](software/report.json) record commands and timing. Ten applicable JavaScript/bridge/crawler commands passed; two first attempts hit `spawnSync python3 EPERM` under the default sandbox, then passed with execution permission. Both attempts remain in `interface-first-attempt/` and `interface-permitted-rerun/`. There was no JavaScript source change. Physical-browser, deployed-site, WebAssembly and live-model tests were not rerun for this Python test-tool addition.

[Pre-freeze engineering attempts](engineering-attempts/index.json) preserve an initial failing test, corrected test runs and the earlier 30-case pilot. Fixture context errors were corrected before the official freeze. No failed official cases were discarded, relabeled or silently retried. The first final documentation audit also stopped on a stale date marker in the edited documentation index;the marker was corrected and the first audit output retained. Software passing is not the same as the capability benchmark passing.

## Independent assessment readiness

Give a fresh assessor only `public-packets.tar.gz` and `raw-execution.tar.gz`, not the key, score, family table or change log. Require a cited source span for every correctness judgment, explicit missing evidence for overreach, and preservation of policy, attribution, negation and date roles. Label a fresh-model review **AI assessment**, not human-independent validation. Freeze its unedited responses and hashes before comparing with the key. No such review was run here.

Relationship precision/recall, false-link rates, event identity accuracy, historical truth, live-model quality, independently reviewed refusal correctness and human effort remain **null / NOT RUN**. Private structural graph hints are review prompts, not automated semantic scoring. The next milestone is reducing these frozen over-refusals without increasing false support, followed by a new genuinely held-out batch. The broad historical reconstruction objective remains unproven.
