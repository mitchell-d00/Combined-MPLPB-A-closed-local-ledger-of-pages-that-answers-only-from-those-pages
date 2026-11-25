# Shared source-attribution trial

Last reviewed: 2026-11-25.

Baseline PR #101 head: `28b8feb871cd0c2eb29440f2ab46623e410622b6`.
[Rule and acceptance](rule.md), [freeze and seed](freeze.json), and
[maintainer clarification](maintainer-direction.md) were committed before
runtime changes in `be167fb`, followed by the result-index correction `3fffe29`.
The native baseline is unchanged from the specified pin. Main's publication
merge was incorporated as ancestry only with the same source tree.

## Custody and freeze

[Development inputs](development/inputs.json) contain 48 cases. Twenty-four
transfer inputs, their baseline output and both keys are held separately. The
worker receives no key path. The transfer baseline worker read the instances;
the implementer has not opened their bytes, key or output. [Transfer baseline
seal](baseline-transfer-seal.json) binds that output before implementation.

This is **same-operator transfer testing**. Betty authored and saw the generator,
including all transfer templates, and prepares and scores both sets. Exact
transfer instances and key stay unopened until a committed candidate and source
ZIP freeze. This is procedural separation, not independent preparation,
blinding or adjudication. Transfer uses passive/recipient-first and postposed
quotation structures, different question forms, disjoint actors and new tasks.
Known generator templates limit the transfer claim; unopened instances do not
make their grammar unseen. Historical/semantic evaluations, outside-custodian
scoring, independent preparation/blinding and native OOCC remain **NOT_RUN**.

The clarification superseded the initially proposed counts before any freeze:
a correctly named quoted speaker is a positive target. Development contains
24 positives and 24 withholds; transfer contains 12 of each. Expectations follow
the actor and reporting layer, not a forced positive/negative ratio.

## Development result before transfer

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
all 56 focused controls. No frozen expectation was edited. Transfer remains
unopened and candidate archive/transfer acceptance is pending.

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
