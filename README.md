# Combined MPLPB

Last reviewed: 2026-11-20.

[Source-field aliases and final measured evidence](docs/SOURCE_FIELD_ALIASES.md) extend
bounded source-declared field access: expanded stress complete matches **168→189/420**,
with580/580 expected refusals retained. OriginalD% stays200/600; historical replay
stays3 native complete/22 on the development branch. The older paper below retains
its own revision and252-miss result; the alias iteration leaves231 misses.
[Known-weakness D% sampling](docs/DPERCENT_KNOWN_WEAKNESSES.md) adds a separately
sealed4,096-case study:657/1,262 complete matches,2,834/2,834 expected
refusals retained,75 executable classes and15 explicit unmeasured gaps.
Independent semantic review remains NOT RUN.

[New response paper: source attribution, reproduction and remaining gaps](docs/research/field-question-normalization/README.md)
provides Markdown/TXT/PDF, 1,482 passing native tests,900/900 public field matches,
and a frozen stress improvement from 156 to 168/420, with 580/580 refusals retained.
M6 is not included in the supplied public package. Historical accuracy remains
unmeasured; 252 generated positive obligations remain unresolved.

[Bounded field-question normalization](docs/FIELD_QUESTION_NORMALIZATION.md) adds ordinary literal-field
request structures while retaining strict source verification. Its public synthetic
reproduction improves paraphrase support from 0/750 to 750/750; broader semantic
and historical accuracy remain unmeasured.

Combined MPLPB is a closed local ledger with tools for raw-material sorting,
bounded source questions, documentary inspection and retained work history.
Its browser, native CLI and agent adapters preserve the existing authority rules.

The current research focus is **archival document inspection**: establish source
claims and their explicit relationships before expanding historical narration.
Start with the [five-minute offline tutorial](docs/ARCHIVAL_INSPECTION.md) or inspect
the [compact benchmark dashboard](docs/benchmarks/dashboard.md). Synthetic scores,
authentic development results and unrun independent evaluation stay separate.

**One owner returns; two stop; none refuses.** This is the ownership rule:
one eligible owner may return its page, competing owners stop for ambiguity,
and no eligible owner means refusal. A returned page is not automatically a
supported answer. Strict answering additionally checks eligible source wording
under the finite proof rules. Source integrity does not establish historical truth.

**Research status:** attributable engineering contribution and technical case
study, still being tested. The particular combination may be distinctive;
it is not proven world-first. Independent historical semantic accuracy and
shared-service production readiness remain unestablished.

[Open the application](https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/)
· [Package guide](docs/PACKAGE_GUIDE.md)
· [Installation](docs/INSTALLATION.md)
· [All documentation](docs/README.md)
· [Current evidence](docs/CURRENT_STATUS.md)

## What is in the package?

| Part | What it does | What its output establishes |
|---|---|---|
| [Offline sorter](docs/PREPROCESSING_SORTER.md) | Extracts keys, dates, headers, references and repeated phrases from raw UTF-8 text/Markdown, with exact source spans | Textual observations and optional review edges; no supported answers |
| [Optional sorter review aids](docs/SORTER_REVIEW_OPTIONS.md) | Rank exact/search-neighbor wording and propose source-linked reviews | Inspectable suggestions; no ownership or source support |
| [Candidate review workspace](docs/CANDIDATE_REVIEW_WORKSPACE.md) | Compare processed passages with eligible originals, explore unmatched topics and inspect disagreements | Processed material stays outside approved evidence; original approval never transfers |
| [Ledger and provenance gate](docs/PROVENANCE_GATE.md) | Keeps sealed pages, revisions, ancestry, restrictions and current serving eligibility | Which source bytes and pages may be inspected under the selected policy |
| [Strict answer reader](docs/GENERAL_ANSWER_PIPELINE.md) | Checks eligible body statements against bounded question/proof rules | Source-attributed support where established; ambiguity or refusal otherwise |
| [Page and source inspection](docs/PAGE_RETRIEVAL.md) | Retrieves an eligible owner page or keeps matching sources separate | Inspectable pages/bundles, not a factual answer merely because retrieval succeeded |
| [Documentary research](docs/HISTORICAL_RECONSTRUCTION_ENGINE.md) | Separates checked source assertions, exact wording comparisons, question parts and candidate relations | Checked portions and unresolved evidence; no automatic event identity or historical truth |
| [Documentary article dossiers](docs/DOCUMENTARY_ARTICLES.md) | Assemble several existing research reports with conflicts, open questions and shared declared ancestry | Read-only inspection snapshots; no new historical conclusions or independent-witness count |
| [Conversation and reference library](docs/CHAT_WORKFLOW.md) | Offers local Chat, Serious and off-the-record modes, bounded follow-ups, dictionary lookup and library routing | Conversation, context and source evidence retain distinct labels |
| [Collections and acquisition](docs/EXPLORATION_COLLECTIONS.md) | Imports supplied text and permitted captures into local collections | Captured/supplied sources with provenance; acquisition does not authenticate testimony |
| [Specialist work](docs/SPECIALIST_CONTINUITY_API.md) | Retains tasks, claims, revisions, capabilities, attempts and handoffs | Recoverable work history; a saved claim or completion statement is not proof of execution |
| [Integration](docs/AGENT_MIDDLEWARE.md) | Exposes the existing engine through the page-local JavaScript API and native adapters | The same decisions and restrictions; client success is not answer support |

