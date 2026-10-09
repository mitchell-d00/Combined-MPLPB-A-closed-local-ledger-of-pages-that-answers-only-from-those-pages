# Combined MPLPB

A closed local ledger of pages that answers only from those pages.

Each page carries its own id, scope, status, hash, parent and depth. The reader reads the
explicitly configured corpus folder. One current page owns the question: it returns that page. Two own it: it stops. None
own it: it says not in the corpus. A change writes a new page and retires the old one. A
derivation writes a new page and adds one to the depth.

No model. The core reader uses local pages and the Python standard library. Optional search/crawl/import commands contact public sources explicitly; standalone browser mode uses IndexedDB for saved state.

## Topic-bound follow-ups

Selected topics persist across chat turns and reloads. Ask `how big is it?` or
`how old is it?` to request a supported source quotation. Missing facts offer
explicit source expansion. See [grounded chat](docs/GROUNDED_CHAT.md) and the
[experiments and independent evaluation protocol](evaluation/contextual/README.md).
These are finite extraction rules; independent human validation is still pending.

## Casual chat and offline references

Say `what are you?`, `why do you exist?`, `I'm tired`, or `can we talk about nothing?`
for casual conversation. Say `I had a bad day`, then `sure` to start a
chat about your day; `just listen`, `change the subject`, and `not now` steer it.
This uses saved local conversation rules and needs no AI account or model.
Mentioning an exact eligible page title in a recognized
casual phrase invites a more serious, source-backed conversation. It waits for
your acceptance and checks the page again before selecting it.

The repository includes these local resources, with original licenses and source pins:

| Resource | Included | How to use |
| --- | --- | --- |
| Open English WordNet 2025 | 128,009 dictionary entries and 107,558 synsets | `define dog`, `synonyms dog`, `what does fossil mean?` |
| CMU Link Grammar English data | 111 grammar, word-list and reference files | `grammar resources`; data archive in `resources/language/` |
| Simple English Wikipedia selection | 23 archived articles on language, computing, animals, geology and games | Choose **Reference encyclopedia**, then `show my MPLPB` |

These are downloaded data, not remote lookup dependencies. Ordered archive parts
are committed under `resources/language/archive-parts/`; the app reconstructs and
verifies the ZIPs locally. The standalone browser build embeds the same resources.
See [licenses, attribution and exact revisions](resources/README.md).

Conversation is rule-based, not a general language model. Grammar data is available
as a reference; a syntax parser is not enabled. The encyclopedia is a selected set,
not all of Wikipedia. Dictionary senses and synonyms never expand ledger ownership
or bypass source checks. Source hashes establish byte consistency, not factual truth.

```
R = (id, scope, status, hash, derived_from, origin_depth)

A(q) = R               if exactly one current R owns q
       ambiguous       if two or more own q
       not in corpus   if none own q
```

Paper: [`docs/Combined_MPLPB.md`](docs/Combined_MPLPB.md) · `.txt` · `.pdf`
(MPLPB-COMBINED-017 v3, draft for owner review) · fixes: [`docs/FIXLOG.md`](docs/FIXLOG.md)

This is the master repository. The `ask` command implements the formula. The separate `gate` command returns lexical
source bundles with provenance, as described below. The five earlier implementations are carried whole under [`parts/`](parts/README.md), and
the papers that are not in any of them are under [`docs/sources/`](docs/sources/README.md).

## Open in your browser

The Pages workflow publishes the standalone runtime at:
https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/

[Publishing setup and walk back](docs/GITHUB_PAGES.md). Deployment status determines
whether that address serves the runtime; a source push alone is not a deployment.

## Browser runtime without a Python server

The generated **MPLPB_Browser.html** embeds the real Python engine through Pyodide
WebAssembly, bundled pages and the RPG-style front end. Open the delivered file in
a current browser, or use static HTTPS hosting. No Python installation or process
is needed to run it. Startup is offline; explicit Wikipedia search/import uses the
network. Browser storage permissions are required to retain state.

