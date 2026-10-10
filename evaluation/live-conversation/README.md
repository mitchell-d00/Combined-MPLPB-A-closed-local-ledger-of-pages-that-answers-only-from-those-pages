# Live acquisition and conversational routing development smoke

This evaluation exercises 1,000 synthetic questions in 25 virtual-user sessions,
40 turns per session, over 25 topics. It is a development smoke test, not an
independent validation set and not a measure of general answer accuracy. Cases
and pilot observations informed these fixes. Consult `summary.json` for observed
counts and `results.jsonl.gz` for each response, including refusals and failures.

## Behavior under test

* Separate social lead-ins from explicit requests, including `cool tell me about
  an apple`, while retaining the original utterance in the transcript.
* Leave an active social exchange when a new topic request arrives.
* Acquire Wikipedia pages when automatic acquisition is enabled and only a
  dictionary entry is available; retain the local reply if acquisition fails.
* Preserve separate source authority, numbered citation order and session chains.
* Keep social questions and requests without searching away from network lookup.

The core ledger ownership and proof engine is unchanged. Imported pages still
pass the normal revision, hash and eligibility checks. Capturing a Wikipedia
revision establishes what was captured, not that its claims are true.

## Method

`input.jsonl` contains the fixed inputs. Each session starts in chat or serious
mode (alternating users), then receives `I had a bad day` before its 40 recorded
turns. Those setup turns are saved separately and are excluded from the 1,000.
Each virtual user gets an isolated application and capture directory. Four
workers run the real bundled Python application and browser bridge in Pyodide.

The runner substitutes only the HTTP transport with real, paced Wikipedia API
requests through curl. It does not substitute encyclopedia content or simulate
successful acquisitions. Successful responses from this evaluation's live
pilots are cached by exact URL, with their original retrieval timestamps and
response bytes retained. Cache reuse is counted explicitly. All other responses
come from Wikipedia during the run. HTTP 429 pauses honor Retry-After. Failed
requests remain in the audit, including partial crawls that saved eligible pages.

`network.jsonl` correlates requests to cases by recorded call order and per-turn
request counts. Some pilot-cache metadata carried its original case/id; those
values remain as `raw_metadata_case` and `raw_metadata_id`. Original worker logs
are retained unmodified in the downloadable audit archive.

## What the checks mean

Routing checks inspect whether supported lead-ins were normalized and avoided
the social-followup route. Citation checks compare each displayed source path
with its numbered source-exploration result. Session checks use the application's
own transcript integrity check. These checks do not independently grade whether
an answer is relevant, complete or factually correct. Attribute questions can
still produce conservative refusals even when an overview was available.

The 1,000 cases run in Node WebAssembly, not 1,000 browser DOM interactions.
Browser CORS, persistent browser storage and the deployed UI are checked in a
separate live smoke test. Timings include four workers and shared network pacing;
they are not production latency benchmarks. The standard regression and browser
WebAssembly smoke suites run separately from this evaluation.

## Reproduction

Use the release-digest-verified Pyodide core and build the standalone runtime:

```sh
python tools/build_browser_runtime.py --core-archive /path/to/pyodide-core.tar.bz2 --output dist/index.html
node tools/live_conversation_wasm.mjs /path/to/pyodide dist/index.html evaluation/live-conversation/input.jsonl /path/to/run
python tools/summarize_live_conversation.py --output /path/to/report /path/to/run
```

The runner requires Node, Python and curl; its paced transport uses POSIX flock.
The output's sibling `live-http-cache` directory holds successful HTTP captures.
For an entirely new acquisition run, use a new output parent directory. Live
Wikipedia content and availability change, so exact replies are not guaranteed.
Each phase records its own bundle manifest. See the final-tightening section for
the application change between the original run and the targeted retest.

Wikipedia captures retain source URLs and revision metadata. Source text remains
subject to the upstream Wikipedia licensing terms; it is not relicensed as MPLPB
code. The audit archive includes raw HTTP captures, responses, session checks,
saved imported ledgers, test logs and the summarized results.

## Recorded result

| Check | Observed result |
| --- | --- |
| Questions / virtual users | 1,000 / 25 |
| Supported prefixed requests | 275; zero routing-check failures |
| Source-exploration replies | 278; zero citation-index mismatches |
| Transcript chains | 25 of 25 intact |
| Unexpected social or no-search network calls | 0 |
| Unhandled application transport exceptions | 0 |
| New Wikipedia collections | 23 |
| HTTP transport calls | 144, including 22 successful-response cache reuses |
| HTTP results | 138 successful, 6 rate-limited (429) |
| Separate regression suite | 518 passed |
| Separate standard WebAssembly smoke | Passed |

There were 278 replies with separate source results, 650 conversational replies,
50 help replies and 22 dictionary-reference replies. Conversation includes both
social responses and conservative source refusals; these counts are not answer
accuracy scores. Of 500 attribute/follow-up turns, 452 used the conversation route,
46 returned separate source results and 2 returned dictionary references. This
shows the remaining limit of the finite question grammar and available sources.

The exact first case, `cool tell me about an apple`, acquired the Apple page and
returned its opening passage with the Apple source at citation [1]. The social
check `How are you today?` returned `I’m functional, thanks! How’s your day going?`
in that session. Source text and social authority remained separate.

## Finding from manual review and final tightening

The original 1,000-case run above preceded one final relevance fix. Targeted
manual review found that requests for a microscope, Japan and a penguin could
receive openings from Paleontology, History of video games or Bird because those
pages mentioned the requested topic elsewhere. Citation alignment alone did not
catch this. `review-findings.json` preserves the observed replies.

The fallback now requires an explicit opening definition of the requested subject
when title navigation finds no candidate. An incidental mention is insufficient.
Existing ownership and eligibility checks still run first. This conservative
restriction can increase refusals; enabled Wikipedia acquisition can then obtain
a dedicated topic page.

The `postfix/` files record a 28-question real-Wikipedia WebAssembly retest of the
three affected topics plus apple, with social and no-search controls. The complete
1,000-question run was **not rerun after this final tightening**. The full regression
suite was rerun separately. Neither run is independent semantic validation.

Final targeted result: all 28 turns completed; all four primary Wikipedia topic
pages were captured; all 20 tested prefixes routed correctly; all four transcript
chains remained intact. No application exceptions, citation-index mismatches or
unexpected social/no-search network calls were observed. The 24 HTTP transport
calls succeeded, including 8 cache reuses. The final full suite passed 519 tests.

A remaining limitation is visible in this retest: capturing the primary page does
not guarantee it becomes the unique eligible owner. The microscope reply quoted
Optical microscope and Electron microscope; Japan quoted Imperial crest of Japan
and Territorial disputes of Japan; penguin quoted Chinstrap penguin. These remain
separate, labeled page results, not complete general overviews. The strict owner
gate was not bypassed to force the primary page to answer.
