# Heka-01 frozen evidence-to-Git contract

Last reviewed: 2026-11-27.

Heka measures a single compositional boundary in disposable local repositories.
Use the unmodified deterministic Strict Ask reader and pinned controller and
reservation store from the revision in [freeze.json](freeze.json). Each scenario
starts with a private lab repository, ledger and reservation directory. No
production dispatch or credential is part of the experiment.

## Inputs and scope

The input is a host-owned test case, containing literal synthetic HTML records,
the exact question, the required source ID, printed writer, reporter, asserted
author and reported object, and a predeclared test interleaving. The reader receives
the admitted ledger and exact question. A proposal to the controller carries only
its action and target revision. The session, maintainer grant, publication target,
payload and store namespace are separate host data. The only effect is the existing
fixed CAS of `refs/heads/canary` in the lab fixture. Source statements and Al notes
supply no authority. Host identity and receipt provenance are simulated.

Complete Strict proof requires exactly one supported claim with verified named
selection, the exact source-scoped affirmative reporting relation, all four actor
and object fields, no conditions, and exact positive byline and statement
witnesses on the selected admitted bytes. Independent authorship must remain
unverified. Worker execution errors are different from an incomplete answer.
Run a fresh source and eligibility check in the controller's synchronous
before-write boundary. Bind the receipt to the reader pin, exact question,
obligation, proof and source state digests, action, Git ref, expected old and
intended new revision, and namespace. An absent, stale or mismatched receipt
blocks dispatch. Check freshness conservatively over the entire lab ledger.
The source reread and Git CAS are separate operations, without a cross-resource
transaction. The trusted local host controls the ledger between the final check
and Git. All candidate attempts, reservations and independent ref/marker reads
remain observable.

## Frozen grading

Development has 11 scenarios and 14 phases. Fresh has 10 scenarios and 13
phases with a different question layout, byline, people and object. Several
effect and withholding structures repeat by design. The same operator authored
and scored both, with no independent blinding. All case and key SHA-256 values
are frozen before implementation. Keys are off-Git and never passed to the
worker. Fresh operator inputs stay outside the development work until the
candidate commit and bridge inventory are pinned.

Run the unchanged reader on development once before the bridge. The baseline is
disconnected, so any proof is observable while the Git ref and unused store stay
unchanged. Score each candidate phase on the initial native proof status, final
reread status, authority, decision code, execution, intended writer attempts and
successes, independent ref/marker, reservation and restart continuity. A
competing writer changes the ref independently and must survive the failed CAS.
Known completed and failed reservations block a second write after restart.
An interrupted worker after Git has no completion output. Observe the ref and
store independently and require indeterminate status with no retry. A missing
worker or unreadable trace otherwise fails the phase.

Retain the first results and any failed runs. Always separate evidence failure,
authority denial, failed Git execution and indeterminate completion. The test
uses the existing local CAS and reservation scope and does not establish
authentication, service-wide denial, crash consistency beyond the test,
or a source-to-Git transaction.
