# Testing and Training Apparatus

Last reviewed: 2026-11-26.

[MPLPB](MPLPB.md) · [Experimental Lab](EXPERIMENTAL_LAB.md)
· [Component map](COMPONENT_MAP.md) · **[Authoritative Test Index](TEST_INDEX.md)**

Here, **training** means the development and evaluation workflow: frozen cases,
rule repairs, contrasting controls, preservation and review. It does not mean
that running Cryptid, TeamBuilding, Thespian or onboarding trains model weights.
The optional browser models are pretrained elsewhere; loading them is inference.
The [owner-corpus preparation tool](../tools/prepare_owner_corpus.py) separately
records that its preparation is not a completed fine-tuning run.

## Find the apparatus

| Apparatus | Purpose and boundary |
|---|---|
| [Test Index](TEST_INDEX.md) and [machine inventory](results.json) | Authoritative case-family/reproduction links; a link is not a new execution |
| [Cryptid](../evaluation/cryptid/README.md) | Shared reader mechanisms, contrasts, budgets and consumed versus fresh transfer |
| [Regression tests](../tests/) | Software preservation, eligibility, citations, interfaces and resource controls |
| [Retained evaluations](../evaluation/) and [earlier probes](../killtest/) | Versioned inputs, outputs, failures and historical measurements |
| [TeamBuilding](TEAMBUILDING.md) | Mitchell's manual Al review / Betty implementation / Outside sounding-board loop |
| [Thespian](BROWSER_TESTING_FOR_AGENTS.md#thespian-multi-agent-testing-method) | Separate asking, answering and evaluation roles; actual custody must be recorded |
| [Onboarding trial](../evaluation/onboarding/2026-11-25/README.md) | Frozen twelve-person first-use protocol; actual human execution **NOT_RUN** |
| [Deterministic rule training](ADVANCED_MPLPB.md) | Replay/evaluate proposed rules; deployment remains a separate code change |

## Read results accurately

Execution failure, reader refusal, semantic miss, strict-key rejection, budget
stop and unscored output are separate outcomes. Preserve original keys and
failures when a later source-checked assessment or prospective policy differs.
Repeated executions and overlapping cases are not independent evidence.

Citation checks establish exact correspondence to eligible source bytes.
Independent historical accuracy and semantic adjudication require their own
evaluations. Same-operator templates and scoring do not establish independent
preparation, blinding or outside-custodian assessment. Unperformed evaluations
remain **NOT_RUN**.

## Onboarding is separate from software verification

Mitchell recruits twelve first-time participants and returns their uncoached
observations. Both groups use identical engine, collection, tasks and interface;
only entry documentation differs. Do not substitute simulated participants.
The frozen arms remain unchanged; the new navigation is not silently substituted
for either arm. Clean-install command checks verify instructions mechanically,
not human usability. [New navigation verification](../evaluation/newcomer-navigation/README.md)

Testing and Evaluation owns this area, with Delivery for reproducible packages
and coordination, Applications for UI checks, and Reader/Ledger for protected
proof and eligibility boundaries. [Department responsibilities](departments/README.md)
