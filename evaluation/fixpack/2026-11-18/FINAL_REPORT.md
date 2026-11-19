# Final fixpack and historical-gap engineering report

2026-11-18. Working branch `fix/fixpack-strict-routing-classing`; local commits only. **Nothing pushed or merged.**

Baseline: `bbf6690d69b32d16969cc10e5ce9d380427ead40`. Tested final runtime: `7c92db5caa39e90fca01fd8e3be5c8c8a2a11c4a`. Its extracted source ZIP SHA256: `479b24819daf6747e46b5f03fabd84d74d06f688bf84bc4e183a6917949e9a8f`. Subsequent edits add evidence, documentation and handoff only; runtime equality is audited separately. The earlier [checkpoint](REPORT.md), original fixpack ZIP, first freeze, failures and every final worker are retained.

## Measured outcome

| Metric | Baseline | Updated |
|---|---:|---:|
| Complete source-supported answers | 2/22 | 2/22 |
| Checked partial answers | 1 | 2 |
| Native retrieval conflicts | 3 | 3 |
| Abstentions | 16 | 15 |
| Surfaced full draft anchors, native | 27/32 | 27/32 |
| Native plus separate exploration | — | 27/32 |

The one gain is U06: the eligible source states “Ferdinand Hayden surveyed the area in 1871.” The checker retains its exact source wording and full local paragraph, but **does not resolve “the area,” establish the later actions, or complete the question**. H02's arrangement remains a reported instruction, with no receipt or executed delivery inferred. H05 remains complete with exactly the same 4 citations/4070 characters at the original 12-passage/8000-character strict budget. All other native semantic outputs remain unchanged. Three conflict outcomes are retrieval ambiguity, not independently established historical contradictions.

The [22-case analysis](CASE_ANALYSIS.md) separates exact source excerpts, fresh AI observations and native checker limits. [Machine-readable comparison](comparison.json) retains checked canonical/original-byte anchors and all 5 missed draft spans. No original document, frozen question, prior result or reference key was edited. The preservation audit covers 5614 existing tracked evaluation files; legacy sorter v1 retains its original SHA.

**The discovery milestone was not achieved:** separate per-part retrieval, source-fair context indexing and counterwording retention did not recover any of the 5 missing full draft anchors under the frozen 12/16000 exploration display budget. Some relevant contexts cross window boundaries or rank below displayed passages. Native proof slots remain untouched. This is a useful inspectability repair with a positive starvation fixture, not a measured historical coverage gain.

## Changes and boundaries

* Strict field answering now refuses stacked Sender/Recipient/Cargo values rather than certifying glued text. Separate paragraphs and ordinary colon-containing values remain usable. This is a deliberate fail-closed tightening, not a changed ownership rule.
* Separate `sorter_v2.py` preserves v1 and rejects reported/quoted/conditional correction proposals. Its existing matching positives remain; matching vocabulary is still not identity proof.
* `answer_router.py` runs strict answering first. Rewrite success is official only for the displayed reformulation. Unofficial material stays explicitly labeled and must pass original-question/profile eligibility, current hashes, retirement and source-state replay. External raw dump inspection is disabled. Classified source copies cannot bypass delivery restrictions; duplicates of served paragraphs are dropped.
* `classing.py` re-derives literal source observations before writing, forbids edits to extracted source meaning or decision inventory, requires explicit serving choices and named declarations, rehearses with native validation, and rechecks sources before publication. Named review/ratification is a declaration, not authenticated independent review. Ordinary append rollback remains available but is not crash-atomic.
* Kernel v5 independently rereads action and complete local paragraph witnesses. Local topic overlap can retain a checked partial, never bind a pronoun/referential object or establish an event. Negated, conditional, quoted, changed-source and cross-paragraph controls remain fail closed.
* `semantic_triage.py` is optional, local, bounded and flag-only. Exact eligible paragraph pairs enter a strict schema. It can emit only quarantined ambiguous-link/possible-contradiction flags; no prose answer, ledger writes, ownership changes, proof slots or promotion. Backend schema constraints are backed by deterministic validation and source-state rechecks.
* `ledger_generations.py` adds optional POSIX staged generations, file/directory fsync, a process-death-released advisory writer lock and atomic `current` pointer replacement. Six subprocess exits test every publication checkpoint. Before pointer replacement the old generation remains selected; afterward the new complete generation is selected. Recovery validates explicit operator selection. This is not physical power-loss certification, a filesystem adversary defense, or a global revocation registry for old copied ledgers. Concurrent multi-read consumers must pin a resolved generation path once.

