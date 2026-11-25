# Shared source-attribution trial

Last reviewed: 2026-11-25.

Baseline PR #101 head: `28b8feb871cd0c2eb29440f2ab46623e410622b6`.
[Rule and acceptance](rule.md), [freeze and seed](freeze.json), and
[maintainer clarification](maintainer-direction.md) were committed before
runtime changes in `be167fb`, followed by the result-index correction `3fffe29`.
The native baseline is unchanged from the specified pin. Main's publication
merge was incorporated as ancestry only with the same source tree.

## Custody and freeze

[Development inputs](development/inputs.json) contain 48 cases. Twenty-four transfer inputs, their baseline output and both keys were held separately before the candidate freeze. [Consumed transfer inputs and outputs](transfer) are now public; keys remain separately held. The
worker receives no key path. The transfer baseline worker read the instances;
the implementer did not open their bytes, key or output before the candidate freeze. [Transfer baseline
seal](baseline-transfer-seal.json) binds that output before implementation.

This is **same-operator transfer testing**. Betty authored and saw the generator,
including all transfer templates, and prepares and scores both sets. Exact transfer instances and key stayed unopened until the committed candidate and source ZIP freeze. This is procedural separation, not independent preparation,
blinding or adjudication. Transfer uses passive/recipient-first and postposed
quotation structures, different question forms, disjoint actors and new tasks.
Known generator templates limit the transfer claim; unopened instances do not
make their grammar unseen. Historical/semantic evaluations, outside-custodian
scoring, independent preparation/blinding and native OOCC remain **NOT_RUN**.

The clarification superseded the initially proposed counts before any freeze:
a correctly named quoted speaker is a positive target. Development contains
24 positives and 24 withholds; transfer contains 12 of each. Expectations follow
the actor and reporting layer, not a forced positive/negative ratio.

## Original development and limited first transfer

| Frozen measure | Baseline | Candidate |
|---|---:|---:|
| Expected decisions | 24/48 | 48/48 |
| Positive source-attributed instructions | 0/24 | 24/24 |
| Withholds (wrong actor or execution) | 24/24 | 24/24 |
| False-supported decisions | 0 | 0 |
| Budget failures | 0 | 0 |

Each source form contributes eight positive and eight withholding targets.
All 17 permanent PE-02 answer contracts and discovery arrays are identical,
excluding only code fingerprint fields. Meanings, actors, missing obligations,
qualifications, citations and prior diagnostics stay identical. The 28 earlier
targeted regressions and 28 new attribution/state/budget controls pass (56 total).
[Exact comparison](development-evidence/preservation-candidate-3-score.json).


The first transfer packet was executed **once** on committed source `d0f6c67e0684d952afc47c13b83963ca7976d2bb`, from its checked ZIP extraction. Expected decisions improve **12/24 → 24/24**: positives **0/12 → 12/12**, all **12/12 withholds** retained, zero false-supported decisions and zero budget failures. Each form has **4/4** positive and **4/4** withhold decisions. The separate source-byte audit verifies all 24 transfer bodies and 28 citations. [Transfer scores](transfer/candidate-score.json) and [custody timeline](custody-timeline.json) retain the distinction between worker access, generator visibility and implementer inspection. No transfer-informed repair occurred. This packet is consumed. Supplemental development controls had already exercised passive/postposed constructions, so its structural novelty is limited. Its decision passes do not meet a strong unfamiliar-structure claim. A fresh 24-case packet with different constructions is being frozen before any further native repair.

Historical completion remains **1/4**, historical partials remain **1/4**, and source propositions across the permanent 17 remain **five**. This cycle adds synthetic class coverage, without a new historical answer-coverage gain.

Tested source ZIP SHA-256: `0f3148b4a3ef061388a990ef0d0fc306838077ddde18f004285ac404faeee155`. [Candidate freeze](candidate-freeze.json) binds the commit, complete tree and native fingerprints. Its first extraction lost one shell executable bit; permissions were restored from the unchanged ZIP metadata, then the full tracked extraction matched the commit. Source-byte/citation and preservation audits pass; full archive release validation and exact-head CI remain pending.

## Fresh structural transfer after protocol correction

A separate [fresh rule](fresh-transfer-rule.md), [freeze](fresh-transfer-freeze.json)
and baseline seal were committed at `e787bde` before the next native change.
Recipient-fronted nominal and possessive argument-order constructions differ
from the original 48 and all supplementary controls. Actors, tasks and seed are
new. Question interfaces are held constant with the consumed first packet,
so the new structural test focuses on source language. Templates were authored
and seen by the same operator; exact instances stayed unopened until the new candidate/source ZIP freeze. No fresh-structure development examples were run.
The candidate preserves the original 48, consumed first 24, all 56 controls and
17 PE-02 contracts. Fresh transfer passed **24/24** decisions on its once-only candidate run: **12/12 positives**, **12/12 withholds**, zero false support and zero budget failures. Each form has four positive and four withholding targets passing. The separate audit verified 24 bodies and 28 citations. [Fresh outputs and scores](fresh-transfer) retain the original first packet separately. No native source changes followed fresh transfer inspection. Exact-head CI remains pending.

