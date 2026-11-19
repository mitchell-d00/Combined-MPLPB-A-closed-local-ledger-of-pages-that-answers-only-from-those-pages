# Documentary article assembly: development record

Last reviewed: 2026-11-19.

This study adds a bounded research dossier over the existing checker. It does
not add a historical proof rule, choose between competing accounts, merge
events, infer missing links or count independent witnesses. Source authority
and article assembly remain separate. See [usage and contracts](../../../docs/DOCUMENTARY_ARTICLES.md).

Baseline source: `c10a81bcc519a0208ddcc5762edda8e79ea6f9b8`, the source tree
merged in PR #54 (`3a79603e1865f1ef0a1cd1dc72bb656ba5542d8c`).
The 52 focused reconstruction/assertion baseline tests passed. The new article
test module initially failed to import because the capability did not exist;
this is a missing-feature control, not evidence of an old authority defect.

Fifteen new development controls passed in the working tree: separate checked
sections; explicit conflicting positive/negative accounts; three appearances
sharing one declared root; absent ancestry; shared roots across questions;
unchanged native qualifiers/dates; all delivery profiles; question restrictions;
missing causal bridges and actors; source changes between sections; source
corruption; admission budgets; strict plan shape; deterministic replay; and CLI.
These are fictional author-written controls, not independent historical scoring.

At the initial source freeze these checks were pending. They have now completed;
the final results and receipts follow below. The source archives retain that
initial coordination state rather than retrospectively changing its claims.

The original-record study groups the 22 unchanged questions in source order into
plans of at most eight sections, using the same 12-passage/8,000-character native
budget. It compares entire native contracts against standalone calls, keeps
source import receipts and candidate graphs, rechecks seals, and checks ledger
immutability. Frozen seal verification hashes recorded files, including reference
files; expected answers are not parsed, scored or supplied as checker input.
This is a same-process preservation experiment, not a key-isolated or
independently judged accuracy benchmark.

The prior historical result of 2 complete answers out of 22 is not a claim of
improvement from this work. Prior D% results are unchanged retained evidence;
this addition does not rerun or supersede that benchmark.

Independent semantic review: **NOT RUN**. Hidden historical dependencies,
undocumented copying, source authenticity and general event reconstruction
remain unmeasured. Article-level support and historical truth remain false.

Reproduction:

```sh
python -m unittest tests.test_documentary_article -q
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/article-public.json
python -m tools.article_study --output /tmp/new-original-article-study
```

Run against the recorded source revision in a fresh extracted archive. New study
output directories are required so prior runs cannot be overwritten. Costs
measure the entire preservation study, including standalone comparisons and
imports; they are not isolated per-query latency or an efficiency improvement.

## Final results

