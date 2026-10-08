# Wiki provenance repair and rollback

Base: `23f3cb84ce470778a2d1261a93618cc69fe15915`.

The previous fetch path stamped imported wiki pages as human-origin and did not retain the source response required to substantiate payload pins. Live checking therefore stopped before retrieval. The old snapshot cannot be repaired retrospectively without inventing evidence.

The replacement fetch path creates a fresh capture, retaining the exact API response and complete source-page payloads. Imports declare unknown source authorship and prohibit external delivery. Checks bind the local text to the saved source transformation, verify page and code bytes, and compare full live payloads before invoking the reader. They distinguish local retrieval from external withholding. Historical artifacts and original pottery probe files remain unchanged.

Fifteen new regression tests cover missing payload pins, original incomplete manifests, modified response bytes, changed source payloads even at the same revision, altered local pages, extra pages, code mismatch, resealed substitutions, false human-origin declarations, non-overwriting captures/reports, and explicit offline replay. These tests use synthetic API responses. Separately retained live reports record real Wikipedia requests and are the evidence for live results.

The early development capture remains pinned to the checker that produced it. After strengthening metadata verification, a new capture was produced rather than changing its pins. Use the latest capture with the finished checker. Any later change to core/checker bytes requires another new capture.

## What this establishes

Matching bytes, correct title retrieval on a small fixture, expected absent/two-title refusal, and external withholding. Authenticated authorship, independent question labeling, semantic retrieval, and broad factual accuracy are not established.

## Walk back

Revert the fix commit to restore the earlier checker. Preserve captured responses and reports separately if they are needed as evidence: reverting also removes the newly added run artifacts. Do not copy schema-2 hashes into the historical manifest or relabel unknown source authorship as verified human. New capture directories and reports are additive; the old corpus and original probes do not need repair or rollback.

## Fresh-run follow-up

Base: `92ee0f07dd1a7bc72923e648361a81c2db638f56`. A reviewer observed a 429, followed by an HTTP-200 source mismatch for three pages. A subsequent diagnostic request matched all five old payloads; the cause of that intermittency was not established. No revision or payload requirement was relaxed.

`run` and the wiki menu now create a new capture and make a second strict live check, instead of treating a shipped snapshot as permanently current. Six additional tests cover fresh capture preservation, mismatch without silent refetch, capture/check rate-limit handling, HTTP-error translation, and refusal to overwrite an existing capture. Reports expose expected/observed payload hashes and revision IDs separately from extract matches. Rate limits are unscored source failures, not drift or passing evaluations.

Walk back this follow-up by reverting its commit, restoring `check` as the menu action and the previous checker. Keep the new reports if needed for history. Earlier snapshots keep their original checker pins and remain runnable with their corresponding earlier release; no historical pins were changed.

## Dated drift archives

Base: `d01aad791b232c2f80f39d700f73040bbf640e0f`. A mismatch now archives the exact observed response and a new local corpus, links the previous immutable capture by manifest/response hashes, and records source URLs, source revision IDs/timestamps, and observation time separately. No replacement fetch occurs and the mismatch remains unscored. Incomplete source responses retain dated raw evidence without a fabricated corpus. Archives are excluded from default capture selection. Three new tests verify original-file preservation, complete source/time links, incomplete observations, repeated archives, and archive exclusion from latest selection.

Rollback: revert this follow-up to remove automatic archival while preserving strict mismatch refusal. Retain any runtime `archives/` directories separately if reverting or deleting a checkout. Do not alter previous captures or promote an archived unscored observation into a passing report.

## Verified newest head

New captures link prior same-source observations. `sync` checks the current head, archives drift, and verifies one successor. Only a passing live successor becomes the active local head. Old captures remain immutable. Offline replay, a rate limit, repeated drift, or an older capture cannot replace a newer verified head. Eight additional tests cover parent links, source separation, successful promotion, failed successor retention, no offline promotion, no backwards movement, bounded synchronization, and linkage after an archived head. Together with the three archive tests, this release adds eleven tests to the prior 197.

Rollback also restores the previous menu behavior and removes `head.json` from the shipped tree. Keep runtime head pointers and archives separately if needed as historical evidence; an older checker cannot verify this release's checker pins.

## Revision-source correction

Base: `71c753b1d5a23c36a902cd0d4b59ca7b474c863a`. The previous stop rule was aimed at generated TextExtracts payloads, which do not establish revision content. It over-refused when generated intros differed at the same revision. Fresh snapshots and clearer archives did not correct that source identity error.

Schema 3 fetches stored main-slot content and advertised main-slot SHA-1, checks that SHA-1 against received UTF-8 bytes, and pins revision ID, slot SHA-1 and wikitext SHA-256. A separate versioned local lead stripper produces the derivative. Whole API envelopes and generated extract fields are no longer the live source gate. Raw responses, exact wikitext, renderer bytes and complete local pages remain independently retained and pinned. Source revision permalinks and revision/observation times remain explicit.

An unchanged source with a changed generated extract records a renderer observation and scores only the deterministic local derivative. Changed source pins stop and archive. A same-revision content conflict cannot be promoted by sync or silently repinned by a fresh run with intact lineage. New revision successors still require passing live verification before becoming head.

Twelve new regression tests cover repeated archival within one tree root, generated-extract and envelope independence, same-revision conflict refusal in sync and fresh runs, advertised SHA-1 disagreement, missing slots, revision-only changes, retained wikitext tampering, independently retained source/renderer pins, source-only API requests, and bounded deterministic lead rendering. Existing source-change fixtures now carry revision slots and test the revision gate; frozen pottery probes were not rewritten.

Rollback: revert this correction to restore the earlier extract checker and previous head, keeping new schema-3 evidence separately. Do not add wikitext hashes to schema-2 records: they did not retain that content. Renderer changes require fresh derived captures rather than changes to old source pins. See the current wiki README for the active contract; earlier sections above describe historical implementations.
