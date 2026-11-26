# Bunyip round 2: recovered C3 review checkpoint

Last reviewed: 2026-11-26.

**Source and public evidence are published on PR #106. Release is BLOCKED.**
The 572-case development comparison passes its source-key assessment, and all
832 public preservation contracts are unchanged. The remaining 17 private
preservation cases cannot currently execute under required local isolation.
A publication custody incident also remains unresolved in earlier Git history.
Neither held transfer packet has been opened. No merge or deployment occurred.

## Measured software results

| Set | Released main | C3 | Scope |
|---|---:|---:|---|
| Exposed development source-key decisions | 489/572 | 572/572 | Same original inputs and questions |
| Positive targets | 57/128 | 128/128 | 71 recovered positive executions |
| Contrasting decisions | 432/444 | 444/444 | 12 prior unsupported admissions corrected |
| Public consumed preservation | 832 reference contracts | 832/832 exact | No changed contract or execution failure |
| Private consumed preservation | 17 reference contracts | BLOCKED | One failed isolation probe; 16 not run |
| Bunyip BB positives | 900/900 | 900/900 | 150 canonical + 750 paraphrases, unchanged |
| Bunyip BB negative controls | 200/200 withheld | 200/200 withheld | Original benchmark expectations |

Development candidate: `483f35a97a32be4cadb4eb224e976e045124901d`.
Preservation candidate: `3bf9657c7b956623f07ed4b94765e0edd5cd3f02`.
Both contain the same recovered C3 native bytes first published at
`baa19f5b9d6d733735b4c570c74d7a643cd06e6e`.
Released baseline: `2622813aba9ee1f1880693eeb71ae015cb3da999`.

The 71 recovered positive executions represent **34 original question strings
and 71 unique source–question inputs**. The matched-source wording diagnostic
accounts for 40 executions / 19 strings; the other 31 source/proof recoveries
remain separate. The 572 memberships contain 524 unique inputs and 89 question
strings. Repeated executions, tags and rewritten-question diagnostics are not
additional newly answerable original questions. Already-working title decoys
are preservation evidence. Ownership policy and native caps are unchanged.

[Development outputs and original scores](remote-development-v1.json) ·
[Public preservation receipt](public-preservation-remote-v2.json) ·
[BB matched-source receipt](bb-c3-receipt-v2.json).

The [exact README software walkthrough](quickstart-software-v1.json) passed all
11 checks from an empty setup using the released wheel. Its actual commands and
stdout are retained; the twelve-person human trial remains NOT_RUN. Four new
public artifact downloads were independently checksum-checked after publication.

## Original failures and qualifications

The original strict key still fails **22/572** candidate outputs. A separate
source audit finds all 22 correct under the polarity/readable-output contract
frozen before implementation, with exact quotation fidelity. Original keys,
scorers and failed scores were not changed. Source support and output-contract
compliance are reported separately.

Rejected C1 and C2 remain rejected for two and four unsupported contrasting
cases. The local C3 primary attempt completed 75/444 and had 369 execution
failures; its guards completed 0/44. Remote preservation attempt 45870399223
completed 321/849 with exact contracts, left 528 execution failures and then
failed artifact retention on file permissions. Its complete job log is retained;
its first-attempt raw outputs were not successfully retained by Actions.
The subsequent public-only run completes 832/832 and does not turn the 17
private cases into passes.

An initial BB archival comparison failed because separately generated ledger
timestamps produced different source hashes. Those original runs and the failed
assertion remain recorded. A new matched-source audit uses the exact same 100
source-file hashes for both readers: 900 unchanged positive contracts and 200
unchanged withholding decisions. Ben Gelhaus authored the external benchmark and
analysis; Mitchell authored the implementation. This consumed benchmark is
regression evidence, not unseen transfer or historical accuracy.

## Custody incident and release blocker

The new archive introduced at `9b4bdf98453b017187256904af8f7bec9a54c80c`
mistakenly included 17 PE-02 outputs whose original manifest marks
`public_raw_output=false`. Its interrupted companion included 34 log files
from those cases. Both archives were removed from the current tree at
`bfd41a5a1392ccd5579b0e789be98690cffb6a1b`.
**Earlier Git objects may remain retrievable. This is not history erasure.**

[Incident record](custody-incident-v1.json) and
[public-only replacement receipt](public-preservation-v2.json) retain what
happened. The replacement uses the original disclosure flags for every member;
no private case payloads are in it. Original local archives remain unchanged.
The full original reference is also retained privately at
`/workspace/cryptid-custody/released-849-reference-private-retained-v1.tar.xz`
with SHA-256
`71bd781c5a10041652a6b83d7d4b29ff30042f79006c00c7f5301b75fc1ae7a2`.