PR: [#55](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/55), open and unmerged.

- **1,446 Python tests passed**, no failures or skips, from the complete extracted
  source archive `2c173b3ed1533e1f0373756fc02c191dc5da7c3f`.
- Native boundary subset and **52 public-evidence controls passed**, all exit 0.
- Fifteen focused article controls passed from that same extraction. UI script,
  JavaScript/native API parity, browser transport and fixture crawler checks
  passed; these are not real-browser or WebAssembly reruns.
- **All 22 entire native answer contracts matched** their standalone equivalents:
  2 supported answers, 2 partial answers, 3 conflicts and 15 abstentions, assembled
  into 3 dossiers. All source-seal, source-state, ledger-immutability and
  non-promotion guards passed. This is not independent correctness scoring.
- The fictional example retains three source appearances under one declared
  root, leaves witness independence unknown, and displays an opposing fourth
  account as a conflict. All four example checks passed.

The complete archive SHA-256 is
`93c2a17e8956b33c29c42291ef1e120e5f2ad4ac6fde34312d8178b3cad8bc46`.
[Software receipts and complete archived logs](software/report.json) retain the
commands, CPU/wall costs and memory scope. Full-suite wall time was 619.147 seconds,
CPU 600.163 seconds. The runner's process-lifetime maximum child RSS was
389,386,240 bytes, including archive operations; it is not aggregate memory.

The exported-tree study ran the corrected runner from source archive
`c9500e53bbd57e892f87c6fc4968dac0f81cb8b7`, SHA-256
`0e0b0a0e18cbdc9f284418aea90a06f7757c5ae3fba3e944f69babb7840f2ca0`.
Only runtime packages, tools and original-record corpora were extracted for that
study; the complete earlier extraction supplied the full Python suite. All
runtime package bytes and tests remain identical to the full-tested candidate.
[Runner receipt](runner-archive.json) records the scope. The exported study
correctly records a null Git revision and full runtime file hashes; the external
archive receipt supplies the version. This fixes a Git-metadata assumption found
during archive inspection. It did not change the assembler or proof rules.

### Original-record study costs

| Measurement | Value |
|---|---:|
| Whole study wall seconds | 160.004 |
| Whole study CPU seconds | 159.696 |
| Peak study-process RSS bytes | 143,921,152 |
| Total source bytes read | null |
| Human review/correction seconds | null |

These costs include imports, standalone comparisons and reconstruction/assembly.
Linux x86-64, Python 3.12.14; container CPU quota 4 CPUs, memory limit 16 GiB.
Other checks ran concurrently. Neither per-query latency nor an efficiency gain
was measured. [Full study report](archived-originals/report.json),
[raw packets](archived-originals/packets.json.gz), import receipts and
[case table](archived-originals/cases.csv) are retained, along with the earlier
working-tree replay. Exact original excerpts, hashes and canonical coordinates
are inside the native claims and candidate maps. Import receipts enable the
existing reverse mapping; no independent original-byte review is claimed.

### Failures and limits

The first restricted working-tree suite exited 1: 1,434 tests ran, 3 failures,
11 errors and 2 skips. Local sockets were denied with `PermissionError`; the
researcher-pilot workflow assertions also failed under restricted sandbox
execution. The authorized archived rerun allowed the required sockets and
namespaces and passed all 1,446 tests. [Development controls](development-controls.json)
retain the failed-run summary, initial missing-module test and a stale handoff
check invoked before its asynchronous builder had finished. That check passed
after the builder completed. No gate was relaxed to remove these errors.

No new historical answer-coverage gain, event identity, inferred causal bridge,
source transmission authenticity or independent witness claim is established.
Prior D% results are retained, not rerun here. Actual browser/WASM deployment,
live-model efficacy and independent semantic review are **NOT RUN** for this
feature. The next milestone is a general independently checked connection across
sources, contrasted with missing-link, copied-account and conflicting-account
controls. Article prose must not become its own supporting source.

## Every unchanged question

These are native outcomes, not independent judgments of answer/refusal correctness.

| ID | Original question | Native result | Diagnostic |
|---|---|---|---|
| H01 | How could Lyell have finished Darwin's volume on October 3, 1859 before its public release? Separate the letter, proof copies and publication. | abstain | interpretation_unsupported |
| H02 | Who arranged for Wallace to receive Darwin's book, and which dated letter records the arrangement? | supported_answer | supported_documentary_assertion |
| H03 | Does Huxley's November 23rd letter describe a second publication of the book, or his own reading of an earlier copy? | conflict | retrieval_ambiguous |
| H04 | What does the diary say Darwin was correcting at the end of November and beginning of December, and what does that establish about a later edition? | conflict | retrieval_ambiguous |
| H05 | Compare the opening truth claim in Jefferson's rough draft and the final Declaration transcript. What wording changed and what remained? | supported_answer | supported_documentary_assertion |
| H06 | Which passage about the slave trade appears in the rough draft but not in this final Declaration transcript? Can these pages alone identify every person responsible for the deletion? | abstain | interpretation_unsupported |
| H07 | Distinguish the bombardment, surrender, evacuation and telegram dates in the Fort Sumter record, without treating the webpage review date as an event date. | abstain | interpretation_unsupported |
| H08 | According to the Apollo 13 summary, why was the landing aborted and what spacecraft supported return to Earth? | abstain | documentary_assertion_not_established |
| H09 | The Apollo 13 OCR has a change sheet marked May 1970 and a title page marked September 1970. What can this text alone establish about revision order and mission elapsed time? | abstain | interpretation_unsupported |
| H10 | Does the shared language of withdrawal and return establish a causal relationship between the Sumter telegram and the Apollo 13 mission? | abstain | interpretation_unsupported |
| H11 | Did Darwin's note arranging Wallace's book delivery cause the Apollo 13 abort? Provide a source-supported link or explicitly state that it is unavailable. | abstain | interpretation_unsupported |
| H12 | Which named engineer personally authorized an oxygen-tank fire, and which original letter proves that authorization? | abstain | interpretation_unsupported |
| H13 | Which distinct documentary layers in the Sumter page refer to the same historical message, and which statements belong to modern archival framing rather than the telegram? | abstain | interpretation_unsupported |
| H14 | Can the selected Darwin correspondence alone establish whether Darwin or Wallace first conceived natural selection, rather than who read or sent a particular book? | conflict | retrieval_ambiguous |
| U01 | Who appointed Eisenhower to command Overlord, and how does that differ from Eisenhower deciding to proceed on June 5? | partial_answer | partial_documentary_evidence |
| U02 | Did Eisenhower actually report a failed invasion, or prepare a conditional message accepting responsibility if it failed? | abstain | interpretation_unsupported |
| U03 | Distinguish drafting, distribution and the date of Eisenhower’s Order of the Day. Does one date identify all three events? | abstain | interpretation_unsupported |
| U04 | How does the final Emancipation Proclamation quote the earlier proclamation, and what scope qualification limits its application? | abstain | interpretation_unsupported |
| U05 | Does the proclamation free every enslaved person in every state without exceptions? Show the limiting language rather than silently removing it. | abstain | interpretation_unsupported |
| U06 | Who surveyed Yellowstone, and what documentary actions did he subsequently take to promote protection? Separate archival framing from the act itself. | partial_answer | partial_documentary_evidence |
| U07 | Does the Yellowstone law make leasing compulsory, or grant discretion subject to a term limit? | abstain | interpretation_unsupported |
| U08 | Did the Yellowstone legislation cause the Normandy invasion? Is there a documentary causal link between these records? | abstain | interpretation_unsupported |
