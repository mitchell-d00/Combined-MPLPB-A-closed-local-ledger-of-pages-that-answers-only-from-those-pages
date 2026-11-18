# Classing: from a data dump to a strict-readable ledger

Last reviewed: 2026-11-18. Proposed addition. Writes only through `mplpb_combined.ledger`.

```sh
python -m mplpb_work.classing propose RAW --auto-accept-clean --output review.json
python -m mplpb_work.classing status review.json
# a person edits review.json
python -m mplpb_work.classing build review.json --dump RAW --ledger NEW_LEDGER --ratify-by "Full Name" --receipt receipt.json
```

## What `propose` drafts

One page per source occurrence (sorter v2 boundaries):

- **ID:** declared `Message-ID` / `Document-ID` / `Record-ID` / numbered designation; otherwise a stable generated `PREFIX-XXXXXXXX`. Unsafe IDs get a generated ID and stay as a field.
- **Fields:** every `Label: value` line of the leading header block, each written as its own paragraph so the strict field route can read it. Values are byte-exact copies with recorded spans.
- **Provenance:** `Classing source file`, `Classing source SHA-256`, `Classing source bytes`.
- **Body:** the occurrence text after the header block, verbatim.
- **Page metadata:** title from `Subject` or first line; scope `"<ID>: <title>"`; `origin=machine`; `source_authorship=unknown`.

And **decisions**, each with options, evidence and help text, all unanswered:

| kind | from | options | blocking |
|---|---|---|---|
| `duplicate_id` | same declared ID, different text | `keep_both`, `second_supersedes_first`, `reject_second` | yes |
| `correction` / `partial_correction` | sorter v2 correction edge | `ignore`, `supersede`, `field_correction` (+ `corrects_field`, optional window) | no |
| `declared_status` | `Status: retired/superseded/withdrawn` | `ignore`, `withdraw_after_write` | no |
| `reference_review` | unresolved, qualified or descriptive reference | `ignore`, or set `to_draft` + action yourself | no |

`--auto-accept-clean` sets `decision: accept` only for drafts with a declared, safe, unique ID and no blocker.

## What a person does in `review.json`

- `decision`: `accept` / `reject` per draft.
- Edit `page` fields (title, scope, when_to_use, not_for, owner, `source_authorship`, external, event/occurrence IDs).
- `reviewer_fields`: `{"label", "value", "quote"}`. The quote must occur verbatim in the source and contain the value. Example: SHIP-8's prose says "the cargo count changes only to thirty-eight barrels"; a reviewer adds `Cargo: thirty-eight barrels` quoting it.
- `choice` for each decision; `corrects_field` for a field correction.
- `"ratify": true` on drafts you personally stand behind, then build with `--ratify-by "Your Name"`.

## What `build` checks

The dump still hashes to the reviewed sorter graph; every accepted value is still literally in its source file; blocking decisions are answered; choices are valid; no ID clashes; no supersession cycles. It then writes in dependency order into a temporary copy, validates with the native validator, and only then publishes (a new ledger is moved into place; `--append` replays on the real ledger after a clean rehearsal). The receipt records pages, hashes, depths, ratifications, withdrawals and validation results.

## Serving consequences (MPLPB's rules, not classing's)

- `internal`, `lab`: machine pages (depth 1) are served.
- `external`: needs depth 0 (ratified) **and** declared source authorship. The router quotes the gate's reason when this withholds a page.

## Hardened admission and publication

Build independently re-extracts the dump and compares occurrence IDs, source hashes/coordinates, literal fields, complete body, declared status and decision evidence/options. Extracted observations cannot be edited into a new claim; reviewer-added fields are explicit, source-local and quote checked. Truncated graphs cannot authorize builds. Field text is HTML-escaped into separate preformatted blocks without normalizing source whitespace; the native canonical projection still applies its documented normalization for citations. Source files remain unchanged.

Correction/retirement drafts are not auto-accepted. Accepted serving decisions must have explicit choices and a declared person via `--reviewed-by` or `--ratify-by`; neither authenticates identity. Only explicitly marked ratification lowers machine depth, and unknown authorship can still prevent external delivery. The receipt hashes the effective edited review separately from the proposal.

Append stages the native writer's exact sealed output, validates it, rechecks dump bytes and the bounded target snapshot, then publishes changed UTF-8 files under the existing writer lock with rollback on ordinary publication errors. Existing ledgers with symlinks or staging inputs over 4096 files/64MiB are refused. This is not crash-atomic multi-file storage or protection against hostile manual filesystem edits; use exclusive local maintenance and retain backups. No online reader transaction guarantee is added.