No held transfer inputs, held keys or private correspondence were included.
The **36 routing + 64 cross-family cases remain UNOPENED / NOT_RUN**.
Preparation, implementation and scoring remain same-operator work.
Independent preparation/blinding, semantic/historical adjudication,
outside-custodian scoring and native OOCC remain NOT_RUN.
Human onboarding remains NOT_RUN until Mitchell supplies observations.

The superseded source-ZIP run 45870407049 was force-cancelled before artifact
publication to avoid redistributing the withdrawn archive; the observed artifact
list is empty. It remains a cancelled gate, not a pass. Current-head checks run
separately. A duplicate documentation review marker also caused a retained CI
failure; its prospective label fix preserves the original date.

The private probe failed closed with
`bwrap: Can't fork for pid 1: Resource temporarily unavailable`.
No unsandboxed fallback was used. The denied PID1 diagnostic was not executed.
A failed tool approval is infrastructure evidence, not a reader test failure.

## Continuation and navigation

1. Resolve the publication incident's remaining history exposure.
2. Run the 17 unchanged private cases in their original custody with working
   required isolation; compare their complete contracts.
3. Freeze a committed source ZIP and its checksum after preservation; open each
   held packet only at its designated freeze, once. Retain every result.
4. Complete exact-head checks, then protected merge and deployed fingerprints
   under Mitchell's existing authorization. Do not bypass a required gate.

