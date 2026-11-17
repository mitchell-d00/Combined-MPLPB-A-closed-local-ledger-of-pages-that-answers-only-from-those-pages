# General web crawler setup

Last reviewed: 2026-11-17. See [current status and result-to-test index](../docs/CURRENT_STATUS_2026-11-02.md). Dates and numeric results in historical validation sections retain their original scope; this review is not a rerun or independent certification.

The browser's **Web · hosted crawler** mode needs this separate Cloudflare Worker.
GitHub Pages serves the interface; it cannot fetch arbitrary sites server-side.
This Worker has not been deployed by the Pages workflow. Without its URL and access
token, `search TOPIC` refuses and creates no collection. Choose a Wikipedia mode
for browser-only topic exploration without a search account.

## Free search option

The default provider is Tavily basic search. As checked on 2026-10-08, Tavily offers
1,000 free credits/month without a credit card; basic search uses one credit/request.
See [official pricing](https://docs.tavily.com/documentation/api-credits) and
[search API](https://docs.tavily.com/documentation/api-reference/endpoint/search).
Stay on the free plan; this code does not purchase a plan or enable paid overage.
Search ranking is supplied by the provider; MPLPB's reader remains deterministic.
Only result URLs/titles become crawl seeds. Provider snippets and generated answers
are not imported as evidence. An API key is needed for this implementation.

## Deploy

1. Create/sign into your Cloudflare and Tavily accounts, and obtain a Tavily API key.
2. With Node installed, open a terminal in `crawler/` and run:

   ```sh
   npx wrangler login
   npx wrangler secret put TAVILY_API_KEY
   npx wrangler secret put CRAWL_TOKEN
   npx wrangler deploy
   ```

   The secret prompts take the search key and a separate strong access token you
   choose. Do not put these in repository files or send them in chat. Keep the
   search API key server-side. Cloudflare's [secret documentation](https://developers.cloudflare.com/workers/configuration/secrets/)
   describes this storage. Free Workers limits still apply.
3. In the browser's crawler settings, save the deployed HTTPS URL ending `/crawl`
   and enter the access token. The browser retains the URL; the token lasts only
   for that tab and must be entered after reload. Use **Web · hosted crawler**,
   then send `search TOPIC`.

`wrangler.jsonc` allows `https://mitchell-d00.github.io` as the browser origin.
Change it if hosting elsewhere. CORS alone is not authentication; the access token
protects the endpoint. Anyone given that token can use the configured search quota.
For Brave, set `SEARCH_PROVIDER` to `brave` and store `BRAVE_SEARCH_API_KEY` instead.

## Captures and limits

One search supplies up to two seeds. The Worker fetches at most five successful
HTML/plain-text pages, follows at most four same-origin links per seed for one hop,
and attempts at most ten page URLs. Robots requests are additional. Each source is
limited to 512 KiB; redirects, credentials, literal IP addresses and non-HTTPS URLs
are refused. Robots restrictions, unavailable robots and positive crawl delays
stop that origin's fetch. HTTP failures are recorded, with no bypass.

The browser checks each returned payload hash, derives text locally, and seals it
in a new named collection. The crawl record retains URL, server observation time,
local capture, hash, limits, links and failures. Navigation is not proof of a factual
relationship. Server-reported capture provenance is not an independently verified
site download or authorship declaration. A zero-page crawl does not invent evidence.
Ordinary chat then reads that local collection; it does not search again implicitly.
Refresh retains sources/chats until reset, subject to browser storage limits.

## Direct historical source captures

The same authenticated `POST /crawl` route now also accepts an explicit source set:

```json
{"seeds":[{"url":"https://archive.example/original.txt","sha256":"OPTIONAL_64_LOWERCASE_HEX_DIGEST"}]}
```

Supply one or two public HTTPS URLs, optionally with known original-byte hashes;
omit `sha256` when unknown. Use either `seeds` or a search `query`. Direct seeds do
not call a search provider or require a search key. Origin/token authentication,
robots checks, failure handling, type/byte/count/depth/time limits and redirect
refusal remain the existing crawler's rules. HTML/plain text are supported; PDF
and automatic OCR are not. Source bytes are returned unchanged in base64 with
their SHA-256. A pin mismatch produces a failure, never an accepted replacement.
Capturing a webpage does not automatically admit it to an authoritative ledger.
Use the existing capture/import path, retain provenance, and inspect source policy.

`crawlSources` exposes the same set operation to a native Node caller. Async `sourceIdentity` rehashes both bounded raw captures before accepting digest equality. It
distinguishes identical captured-byte digests from the same URL with changed bytes;
URLs, digest strings and server observation times do not authenticate authorship.
Identical copies are not independent corroboration and never establish event identity
or historical truth. Keep every original capture/version. This update does not
deploy a Worker or configure accounts/secrets.

Run `node crawler/test_historical.mjs` as well as the existing worker tests. These
use authored fixture responses; actual publisher/network availability is separate.

Node tests use fixture responses, not a paid/free provider account or a deployed
Worker. Run `node test_worker.mjs`. General-web live deployment remains a separate
verification step. To walk back, remove the crawler URL/token and use a Wikipedia
mode; retain/export existing source captures. Do not expose provider keys in HTML.

> Update 2026-11-16: The [public 52-case evidence suite](../docs/PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](../docs/HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.
