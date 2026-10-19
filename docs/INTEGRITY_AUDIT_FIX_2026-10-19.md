# Ledger integrity and source-answer audit — 2026-10-19

Baseline: published GitHub Pages build from main commit `b98ee7e`; additional adversarial report and nine developer reproductions in `mplpb_bug_repros.py` supplied in the issue discussion.

## Corrections

1. **Withdrawal must be final**: a valid `retire` event in the local chained ledger log overrides a file that was later manually changed from `retired` to `current`. Serving refuses the page, and validator reports C16. This does not authenticate the log: an attacker who can replace both page files and all log bytes may still forge a consistent chain.
2. **Header integrity**: read `<title>` and `mplpb:` fields only inside `<head>`; duplicate normalized metadata fields produce C17 and quarantine the page. Writer refuses duplicate updates rather than updating just one of several copies. Do not auto-reseal malformed records.
   Legacy aliases such as `mplpb:taught_from` are updated in place during explicit adoption rather than creating a duplicate normalized field.
3. **Quantity constraints**: a lexical majority can no longer match a numeric question unless all explicit numeric tokens appear in that page's declared scope or when-to-use. This intentionally sacrifices some loose recall for safety; particularly `cone 04` cannot silently be treated as `cone 6`.
4. **Negation and exclusions**: preserve `not` as a content token, and decline negative questions in the legacy lexical owner, which cannot establish logical polarity. Map `severe/critical` to `serious` only when applying excluded high-risk burn/injury topics, avoiding an unsafe synonym bypass.
5. **Unicode**: preserve Unicode word runs instead of shredding non-ASCII terms. Unknown non-English questions are unknown terms rather than falsely reported as having no content words.
6. **Answer presentation**: keep unsupported retrieval diagnostics under `answer_support.candidate_checks` but do not list zero-match owners as supported answer candidates. The Ask tab now has an explicit `Strict` and `Inspect` selector; Inspect is tagged candidate-only, never evidence of a supported answer.

## Historical compatibility

- Existing archived evaluation JSON files are not regenerated; regression tests compare the new reader's safety metrics with those frozen baselines instead of requiring identical old mistakes.
- A validated legacy supersession can still restore its original page when its successor is corrupted, as the original lineage rule requires. A standalone withdrawal remains non-servable after its log `retire` event, even if its unhashed status attribute is edited. A corrupted existing log makes the reader abstain.
- The historical reference encyclopedia capture still retains its original `engine_sha256` pin and has not been modified. After core code changes, read-only archival reference browsing is permitted only when the saved source, served-page and renderer pins validate. This does **not** mean that the old capture was revalidated under identical engine bytes; strict code-pin verification continues to report engine drift.

## Limitations

The finite statement grammar is deliberately conservative: no change converts all built-in demo questions into verified answers. The new Inspect UI allows readers to see lexical candidate pages separately; it must never relabel them as verified. No machine-learning system, online authority, or broadened delivery profile is added.

No archived ledger page, stored browser session, source pin, historical evaluation file, or persisted metadata is automatically rewritten. Existing malformed pages are quarantined until explicitly repaired.

## Validation

```sh
python3 -m unittest tests.test_integrity_hunt tests.test_record tests.test_ledger tests.test_answer_support -q
python3 -m unittest discover -s tests -q
python3 tools/check_ui_script.py
node tests/javascript-api.cjs
```

PR CI additionally exercises the actual browser/WebAssembly runtime. Report numbers only after completed runs. This is regression testing and does not prove correct answers on arbitrary corpora.