Existing native ownership, provenance gate, reader and ledger modules are byte unchanged. Browser and MCP pathways remain native; these optional tools add no automatic model or ledger-write path.

## Actual validation

| Check | Revision/scope | Result, exit code |
|---|---|---|
| Full unittest discovery | baseline archive | 1267 passed,0 |
| Full unittest discovery | first freeze f030570 | 1362 passed,0 |
| Full pytest | first freeze f030570 | 1362 passed in457.26s,0 |
| Full unittest discovery | final repaired archive7c92db5 | **1364 passed in398.110s,0** |
| Focused pytest router/discovery | final repaired archive | 23 passed in0.69s,0 |
| Public evidence, require capabilities | baseline and final archives | 52/52 each,0; zero observed false-supported bridges in these fictional controls |
| Unchanged historical direct workers | final source pins | 22/22 completed,0; see table above |
| Separate isolated exploration workers | final source pins | 22/22 completed,0; no expected keys mounted; zero strict slots consumed |
| JS API, UI, transport, crawler | final archive | all retained commands exit0 |
| Actual pinned Pyodide/WebAssembly and collection policy | final archive build | passed,0 |
| Chromium local candidate plus scripted collection/IndexedDB journey | final archive build | passed,0; deployed live site NOT RUN |
| Isolated installed wheel / optional module imports | final archive | passed,0 |
| Classing/router fictional walkthrough | final archive | completed,0; native validate0 errors/0 warnings |

[Final native logs](final-software/report.json), [interface commands](final-interfaces/report.json), [Chromium receipt](final-interfaces/candidate-browser.json), [installed-wheel commands](final-installed-wheel/commands.json) and development logs retain actual outcomes. Full pytest was not rerun after the two additional discovery tests; the final full unittest and all affected pytest tests were rerun. Source ZIP/evidence CRC and SHA seals are retained.

## Costs and semantic sidecar result

Hardware/environment: Linux x86_64, Python3.12.14, AMD EPYC9V74,5 reported logical CPUs with4-core cgroup quota,16GiB memory limit. Updated test/replay runs overlapped, so timings are observations, not isolated speed measurements.

| Native22-worker cost | Baseline | Updated |
|---|---:|---:|
| Native-phase CPU seconds | 245.197 | 268.751 |
| Native-phase wall seconds, summed | 245.368 | 278.334 |
| Peak individual worker RSS bytes | 52523008 | 52588544 |
| Logical original HTML bytes read | 9658683974 | 9658683974 |
| Source-read calls | 54344 | 54344 |

The repeated-source-read cost remains substantial; **no speed improvement is claimed**. Separate exploration cost 14.631s CPU/14.653s worker wall. Final full regression: 373.136s child CPU/399.565s parent wall; maximum child RSS 317009920bytes, not aggregate process-tree memory. Physical disk reads, exploration source-read bytes, remote-server tokens, compute price and human review/correction time remain null/unmeasured.

Live local model: official llama.cpp b12521/6f311d7ad, Qwen2.5-0.5B-Instruct Q4_K_M immutable revision9217f5db79a29953eb74d5343926648285ec7e67, CPU 2 threads,4096 context, no GPU. [Download/runtime pins](downloads.json) record exact URLs/checksums; weights and native binary are not repository dependencies. First pilot6/6 malformed responses rejected. Schema-constrained pilot6/6 valid but all abstained; frozen replay likewise **0 useful flags,0 unexpected flags,4 developer-expected flags missed**, 15.922s controller wall. These6 fictional probes have developer utility expectations, not independent historical labels. Precision is undefined with 0 emitted flags; historical precision/recall stay null. Whole server lifetime across loading and all pilots:75.0 CPU seconds,708771840 peak RSS bytes. Server was stopped normally after measurement. **No demonstrated semantic utility gain.**

