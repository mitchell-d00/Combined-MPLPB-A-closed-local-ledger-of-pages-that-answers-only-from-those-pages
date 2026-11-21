# Executable Gates and Human-Maintained Indexing

Mitchell D. McPhetridge · 21 November 2026

## Abstract

A check enforced inside the path to an action can be shown to stop that action. A check written into notes beside the action can only be shown to have been right when someone last applied it. We test this on Combined MPLPB, a closed local ledger whose work coordinator recomputes source support and seat permission before calling a host executor. In seven paired probes at revision `6ba371c`, every supported control reached the executor (marker file written, two events appended), and every unsupported or unauthorized variant was refused (no marker, zero events appended, zero executor calls). A matched pair of Git repositories shows the same split for document collections. A rule stated only in a README did not stop a push that broke it. The same rule in a server-side hook did stop it. The distinction that matters is not code versus people. It is whether enforcement sits on the only path to the effect, or beside it.

## 1. Introduction

Work that passes between people, model sessions and tools usually carries its rules in prose. A folder holds a file marked "current map". A README says a file is off-limits. A continuity note says "do not expand this relation". These notes can be exact. They still bind only the readers who consult them.

This paper compares two ways of holding the same rules. An executable gate decides in code, on the only path to the effect, whether an action may run. A human-maintained index records the rules where a reader can find them, and relies on someone continuing to apply them.

An earlier draft framed this as code versus people. That framing does not survive scrutiny. A ledger's checks are also written, configured and pinned by a person, and a GitHub protected branch is code that rejects pushes. The claim tested here is narrower: **a rule stops an effect only if it is evaluated on every path to that effect, at the moment the effect would happen.** This is the complete-mediation requirement of a reference monitor (Anderson, 1972), applied to document work.

Section 3 describes the ledger. Sections 4 and 5 report seven paired probes against its executor. Section 6 runs the same kind of probe against Git repositories with and without server-side enforcement. Section 7 states what these results do not show.

## 2. Definitions

| Term | Meaning in this paper |
| --- | --- |
| Eligible source | A page in a registered corpus whose bytes still match the hash pinned when it was cited. |
| Support | A claim is `supported_under_scope` only when a checker finds a complete matching sentence in a pinned quote, with the same subject and polarity, no conditions or assumptions, and no opposing statement anywhere in the cited page. Otherwise it is `contested` or `needs_recheck`. |
| Authority state | The current grant held by a seat: allowed operations, tools, scopes, expiry, revocation and fencing token. |
| Permission | The result computed for one proposed action: `allowed`, `blocked` or `requires_authorization`. |
| Executable gate | A check that runs on the only path to an effect, at the time of the effect, and refuses by default. |
| Practice | The same distinctions held in readable notes, folder layout, commit messages or index rows, and applied by whoever reads them. |
| Effect | Here, a call to the host executor, observed as a marker file written by that executor. |

The support checker is deliberately narrow. Version `work-source-status-v1` handles only unconditional status sentences such as "X is/remains [not] available". It does not test general entailment or factual truth.

## 3. System under test

The system is the specialist-continuity coordinator in [Combined MPLPB](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages) (`mplpb_work`), tested at commit `6ba371ca07dd9269f28af762ed1971ad484fb6b5`. It keeps an append-only, hash-chained event log in SQLite. Every read rebuilds state from that log and verifies the chain, so there is no separate mutable copy to trust.

Work is recorded as typed records: tasks, evidence, claims and action proposals. Seats receive host-issued credentials. An action reaches the executor only through `WorkStore.execute`, which runs these steps:

1. Authenticate the seat's credential and reject it if revoked, expired or fenced out.
2. Check the expected ledger head and action revision, rejecting stale requests.
3. Recompute support for every claim the action depends on, from the current source bytes, and compute permission. Anything other than `allowed` raises `Denied`.
4. Append a `start` event that reserves the dispatch.
5. In a second transaction, recheck the fence, the task revision and every dependency.
6. Call the host-registered adapter, then append a `finish` event with the receipt and attempt record.