The [package guide](docs/PACKAGE_GUIDE.md) explains the implementation modules,
optional components, storage boundaries and how these parts connect. It includes
the [local MCP adapter](docs/MCP_AGENT.md), [crawler](crawler/README.md),
[optional browser helper](docs/FREE_PUBLIC_HELPER.md),
[constrained native local narrator](docs/LOCAL_NARRATOR.md),
[lab-only reference corpus](reference_corpus/README.md),
[resources](resources/README.md), and preserved [earlier implementations](parts/README.md).

## Choose how to run it

| Delivery | Start | Scope |
|---|---|---|
| Hosted browser | Open the application above | Python runs locally in browser WebAssembly; visitor sources and saved sessions belong to that browser origin |
| Standalone browser ZIP | Extract `mplpb-monster-browser.zip`, then open `MPLPB_Browser.html` or serve it over static HTTPS | Core engine works offline after download; storage permissions and optional sidecars affect features |
| Full source checkout/ZIP | Run `python3 launch.py`; Windows can use `Launch_MPLPB.bat` | Desktop interface, filesystem saves, source tools, MCP launcher, examples and retained evidence |
| Python wheel/install | Run `python -m pip install .` or install the release wheel | Ledger/answer, library, work and evaluation CLIs, plus the sorter module; does not install the full chat UI or bundled reference data |

Python 3.8+ is the declared native minimum; CI exercises Python 3.12. The core
runtime uses the standard library and needs no model or inference account.
Network acquisition, hosted crawling and optional models have separate requirements.
The root `index.html` is the desktop entry point. GitHub Pages serves the generated
`dist/index.html` through its deployment workflow, not the unbuilt root file.
[Package contents and installation](docs/INSTALLATION.md).

## Raw material, review and safe publication

The [strict-first router](docs/ANSWER_ROUTER.md) explains refusals, labels rewritten questions and keeps unofficial inspection separate. [Classing](docs/CLASSING.md) prepares literal reviewed pages; the [v2 sorter](docs/SORTER_V2.md) is a separate engine, with v1 pins unchanged. Optional [semantic triage](docs/SEMANTIC_TRIAGE.md) emits quarantined flags only. [Ledger generations](docs/LEDGER_GENERATIONS.md) publish complete staged ledgers through an atomic pointer. These tools do not establish historical truth or general reconstruction accuracy. The [gap workflow](docs/HISTORICAL_GAP_WORKFLOW.md) separates proof coverage, evidence discovery and semantic assessment.

## Try the sorter

From a source checkout, this example uses explicitly fictional development files:

```bash
python -m mplpb_work.sorter sort tests/fixtures/sorter \
  --mode not-compared --output /tmp/mplpb-observations-new.json
python -m mplpb_work.sorter sort tests/fixtures/sorter \
  --mode compare --output /tmp/mplpb-comparison-new.json
python -m mplpb_work.sorter peruse /tmp/mplpb-comparison-new.json \
  --sources tests/fixtures/sorter
python -m mplpb_work.sorter export-retired /tmp/mplpb-comparison-new.json \
  --sources tests/fixtures/sorter --ledger /tmp/mplpb-snapshot-new
python -m mplpb_answers validate /tmp/mplpb-snapshot-new --strict
```

Use your own raw-material directory instead of the fixture directory. Outputs must
be new and outside the input tree; use fresh names for repeat runs. `/tmp` is a
POSIX example path; use an appropriate temporary directory on Windows.

