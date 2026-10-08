# Wiki capture and live check

This tests lexical retrieval and refusal using external wiki text. It is not semantic retrieval, independently labeled validation, or authenticated authorship.

```sh
python3 tools/wiki_live_eval.py run
```

`run` explicitly creates a new capture and immediately performs a second live request to verify it before scoring. The menu uses this fresh-run workflow. It never updates an old capture's pins or retries until a mismatch disappears. HTTP 429 is reported as source unavailable, with Retry-After when supplied, and produces no score or automatic retry. A live match is an observation at the recorded request time, not a promise that a later check will match.

To inspect an existing capture, use `check`. Source changes still stop scoring. Mismatch reports include expected and observed payload hashes and revision IDs, and whether the raw extract matched; a matching revision ID alone does not authenticate the extract.

`fetch` creates a new directory under `captures/`. It never repairs or overwrites the historical `corpus/` and `manifest.json`, or an existing capture. It saves the exact API response, a schema-2 manifest, full sealed local HTML pages, and separate engine/checker byte pins. Each page pins the complete canonical source-page payload, raw extract, source identifiers, and complete served HTML. The manifest records the developer-written title lists before retrieval.

`check` selects the latest capture by default. Before asking the reader, it verifies the retained response, complete page inventory, code bytes, source-to-local transformation, and unknown-authorship delivery declarations. It fetches the live source again and requires every full page payload to match. Missing provenance, tampering, code changes, or source drift stop scoring with exit 2. A scored failure exits 1; all passing checks exit 0. Reports and the live response are written to new paths under `reports/`.

```sh
python3 tools/wiki_live_eval.py fetch --wiki english
python3 tools/wiki_live_eval.py check --snapshot evaluation/wiki/captures/NEW_CAPTURE
python3 tools/wiki_live_eval.py check --snapshot evaluation/wiki/captures/NEW_CAPTURE --offline
```

Offline replay is explicitly labeled and makes no live-match claim. Code changes require a new capture; do not replace old code pins to make an old run pass.

The five-title smoke test has 19 checks: five local title returns, five external ask refusals, five external gate refusals, three absent-title refusals, and one two-title refusal. Local calls use the existing internal profile, including its lexical prose-containment fallback. Paraphrases are reported without scores. The reader's ownership rule is unchanged.

Imported records use `origin=machine` for the import operation, `source-authorship=unknown`, `owner=unknown`, and `external=no`. This does not claim Wikipedia text was written by a machine. Contributor authorship remains unverified. Unknown-source text can be read locally but both external delivery paths withhold it.

## Historical evidence

The old snapshot remains incomplete and unscorable: it lacks retained API response bytes and payload pins. Those cannot honestly be manufactured after the fact. Its corpus, manifest, pins, review, and original reports are preserved. See [the historical review](REVIEW.md) and [delivery policy](../../docs/DELIVERY_AND_CLARIFICATION.md).

The first new capture and report also remain as development evidence. A subsequent checker strengthening means that first capture's checker pin no longer matches the finished checker. Use the latest capture for the finished version; this is recorded rather than silently repinning it.

Each checker release requires its own new capture. Captures from earlier releases retain their earlier checker pins; run them with that release, or create a fresh capture with the current checker. The original 16:04 UTC live pass does not claim that later source requests match.

Text attribution: Wikipedia contributors, CC BY-SA 4.0, with each page's wiki source URL retained. Hashes prove byte consistency against the stored pins, not authenticity of whoever supplied those pins. Five title probes cannot establish broad factual accuracy or usefulness.
