# Test tools

Last reviewed: 2026-11-22.

Use these tools to test the engine and reproduce project results. See the [Test Index](TEST_INDEX.md) to choose a suite and interpret its role in deterministic training. For collecting sources and asking questions in the app, see [MPLPB tools](TOOL_DIRECTORY.md).

| Task | Tool |
|---|---|
| Run the Python regression suite | `python -m unittest discover -s tests -q` |
| Replay the public evidence cases | `python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/mplpb-public-results.json` |
| Test ownership and group alias misses | [D20](../evaluation/d20/README.md) |
| Run scripted personas on eight synthetic topic collections | [Persona and corpus transfer panel](../evaluation/persona-corpus-transfer/README.md) |
| Build and run a blind live-web catalog batch | [Dice Bag](../evaluation/dice-bag/README.md) |
| Build a persistent SQLite synonym graph | [Synonym graph](SYNONYM_GRAPH.md) |
| Test extracts from firsthand historical books | [Primary Book Test](#primary-book-test) |
| Repeat a published test at its recorded revision | [Results and tests](RESULTS_AND_TESTS.md) · [Evaluation archive](../evaluation/) · [Benchmark dashboard](benchmarks/dashboard.md) |
| Verify a release candidate | [ZIP-first release checks](ZIP_FIRST_RELEASE_TESTING.md) · [Browser testing](BROWSER_TESTING_FOR_AGENTS.md) |
| Run MPLPB tests from a separate harness or inspect cross-system tests | [B-Tests repository](https://github.com/mitchell-d00/B-Tests) |
| Replay the MPLPB dispatch and Git enforcement comparison | [Executable Gates comparative tests](../evaluation/comparative-tests/executable-gates/REPRODUCTION.md) |

## Collect a fresh real-world test batch

Run from the full source checkout and give the generated prompt to an AI with web or HTTP access.

```sh
python -m test_tools.generate_open_data_seeds --count 6 --prompt
python -m test_tools.generate_open_data_seeds --seed 2a --count 6 --prompt
```

The first command chooses a fresh seed. The second repeats the draw plan for seed `2a`. Omit `--prompt` for the JSON plan alone. Draws use Wikidata CC0 structured records and openly reusable records from the USGS earthquake catalog. The collector checks reuse terms and saves response bytes, source references, and questions. Keep the answer key separate and score every draw, including missing records and unanswered questions. [Wikidata reuse terms](https://www.wikidata.org/wiki/Wikidata:Licensing) · [USGS reuse terms](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits)

Save the emitted plan and retrieved bytes to replay a batch. Live catalogs can change after the plan is generated. Independent review is needed to verify that each question and expected outcome follow from the captured sources.

## Primary Book Test

This test draws two adjacent prose paragraphs per book from pinned editions of Mary Seacole’s *Wonderful Adventures of Mrs. Seacole in Many Lands*, Charles Darwin’s *The Voyage of the Beagle*, and Booker T. Washington’s *Up from Slavery*. These works are firsthand accounts. Their descriptions reflect each author’s perspective and may contain recollections or secondhand reports. [Seacole](https://standardebooks.org/ebooks/mary-seacole/wonderful-adventures-of-mrs-seacole-in-many-lands) · [Darwin](https://standardebooks.org/ebooks/charles-darwin/the-voyage-of-the-beagle) · [Washington](https://standardebooks.org/ebooks/booker-t-washington/up-from-slavery)

### Generate, run, and score a batch

From the source checkout, choose a new output folder. `generate` downloads verified chapter bytes and draws fresh excerpts by default. Each batch includes three quote-location questions and three altered-quote controls. The controls measure exact source and citation handling. For chronology, conflicting accounts, and historical interpretation, add authored questions and check them independently.

```sh
python -m test_tools.primary_book_test generate --output primary-books-01
python -m test_tools.primary_book_test run --inputs primary-books-01/engine-inputs --output primary-books-01/run.json
python -m test_tools.primary_book_test score --run primary-books-01/run.json --key primary-books-01/custodian/answer-key.json
```

Run `generate` again with a new folder for another draw. `--seed` replays a seed recorded in `custodian/answer-key.json`. For offline replay, pass `--source-dir primary-books-01/custodian/originals` with the same seed. Excerpts can recur across independent draws from the same books.

Share `engine-inputs/` with the runner. Keep `custodian/` with the scorer. To test prose questions, have a reviewer use the excerpts to write a JSON list containing objects with `id` and `question`, then pass the file with `run --questions FILE`. Before running, record each expected answer or refusal and its exact evidence in a separate key. Review the prose results manually for the complete answer, attribution, qualifications, and cited passage. Keep a fresh holdout batch outside development and training.

### Find and gather more historical books online

1. Search for a firsthand source such as an eyewitness travel account, diary, memoir, or published letters. Include the person, place, or period in the search. Open the complete edition and check who wrote the passage and how they learned what it describes. [Standard Ebooks](https://standardebooks.org/ebooks) · [Project Gutenberg](https://www.gutenberg.org/ebooks/) · [Wikisource](https://en.wikisource.org/)
2. Check the original text’s public-domain status and the edition’s reuse terms. Record the title, author, edition, chapter or page, URL, license, and retrieval date. Download the ebook or chapter and save the unmodified bytes. Use a repository commit or page revision as a permanent link when available. Hash the file with `sha256sum FILE`.
3. To extend the automated sampler with another Standard Ebooks title, open its linked GitHub repository and pin the full commit SHA. Download `src/epub/text/chapter-1.xhtml` and `chapter-2.xhtml` at that commit. Add the book slug, author, title, repository name, commit SHA, and ordered chapter hashes to `BOOKS` in the test tool. For a local cache, save the files as `SLUG-chapter-1.xhtml` and `SLUG-chapter-2.xhtml`. Start a new batch after changing the catalog. [Sampler source](../test_tools/primary_book_test.py)
4. For a book from another archive, copy a contiguous passage with its surrounding qualifications and speaker or author attribution. Use the plain text as a source in a separate MPLPB collection and keep the downloaded original and provenance for reviewers. Ask what the author states, what two passages disagree about, and what the selected material leaves unresolved. [Collection import](EXPLORATION_COLLECTIONS.md)