Fresh tested source: `7ed65a589d8051ff659495972fab922ff802b20e`. ZIP SHA-256: `93d801d6554575542d50fee557ddbd099c607f1325ef6c8aed917d32768918fb`. The complete tracked extraction matches the committed tree. Its [focused/software/browser checks](fresh-archive-checks) and exact-head CI have distinct receipts; the earlier 1,779-test local pass belongs to source `d0f6c67`, not these later bytes.

## Mechanism and rejected candidates

A shared [source-attribution checker](../../../mplpb_answers/source_attribution.py)
derives a writer from canonical salutation/full signature or an explicit
recording/writing byline. Complete instruction predicates derive the speaker,
recipient, task and quotation boundary separately. Active, nominal, passive and
postposed quotation constructions reach the same role representation. The
[native instruction checker](../../../mplpb_answers/attributed_instruction.py)
rereads currently eligible originals and verifies witnesses before accepting
one unambiguous proof. Its claim retains the writer/reporter layer, instruction
modality, qualifications and no-completion status. It does not authenticate an
instruction's historical occurrence or prove execution.

The old PE-02 questions continue through their existing signed-letter rule;
new source-framed requests use the shared attribution rule. No runtime branch
uses fixture identifiers, actors, labels, seeds or a scoring key. Limits remain
eight records, 200,000 canonical characters, 1,000 units, twelve passages,
8,000 citation/output characters and existing bounded phrase sizes. Withdrawal,
source mutation, unresolved context, competing sources and exhausted budgets
withhold rather than pruning hard evidence.

All rejected sources, native outputs and control logs are retained in
[development-evidence](development-evidence). The first candidate passed the
48 frozen decisions but supplemental controls found passive capitalization
misses and one false support under a separate conditional governor. Early
control-harness record lookup and invalid minimum-budget errors are retained
alongside corrected controls. The second passed those repairs but an expanded
control found a falsely supported claim after an unframed competing instruction
was pruned. The third retains such relevant unresolved competition and passes
all 56 focused controls. No frozen expectation was edited. No native source was changed after the once-only transfer run.

## Reproduction and preservation

Use `tools/attribution_trial.py prepare` with the seed in `freeze.json`, a fresh
separate custody directory and the frozen rule. Require exact generator/harness,
packet and key hashes. Run baseline with `--implementation` at the specified PR
head, and candidate on the committed ZIP extraction. The run command has no key
argument; only `score` receives one. Transfer candidate execution additionally
requires a committed archive receipt and creates an exclusive once-only marker.
Retain all outputs; never overwrite an attempted run.

For permanent historical preservation, restore the unchanged originals under
FRUS-PE02's existing permission/seal rules, replay the same 17 with
`tools/pole_frus_pe02.py`, then compare with
`tools/compare_attribution_preservation.py`. Public receipts omit permission-
reprinted text but retain hashes. Do not publish the restricted originals.

Run `python -m unittest tests.test_source_attributed_instructions
 tests.test_signed_instructions tests.test_documentary_named_advice
 tests.test_documentary_presentation tests.test_documentary_errata
 tests.test_pole_focus_extend -q` (join into one shell command).

After a committed candidate/source ZIP freeze, run transfer once. Preserve
failures as failures. A repair informed by them consumes that packet as
development; a new transfer claim requires a fresh frozen set.


## Final local release checks

[Validation receipt](validation.json) separates source `7ed65a5` from the prior
full-suite archive. The revised ZIP passes 48 original development decisions,
24 consumed-first-packet complete contract comparisons, the fresh transfer
once, all 17 PE-02 contracts/discovery arrays, 56 focused controls, 52 public
controls, fifteen JavaScript/HTTP/report-pin/infrastructure checks, actual
WebAssembly, both Chromium contexts, installed-wheel and 45 SDK checks. Its
candidate browser module hashes match the frozen native source. Published
Chromium here is a premerge baseline, not the new deployment. Exact-head
archive-first/regression CI performs the complete revised-source suite before
merge; its result and archive checksum are recorded in the live Betty report.

No native source was edited after fresh transfer inspection. Historical,
semantic, outside-custodian, independent preparation/blinding and native OOCC
evaluations remain NOT_RUN. Future cycles preserve the original 48, both
consumed 24-case packets and all earlier controls, using their consumed
`development` freeze descriptors. Fresh transfer claims require fresh packets.