Both modes emit **identical nodes, spans, source hashes and provisional statuses**.
Not-compared stops at observations. Compare adds non-authoritative review edges;
matching subjects never force event identity, and missing intermediate records
stop links. The native snapshot is sealed and retired before publication. Existing
`validate` and `show` accept it for inspection; `gate` and `ask` withhold it under
all three profiles. It must not be reactivated as factual evidence.

Sorting does not automatically admit originals for supported answering. Use the
existing source-management/import workflow with the originals' actual permissions,
provenance and delivery policy. [Input/output contract and commands](docs/PREPROCESSING_SORTER.md).

## New optional review tools

**Sorter suggestions for review. MPLPB has not verified these links or answers.**
The Synonym Ranker keeps exact and neighbor signals distinct. The Candidate Relater
retains unresolved references, possible corrections and wording reviews. The review
workspace compares processed text with eligible originals, shows both evidence
statuses, and keeps exploration separate from strict proof admission.

Replace `PROCESSED_DIRECTORY` and `NATIVE_LEDGER` with your own source directories;
use fresh output names outside both input collections:

```bash
python -m mplpb_work.sorter_suggestions sort PROCESSED_DIRECTORY --mode compare \
  --query 'Who received the report?' --synonym-ranker --candidate-relater \
  --output NEW_SUGGESTIONS.json
python -m mplpb_work.sorter sort PROCESSED_DIRECTORY --mode compare --output NEW_GRAPH.json
python -m mplpb_work.candidate_workspace build NEW_GRAPH.json \
  --processed PROCESSED_DIRECTORY --originals NATIVE_LEDGER \
  --question 'Who received the report?' --output NEW_WORKSPACE.json
python -m mplpb_work.candidate_workspace peruse NEW_GRAPH.json \
  --processed PROCESSED_DIRECTORY --originals NATIVE_LEDGER --workspace NEW_WORKSPACE.json
```

The workspace takes the base sorter graph. Every processed passage/conclusion is
**candidate for review** and **Exploratory · outside MPLPB-approved evidence.**
Eligible-original citations show their own status. Matching an original never
approves a processed copy. One eligible owner returns its page and independently
checked strict evidence; competing owners require disambiguation; no owner retains
labeled exploration without returning support through that ownership route.

Review has its own bounded passage/character budget, with explicit truncation;
it never consumes strict proof slots. Perusal rechecks source bytes, permissions,
eligibility and decisions. These are native/CLI tools, including the installed
wheel; this update adds no browser workspace. The standalone multi-source strict
pipeline remains distinct from the workspace's single-page ownership panel.
[Full workspace commands and boundaries](docs/CANDIDATE_REVIEW_WORKSPACE.md).

The [frozen workspace report](evaluation/candidate-review-workspace/2026-11-18-runtime/REPORT.md)
retains all22 native results unchanged at2 complete source-supported answers.
H05 still uses4 witnesses/4070 characters within12 passages/8000 characters.
Five public-document workspace executions retain15 exact matches and49 literal
phrase reviews, with39 processed passages displayed versus28 in the initial trial.
These are development navigation results, not verified historical relationships.
The extracted runtime ZIP passes1267 tests; the installed wheel and separate52
fictional contract controls pass. Independent human/unseen evaluation is NOT RUN.
The goal remains22 evidence-justified outcomes, counting completeness separately.

Source-checkout evaluation tools are also available:

| Tool | Purpose |
|---|---|
| `tools/sorter_first_study.py` / `sorter_options_study.py` | Freeze and replay original questions with fixed reader/source/budget conditions |
| `tools/evaluate_candidate_workspace.py` | Execute real source-linked workspace development cases and measure actual costs |
| `tools/report_candidate_workspace.py` | Compare all22 native outputs and inspect separate candidate-budget invariants |
| `tools/check_candidate_workspace_install.py` | Verify the installed wheel under isolated Python without checkout-only tools |

## Ask, retrieve or investigate deliberately

| Interface | Result meaning | Support boundary |
|---|---|---|
| `mplpb-combined ask` / `python -m mplpb_answers ask` | Strict answer contract, including supported, partial, ambiguous and refused outcomes | Only an accepted deterministic proof can set strict source support |
| `candidates` / legacy `python -m mplpb_combined ask` | Lexical owner/candidate inspection | Candidate selection is not answer support |
| `MPLPB.retrieve()` / Python gated `retrieve()` | Selected owner page passes provenance and serving policy | `answer_supported:false`; page inspection only |
| `gate` | Separate eligible source bundle | Matching vocabulary does not establish a relationship |
| `reconstruct` / `investigate` | Documentary report with checked portions, candidates and unresolved evidence | A checked portion need not complete the question; no invented bridges |
| Optional model-assisted reading | Strict-first proof if available; otherwise labeled assisted interpretation | Model-only output remains unsupported; matching quotations do not prove semantics |

