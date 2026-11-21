# Combined MPLPB

Combined MPLPB is a local notebook that answers questions from the pages you give it. It keeps earlier versions when you revise a page, cites the text that supports an answer, and tells you when the available pages leave a question open.

[Open the browser app](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/) · [Download the small Python package](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/downloads/mplpb-native.zip) · [Installation guide](docs/INSTALLATION.md)

## Try it in 30 seconds

1. Open the browser app, choose **Chat logic · synthetic facts** from the collection list, and open **Ask**.
2. Ask **What is Dungeons and Dragons?** The demo page identifies it as a tabletop RPG.
3. Ask **What time does the museum close?** The demo collection provides no answer, and MPLPB says so.

The browser runs the engine on your device. The demo needs an internet connection to load the app and uses its bundled pages for both questions. You can start your own collection with text you supply.

## Try it from the terminal

Download and unzip the Python package, then install the enclosed `.whl` file. Use its actual filename in the install command. The example creates a new folder called `demo-ledger`.

```sh
python -m pip install combined_mplpb-2.1.0rc1-py3-none-any.whl
mplpb-combined write demo-ledger --title "Museum hours" --scope "museum hours" --body "Opening time: 09:00."
mplpb-combined ask demo-ledger "When does the museum open?" --record-id DOC-0001 --field "Opening time"
mplpb-combined ask demo-ledger "When does the museum close?" --record-id DOC-0001 --field "Closing time"
```

The first question returns **09:00**. The second returns **No supported answer** because the page has no closing time. The installed package uses the Python standard library. It contains the ledger, answer and work tools, plus the sorter. The desktop launcher, example datasets and research archive are available in the full distribution. [Installation and downloads](docs/INSTALLATION.md)

## How it decides

For page lookup, one eligible owner returns its page, competing owners stop for clarification, and a search with no eligible owner refuses. Answering is a separate check. MPLPB reads the eligible source text and can return a supported answer, cite the parts it can verify, show conflicting evidence, or leave the question open.

A citation establishes what an eligible record says. Historical accuracy and independent corroboration require their own evidence. The answer rules cover a limited range of questions. [Page lookup and answer results](docs/PAGE_RETRIEVAL.md) · [What has been tested](docs/CURRENT_STATUS.md)

## Work with your own material

- **Organize raw files.** The sorter turns text and Markdown into drafts and suggested links for review. Clear drafts with unique declared identifiers can be accepted automatically. [Build a collection](docs/COLLECTION_AUTOMATION.md)
- **Follow the evidence.** Inspect source relationships and revisions, find unresolved questions, and group research findings into a dossier. [Offline archival tutorial](docs/ARCHIVAL_INSPECTION.md) · [Documentary reports](docs/DOCUMENTARY_ARTICLES.md)
- **Use the optional tools.** Keep task history, control covered actions, or connect another application. [Package guide](docs/PACKAGE_GUIDE.md) · [Specialist work](docs/SPECIALIST_CONTINUITY_API.md) · [JavaScript API](JAVASCRIPT-API.md) · [Local MCP](docs/MCP_AGENT.md) · [Browser helper](docs/FREE_PUBLIC_HELPER.md)

## Research and development

Benchmark results and their limitations are indexed alongside the original reports and test commands. The full source checkout includes the retained evaluation archive, earlier implementations, and the optional lab reference corpus. [Evidence and tests](docs/RESULTS_AND_TESTS.md) · [Evaluation archive](evaluation/) · [Earlier work](PAST_DOCUMENTATION.md) · [Lab reference corpus](reference_corpus/README.md)

[All documentation](docs/README.md) · [Developer quickstart](docs/DEVELOPER_QUICKSTART.md) · [Contribution and handoff](AGENTS.md) · [Release checks](docs/ZIP_FIRST_RELEASE_TESTING.md)

Code is MIT licensed and project documentation is CC BY 4.0. Bundled sources and other materials carry their own notices. [License](LICENSE) · [Resource notices](resources/README.md)

Last reviewed: 2026-11-20.
