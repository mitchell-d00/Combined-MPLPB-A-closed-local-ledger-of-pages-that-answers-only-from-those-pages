# Bunyip: ordinary-language questions over source-supported propositions

Last reviewed: 2026-11-26.

**Released reader: main `2622813` (PR105). Required exact-head checks, protected
merge and deployed verification passed.** See the [release receipt](round2/released-state.json).
[Round2](round2/README.md) has published actual C3 source and reviewed public evidence;572 exposed development source-key decisions pass. Preservation/fresh transfer/latest-head checks remain pending; no round-two release or historical-accuracy claim.
Earlier candidate snapshots below retain their original measurement scope.

## Primary goal and separate measures

Broader ordinary-language generalization is the primary development goal. Memory,
provenance and source admission are preservation requirements. Count newly
answerable fresh wording, lost valid support and unsupported claims separately.
Tag validation, layout repair and test infrastructure are never wording gains.
Matched canonical-source probes distinguish wording recovery from newly admitted
source/proof operations; these post-run diagnostics are not additional fresh or
independent evaluations. Original fresh outcomes remain unchanged.

First two fresh packets: **11 newly answerable question strings /22paired
executions versus released main** on sources whose canonical question was already
supported; versus PR105,14strings/28executions. Eight other successful executions
versus main require source/proof-operation reach and are separate. No tag/layout/
API/infrastructure success counts as a language gain.
[Canonical-source diagnostic and retained v1/v2 assessment](final-review/wording-diagnostic-first-two.json)
are same-operator post-run attribution, not extra fresh cases or independent scoring.

## Matched development results

| Same frozen inputs | Released main c01021c | PR105 ab8f73e | Revised reader |
|---|---:|---:|---:|
| Positive completions /60 | 12 | 16 | 56 |
| Withholding controls /42 | 42 | 42 | 42 |
| Original strict decisions /102 | 50 | 58 | 98 |

Paragraph HTML and newline-preserving plain text each improve8→28/30positives
versus PR105 (released main6/30). The40additional completed executions represent
**20unique primary question strings**, repeated across two renderings. Every
recovered claim, qualification and exact citation is checked by the frozen
[source scorer](../../../tools/bunyip_score.py). Four explicit field-of-ID
questions still miss at proof. Original inputs, keys and failed scores remain
unchanged. Four main strict flags concern absent additive polarity metadata,
not four established false facts: [representation review](baseline-representation-review.json).

[Protocol](protocol.json), [development seal](development/freeze.json),
[main baseline](runs/baseline-main/run.json), [PR baseline](runs/baseline-pr105/run.json).
Al's separate8/24paragraph/4/24plain diagnostics were leads; their inputs were
not supplied, so these are not claimed as that reviewer's diagnostic replay.

## Rejected attempts and preservation

- C1: primary98/102but four unsupported scope-Wrap completions; rejected.
- C2: primary98/102and scope24/24but ten unsupported long/governor cases; rejected.
- C3: development138/142and849prior contracts exactly unchanged from PR105.
  Full native1882tests found one failed test containing two public preservation
  regressions: owner conflict and partial correction. C3 is rejected.
- First title repair C4a: public52and16focused tests pass, but title controls
  remain12/16because imported headings duplicate the generated display title.
  Its full native-package ZIP, source hashes and original failures are retained.
- C4b: development154/158, including all16title controls, zero false-support
  flags. Four primary proof misses remain. Consumed42 stays36/42unchanged.

The shared title repair permits literal source correspondence under leading
fictional display headings matching the record title, including duplicate
imported display titles. It retains other qualifiers, body headings, quotations
and conditional scope. Documentary action verification keeps its conservative
default; no independent real-world truth is established.

