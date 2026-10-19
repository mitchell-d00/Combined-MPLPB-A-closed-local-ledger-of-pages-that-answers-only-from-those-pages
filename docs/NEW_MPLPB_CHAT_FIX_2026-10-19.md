# Newly built MPLPB chat and clean source previews — 2026-10-19

## User-observed reproduction

After a bounded `search God` crawl, the browser built five pinned pages (God (word), God, Christianity, Judaism, Islam). `show my MPLPB` listed them, but typing `Islam` in Serious mode returned generic guidance instead of selecting its exact page. After selecting the page manually with `focus collection :: Islam`, `summarize it` displayed Wiki navbox parameters such as `abovestyle`, `list1name` and CSS.

## Change

- **Serious mode:** An exact eligible page title now selects its hash-pinned page, the same as choosing its explicit `focus collection :: title` command. Duplicate titles remain ambiguous and require an explicit collection choice. Other loaded collections cannot silently supply facts after selecting a specific page.
- **Loose Chat mode:** An exact saved page title opens separately labeled source exploration *without* adding collections to the active serious scope. Follow-ups like `summarize it` and `tell me about it` use the current saved topic; any returned sources retain their independent corpus/path/hash pins.
- **Dictionaries:** The existing WordNet dictionary/thesaurus requests remain available in both modes, with `lexical_reference` rather than page evidence authority. No dictionary synonyms become ledger ownership evidence.
- **Summaries and topic snippets:** A presentation-only filter hides unmistakable navigation/template markup while keeping literal source lines untouched. If no readable body prose remains, a summary refuses with a direction to inspect the original pinned source instead of repeating navigation code or inventing content.
- **Unchanged:** Stored capture bytes, page and lineage SHA-256, ownership decisions, source eligibility, delivery profiles, archived provenance, network controls and all existing API method contracts.

## Test

```sh
python3 -m unittest tests.test_chat_environment tests.test_mind_session -q
python3 -m unittest discover -s tests -q
```

PR validation also checks JavaScript, browser transport and the real WebAssembly build. Developer fixtures are regression checks, not independent human evaluation. No prior saved data should be cleared or rewritten for this change.
