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