[Raw retained runs](final-review/retained-runs-2.json) and
[C3 software/legacy/failed title repair](final-review/c3-software-and-legacy.json)
point to hashed lossless archives. The initial nested worker launch102failures,
first legacy replay390completed/610disk execution failures, missing wheel build
backend and two consumed-baseline prelaunch path failures remain distinct from
reader outcomes. The wheel retry passed; no unsandboxed fallback was used.

All849C3contracts match PR105 exactly after removing only the code fingerprint.
All145claim-bearing main cases were assessed:137unchanged; eight invalid
header-fused actors were corrected(four) or withheld(four), not valid support
losses. [Classification audit](assessments/main-support-classifications.json).
C5 local preservation matches all849PR contracts exactly; full final native CI remains required.

## First fresh packet: retained, now consumed

The first once-only42completed36/42decisions:22/28positives,14/14withholds,
zero false-support flags, six positive misses. Both pinned baselines complete
0/28on identical inputs. The22executions represent11unique question strings.
Paragraph and plain renderings each complete11/14. No native repair used those
six misses. The later title repair was required by the public preservation gate.
The packet is now preservation/development evidence for the revised candidate.

[Unchanged score](final-review/fresh-transfer-once-score.json) and
[remaining misses/policy disagreements](final-review/remaining-misses-and-policy.json):
four instruction-paraphrase interpretation misses; two opening-hours questions
whose key treats an opening time alone as complete. That obligation/policy
ambiguity is reported separately; the original strict-key failures remain.
A new prospective partial policy would require fresh fixtures, not relabelling.

The [24-case composition packet](fresh2/transfer-seal.json) was prepared before C4 repair,
opened once on committed C4 and is now consumed. It tests
limited composition of unseen question prefixes and new document/header layouts;
visible same-operator templates do not establish independent blinding or broad
language transfer. The recorded seed is a protocol identifier; generation uses
deterministic templates rather than random sampling.

## Acceptance policy versus reader gains

The legacy RAM-staged retry completes1000/1000workers and preserves1000full
contracts. Its old strict-key result is still FAIL. The separately frozen
[source-checked v2 policy](assessments/prospective-retention-v2-policy.json)
validates44formerly unscored outputs plus21additive-field cases against original
source bytes and qualifications, then requires complete execution and exact
retention of all1000contracts. It passes on C3; this is a prospective acceptance
assessment, not additional reader coverage. The host-only script invocation
failure is retained; CI uses its correct module invocation. C4 exact-head checks
remain required before merge.

## Reproduce and inspect

```sh
MPLPB_REQUIRE_SANDBOX=1 python tools/cryptid_trial_v5.py --registry evaluation/cryptid/bunyip/development/registry.json --implementation . --source-commit COMMIT --output /tmp/bunyip-run
python tools/bunyip_score.py --registry evaluation/cryptid/bunyip/development/registry.json --key evaluation/cryptid/bunyip/development/key.json --run /tmp/bunyip-run --output /tmp/bunyip-score.json
```

Use `tools/cryptid_replay_packet_v5.py` for consumed packets. Keep scoring keys,
generators and Git outside readonly, networkless workers. Existing8record,
200000character,1000unit,12passage,8000output caps remain unchanged; worker
CPU30seconds/wall45seconds. Execution failure is unscored, never an abstention.
The [Test Index](../../../docs/TEST_INDEX.md) is authoritative.

[Newcomer command verification](../../newcomer-navigation/README.md) is separate
from the unchanged human protocol. Human execution, independent historical and
semantic adjudication, independent preparation/blinding, outside-custodian scoring
and native OOCC remain **NOT_RUN**. Preparation/scoring are same-operator.

## Final compatibility repair and fresh material

C4 full native1884 completed with one API error: a body-only imported record
lacked optional title metadata. All other36software gate records passed, public52
passed, all849contracts matched PR105, and legacy1000completed with1000exact
contracts under prospective v2. The original strict score remains FAIL.
[Raw C4 retention and failed-gate record](final-review/c4-completed-gates-and-transfer.json)
uses [verified lossless reference storage](final-review/c4-raw-storage.json); the
original receipt/container and every raw outcome are retained.

