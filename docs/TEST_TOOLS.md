# Test tools

Last reviewed: 2026-11-21.

Use these tools to test the engine and reproduce project results. For collecting sources and asking questions in the app, see [MPLPB tools](TOOL_DIRECTORY.md).

| Task | Tool |
|---|---|
| Run the Python regression suite | `python -m unittest discover -s tests -q` |
| Replay the public evidence cases | `python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/mplpb-public-results.json` |
| Repeat a published test at its recorded revision | [Results and tests](RESULTS_AND_TESTS.md) · [Evaluation archive](../evaluation/) · [Benchmark dashboard](benchmarks/dashboard.md) |
| Verify a release candidate | [ZIP-first release checks](ZIP_FIRST_RELEASE_TESTING.md) · [Browser testing](BROWSER_TESTING_FOR_AGENTS.md) |
| Inspect cross-system tests | [B-Tests repository](https://github.com/mitchell-d00/B-Tests) |

## Collect a fresh real-world test batch

Run from the full source checkout and give the generated prompt to an AI with web or HTTP access.

```sh
python -m tools.test_tools.generate_open_data_seeds --count 6 --prompt
python -m tools.test_tools.generate_open_data_seeds --seed 2a --count 6 --prompt
```

The first command chooses a fresh seed. The second repeats the draw plan for seed `2a`. Omit `--prompt` for the JSON plan alone. Draws use Wikidata CC0 structured records and openly reusable records from the USGS earthquake catalog. The collector checks reuse terms and saves response bytes, source references, and questions. Keep the answer key separate and score every draw, including missing records and unanswered questions. [Wikidata reuse terms](https://www.wikidata.org/wiki/Wikidata:Licensing) · [USGS reuse terms](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits)

Save the emitted plan and retrieved bytes to replay a batch. Live catalogs can change after the plan is generated. Independent review is needed to verify that each question and expected outcome follow from the captured sources.