The synthetic demonstration can be queried without adding any source fields:

```bash
python -m mplpb_answers ask examples/chat-logic \
  'What is Dungeons and Dragons?' --profile internal
```

The example corpus is authored demonstration material. It is not a historical
accuracy benchmark. Public-facing code must preserve support flags, qualifications,
citations, conflicts and refusals. `ok:true` means an API call completed, not that
its claims are supported. [Result contracts](docs/PAGE_RETRIEVAL.md).

## Use the application or connect a client

The interface provides source inspection, revisions, named collections and
bounded conversation. Chat, Serious and off-the-record free chat have different
scope/storage rules. Saved user context and research notes do not become ledger
facts. Transcript export is not a complete source-ledger backup.
[Browser controls](docs/BROWSER_UI.md) · [Conversation](docs/CHAT_WORKFLOW.md)
· [Storage and recovery](docs/PACKAGE_GUIDE.md#storage-and-recovery).

In the running application page:

```javascript
await window.MPLPB.handshake();
const result = await window.MPLPB.relay(
  'What is Dungeons and Dragons?', {corpus: 'logic'}
);
```

Live calls require that browser context; a published URL is not a remote query
server and does not expose another visitor's IndexedDB. The native MCP server
requires a full checkout and host-authorized collection roots. It does not share
browser saves or provide source-writing tools.
[JavaScript API](JAVASCRIPT-API.md) · [Local MCP](docs/MCP_AGENT.md).

## Evidence, limits and research

The retained [sorter contract](evaluation/preprocessing-sorter/2026-11-17/RESULTS.md)
and [native-export refinement](evaluation/preprocessing-sorter/2026-11-17-native-export/RESULTS.md)
cover source fidelity, identical nodes, stopped links and all-profile withholding.
These are developer-authored controls, not independent historical accuracy results.

The earlier [unchanged22-question experiment](evaluation/solo-milestone/2026-11-17/RESULTS.md)
records two complete source-supported answers and one checked partial at that
revision. The subsequent [article preservation replay](evaluation/documentary-articles/2026-11-19/REPORT.md)
retains **2 complete, 2 partial, 3 conflict and 15 abstention outcomes** across the
same 22 questions. These categories are not independent judgments of historical
correctness. Preprocessing and article assembly did not increase complete answers.
The latest [explicit source-date experiment](evaluation/archival-inspection/2026-11-19/REPORT.md)
records **3 complete, 2 partial, 3 conflict and 14 abstention outcomes**: only H07
changes, through independently checked source/date relationships. All 21 other
answer meanings remain unchanged. **1,468 archived Python tests and 52 public
controls passed.** An unsafe intermediate actor rule was rejected and its failing
controls/partial runs are retained. Independent semantic review is **NOT RUN**.

The [result/test index](docs/RESULTS_AND_TESTS.md) distinguishes original measurements,
software controls, AI assessments and unrun independent evaluation.

A hash does not authenticate testimony. Similar sources are not automatically
independent corroboration. Unsupported grammar, ambiguous identities, conditions,
contradictions, incomplete evidence and exhausted budgets can still prevent an
answer. [Current status](docs/CURRENT_STATUS.md) · [Readiness and threat model](docs/PRODUCTION_READINESS.md)
· [Research status](docs/research/mplpb-originality/RELEASE_NOTE.md).

The sorter paper by Mitchell D. McPhetridge is available as
[Markdown](docs/research/dual-mode-sorter/dual-mode-sorter.md),
[text](docs/research/dual-mode-sorter/dual-mode-sorter.txt) and
[PDF](docs/research/dual-mode-sorter/dual-mode-sorter.pdf).
[Earlier papers and notes](PAST_DOCUMENTATION.md) retain their original bytes and scope.

The [D% randomized prose challenge](docs/DPERCENT.md) retains 1,240 frozen fictional cases with answer/refuse expectations and a private key withheld from runtime. [General checked prose rules](docs/PROSE_RULE_CLASSES.md) increased complete checked answers from **20 to 200 of 600**: **160 source assertions and 40 word-location answers**. All **640 expected refusals** were retained, with zero observed false support in that set; **400 answerable cases remain incomplete**. That measured historical replay retained **2 complete answers out of 22**; the later source-date extension records **3/22 native completions**, without an independent accuracy claim. The [full findings](evaluation/dpercent/2026-11-19-class-rules/FINAL_REPORT.md) preserve costs, failed/interrupted attempts and 1,431 archived tests plus 52 public controls. This is developer-authored evaluation; independent semantic accuracy and general reconstruction remain unproven.

## Assemble a documentary research dossier

The native [article mode](docs/DOCUMENTARY_ARTICLES.md) combines existing research
reports while keeping checked documentary claims, candidate connections,
conflicting accounts and unanswered questions separate. It adds no narrative
bridges or historical proof rules. A shared declared ancestor stays visible;
three copies are not counted as three independent witnesses. Missing ancestry
also leaves independence unknown.

Create a UTF-8 `plan.json` with a topic label and 1–8 original questions:

```json
{
  "title": "Appointments and correspondence",
  "questions": [
    "Who appointed Ellis Marsh?",
    "Who wrote the harbour report?"
  ]
}
```

These are fictional example questions. Import your original sources through the
existing collection workflow, then run:

```sh
python -m mplpb_answers article LEDGER --plan plan.json --format text
```

JSON is the default output. Each section retains its own source eligibility,
exact citations, native answer and candidate graph. Changes detected during
assembly discard the entire dossier. Exports are snapshots: rerun for current
eligibility. Article-level support and historical truth remain unestablished.
This mode is available in the native CLI/library; it is not a browser article editor.

The [recorded checks](evaluation/documentary-articles/2026-11-19/REPORT.md) include
**1,446 archived Python tests and 52 public-evidence controls passed**, a
source-linked shared-ancestry/conflict example, and exact preservation of all
22 native historical answer contracts. Initial permission-related failures are
retained. This demonstrates assembly preservation, not a gain in historical
answer coverage or independent accuracy. The next research milestone is a
checked cross-document connection with evidence for every necessary link.

## Development, packaging and licenses

The [developer guide](docs/DEVELOPER_QUICKSTART.md) maps the implementation;
[CONTENTS](CONTENTS) maps the repository. Follow [AGENTS.md](AGENTS.md) for handoffs,
[ZIP-first release requirements](docs/ZIP_FIRST_RELEASE_TESTING.md) for committed
candidate validation, and [infrastructure synchronization](docs/REPOSITORY_INFRASTRUCTURE.md)
for linked source/API/browser artifacts. Main's required archive/regression checks
and postdeployment browser checks are separate evidence. Historical green runs do
not certify later commits.

Code is MIT licensed; documentation is CC BY 4.0. Bundled data, models and preserved
parts retain their own notices. See [LICENSE](LICENSE) and [resource attribution](resources/README.md).

Measured fixpack/gap update: [final experiment](evaluation/fixpack/2026-11-18/FINAL_REPORT.md) and [22-case source/checker table](evaluation/fixpack/2026-11-18/CASE_ANALYSIS.md). Complete answers remain2/22; checked partials increase1→2. Separate exploration does not recover the5 missing draft anchors; the tested tiny flagger provides no utility gain. Original authority boundaries remain in force.


The [sorter exploration view](docs/SORTER_EXPLORATION.md) adds visible tags for textual observations, possible connections, changed bodies, unresolved entity identity/event co-reference and unverified historical truth. `python -m mplpb_work.sorter_explorer sort DIRECTORY --mode compare` shows them without changing the underlying sorter format. Its separate `ask` command accepts unofficial free-form research questions; optional local-model hypotheses remain explicitly unverified beside the native MPLPB decision. Neither the labels nor model proposals establish historical truth or change ledger authority.

Sorter exploration validation: [frozen execution record](evaluation/sorter-exploration/2026-11-19/FINAL_REPORT.md) includes15 new boundary tests,unchanged source graphs and native H05 proof,a live small-model smoke with no demonstrated reasoning gain,and retained failed storage runs. These are inspection/authority-boundary results,not historical accuracy scores.

A [fresh local B-Tests d100 run](evaluation/sorter-exploration/2026-11-19/d100/REPORT.md) passed100/100 fictional cases and100/100 companion exploration checks. This checks authority/routing invariants on randomized inputs,not historical truth or model accuracy. Publication requires the exact-head release gates.


Temporary duplicate source extractions are recorded in
[the retained-source path map](handoff/duplicate-source-retention.json) and
[per-member checksums](handoff/duplicate-source-members.json.gz). Only verified
recreatable temporary copies were removed; their original ZIPs, logs, pinned Git
revisions and all evaluation records remain preserved. No entries were removed
from those ZIPs. Local `/tmp` paths are instance-specific; pinned Git revisions
provide the portable source reference.