A refusal in steps 1 to 3 rolls back its transaction, so nothing is written. A claim's own `assessment` field is never trusted. Support is recomputed at each read, handoff and dispatch.

The executor in these probes is a fixture adapter that writes a marker file and reports a pass. It stands in for any host-controlled operation with a local side effect.

## 4. Method

Each probe is a pair run on two fresh stores built from the same fixture. The control is a fully supported, authorized action. The variant changes exactly one thing that should make the action unsupported or unauthorized.

The fixture corpus is one page, `SRC-0001`: "Configuration AX-14 is discontinued. Component X remains available." Four seats are assigned (finder, critic, builder, reviewer). The finder records evidence and a claim. The builder proposes action `A1` and then calls `execute`.

For each run the harness records:

- the claim's recomputed status and the action's permission, read from the builder's snapshot just before dispatch;
- the row count of the `events` table, read directly from SQLite before and after the `execute` call;
- whether the marker file exists afterward, and how many times the adapter was called;
- the exception or receipt returned by `execute`.

Readback is separate from the code under test. The event count comes from a direct SQL query, and the marker is checked on disk. The harness ran twice, and both runs gave identical results. Environment: Python 3.13.18 on Linux.

## 5. Results

All seven pairs separated. Every control reached the executor, and every variant was refused before it. All seven controls behaved identically: claim `supported_under_scope`, permission `allowed`, marker written, one adapter call, events 9 → 11 (+2), and a receipt of `passed`.

**Table 1. Paired work-boundary probes at commit `6ba371c`**

| Probe | Variant: the single change | Recomputed status | Permission | Refusal at `execute` | Marker | Events before → after | Adapter calls |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 Contradicted proposition | Claim says "Component X is discontinued"; the cited page says it remains available | `contested` | `blocked` | Denied: action not permissible | absent | 9 → 9 | 0 |
| P2 Partial quotation | Evidence quotes only the fragment "AX-14 is discontinued." | `needs_recheck` | `blocked` | Denied: action not permissible | absent | 9 → 9 | 0 |
| P3 Unstated assumption | Claim adds the assumption "Assume source applies" | `needs_recheck` | `blocked` | Denied: action not permissible | absent | 9 → 9 | 0 |
| P4 Claim-only chain | Action depends on a claim that cites only another claim | `needs_recheck` | `blocked` | Denied: action not permissible | absent | 10 → 10 | 0 |
| P5 Source changed after planning | Cited page edited after the action was proposed | `needs_recheck` | `blocked` | Denied: action not permissible | absent | 9 → 9 | 0 |
| P6 Revoked seat | Host revokes the builder seat before dispatch | not readable | credential rejected | Denied: credential rejected, revoked, expired or fenced out | absent | 10 → 10 | 0 |
| P7 Tool not granted | Successor builder seat's contract lists no tools | `supported_under_scope` | `requires_authorization` | Denied: action not permissible | absent | 10 → 10 | 0 |

Variants P4, P6 and P7 start at 10 events because their setup writes one extra record, grant or revocation. The count before dispatch is the baseline that matters.

Three observations follow from the table:

- **The supported path adds two events, not one.** A dispatch writes a `start` reservation and a `finish` receipt. The earlier draft's "+1" should read "+2".
- **Support and permission are independent gates.** P7 keeps a supported claim and is still refused, because the seat lacks the tool. P1 to P5 hold permission constant and fail on support.
- **The claim's own label is ignored.** Every variant claim was submitted with `assessment: supported_under_scope`. The coordinator recomputed the status and refused to dispatch.

The harness (`run_probes.py`) and its raw output (`results.json`) come with this paper. They are not yet in the repository. Running `python3 -I run_probes.py <checkout> results.json` against a checkout of the pinned commit reproduces Table 1.

## 6. Comparison: document collections