The [product guide](../../../../docs/MPLPB.md),
[Experimental Lab](../../../../docs/EXPERIMENTAL_LAB.md) and
[testing apparatus](../../../../docs/TESTING_APPARATUS.md) are the three entry
areas. The [Test Index](../../../../docs/TEST_INDEX.md) remains authoritative;
the [component map](../../../../docs/COMPONENT_MAP.md) connects all seven
departments without moving implementation or frozen evidence.
[Working-state handoff](../../../../HANDOFF.md#betty-report-for-al).

## Retained earlier round report

The following dated report preserves its original baseline and earlier
checkpoint statements; the current state above supersedes its pending-status
language without changing its measurements.

# Bunyip round 2: whole-question relation and argument binding

Original round report review date: 2026-11-26.

**Current state: actual C3 source and reviewed evidence are published. All572 exposed development source-key decisions pass after remote execution; preservation/fresh transfer/latest-head gates remain unfinished. No merge or deployment.**
The unchanged baseline completed21/78 positives and360/366 withholds, with57
positive misses and six unsupported competing-time answers. C1 and C2 recovered
those primary targets but failed new contrasting controls and were rejected.
C3 focused37 tests pass; broad checks remain incomplete. See the
[current working-state handoff](../../../../HANDOFF.md#betty-report-for-al).

The baseline sections below retain their original results; they are not the
current candidate's acceptance result. Original strict-key failures remain
separate from later source-checked assessments and prospective output contracts.
Released main is `2622813aba9ee1f1880693eeb71ae015cb3da999`, containing PR105.
Its eleven exact-head checks, protected merge and deployed verification passed;
[release reconciliation](released-state.json) records the receipts. The exact
old handoff is preserved in [dated history](history/pr105-pre-reconciliation.tar.xz).

## Current decisions and continuation

The repair carries relevant unresolved evidence to final admission rather than
treating failed interpretation as absence of competing evidence. It must also
preserve answers when unreadable material is irrelevant. Ownership policy and
native budgets remain unchanged. C1's two reported-field unsupported completions
and C2's four mixed-binding unsupported completions remain failures and exposed
development controls; neither candidate opened transfer.

Canonical [roles and acceptance](../../../../docs/TEAMBUILDING.md#al-and-betty-work-steps)
and [artifact/working-state recovery](../../../../docs/TEAMBUILDING.md#recover-artifact-state-and-working-state)
govern continuation. [Documentation clarification receipt](role-clarification-v1.json)
links the prior handoff snapshot. Completed attempts and the interrupted C3
attempt are durably retained in versioned local custody archives listed in
HANDOFF; historical source archives remain untouched.

Both held packets (36 routing and64 cross-family cases) were sealed before reader
changes and remain unopened/unrun. Preparation, implementation and scoring are
same-operator. Freeze a committed candidate ZIP after preservation checks before
opening either designated packet. Publication remains authorized only through
passing acceptance and required normal release gates.

Approximately32285 adopted zombie processes were observed; new process/thread
launches fail EAGAIN. The PID1 diagnostic probe was denied and not executed.
This is an infrastructure/approval failure, not a reader refusal. Required
isolation must not be bypassed. Inspect retained C3 logs and rerun affected checks
after process capacity is safely restored.

## Frozen development

[Public source/question bytes and outputs](public-evidence-v1.tar.xz), [version/seal receipt](freeze.json), and [baseline summary](baseline-summary.json) retain the original experiment.

444 cases use the unchanged D% worker, runner and scoring, Dice Bag seals/replay,
and D20 unique/competing/missing/retired conditions. Three everyday domains cover
medial source attribution, category/time wording and object-free task questions.
Actual adjacent-line and paragraph source bytes differ. Wrong arguments, negation,
conditions, additional obligations, task ambiguity and classification yes/no/
unmentioned contrasts remain in the matrix. Nothing is filtered by reader result.

The generator is [tools/bunyip_round2_packets.py](../../../../tools/bunyip_round2_packets.py).
Original questions are scored; canonical probes are diagnostics, never recoveries.
Same operator prepared and scores development; no independence is claimed.
At baseline freeze, fresh wording structures were NOT_PREPARED. Subsequently,
36 routing and64 cross-family cases were sealed before native edits; neither
packet has been opened for evaluation.

## Baseline execution accounting and storage receipt

The initial script invocation failed before any worker with ModuleNotFoundError;
the retained retry uses `python -m tools.dpercent`. Required Bubblewrap is enabled;
no unsandboxed fallback is allowed. All444 baseline workers completed/scored with zero worker failures; one separate prelaunch failure executed no readers. There are78 unique question strings,396 unique source-question-state inputs and48 repeated memberships. Full positive discovery is78/78; interpretation/proof misses remain. The six false flags involve competing opening times and require source/proof investigation. Keys, inputs and all raw baseline outputs are durably retained: [baseline container](baseline-retained.tar.xz), [hashes and denial receipt](retention.json). Every896 original output/score/log file was byte-verified. The workspace has less than400KiB free.

At that baseline stage, auto-review rejected replacing a full frozen archive with a verified lossless
encoding: specific storage modification had not been authorized. That action was
NOT_EXECUTED; the original archive is untouched. This is infrastructure, not a
reader failure. Full candidate/preservation/transfer/release remain pending. The original feature breakdown omits72 typed-instruction rows; overall/by-family totals include all444. No scorer amendment or relabelling was made.

## Reproduction

```sh
python -m tools.bunyip_round2_packets --out /tmp/bunyip-r02-public --custody /tmp/bunyip-r02-key
MPLPB_REQUIRE_SANDBOX=1 python -m tools.dpercent run --packets /tmp/bunyip-r02-public --out /tmp/bunyip-r02-baseline --implementation .
python -m tools.dpercent_expanded score --packets /tmp/bunyip-r02-public --custodian /tmp/bunyip-r02-key --run /tmp/bunyip-r02-baseline --output /tmp/bunyip-r02-score.json
```

Keep original strict-key failures and all earlier Cryptid packets unchanged.
Bunyip BB is separate consumed external regression evidence, not unseen transfer.
Human onboarding, independent historical/semantic adjudication, independent
preparation/blinding, outside-custodian scoring and native OOCC remain NOT_RUN.

## Appended routing, polarity and museum-copy baseline

[Routing seals, baseline results and retention](routing-freeze.json) preserve the
Outside-reported ownership lead as synthetic contrasts; the original Outside
packet was not supplied, so this is not an exact replay. Development54completed:
10/16positives,38/38withholds, six interpretation misses, zero unsupported
completions. Six lexical ambiguities already resolve through native body checks;
there is no new routing gain. The conjunction inside Dungeons and Dragons is
rejected by the ordinary-question entity guard before yes/no proof.

A separate18-case polarity control set completes4/6positives and12/12withholds.
The prospective [yes/no contract](routing-yes-no-contract-v1.json) fails6/18:
four existing positive answers lack explicit structured polarity/readable Yes
output; two explicit negatives remain withheld. Original scores stay unchanged.
This is a new contract/coverage target, not a retroactive released promise.

Conflict, similar-entity identity, ineligible support, title/scope-only claims,
quoted negation, cross-page implication and existing agreeing-owner ambiguity
remain protected. Four metadata-adapter parity executions preserve exact original
answer contracts. The unchanged D% runner/scorer were reused; at that baseline,
no native or ownership policy had changed. A36-case structurally different packet/key/generator is sealed,
NOT_RUN and unopened after generation apart from byte hashing/archival. Visible
same-operator templates are not independent preparation or blinding.

[The museum-copy protocol](museum-copy-protocol.json) is separate. At baseline it was NOT_RUN;
subsequent software CLI/JavaScript checks are distinct from human execution.
It distinguishes displayed supporting sources from eligible corpus passages and
requires decision-preserving, diagnostic-driven wording. A local UI-copy change
now exists; candidate/deployed verification remains pending.
All original/amended inputs, keys, raw results and failed assessments are retained
in the hashed local custody archive named in the receipt; held keys stay outside
the candidate source ZIP. The original key-bearing input container remains in custody. Public subsets and rejected source snapshots are versioned separately; source publication is not release acceptance.

## Published and measured state

Actual native source was recovered directly, not reconstructed:
[source hashes](recovered-source-v1.json). [Public artifacts](public-artifacts-v1.json)
and [input/adapter receipt](public-input-supplement-v1.json) record versioned
payloads. Initial public HTTPS downloads at commit73e07a8 matched all four SHA256
receipts. Original baseline and rejected C1/C2 source archives are byte-identical.

| Same frozen development inputs | Released main | C3 source-key result |
|---|---:|---:|
| Primary positive answers /78 |21|78|
| Routing positives /16 |10|16|
| Explicit polarity positives /6 |4|6|
| Contrast positives /20 |14|20|
| Relevant mixed-binding withholds /4 |0|4|
| Irrelevant-evidence positives /8 |8|8|

All572 cases completed on each revision under the existing Bubblewrap worker.
C3 passes572/572 source-key decisions:128 supported positives and444 correct
withholds, zero unsupported admissions, lost valid support, citation changes to
preserved support, execution failures or budget stops in this comparison.
There are89 distinct original questions and524 unique source-question inputs;
48 repeated memberships do not add independent evidence.

Recovered positive executions:71 across34 original question strings and71
source-question inputs. The post-run wording-only diagnostic accounts for40
executions/19strings on sources whose canonical proposition the baseline already
admitted;31 other source/proof-reach recoveries remain separate. No rewritten
question, tag validation or infrastructure success is counted as an answer to
the original question. These are exposed development results, not fresh transfer.

Original strict-key scoring still rejects22 outputs. Each passes the prospective
polarity/output contract frozen before implementation and exact citation checks.
Those strict failures remain unchanged beside the separate source assessment.
Twelve lost-support flags are corrected baseline unsupported answers; all twelve
were frozen refusal controls, not lost valid support.

The interrupted local attempt remains75/444 completed,369 execution failures;
its44-case guard run completed zero. These failures are preserved, not relabelled
as reader refusals. C1/C2 remain rejected for their2 and4 contrasting unsupported
completions even though their primary recovery passed. Remote regression at
source commit baa19f5 passed1904tests(1skip), JS/API, WASM and Chromium; later-head
and full preservation requirements remain in force.

The public bundle contains identical development bytes under inputs/primary,
inputs/guards, inputs/mixed-binding and inputs/irrelevance. The routing supplement
contains inputs/routing and inputs/polarity and original baseline outputs.
The original key-bearing frozen input container stays in designated custody.
No held key, sealed transfer input or private correspondence is published.

### Reproduce public execution

Extract public-evidence-v1.tar.xz and public-routing-inputs-v1.tar.xz into one
new directory. Reuse the existing API; output paths must not already exist.

    from pathlib import Path
    from tools import dpercent as D
    D.run(Path("/tmp/public/inputs/primary"), Path("/tmp/replay-primary"),
          implementation=Path.cwd())
    D.ROOT = Path("evaluation/cryptid/bunyip/round2/metadata-adapter").resolve()
    D.run(Path("/tmp/public/inputs/routing"), Path("/tmp/replay-routing"),
          implementation=Path.cwd())

Require Linux Bubblewrap and unchanged budgets. Launch failure is execution
failure, never an unsandboxed fallback. The custodian scores original outputs
with the original held development keys and unchanged published assessor.
All36routing and64cross-family transfer cases remain unopened/NOT_RUN until
candidate ZIP freeze. Same-operator custody limits remain; independent historical,
semantic, preparation/blinding, outside-custodian, OOCC and human execution stay
NOT_RUN. Publication, verification, merge and deployment are separate states.

The complete matched remote comparison is retained in
[the versioned result receipt](remote-development-v1.json),
[original baseline outputs](remote-483f35a-baseline.zip),
[original candidate outputs](remote-483f35a-candidate.zip), and
[strict scores, source assessments and audit](remote-483f35a-assessments-v1.tar.xz).
The executed candidate was483f35a97a32be4cadb4eb224e976e045124901d;
the baseline was2622813aba9ee1f1880693eeb71ae015cb3da999. The worker made no
model calls. Native original questions, source bytes and budgets were unchanged.
