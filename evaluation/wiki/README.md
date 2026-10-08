# Wiki revision source gate

The source is the stored main-slot wikitext, not Wikipedia's generated TextExtracts output. Schema-3 captures pin three values for each page: revision ID, advertised main-slot SHA-1 (checked against the received UTF-8 wikitext), and wikitext SHA-256. Page identity is also checked. Complete API response bytes are retained as transport evidence, not compared wholesale to decide whether a live source changed.

```sh
python3 tools/wiki_live_eval.py run
python3 tools/wiki_live_eval.py sync
python3 tools/wiki_live_eval.py check --offline
```

`run` creates a new capture and verifies its source before scoring. `sync` checks the active head and, for a newer source revision, archives and verifies one successor. Only a passing live score promotes the successor to `head.json`; old versions stay immutable. Same-revision wikitext conflicts are archived and unscored, and `sync` does not promote them. A new `run` cannot repin a known same-revision conflict in its intact local lineage. Rate limits, missing/suppressed slots, inconsistent advertised hashes and additional drift remain unscored. There are no retry loops. Offline replay cannot promote a head.

The request uses `prop=revisions`, `rvslots=main` and `rvprop=ids|timestamp|content|sha1|slotsha1|contentmodel`. `slotsha1` explicitly requests the main-slot hash; a whole-revision SHA-1 need not mean the same thing in a multi-slot revision. See the [MediaWiki revision API](https://www.mediawiki.org/wiki/API:Revisions).

## Source and derivative

Each capture retains:

- `response.json`: exact API response bytes and a separate response hash.
- `source/*.wiki`: exact main-slot UTF-8 wikitext, checked against the source response.
- `source/renderer.py`: the captured deterministic renderer implementation.
- `corpus/*.html`: sealed locally derived pages, with separate derived-text and complete-page hashes.
- `manifest.json`: schema 3, source pins, renderer version/hash, engine/checker byte pins, source URLs, revision permalinks, revision times, observation times and lineage.

The local renderer is `tools/wiki_render.py`, version `wikitext-lead-stripper-v1`. It retains literal prose before the first section heading and omits templates, tables, references, comments and file/category links. It never expands templates or calls a live parser. This is a bounded local lead-text rendering, not Wikipedia's visual page or live intro. The full wikitext stays available even though the scored derivative is only its lead.

Scoring begins only after the revision source pins match. API extract changes, if present in a supplied response, are recorded as renderer observations and do not fail source matching. The reader scores the local deterministic revision rendering, never an old API intro relabeled as current. Renderer/version changes are separate reproducibility errors and require a newly rendered capture with the same source contract; they are not described as source drift.

## Revision tree and active head

A detected source mismatch retains the old capture and archives the exact newly observed response under `archives/<UTC timestamp>/`. Complete observations include new local pages and lineage hashes. Missing/deleted/invalid slots keep raw evidence and a dated incomplete `observation.json`, without a fabricated corpus. Revision dates and observation dates are distinct. A same-revision content contradiction is recorded without inferring an authenticated source edit.

New captures link prior intact schema-3 captures or verified heads for the same wiki and title list. The head pins its manifest and response and records capture and verification time. Unverified archives do not become the default head. A verified successor can be the head; checking an older capture cannot move it backwards. Immutable manifests describe capture time; later scored reports and head pointers record verification separately.

```sh
python3 tools/wiki_live_eval.py run --wiki english
python3 tools/wiki_live_eval.py check --snapshot evaluation/wiki/captures/NEW_CAPTURE
python3 tools/wiki_live_eval.py check --snapshot evaluation/wiki/captures/NEW_CAPTURE --offline
```

Live source verification and offline replay are explicitly distinguished. Exit 2 means unscored; exit 1 means a scored smoke-test failure; exit 0 means all scored checks passed. Reports and live response bytes are written to new paths under `reports/`.

## Evaluation limits and history

The five-title smoke test has 19 rows: five internal title returns, five external ask refusals, five external gate refusals, three absent-title refusals and one two-title refusal. The existing lexical reader and internal prose fallback are unchanged. Paraphrases are reported without scoring. Titles and labels are developer-written, not independent human validation.

Imports declare `origin=machine` for the import operation, `source-authorship=unknown`, `owner=unknown` and `external=no`. This does not claim the source prose was machine-authored. Contributor identity remains unverified; external delivery is withheld.

The original incomplete snapshot and all schema-2 extract snapshots/reports remain unchanged. This checker refuses to score them as revision-bound sources because they lack retained main-slot evidence. Earlier checker releases can replay their own snapshots, but their extract-payload gate did not establish this revision source contract. No old pins were fabricated or replaced. Earlier live passes are historical observations, not permanent live guarantees.

Text attribution: Wikipedia contributors, CC BY-SA 4.0, with source and revision URLs retained. Hashes establish consistency against stored pins, not authenticated authorship or broad factual accuracy. See [historical review](REVIEW.md), [delivery policy](../../docs/DELIVERY_AND_CLARIFICATION.md), and [change/rollback notes](../../docs/WIKI_CAPTURE_FIX.md).
