# Al Notes: versioned repository relay

Last reviewed: 2026-11-27.

This is the canonical Al-note set for this repository. Mitchell authorized
repository notes to replace the manual copy-paste relay. The first example is
[0001: Gremlin and the repository relay](0001-gremlin-and-repository-relay.md).
[Note 0002](0002-first-live-relay-and-bastet-integration.md) records the first
reported successful live relay and the concurrent Bastet integration. The notes
are coordination records; they are not imported source-ledger facts.

## Roles and authority

Al normally reviews evidence and proposes bounded next work. Publishing an Al
note records advice without turning it into a Betty result or a maintainer
instruction. Implementation outside that normal Al role needs an explicit
maintainer override recorded with its scope. Note 0001 records Mitchell's
Gremlin override. This does not imply a permanent change of role or independent
review of Al's own implementation.

Mitchell's authorization is identified separately from advice, software output,
and the note's claimed role. An author or role label is not authentication.
Nothing reads this directory and automatically dispatches work, grants a
capability, changes release requirements, or merges a PR.

## Write and consume a note

Use a numbered Markdown file and the [template](TEMPLATE.md). Record the
reviewed base revision, evidence, recommendations, authorization scope,
implementation under any override, checks actually performed, limits and next
step. Link the note from the PR report. Do not edit a published historical note
to claim a later outcome; append a dated follow-up or a new numbered note.

Betty reads the note at its actual Git commit, then records in her own PR report
and handoff: note path, note commit, read status, what she applied, deferred or
rejected, resulting implementation commit, and checks or blockers. Reading and
applying are separate events. A non-implementation note can be acknowledged
without changing source. A note commit is an identity pin, not proof that its
recommendations are correct or authorized.

After compaction or a fresh session, recover the newest applied PR report and
handoff before following a note. A newer proposal does not supersede a checked
result by date alone. For concurrent Bastet and Gremlin work, preserve both
working-state records and reconcile deliberately.

## Visibility and custody

Only publish approved public coordination material here. Do not copy held keys,
restricted source text, private correspondence, or hidden scoring material.
An unlinked public file remains public. A fresh evaluation participant must
follow its frozen reading route; prior answers and scores in notes are exposure,
not fresh evidence. The note relay's effect on time, cost and correctness is
unmeasured until a separately designed evaluation runs.

`/workspace/AL-NOTES.md` may serve as a local pointer to this set. A local path
is not automatically present on another machine. Use the repository commit
and note path for the durable cross-session relay.

## Later Al advice

[Note 0003: next phase](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/a36cc00a52d28588e22a1e0faa5e6451451976fa/handoff/al-notes/0003-next-phase-evidence-to-git-effects.md)
retains its original publication pin. [Note 0004](0004-heka-diagnostic-disposition.md)
addresses the held Heka-01 diagnostic differences; it records advice rather than
a new implementation or a changed score.
