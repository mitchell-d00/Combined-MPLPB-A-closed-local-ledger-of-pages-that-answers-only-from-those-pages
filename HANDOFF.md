# Repository handoff

Last reviewed: 2026-11-17.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `30f0d89c5954b1f1226d0e30c78dc671011849e1` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `4bbe009bea556f17d4090debb3449dee474d53ff4d2f37e0478b8fd96bfff9af`.

## Latest user update instructions

Build (or refine) a sorter whose goal is to take piles of unformatted information and convert them into MPLPB-compatible format so the existing Combined MPLPB ledger and reader can accept, reject, or gate the result under their current rules.

Primary goal
Turn raw piles of text, notes, letters, markdown, or extracted document content into inspectable MPLPB pages or gated candidates. The sorter must produce output that a plain MPLPB checkout can validate, import, or peruse without changing MPLPB’s finite grammar, eligibility checks, or fail-closed refusal behavior.

What the sorter must do
- Accept a directory or collection of unformatted source files.
- Extract candidate keys, dates, headers, cross-references, and repeated phrases while preserving exact source spans and byte/character offsets.
- Assign provisional MPLPB statuses (current/retired candidate, source-occurrence vs. event-candidate, possible correction) without forcing identity. Similar headers or subject lines must not automatically become the same node; changed bodies that share headers must be flagged rather than silently merged.
- Emit two modes from the same extraction:
  - “not-compared”: textual observations and provisional statuses only, with no forced identity or chronology edges.
  - “compare”: the same nodes plus review proposals, relation edges, correction windows, and candidate identity clusters. All edges remain non-authoritative.
- Produce a machine-readable graph or MPLPB-ready pages (with source hashes, spans, and provenance) that the existing reader can seal, withhold, or leave gated.
- Ensure missing intermediate evidence stops a proposed relation. Every output retains the original statement, source location, and any prior assessment.

Constraints that must be preserved
- Never promote weak matches or inferred connections into supported answers.
- Never alter MPLPB’s grammar, gates, or refusal rules. The existing reader must still withhold retired or ineligible material under all delivery profiles.
- Keep the tool offline and runnable beside a plain MPLPB checkout.
- Provide fixtures and tests that demonstrate identical nodes across modes, differing only in edges, and that the reader continues to refuse unsupported claims from the sorter’s output.

Deliver
- Source that implements the conversion from raw piles to MPLPB-compatible format or gated candidates.
- Clear documentation of the input contract, the two modes, the output schema, and the exact commands that show a plain MPLPB reader accepting or withholding the result without modification.
- Explicit notes that the sorter supplies inspectable candidates and does not itself complete historical reconstruction or produce authoritative answers.

## Implemented scope

- Refine existing offline sorter rather than introducing a second conversion engine. Preserve extraction and identical nodes across modes.
- Harden retired snapshot publication with the existing strict native format findings, intact retired-page re-read and exact embedded-graph round trip.
- Expose native validate/show acceptance separately from native gate/ask refusals in documentation and reproducible runner.
- Add both-mode native CLI acceptance, Unicode/CRLF/HTML roundtrip, native-error/warning and validly sealed wrong-body negative tests.

## Validation recorded

- Fresh pre-edit baseline:24 sorter tests passed0.490s; baseline runner passed and native validate --strict reported one retired record with zero errors/warnings.
- Updated focused suite:27 sorter tests passed0.878s. Updated development evaluation runner passed mode equality, native validate/show, gate and ask under all three profiles.
- First new roundtrip assertion omitted the native writer heading and failed two export tests. Corrected the sorter expectation to the existing native format without changing the writer or reader; failed attempt retained.
- Frozen30f0d89 archive:1184 Python tests passed353.340s; public evidence52/52 with required capabilities, false supported bridges0 on authored controls; boundary suite51 passed.
- Actual pre-sorter3df2c6e checkout without sorter: native validate --strict and show exit0; gate/ask exit3 under lab/internal/external, no eligible sources or supported claims. Native reader package bytes identical, per-file hashes retained.
- Compatibility runner --reader-checkout records native command working directories and code hashes; deliberate native-reader mutation refused before command execution.
- Both modes retain176 identical nodes,264 raw edges and341 compare edges; fixture sources/nodes/edges byte-equivalent in meaning to baseline, no forced identity or chronology.
- Actual JS API, browser transport, fixture crawler, pinned WebAssembly and real Chromium published-live/candidate-preview checks passed.
- New versioned evidence directory preserves all prior historical reports and data. Source byte costs2804 per sort; native export development run0.192s wall/0.191s CPU, cumulative child max RSS24,961,024 bytes; no speedup or large-pile accuracy claim.

## Limitations and blocked checks

- Candidate extraction remains lexical and incomplete; no historical reconstruction, semantic accuracy or supported-answer gain claimed.
- Original UTF-8 source bytes and prior assessments remain unchanged; raw headers do not supply ingestion authority or access policy.
- New implementation fingerprint intentionally invalidates old extraction replay; old graphs and dated reports remain preserved.
- Independent historical semantic validation NOT RUN; unknown historical precision/recall and human review time remain null.

## Next steps

- Use python -m mplpb_work.sorter sort on raw UTF-8 text or Markdown and export-retired to a new ledger directory; inspect and validate without activating proposals.
- Use tools.evaluate_sorter --reader-checkout with a separate unchanged checkout to reproduce native format acceptance versus all-profile answer withholding.
- Keep relationships provisional; independent historical semantic evaluation remains NOT RUN and the22-question historical supported-answer metric was not rescored.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