The repository includes the reproducible builder: `python3 tools/build_browser_runtime.py`.
This creates `dist/MPLPB_Browser.html`; generated output is excluded from Git.
[Runtime details, requirements, verification and walk back](docs/BROWSER_RUNTIME.md).
The desktop mode below remains available in root `index.html`.

## Local browser UI

The front end follows Mitchell's **Give It Back: The RPG**: a corpus tile map,
status panels, source dialogs, journal and three visual settings. It calls the
real local reader and gate. The complete front end is in `index.html`.

On Windows, double-click `Launch_MPLPB.bat`. On Mac/Linux, run
`sh Launch_MPLPB.sh`, or run `python3 launch.py` on any system with Python 3.
The launcher opens <http://127.0.0.1:8766>. Keep the terminal running.

New users can choose **Guide me** for a saved step-by-step introduction. Chat offers
suggested questions and can present the selected MPLPB’s page titles. App-help
questions also work in Ask, including when source verification is blocked.
[Guided chat details](docs/GUIDED_CHAT.md).

The **Chat** view supports `search TOPIC` to build a saved MPLPB from a bounded crawl, `find TOPIC` for Wikipedia suggestions, explicit Wikipedia title imports,
follow-up context and bounded source-assertion rules. See
[the chat workflow](docs/CHAT_WORKFLOW.md) and [system/creator reference](docs/SYSTEM_SELF.md).
It uses no language model; general semantic conversation is not implemented.
General web mode needs a deployed [Cloudflare crawler and search key](crawler/README.md); GitHub Pages alone cannot crawl arbitrary sites. Wikipedia modes run without that backend.

See [browser UI instructions](docs/BROWSER_UI.md) for your own corpus, controls and
validation limits. The [patch-canned notes](docs/patch-canned/README.md) preserve
the supplied experiment and include the corrected reader patch and demo.

## Try it

```bash
python3 -m mplpb_combined ask examples/studio "how fast should I heat raw clay on its first firing"
python3 -m mplpb_combined ask examples/studio "what is the glaze firing schedule for cone 6"
python3 -m mplpb_combined ask examples/studio "what is the capital of France"
```

The first returns one page with its citation. The second stops and names the two pages that
both own the question. The third says not in the corpus. Exit codes are 0, 2 and 3.

```
$ python3 -m mplpb_combined ask examples/studio "the glaze pulled away from the pot"
Glaze faults

  Crawling comes from dust or grease on the bisque, or a coat put on too thick that
  cracked as it dried. ...

  [STUDIO-0012 · glaze/studio-0012.html · current · origin human d0 · sha256:... · local]
```

A page owns a question when its `scope` and `when-to-use` fields declare more than half of the
question's words. Before that majority check, two fully named declarations that
are not strict subsets of another fully named declaration cause ambiguity. Strict
subsets retain the more specific match. Only when no page owns it that way does the reader look at prose, and then a
page must contain every word. A return decided by prose says so in its citation. Add `--why`
to see which step decided, or `--no-prose` to allow scope only.

A page can also say what it is **not for**. `--not-for "booking; permission"` on a kiln
schedule sets that page aside for any question containing those words, and the refusal says
which page stepped back and why.

## Provenance gate and additional corpora

`gate` returns every eligible lexical source separately. For “1974 dungeons and dragons budget”, game context and general budget material retain separate origins; both sources remain visible if both contain budget material. Their coexistence does not establish the historical D&D budget.

```bash
python3 -m mplpb_combined gate examples/provenance-gate/separate "1974 dungeons and dragons budget" --json
python3 tools/provenance_bench.py --serve
```

See [the gate specification](docs/PROVENANCE_GATE.md) and the [offline demonstration](examples/provenance-gate/index.html). Six additional topic corpora and ninety frozen lexical probes are under [examples/topics](examples/topics) and [evaluation/topics](evaluation/topics/README.md). These are controlled fixtures, with failures retained.

