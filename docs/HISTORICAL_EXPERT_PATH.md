# Historical expert path and bounded relation crawling

Last reviewed: 2026-11-20.

Package role: [how this part fits Combined MPLPB](PACKAGE_GUIDE.md#documentary-research). This guide covers documentary inspection; source assertions, candidate relations and historical truth remain distinct.

The explicit `investigate` path uses MPLPB's existing specialist work coordinator
to inspect original source declarations and crawl their relationships. It keeps
the strict answer contract separate: an investigation is a documentary evidence
report with `answer_supported:false`, not a certified historical conclusion.

```sh
python -m mplpb_answers investigate CORPUS "Trace the declared relationships and document dates" \
  --source DOCUMENT-0001 --max-hops 2 --max-sources 12
```

`mplpb-combined investigate` is the installed equivalent. The Python entry is
`mplpb_work.investigation.investigate(root, question, ...)`. Starting source IDs
are actual ledger record IDs; the original document IDs inside their bodies are
separate identities. Without `--source`, bounded passage retrieval selects source
material for inspection, not a winning answer. All source pages remain unchanged.

## Adaptive Search

```sh
mplpb-combined investigate CORPUS "Find receipt, dispatch and authorization" \
  --source SRC-0001 --max-sources 3 --adaptive-search
```

Use `adaptive_search=True` from Python. The scheduler keeps the seed order and
visits shallow hops first. Within a hop, it prioritizes uniquely resolved
`Supersedes` targets, then source previews that contain question terms absent
from sources already read. It breaks ties in discovery order. Each visit can
change the next choice. These signals schedule inspection and carry no proof
authority. Existing source, character, hop and observation budgets apply.

The discovery pass indexes declared identities across the eligible ledger, up to
4,096 sources and 16 million HTML characters. Each source prefix is bounded at
50,000 HTML characters. When discovery cannot cover the eligible identity
universe, target uniqueness remains unresolved and no hop is taken. The
independent verifier rereads both endpoints. Classing provenance ends a
`Related` continuation and does not supply a target.

The report's `adaptive_search` field gives `deepest_visited_hop` and
`completed_hop` (seeds are hop zero). A missing depth is JSON `null`. A hop
counts as completed when its scheduled work fits the limits. Unavailable
targets, conflicts, and relationships outside the search horizon can remain
unresolved. The independent verifier still checks the reported evidence. A
source-state change discards the findings and depth diagnostics. Ordinary
`investigate` uses its original discovery order when the flag is omitted.

## Existing specialist seats, executable expert work

Three versioned, local software experts run through `WorkStore` action dispatch:

- **Documentary:** reads genuine early document headers, records exact source
  spans, and follows explicitly declared Related and Supersedes document IDs.
- **Chronology:** presents declared document dates with their precision and basis.
  A document's stated date does not become its publication or invention date.
- **Verification:** independently reloads current eligible source bytes, checks
  hashes and offsets, and parses each proposed declaration with a separate verifier.

Each seat has a host-issued capability, one allowed expert operation and a scoped
task. Guarded actions produce host receipts; downstream expert actions retain
source evidence pins, and completion requires all three passing criterion results.
Expert votes and execution success never convert a synthesis into source support.
These are deterministic software roles, not authenticated human historians or
live language-model providers. No model download, network crawl or provider call
runs through this path.

Work is ephemeral by default. `--work-directory NEW_PRIVATE_DIRECTORY` explicitly
retains a native work ledger and a mode-0600 `host-credential.json` for host audit
and recovery. Keep that credential private. An existing work database is never
overwritten. No hosted browser specialist service or scheduler is added.

## Relation and source boundaries

Only a declared target ID can create a crawl hop. A matching version is required
when the declaration names one. Multiple candidate witnesses remain ambiguous;
an unnamed title is not guessed. Cycles are visited once. A header's `Related`
does not become `derived from`, `caused`, endorsement, or corroboration. A paper's
`Supersedes` declaration does not mutate the ledger's operational status.

The original full question and delivery profile are retained at every hop and
in final verification, including its not-for exclusions. Targets must be current,
servable, eligible records inside the selected corpus. Links cannot cross into
another folder or remote service. Retired, restricted, missing, ambiguous and
over-budget targets remain unexpanded; private targets are not disclosed.
Historical versions may be imported as separate documentary witnesses without
reviving a retired operational page or calling its old assertion current truth.

The report distinguishes observations, typed source-declared relations, declared
dates, unresolved targets and budget stops. Its limits are explicit: 0–5 hops,
1–32 visited sources, 1,000–1,000,000 examined source characters, bounded header
and observation discovery. A reached limit is not proof that no more evidence
exists. Partial context and missing targets remain visible. Source or policy
changes discard the old report rather than returning stale quotes.

## Original evidence and verification scope

Original Markdown/plain-text papers can contain line-wrapped prose in `pre`
blocks. Passage retrieval now groups adjacent lines into bounded overlapping
contexts, preserving canonical Unicode offsets and source hashes. Ordinary HTML
paragraphs remain separate. Split contexts retain an incomplete-context marker;
retrieval coverage alone never establishes a relationship.

```sh
python -m unittest tests.test_historical_evidence tests.test_historical_verifier \
  tests.test_historical_investigation tests.test_historical_passages -q
python -m tools.evaluate_historical_experts --output /tmp/new-historical-report.json
```

The replay imports four unchanged, hash-pinned original papers into an isolated
temporary ledger and starts at Combined v3. It inspects declared relationships to
Local Web v4, Smart Local v1 and the retained Combined v1 witness. Missing versions
and external documents remain unresolved; the original non-supersession qualifier
is preserved. The report records actual observed counts when run. This authored,
inspected development replay is not a held-out historical-accuracy study.

The initial historical challenge also exposed limits that this path does not
remove: unrestricted causal reconstruction, implicit entity resolution, automatic
as-of event queries and world-first claims remain unsupported. An author-declared
August date and an October Git timestamp are different evidence types; associating
a commit with a particular file additionally needs a verified path/ref/blob
witness. Neither date proves first publication or development order.

Related: [specialist API](SPECIALIST_CONTINUITY_API.md),
[answer pipeline](GENERAL_ANSWER_PIPELINE.md),
[deterministic graph contract](DETERMINISTIC_EVIDENCE_GRAPH.md).

> Update 2026-11-16: The [public 52-case evidence suite](PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.

## Event candidates and explicit corrections

The report also retains source-declared event candidates and their distinct message occurrences; changed bodies require review. Read-only investigation cannot author a correction. The separate explicit `correct-claim` command preserves a predecessor and unchanged source text. See [the public protocol](PUBLIC_EVIDENCE_TESTS.md) for the exact bounded contracts and 52 visible acceptance cases.
