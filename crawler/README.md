# General web crawler setup

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

Node tests use fixture responses, not a paid/free provider account or a deployed
Worker. Run `node test_worker.mjs`. General-web live deployment remains a separate
verification step. To walk back, remove the crawler URL/token and use a Wikipedia
mode; retain/export existing source captures. Do not expose provider keys in HTML.