Supplied papers are indexed in [papers](papers/README.md), their implications in [the upload review](docs/UPLOAD_REVIEW.md), and earlier documentation in [PAST_DOCUMENTATION.md](PAST_DOCUMENTATION.md).

Supersession follows [explicit policy examples](docs/SUPERSESSION_POLICY.md): restoration pins the terminal head, and stale or incorrectly pinned derivatives are withheld. See [the fix report](docs/SUPERSESSION_FIX.md).

Walk-back instructions: [docs/ROLLBACK.md](docs/ROLLBACK.md).

## Experimental wiki and loose-file tools

The [wiki package](evaluation/wiki/README.md) adds a menu, loose-source formatter, and immutable wiki captures. New captures retain revision main-slot wikitext, revision/slot/content pins, a deterministic local renderer, full local pages, and unknown-authorship delivery policy. The historical snapshot remains incomplete and unscorable; it is preserved with [the review](evaluation/wiki/REVIEW.md). This is a lexical smoke test, not independently labeled validation. Start with `python3 tools/menu.py`.

See [sealed delivery and human clarification](docs/DELIVERY_AND_CLARIFICATION.md) for unknown authorship, shared `ask`/`gate` restrictions, and the dog intent demo.

## Keep your own ledger

```bash
mkdir notes
python3 -m mplpb_combined write notes --prefix NOTE --title "Bisque schedule" \
    --scope "Bisque firing schedule" --when-to-use "first firing; raw clay" \
    --body "Climb 100 C per hour to 600 C."

python3 -m mplpb_combined revise  notes NOTE-0001 --body "Climb 80 C per hour to 600 C."
python3 -m mplpb_combined history notes NOTE-0001        # both versions, oldest first
python3 -m mplpb_combined derive  notes --from NOTE-0002 --title "Checklist" \
    --scope "Firing day checklist" --body "..."          # machine page, depth 1
python3 -m mplpb_combined ask     notes "firing day checklist" --profile external   # withheld
python3 -m mplpb_combined ratify  notes NOTE-0003 --who "Your Name"                 # depth 0
python3 -m mplpb_combined validate notes
```

Pages are plain HTML. Open any of them in a browser. `python3 -m mplpb_combined index notes`
writes an `index.html` to browse from; the reader never answers from it.

A corpus written by Smart Local, the Local Mirror, Swarm or Networked MPLPB can be read after
`python3 -m mplpb_combined seal <root>`, which adds hashes and pins references and changes
nothing else.

## What is here

| Path | What |
|---|---|
| `mplpb_combined/record.py` | The page format: fields, parsing, the hash |
| `mplpb_combined/ledger.py` | The folder as a ledger: status, lineage, depth, validation, writing, the log |
| `mplpb_combined/reader.py` | The answer rule, profiles, hubs |
| `mplpb_combined/killtest.py` | The kill test: three arms, mechanical scoring |
| `tests/` | 220 tests: 165 original, 11 delivery/clarification, and 44 wiki capture tests |
| `examples/studio/` | 25 pages about running a pottery studio; the kill-test corpus |
| `examples/spec/` | The format described as ten pages in the format |
| `examples/hub/` | Two pointers, one at each of the above |
| `killtest/` | Three frozen probe sets, their hashes, the results as run, and earlier runs under `v1/` and `v2/` |
| `docs/` | The paper in three formats, the fix log, the superseded v1 paper, and the source papers |
| `parts/` | Local Mirror, Smart Local, Swarm, Networked, Image |
| `tools/` | Rebuild the examples, check the parts, render the paper |

## Check everything

```bash
python3 -m unittest discover -s tests -t .       # this package
python3 tools/check_parts.py                     # every part, plus adoption of their sites
python3 -m mplpb_combined killtest examples/studio killtest/probes.json
python3 -m mplpb_combined killtest examples/studio killtest/probes_heldout.json
python3 -m mplpb_combined killtest examples/studio killtest/probes_adjacent.json
sha256sum -c killtest/probes.sha256              # run inside killtest/
```