## Fresh blinded assessment and remaining failures

A fresh no-history AI session read only frozen questions, original sources and outputs, without expected keys, prior scores or change log. [AI assessment](AI_ASSESSMENT.json):2 complete correct,2 partial correct,5 appropriate refusals,13 over-refusals. All54 quotations/coordinates matched; packet seal unchanged. The final native meanings and packet cases are byte-identical to the assessed freeze; the intervening repair affected exploration only. This is **AI assessment**, not independent human validation, independently unseen accuracy or historical authentication. A matching quotation does not prove the assessment's interpretation. No population accuracy or zero-error reliability can be inferred from 22 development questions and developer controls.

Remaining gaps include proof-copy/publication interpretation, first-person/actor resolution, diary/revision attribution, full omission comparison, documentary vs event dates, archival vs quoted layers, permissions vs execution, and compound assertions. H08's explicit Apollo summary still fails native completion: prefix quotation/context checks and incomplete contrary-evidence scan remain unresolved. Removing those guards merely to pass this question would weaken the contract. Five draft anchors remain unsurfaced. Event identity, causation and correction precision/recall across unfamiliar prose remain unknown. Refusal explanations sometimes lack structured obligations; the case table makes these omissions visible. A model flagger architecture is implemented, but this tested tiny model did not help.

Independent human review,>=200 genuinely unseen questions, historical relationship precision/recall/false-link rates, and human intervention costs: **NOT RUN/null**. No9/10 rating, production-readiness claim or solved historical reconstruction claim is warranted.

## Reproduction and continuity

Use the exact revision and new output directories; never overwrite prior runs. Baseline uses the same commands at bbf6690. Commands below were executed with the available bwrap/loopback capabilities enabled:

```bash
git switch --detach 7c92db5caa39e90fca01fd8e3be5c8c8a2a11c4a
python -m tools.reproduce_boundaries --revision 7c92db5 --output /tmp/mplpb-fixpack-repaired-software --suite full
# The runner executes from the extracted archive:
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/mplpb-fixpack-repaired-software/public-evidence.json
# From the frozen checkout, with unchanged packages throughout:
python -m tools.sorter_first_study prepare /tmp/mplpb-fixpack-repaired-originals
python -m tools.sorter_first_study run /tmp/mplpb-fixpack-repaired-originals --arm direct
# Only after the direct command completes:
python -m tools.evaluate_fixpack_exploration --native-study /tmp/mplpb-fixpack-repaired-originals --output /tmp/mplpb-fixpack-repaired-exploration
python -m tools.report_fixpack_retest --before /tmp/mplpb-fixpack-before-originals --after /tmp/mplpb-fixpack-repaired-originals --output /tmp/mplpb-fixpack-final-comparison.json --table /tmp/mplpb-fixpack-final-cases.md
python -m unittest -q tests.test_ledger_generations tests.test_semantic_triage tests.test_documentary_local_context tests.test_exploration_budget
```

The tested runtime revision includes the runners. `build_ai_packet.py` beside this report generates a new source-only packet from completed native workers, and is an evidence helper added after runtime freeze. Packet and all full worker outputs are retained as SHA-pinned ZIPs in [archive-seals.json](archive-seals.json). Test/backend commands are also recorded in the linked receipts. A future reviewer can redo semantic judgments without the prior AI instance or its private state. `HANDOFF.md` and `handoff/update.json` retain latest task wording, tested pins, limitations and concrete next tests.

Material failed attempts are preserved: pre-fix stacked-field, router and classing boundary regressions; discovery starvation/wrapped-context negatives; invalid model schemas; discovery scoring started before native files existed; first controller final pin validation failed after the discovery-only code repair changed the working tree; one nonexistent HTTP test-module name; one collection-WASM invocation omitted its required report path. Correctly named/ordered final reruns passed. Fixture corrections for actual native scope precedence and explicit fictional reviewer choices are documented. None of these failures were removed from a denominator or called historical successes.
