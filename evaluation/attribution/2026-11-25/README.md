# Shared source-attribution trial

Last reviewed: 2026-11-25.

Baseline PR #101 head: `28b8feb871cd0c2eb29440f2ab46623e410622b6`.
Native code is unchanged at this freeze. [Rule and acceptance](rule.md),
[freeze and seed](freeze.json), and [maintainer clarification](maintainer-direction.md)
were recorded before implementation. [Development inputs](development/inputs.json)
contain 48 cases; 24 transfer inputs and both scoring keys are held separately.
The answer worker receives no key path. Its transfer baseline was retained
without opening its case bytes or outputs to the implementer.

This is **same-operator transfer testing**. Betty authored and saw the generator,
including its transfer templates, and prepares and scores both sets. Only exact
transfer instances and their key remain unopened until a committed candidate
and ZIP freeze. This is procedural separation, not independent preparation,
blinding or adjudication. Different sentence structures, question forms, actors
and tasks are used; the generator's visible grammar limits any transfer claim.

Development baseline: 24/48 decisions correct, 24 positive misses, zero
false-supported claims and zero budget failures. All 24 withholding targets
withhold. Clarified expectations give 24 positives and 24 withholds; attributed
quotations naming the correct speaker are positive. The original proposed
12/36 counts were superseded before the freeze, not relabeled after results.
Transfer outcomes and candidate acceptance are pending. The candidate must run
on transfer once; inspected failures become development material.

Preservation includes all 17 PE-02 cases and 28 targeted native regressions,
comparing complete answer contracts, citations, qualifiers, missing obligations
and discovery arrays. Historical, semantic, outside-custodian, independent
preparation/blinding and native OOCC evaluations remain **NOT_RUN**.