## What the kill test showed

### Evaluation additions

BM25 and TF-IDF now run alongside the original arms. Each compares stripped
prose against the same current page pool and depth limit available to the reader.
Fixed parameters, zero-overlap refusals, deterministic ties, and per-probe
predictions make the comparison reproducible. Historical results are preserved;
new runs expose `lexical_baselines` and `lexical_rows` in JSON and print totals.

`python3 -m mplpb_combined.evaluate evaluation/manifest.json` runs 36 frozen
developer-authored questions across software operations, library services, and
office procedures. They are synthetic regression fixtures, not independent
validation. Results retain every failure and report metrics by domain and
expected outcome. See [`evaluation/README.md`](evaluation/README.md) for the
independent-review protocol and how to evaluate externally authored corpora.

Implicit retirement now requires a valid successor and valid, uniquely resolved,
hash-pinned lineage. Altered, unsealed, duplicate, cyclic, incorrectly pinned,
or depth-inconsistent records cannot control a predecessor's effective status.
Explicit retirement remains retirement. Legacy unpinned references need `seal`
before they can retire a predecessor implicitly.

### Historical results

The first run found bugs in the reader: it could not find a page by its own prose, and one
stray word declared on another page stopped it. They are fixed, and `docs/FIXLOG.md` records
each error, cause, fix and rerun. The first reader and its results are kept under
`killtest/v1/`.

Correct / wrong page returned / wrong refusal:

| | First set, 56 (fixes were developed on it) | Held-out set, 30 (run once) |
|---|---|---|
| This reader, before the fix | 41 / 0 / 15 | 12 / 4 / 14 |
| This reader, fixed | 50 / 0 / 6 | 20 / 3 / 7 |
| Same code, fields stripped | 26 / 4 / 26 | 10 / 1 / 19 |
| Plain search over the stripped pages | 16 / 40 / 0 | 10 / 20 / 0 |

The fix holds on questions it was not developed against. It does not reach a perfect match,
and it was not pushed there: the six remaining misses on the first set could each be removed
by an adjustment that the held-out set gives no reason to trust.

The three wrong returns on the held-out set are the thing to know about this reader. Each asks
about something the corpus covers from an angle it does not ("who is allowed to use the gas
kiln" returns the gas kiln firing schedule).

The `not-for` field was added for that. With it, the held-out set goes to 22 / 1 / 7. On 20
fresh questions written to test it, the reader scores 15 / 3 / 2 with the field and 12 / 4 / 4
without: it stopped two wrong returns of four, lost no correct answer, and caused one wrong
return of its own where two near-duplicate pages did not carry the same exclusion. The limits, in short: one corpus, one author, the
same hand wrote the pages and the questions.

## What this is not

- Not a fact-checker. A returned page says where the words came from, not that they are right.
- Not tamper-proof. A hash shows a page was not edited after writing. It does not show who
  wrote it. Signatures are in `parts/networked/`.
- Not a search engine. A page is reached by the words in its `scope` and `when-to-use` fields,
  or by a question whose every word is on the page. It can still return the right subject's
  page for a question that page does not answer, unless the page's `not-for` field predicted
  the question's words.
- Not multi-writer infrastructure. Writes take a lock file. Leases with fencing tokens are in
  `parts/swarm/`.
- Not tested on old hardware or old Python. It is written to Python 3.8 syntax and was run
  under 3.12.

## Licence

MIT for code, CC BY 4.0 for documentation. See `LICENSE`. Each part keeps its own.

Mitchell D. McPhetridge · October 2026


Story replies use deterministic sentence construction with sense-checked WordNet adjectives, attributed user details and grammatical follow-up rules. See [construction boundaries](docs/GROUNDED_CHAT.md#compositional-response-construction). Loaded-page answers keep exact evidence quotes; no model or provider is required.