The earlier draft said no equivalent probe is possible for document collections. That is too strong. The same probe can be run whenever there is a path to probe. We ran it on two local bare Git repositories (Git 2.43.0). Each held a README saying "frozen.txt is off-limits. Do not edit." A clone then committed an edit to `frozen.txt` and pushed it.

**Table 2. The same rule held as a note and as a server-side gate**

| Repository | Where the rule lives | Push | Server head changed | `frozen.txt` on server |
| --- | --- | --- | --- | --- |
| D1 | README only | accepted | yes | v2 (edited) |
| D2 | README plus `pre-receive` hook rejecting changes to `frozen.txt` | rejected | no | v1 (unchanged) |

D2 behaves like the ledger, and D1 behaves like a practice. A GitHub protected branch or ruleset is the hosted version of D2. So the line does not fall between "ledger" and "repository". It falls between rules evaluated on the push path and rules that only describe it.

The gates still differ in what they can check. A hook or branch rule sees paths, authors, signatures and status checks. It does not know whether a commit's claim is supported by a cited source unless someone writes that check. The ledger's gate is narrow, but it is aimed at support: it recomputes whether the cited bytes still say what the claim says.

Google Drive folders and plain-text continuity notes usually have no path to probe. Opening a folder shows both the "current map" and a later contradictory file. A note saying "do not expand this relation" constrains only a reader who opens it. Drive's sharing permissions are real gates, but they gate access to a file, not whether its content is current or supported.

## 7. Limits and threats to validity

- **Complete mediation is assumed, not shown.** The gate holds only if every route to the executor passes through `WorkStore.execute`. Any process with write access to the SQLite file or the filesystem can bypass it. The repository's own documentation says the local API is a trusted coordinator boundary, not a sandbox.
- **One executor, one fixture.** The probes cover one host adapter with a local effect and one single-page corpus. They do not show that every downstream tool is covered.
- **Narrow support grammar.** The checker accepts only unconditional status sentences. Wider claims fall to `needs_recheck`. That is safe, but it means the gate refuses a lot that a person would accept.
- **Correct against a spec, not against the world.** Code is right only relative to what someone last wrote for it. The ledger's advantage is not that it is never wrong. It applies its rule every time without anyone needing to remember to.
- **Author-run probes.** The probes were designed by someone who knows the system. Variants written by an outside tester, with no knowledge of the checker, would be stronger evidence.
- **History is not truth.** The hash chain detects changes relative to a trusted head. It does not authenticate authors or reconstruct what was historically true. Earlier revisions that let unsupported claims through are kept in the record. The current revision does not let them through.

## 8. Conclusion

An executable gate can be shown by separate readback to have blocked an action. A practice can be shown only to have been correct when it was last applied. In seven of seven pairs, the ledger let the supported action through and refused the unsupported or unauthorized one with no side effect and no event written. A Git repository showed the same split depending on whether its rule sat in a README or in a hook on the push path.

The practical upshot is a test that can be applied to any tool. Ask where the rule is evaluated, and whether the effect can happen without passing through that point. If the rule is evaluated on the only path, it is a gate. If it sits beside the path, it is a practice, however carefully it is kept.

## References

1. Anderson, J. P. (1972). *Computer Security Technology Planning Study* (ESD-TR-73-51). U.S. Air Force Electronic Systems Division. The source of the reference-monitor and complete-mediation requirements.
2. McPhetridge, M. D. [Combined MPLPB: a closed local ledger of pages that answers only from those pages](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages), commit `6ba371ca07dd9269f28af762ed1971ad484fb6b5` (21 November 2026). The relevant parts are `mplpb_work/store.py`, `mplpb_work/source_support.py`, `docs/SPECIALIST_CONTINUITY.md` and `tests/test_specialist_continuity.py`.
3. Probe harness `run_probes.py`, raw output `results.json`, and Git probe `git_probe.sh`, which come with this paper. Run on 21 November 2026 with Python 3.13.18 and Git 2.43.0.
