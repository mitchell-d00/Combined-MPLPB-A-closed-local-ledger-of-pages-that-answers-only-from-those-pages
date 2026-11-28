# MPLPB

Last reviewed: 2026-11-28.

MPLPB keeps a local collection of documents and answers supported questions from
their text. Each supported claim points back to a source passage. It is useful
for checking a small archive, keeping revisions, and seeing what your documents
leave unresolved.

[Open the browser app](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/)
· [Installation choices](docs/INSTALLATION.md) · [User guide](docs/MPLPB.md)

## Choose a route

- [Use MPLPB](docs/MPLPB.md) for installation, importing documents and checking citations.
- [Develop MPLPB](docs/EXPERIMENTAL_LAB.md) for implementation, experiments and tooling.
- [Inspect the evidence](docs/TESTING_APPARATUS.md) for frozen tests, results and custody.

[Responsibility and distribution map](docs/RESPONSIBILITY_BOUNDARIES.md) · [Component map](docs/COMPONENT_MAP.md)

## What can I do today?

- **Ask about supplied documents.** Get cited answers for supported question forms.
  Ordinary wording can still miss an answer that exists in the source.
- **Keep documents and revisions.** Stored records support continuity; a later
  session must retrieve them to use them.
- **Inspect uncertainty.** See checked parts, competing evidence and unresolved
  questions. A source statement is not an independently verified fact.
- **Use local tools.** Choose the browser, Python command line or desktop
  application. Optional model assistance has separate labels and requirements.

The reader uses finite rules. Citation validation checks the quoted span
against eligible source bytes at the cited revision. Native proof checks
whether the passage supports the claim under the reader’s rules. Outside-world
truth requires independent evidence.
[Capabilities and limits](docs/MPLPB.md#answers-and-their-limits)

## Try it in 30 seconds

1. [Open the browser app](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/), choose **Chat logic · synthetic facts**, then open **Ask**.
2. Select **Strict: only supported source statements**. Type **What is Dungeons and Dragons?** and submit it with **Ask**.
3. Choose **Read source and sealed metadata** under the answer. The passage identifies it as a tabletop RPG. Close the source and ask **What time does the museum close?** to see **No supported answer**.

The app initially needs internet access to load. Its bundled example pages are
synthetic demonstration material. [Browser and offline options](docs/INSTALLATION.md)

**Your documents.** Select **Use my documents**, then [create a collection and review your own text](docs/MPLPB.md#how-to-add-documents).

## Try it from the terminal

In a new, empty directory on macOS or Linux, use Python 3 with `venv` and pip:

<!-- quickstart:start -->
```sh
python3 -m venv .venv
. .venv/bin/activate
python -c "import urllib.request; urllib.request.urlretrieve('https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/downloads/mplpb-native.zip', 'mplpb-native.zip')"
python -m zipfile -e mplpb-native.zip mplpb-native
python -m pip install --no-index mplpb-native/combined_mplpb-2.1.0rc1-py3-none-any.whl
mplpb-combined write demo-ledger --title "Museum hours" --scope "museum hours" --body "Opening time: 09:00."
mplpb-combined ask demo-ledger "When does the museum open?" --record-id DOC-0001 --field "Opening time"
mplpb-combined ask demo-ledger "When does the museum close?" --record-id DOC-0001 --field "Closing time"
```
<!-- quickstart:end -->

**Input format:** `--body` takes plain text; `--title` and `--scope` supply metadata.
No metadata header or prepared input file is required for this example.
The explicit record and field options select the source fact to check.

Expected answer lines (the command also prints diagnostic and source-scope notes):

```text
SUPPORTED ANSWER
Opening time: 09:00.
```

The final command instead begins:

```text
NO SUPPORTED ANSWER
Not in the corpus.
```

That refusal exits with code **3**; the supported answer exits with **0**.
The write command reports `wrote DOC-0001` plus its file and content hash.
[Exact clean-install transcript and verification](evaluation/newcomer-navigation/README.md)
· [Windows and other installation options](docs/INSTALLATION.md)

## Follow an answer to its source

In this example the source body is **Opening time: 09:00.** The question selects
**Opening time** in **DOC-0001**, and the checked answer repeats that field.
To inspect its machine-readable citation, run:

```sh
mplpb-combined ask demo-ledger "When does the museum open?" --record-id DOC-0001 --field "Opening time" --json
```

Inspect `answer_contract.claims[].citations[]`: the quote is **Opening time: 09:00.**, alongside
the source identifier, revision hash and text coordinates. The browser shows
supporting passages with its answer. [Adding documents and inspecting citations](docs/MPLPB.md)

## Limitations and evidence

Complete answers cover the obligations the reader checked. Partial answers leave
named parts unresolved. Conflicts preserve competing source claims. Refusals can
mean missing evidence **or a reader limitation**; inspect the source when it matters.

Experimental results apply to their tested cases. Detailed measurements, version
pins and remaining misses live in the [Test Index](docs/TEST_INDEX.md), the
authoritative test inventory, and its linked reports. Human onboarding execution
is still **NOT_RUN**. [Current technical status](docs/CURRENT_STATUS.md)

For integration and review: [MCP](docs/MCP_AGENT.md),
[browser helper](docs/FREE_PUBLIC_HELPER.md), [reference corpus](reference_corpus/README.md),
[architecture](docs/PACKAGE_GUIDE.md), and [full technical reading guide](README-TECHNICAL.md).
Implementation files, commands and retained evidence remain at their existing paths.

<a id="combined-mplpb"></a>
<a id="deterministic-training-loop"></a>
<a id="train-a-rule-with-the-coordinator"></a>
<a id="how-it-decides"></a>
<a id="advanced-mplpb"></a>
<a id="train-a-deterministic-rule"></a>
<a id="work-with-your-own-material"></a>
<a id="directions-for-an-ai-to-inspect-the-full-combined-mplpb-package"></a>
<a id="read-in-this-order"></a>
<a id="open-the-actual-modules-and-tests"></a>
<a id="verify-these-boundaries-in-code"></a>
<a id="research-and-development"></a>
<a id="contributor-coordination"></a>

Earlier technical sections are preserved in [the technical README snapshot](README-TECHNICAL.md).
