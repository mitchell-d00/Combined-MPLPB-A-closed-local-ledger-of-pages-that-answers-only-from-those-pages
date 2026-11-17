# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `80a4b02d0a13ac0f986f83622514c4be5dddd844` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `57e22ddb23336d92bf91c98a90ff39e100b0a32a8816b3ba40b5e87c3b345484`.

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

- Baselineec41332:74 focused tests passed6.530s; all22 unchanged historical workers completed under original frozen seals and budgets.
- Final native runtime d369346: complete source support1→2/22, partial2→1/22; onlyH02 changes. Other21 native kinds, claims, excerpts and qualifications unchanged; zero new delivery/execution/truth claims.
- Fresh fork_turns=none blinded AI assessment of44 responses: complete correct1→2, correct refusal4→4, errors/over-refusals17→16, unassessed0. All108 original-byte evidence anchors validated; fabricated quote mutation rejected. AI assessment is not human validation or source authority.
- All3 native claims/8 citations independently rerun through current finite kernel and mapped back to pinned original bytes. Frozen corpus/question/protocol/harness/import/worker limits identical.
- ZIP-extracted80a4b02d0a13ac0f986f83622514c4be5dddd844:1157 tests passed337.950s, public52/52. JavaScript API, browser transport, crawler fixtures, actual pinned WebAssembly and11 actual Chromium documentary/UI checks passed; generated release HTML byte-identical to tested d369346 candidate.
- Combined22-case worker CPU852.674→242.284s with identical logical source bytes read. Single shared-host development replay; supporting-only intermediate and all failed full-test attempts retained separately.
- Intermediate482e498 full1148-test run failed one standard-library allowlist declaration; first arrangement d369346 full1157-test run failed obsolete H02 partial-only expectation. Standard-library declaration and regression expectation updated, preserving no-delivery/source-byte invariants. Final full rerun passed.
- Final documentation/infrastructure/handoff audits and10 handoff/documentation tests passed0.118s. Raw assessment-source whitespace/CRLF is preserved with narrow -text/-whitespace attributes; source bytes were not cleaned.

## Limitations and blocked checks

- The measured completion gain is one development question, not22/22 success, general historical understanding, a9/10 rating or unseen accuracy validation.
- AI assessment used one fresh context of the configured model, with unknown provider/version pin and procedural shared-filesystem blinding; it is not human review, model-provider independence or authenticated historical truth.
- Recorded arrangements do not establish instruction acceptance, execution, dispatch, delivery or event/person identity; printed dates retain heading role.16 AI-assessed errors/over-refusals remain.
- Local storage checks establish byte equality at inspection time under the trusted native host/OS, not durable storage, human reading, delivery or completion. Human effort and AI inference charges remain null.
- Apollo evidence is discovered but remains blocked by earlier OCR quotation state; no quotation safeguard was relaxed to award support.

## Next steps

- Use reconstruct --format text to inspect checked question parts and exact evidence; rerun to check current source eligibility.
- Continue source-preserving improvements for the retained16 AI-assessed shortcomings using frozen before/after outputs and fresh labeled AI assessment, without requiring other people.
- Review local commits through exact-head release workflow before push/merge/deployment; no deployment claim in this update.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