C5 treats missing/non-string title metadata conservatively. It preserves ordinary
body-only records while granting no fictional-heading exemption without matching
metadata. Two frozen API controls originally errored;22affected API/ordinary/public
tests now pass. This compatibility repair creates no answer-coverage gain.
[Control freeze](final-review/optional-metadata-control-freeze.json) and
[local preservation](final-review/c5-local-preservation.json) retain the evidence.

C5 development remains154/158with zero false flags; consumed42remains36/42and
consumed24remains20/24. The latter completed8/12positives versus0/12on both
baselines and retained12withholds. Its four misses are two opening-time cases
and two instruction questions. [Mechanism diagnoses](final-review/remaining-miss-diagnostics.json)
preserve original automated stages and distinguish recognized frames from correct
interpretation: explicit field/ID binding is incomplete; a catalogue preamble
closes the leading declared-field block. No reader repair used these transfer misses.

A new [sealed16](fresh3/transfer-seal.json), prepared before the C5 compatibility
patch, remains unopened until the C5 committed ZIP is frozen. It uses a new
source belongs-to form, new composed questions, reversed date-role order and nested
source layout. Same-operator templates are visible; no independent transfer claim.

The final source ZIP receives focused native and preservation checks locally.
The complete1885-test native suite and all required exact-head software gates
must pass in protected CI before merge; the failed C4 full run is never relabelled
as a local C5 pass. Final live publication/deployment state belongs in PR105's
head-pinned Betty report. All unperformed independent/human/OOCC labels remain NOT_RUN.


## Current extension: ordinary questions remain the target

The [D% extension](dpercent/README.md) reuses the existing isolated worker, Dice
Bag custody and D20 matched controls. Current development32/32positives versus
12/32before this extension,108withholds,zero unsupported additions/lost valid
support/citation errors. This is10new original question strings/20executions.
All849old contracts are exact. Fresh separately written packet is pending the
committed ZIP freeze. Canonical rewrites and revealed-confirmation proof are
separate diagnostics, never recovered original questions.

The C5 sealed16has now completed14/16decisions:6/8positive,8withholds,zero false
flags. Original once-only42/24/16packet outcomes remain36/42,20/24,14/16. C6's
consumed replays are40/42,22/24,14/16; those improvements are development, not
new transfer. Two opening-hours policy disagreements, two catalogue-preamble
field misses and two object-free instruction questions remain unresolved.
The raw C5final16and post-run diagnostic are retained in final-review.

[Bunyip BB](bb/README.md) separately preserves Ben Gelhaus's unchanged external
900positive/200negative benchmark. No historical accuracy claim or pooled score.
Broader wording is the primary goal; tags/layout/infrastructure are separate.
Existing coverage gaps can remain backlog under incremental release criteria;
lost valid support and newly unsupported claims require investigation.


## Release review: measured wording gains

Latest [fresh D%packet](dpercent/fresh-summary.json):C5 8/24→C6 14/24positive
executions,84/84withholds,ten remaining misses,zero unsupported additions/lost
valid support/citation failures. Three original ordinary question strings become
answerable, repeated across six executions/fourunique source-question inputs.
No canonical/revealed-proof diagnostic is counted as recovery. Against released
main, wording-only gain is one new question string/two executions; eight additional
positive executions require source/proof reach. Report these measures separately.

Frozen reader source7e272e5d9742931feef05fc004a84d6846a55f39;ZIP SHA-256
93dc3e10895c2670f1952b74840c9d187f5bcc3c942e0d9a0b6870c03fa15b89.
[Complete source/pin receipt](dpercent/c6-source-freeze.json). Subsequent changes
are evidence/navigation only; required exact-publication-head checks remain pending.
Bunyip BB separately preserves900positives/200negatives and900exact citations
on each matched revision. No pooled accuracy or independent historical claim.
