# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `63cea982399280b4fa634893799e6642cbd19436` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `3c40030622e1bb55472279faa3556f5ebaafc9575a4a82d7a28bff4c7097a861`.

## Latest user update instructions

CODEX BUILD PROMPT — MPLPB Historical Reconstruction Engine
Build a working, source-grounded historical reconstruction engine inside the existing Combined MPLPB repository.
Build the actual implementation. Do not merely produce a design document or implementation proposal.
Every accepted source-supported claim must have an inspectable, independently checked evidence path. Every unverified historical interpretation must remain explicitly unverified.

Codex, I want you to take Combined MPLPB to a genuine 9/10 research-engineering standard by making it more capable, accurate, independently verifiable, and easy to use.
Proceed with the implementation and make the strongest measurable progress possible in the available environment. Do not claim a target has been met unless actual results demonstrate it.

Build and test rules then code that resolves source identity and historical truth, but don’t break mplpb, build a crawller set it has basic crawllers in repo

Set rules for historical truth to be entered do synthetic historical truth so the method has a test subject

Summarize what all we are doing and then continue

How can we improve Complete historical answers

Have history built as MPLPB are added if a relationship exists it is set and mplpb can suggest other relationships but not as factual as human eyes seeing what may be historical can that work ?

How can we fix it 2 → 3 out of 22 unchanged questions; complete supported answers remain 0/22.

22/22

Summarize all we are doing and then continue

## Implemented scope

- Extend existing source-unit inspection, complete-context discovery, obligation retrieval and independent documentary kernel for literal causal/temporal/resource/passive assertions and exact wording comparisons.
- Expose a reversible candidate graph and reconstruction CLI using existing source/provenance/reader systems; content-only bounded projection cache never caches serving decisions.
- Extend existing crawler with direct public URL seeds, optional source hashes and explicit byte-versus-event identity boundaries. No deployment or paid search requirement for direct seeds.
- Add capability-gated typed historical-review entries through existing WorkStore; synthetic oracle fixture exercises rules without claiming real historical truth or real independent reviewers.
- Add target accounting after existing human-review/adjudication validation; 200 unseen-question independent evaluation and performance targets remain unmeasured.
- Rehash both bounded raw crawler captures before accepting byte identity; reject forged hashes and missing raw payloads.
- Add an independently derived source-framed literal-comparison completion proof: explicit body-role declarations, unique source/work references, opening-topic paragraphs and all question operations; never force22 affirmative answers to unsupported questions.

## Validation recorded

- Baseline4d0f447:1068 tests passed376.449s;62 focused tests14.641s; public52/52. Fresh baseline22-case runs preserved with exact original seals/questions/budgets.
- Intermediate5b6632a passed1106 tests; fresh comparison full0/22 and partial2→3/22. Its complete outputs, costs and failures remain unchanged in phase1 paths.
- Final extracted63cea982399280b4fa634893799e6642cbd19436 passed1124 tests in394.726s; public52/52; expert stages; JavaScript, both crawler suites, actual WebAssembly, nine actual Chromium UI checks and installed official MCP SDK1.29.0 client45 checks.
- Final unchanged22-case runs completed: full0→1/22 and checked partial2→2/22. H05 closes literal comparison obligations using four body/wording witnesses; source authenticity/finality and historical truth remain unverified. All7 accepted citations passed fresh kernel/digest and original-byte mapping checks.
- Actual-source temporary legal revisions of author/work remove completion; original frozen bytes unchanged. All2246 prior historical evaluation files and baseline tests preserved; final runtime/tests/tools match63cea98.
- Crawler live LOC attempt blocked by robots policy; zero live captures, no bypass. Synthetic truth fixture matches its separately pinned oracle but does not constitute real history or human review.

## Limitations and blocked checks

- The result is not22/22 correctness, a9/10 rating or independent80/95/75/95 performance. Independent human review, adjudication and >=200 unseen questions NOT RUN; unknown semantic metrics/human times null.
- Only the supplied source-declared reconstruction/transcription and literal opening-topic differences are complete. Historical authenticity/finality, person/event identity, motives, missing links and independently verified historical truth are not established.
- General entity/pronoun resolution, arbitrary historical correction/chronology, full-document absence, damaged OCR quotation handling and automatic corpus-wide history maintenance remain incomplete.
- Repeated authority reads remain costly; no material speedup is established. New engine changes are locally committed, not pushed/merged/deployed in this iteration.

## Next steps

- Obtain two independent human reviews/adjudication of complete frozen packets before historical accuracy or target claims.
- Build checked identity/reference, temporal, correction and complete-search obligations for further genuinely answerable questions while preserving warranted refusals.
- Integrate an incrementally maintained history view with existing evidence/claim/review states and current-source invalidation; keep suggestions and accepted interpretations separate from facts.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
