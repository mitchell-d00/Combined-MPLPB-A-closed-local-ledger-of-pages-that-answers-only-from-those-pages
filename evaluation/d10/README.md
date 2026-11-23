# D10 frozen source suites

Last reviewed: 2026-11-23.

D10 uses the B-Tests D100 topic index and the D% weakness inventory for different
parts of an evaluation. The index turns each of the 75 executable D% classes
into a distinct suite entry. The 15 unmeasured gaps retain their status and
reason. One seeded draw picks ten topics across distinct D100 sections. An
operator supplies a live HTTPS capture or a UTF-8 document for each filled
draw, with exact source bytes, hashes, and a sampled paragraph. The topic
metadata supplies a search lead and carries no answer authority.
[D100 topic catalog](https://github.com/mitchell-d00/B-Tests/blob/0e1dd630d5421fc571992e9d70b459372375b23f/fixtures/sorter_web_topics.json)

The implemented adapter is the D% `exact_anchor` class. It reuses the Primary
Book quote generator to make one exact-quotation question and one altered
quotation absent from the filled source packet. Question order is shuffled
from the pinned inputs. The strict runner receives only samples and questions.
The scorer opens the separate key, verifies the key commitment, and reads
back each citation against the sealed source hash, path, and exact offsets.
The remaining class entries are available for planning and need their own
case-generation and scoring adapters. The native reader and sorter are unchanged.

## Reproduce an exact-quotation run

```sh
root=$(mktemp -d)
python -m test_tools.d10_index \
  --topics /path/to/B-Tests/fixtures/sorter_web_topics.json \
  --study evaluation/dpercent-known-weaknesses/2026-11-20/study.json \
  --output "$root/index.json" --suite exact_anchor --seed 20261123 --plan-output "$root/plan.json"

python -m test_tools.d10_capture --seed 20261123 --output "$root/web" \
  --url https://raw.githubusercontent.com/GITenberg/Walden-and-On-The-Duty-Of-Civil-Disobedience_205/0efbef2325160440b0a7ca7e5130ef566a969985/205-0.txt \
  --rights-url https://www.gutenberg.org/policy/license.html
python -m test_tools.d10_capture --seed 20261123 --output "$root/document" \
  --file evaluation/d10/upload-example.txt

python -m test_tools.d10 prepare --plan "$root/plan.json" \
  --capture D10-01="$root/web" --capture D10-02="$root/document" \
  --output "$root/operator" --custody "$root/custodian"
python -m test_tools.d10 run --inputs "$root/operator" --output "$root/run.json"
python -m test_tools.d10 score --inputs "$root/operator" --run "$root/run.json" \
  --key "$root/custodian/key.json" --output "$root/score.json"
```

Keep the custodian directory away from the engine operator. Use a new output
location for each command. The two fixed capture assignments above exercise
the input paths. Their labels are draw slots and do not imply that the
captures were acquired from the corresponding drawn topics. A topic-aligned
run must record relevant captures for each draw. Unfilled draws remain in the
report and are excluded from positive and control denominators. The scorer
exits nonzero for bad outcomes on filled draws, so assess completeness from
the reported filled and unfilled counts.

For frozen replay, retain the source and sample binaries with their capture
manifest. The local route accepts UTF-8 files and the live route accepts public
HTTPS text, both with a 4 MiB limit. PDF/DOCX extraction and automatic topic
collection are outside this implementation.

## Measured release checks

| Check | Result |
|---|---|
| Ten filled synthetic D10 draws | 10 correct source-and-quote decisions, 10 altered quotes withheld, and identical native replay |
| Mixed capture smoke | 2 correct source-and-quote decisions, 2 altered quotes withheld, 8 unfilled slots, and byte-identical native reports |
| Mutation controls | Changed source bytes, key changes, and wrong citation offsets were detected |
| Local frozen D% pass | 75 attempted, zero completed. Bubblewrap failed to create the UID map before the worker ran. The old batch driver exited zero. The patched driver exits nonzero and keeps all attempted failures visible. |

The PR's [study sandbox workflow](../../.github/workflows/study-sandbox.yml)
runs one isolated D% case per executable class and retains its aggregate report.
The D% development cases include known coverage limitations. The run measures
completion and reports outcomes separately. D10 quote matching establishes
source attribution on these fixtures. Historical interpretation and independent
semantic accuracy remain outside this benchmark.
[Sample draw plan](sample-plan.json) · [Mixed capture and failure receipts](results.json)
