# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `482e4987fec1d91c835a08198b140892bb0dc661` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `2402362114547fe6aa0e927586365a896eac2f63634512635f1f52710111dadb`.

## Latest user update instructions

Do the parts we don’t need other humans for I’m solo and have no access to other people

current changes improve inspection and speed is good too but milestones is key imo

That is a clean next step, and the boundary you already drew is the right one.
A letter that contains:
• a reported instruction,
• a named writer and recipient, and
• a printed date
can support a complete answer to the question “What arrangement does this letter state?”
It cannot support a complete answer to “Was the arrangement carried out?” or “Did delivery occur?”
So the rule stays inside the ledger if it is phrased as:
• If the current owner page is a letter that explicitly states an instruction, names the writer and recipient, and bears a printed date, then that combination is sufficient to answer an arrangement question about the content of the letter.
• The same page remains insufficient for any claim that the instruction was received, accepted, executed, or that anything was delivered.
That preserves the distinction the comparative paper already treats as load-bearing: source integrity and proposition support inside the grammar are not outside-world truth. A stored letter is evidence of what the letter says, not evidence of a completed external act.
Practical check on the 22 frozen questions:
• Count how many currently incomplete arrangement answers become complete under this rule.
• Confirm that zero new delivery or execution claims appear.
• Confirm that refusals on the non-arrangement questions stay refusals.
• Run the blinded fresh-session judge against the frozen documents and require it to cite the exact instruction, names, and date. Label the result “AI assessment.”
If those four hold, the rule is a measured completion gain on unchanged documents without loss of precision. If the judge cannot cite all three elements, or if any delivery claim slips through, the rule is still too wide.
The supporting tools stay separate; they do not count toward this milestone.

## Implemented scope

- Cache immutable exact-content record parsing in eight bounded entries while rereading sources and retaining fresh policy/eligibility/hash checks.
- Link documentary question obligations to their actually displayed checked evidence; add readable reconstruction CLI and browser question-part view with canonical coordinates.
- Add native host-only bounded local storage byte inspection/recheck to existing receipt operation, without asserting delivery, human reading, completion or historical truth.
- Rerun unchanged original-record development questions with existing frozen seals and isolated workers, record CPU/wall/RSS/read costs and preserve all old results.
- Add finite independent recorded-arrangement completion with exact printed-party/object bindings, heading date and full-local-letter third witness; delivery/execution truth flags remain false.

## Validation recorded

- Baselineec41332:74 focused source/reconstruction/provenance tests passed6.530s.
- Development88 focused tests passed5.809s and UI script check passed. Initial new test expectations for capitalization/retrieval-versus-display budget were corrected; no support rule changed.
- Final committed source ZIP validation and original-record before/after runs pending.
- Intermediate482e498:1148 tests ran351.638s, one dependency-allowlist failure because functools was not yet explicitly permitted; public52/52, JavaScript and WebAssembly passed. Explicit standard-library dependency list updated without permitting network/model imports.
- New arrangement completion plus existing repo/documentary/solo controls:80 tests passed5.404s; development unchangedH02 gains source-only completion with three citations, pending frozen final runs and blinded AI assessment.

## Limitations and blocked checks

- Independent human semantic evaluation remains unavailable and is not required to use these software improvements; it will stay NOT RUN rather than blocking implementation.
- No historical truth, authentic external delivery or event identity is inferred from recorded arrangements. Full unprepared historical reconstruction remains unresolved; AI assessment will be labeled separately from human review.
- Local storage inspection proves byte equality at inspection time under a trusted host/OS, not durable storage, delivery, human reading or task completion.

## Next steps

- Freeze implementation and run extracted regression/public/JavaScript/WebAssembly/Chromium controls.
- Complete unchanged original-record before/after experiment, retain failures and report actual costs without independent accuracy claims.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
