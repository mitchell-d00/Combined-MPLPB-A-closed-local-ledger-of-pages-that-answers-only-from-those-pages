# Heka-01 withdrawal discrepancy disposition

Last reviewed: 2026-11-28.

Betty applied [Al note 0004](../../../handoff/al-notes/0004-heka-diagnostic-disposition.md)
at `5cd0b2c042a6c6edeec564f55392a614b0b5a8fb` to the lab checkpoint on
[PR #120](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/120).
The original [contract](CONTRACT.md), [grades and effects](README.md), raw
evidence, scorer, key seals and candidate bytes retain their original hashes.
The original grades are 10/11 baseline, 12/14 development and 13/13 first
fresh. Future replays of those packets are consumed preservation.

Both isolated rereads on the unchanged released reader reproduced the
[recorded outcomes](evidence/diagnostic-disposition.json). After withdrawal
neither fixture has an eligible page. Strict Ask returns
`restricted_or_unavailable` at eligibility before it calls the named-report
verifier. The key expected that verifier's later
`named_report_source_unresolved` diagnostic. D-04 differs in its initial
proof diagnostic. D-07 proves the statement initially and differs in the
reread diagnostic after withdrawal. Both have zero writer attempts and
writes, an unchanged Git ref and marker, and an unused reservation.

The mismatch is a frozen expectation discrepancy. All protected Heka effects
and recovery outcomes are unchanged. Each first bridge draw observed three
intended updates, including one interrupted update. Two completions were
durably recorded per draw. The exact phase scores retain both mismatches.

GitHub's active main rules require a PR, current required checks
`archive-first` and `regression`, and reject non-fast-forward updates.
The repository release procedure also calls for exact-head source and
working-state verification. The applicable rules do not make a perfect
Heka phase score a condition of publishing a completed lab study.
The [live PR report](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/pull/120)
tracks the new exact head, readback, merge and applicable Pages check.

The Heka authoring script and both original keys were copied byte-for-byte
to a separate permission-restricted workspace archive and read back. Both
keys match their original SHA-256 seals. An independent off-workspace private
backup has not been verified. The public checkpoint contains the exact source
inputs, logs and scope of custody, with held keys outside public artifacts.
Production dispatch, credentials, the reader and controller remain unchanged.
