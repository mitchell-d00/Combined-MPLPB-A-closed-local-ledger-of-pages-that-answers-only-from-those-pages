# MPLPB product — the usable artifact

Last reviewed: 2026-11-28.

[Open browser app](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/) · [Installation](INSTALLATION.md)
· [Components](COMPONENT_MAP.md) · [Test Index](TEST_INDEX.md)

MPLPB helps you keep documents, ask bounded questions, and inspect the passages
behind supported answers. Use it for a local collection whose sources you can
check. Its finite reader can miss ordinary wording; manually inspect important
omissions. It does not independently authenticate what a document claims.

Scope: released user operations. Check [current status](CURRENT_STATUS.md) and
[the handoff](../HANDOFF.md) for release/version and continuation cues;
[development history](DEVELOPMENT_HISTORY.md) keeps earlier contracts separate.

[Product distribution and responsibilities](RESPONSIBILITY_BOUNDARIES.md) explains what is delivered and what is shared.

## Start

Follow the [browser walkthrough](../README.md#try-it-in-30-seconds) to ask and
open a cited passage, or use the [verified terminal quick start](../README.md#try-it-from-the-terminal). The small native download contains the installed
ledger, answer and work packages. The full source distribution adds the desktop
launcher, examples, research and evaluation tools. Browser and desktop operation
have different prerequisites: see [installation](INSTALLATION.md).

## How to add documents

In the browser, select **Use my documents**, name the collection, and choose
**Create MPLPB**. Give the source a title, paste plain text or load a UTF-8
`.txt` or `.md` file, then choose **Import into selected MPLPB**. A public URL
is optional when supplying text. Open **Review imported source** and select
**Continue to Strict Ask** after checking the source.

For a practice source, paste `Record-ID: WALK-201`, a blank line, and
`Accession Date: 1895-04-18`. Ask **What is the accession date for record
WALK-201?** and open the cited source. Asking for its shelf code yields
**No supported answer**.

The terminal quick start passes **plain text** to `--body` and metadata to command options;
it requires no input-file header. For example, in an empty ledger directory:

```sh
mplpb-combined write studio-ledger --title "Blue Heron Studio" --scope "Blue Heron Studio ownership" --body "Mira Stone owns Blue Heron Studio."
mplpb-combined ask studio-ledger "Who owns Blue Heron Studio?"
```

The answer quotes **Mira Stone owns Blue Heron Studio.** and identifies DOC-0001.
These are synthetic examples, not facts about a real studio.

For files, use [collection import](EXPLORATION_COLLECTIONS.md),
[collection automation](COLLECTION_AUTOMATION.md), or the [offline sorter](PREPROCESSING_SORTER.md).
The sorter accepts raw text and Markdown and proposes drafts and relationships
for review. File import has its own preparation and admission rules; a sorter
candidate is not verified answer evidence. Preserve originals and inspect the
result before treating an imported page as an eligible source.

The [retained museum walkthrough](../evaluation/newcomer-navigation/README.md)
records a checked opening-time answer, its citation and the missing closing-time
refusal. Its native module fingerprints were checked against main `c01021c`.
The [browser walkthrough receipt](../evaluation/newcomer-navigation/browser-route-2026-11-28.json)
records the supported, refusal and pasted-text browser checks.

## Inspect an answer's citations

In the browser, inspect the supporting passage and source record shown with the
answer. With the CLI, append `--json` and inspect `answer_contract.claims[].citations[]`: source
identifier, hash, quoted text and coordinates. Check the complete sentence and
its context, including reporting, conditions and negation. Citation validation
checks that the quotation and coordinates match eligible source bytes at that
revision. Native proof checks whether those passages support the claim under
the reader's rules. Outside-world truth requires independent evidence.
[What each check establishes](RESPONSIBILITY_BOUNDARIES.md#what-each-check-establishes)

Stored records can carry work between sessions, but a session must retrieve the
relevant records. Storage is not automatic awareness of your entire collection.

## Answers and their limits

| Outcome | Meaning | Try it with the museum quick-start ledger |
|---|---|---|
| Complete | The reader checked every requested obligation | Select DOC-0001's Opening time field |
| Partial | Some parts have witnesses; other parts remain unresolved | Ask `What are Opening time and Closing time for record DOC-0001?` |
| Conflict | Eligible sources offer competing claims | Add a second explicit owner for the same studio, then repeat the ownership question |
| No supported answer | The available proof path did not establish the requested claim | Select the missing Closing time field |

The competing-owner example displays `AMBIGUOUS` and exits with code 2.
Partial and unsupported CLI answers can exit with code 3. Keep their checked
parts and diagnostics rather than treating this as a failed program launch.
An instruction supports what someone instructed; it does not prove execution.
A source reporting an assertion establishes that reporting layer, not the
assertion's independent truth. Writing, sending and receiving dates remain
different obligations. A refusal can be a reader limitation even when a page
contains the answer. [Technical result contracts](PAGE_RETRIEVAL.md)

## Tools and departments

Reader, Ledger, Applications, Work Coordination and Delivery provide the main
user-facing path. Intake supplies source preparation; Testing protects their
boundaries. See the [component map](COMPONENT_MAP.md) for implementation and tests,
or the [tool directory](TOOL_DIRECTORY.md) for examples. Optional model assistance
and candidate graphs retain separate labels and never grant source eligibility.
