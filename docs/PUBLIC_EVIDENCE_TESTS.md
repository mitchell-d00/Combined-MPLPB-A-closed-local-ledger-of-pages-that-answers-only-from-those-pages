# Public evidence and relation tests

Last reviewed: 2026-11-16.

The public suite contains **52 inspectable development cases** across source
authority, diagnostic separation, exact routing, event identity, scoped source
correction, candidate inference, receipt boundaries and measured execution cost.
Every case has a visible requirement, expected result and scoring category in
[public-cases.json](../evaluation/historical-experts/public-cases.json).
The fixture generator and evaluator are public in
[evaluate_public_evidence.py](../tools/evaluate_public_evidence.py).

```sh
sha256sum -c evaluation/historical-experts/public-cases.sha256
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/new-public-results.json
python -m unittest tests.test_public_evidence_challenge -v
```

The strict invocation fails if any case remains a capability gap or regresses.
The ordinary evaluator separately records passes, gaps and regressions; an
unavailable capability is never counted as an answered question or safety pass.
The regression suite runs all 52 requirements as well as testing the evaluator's
handling of unknown human-effort measurements and unavailable features.

## Inspectable source and event boundaries

All scenario records are fictional and generated in isolated temporary folders.
The separate original-paper replay uses unchanged hash-pinned sources and is
reported independently. Neither test family claims a blinded holdout: publishing
questions makes them development examples. Future blind questions must be kept
separate and must have their own frozen source, question and scoring receipts.

Source occurrences retain distinct ledger IDs and hashes. The event-candidate
reader groups only explicit `Event-ID` fields, retains each `Message-ID` appearance,
and marks changed message bodies `needs_review`. Equal subjects never force
identity. Missing event IDs remain unassigned; every event remains a documentary
candidate, not a confirmed historical event. Source dates, record-update time and
actual event time are separate. Restricted, excluded or corrupt source material
cannot supply a candidate.

An explicit source correction can replace one unique exact span while preserving
unaffected source text, canonical header line breaks and the complete predecessor. The native authoring command
is deliberately separate from read-only expert investigation:

```sh
mplpb-combined correct-claim CORPUS SOURCE-0001 \
  --old-quote "Mira owns observatory." --new-quote "Sol owns observatory." \
  --effective-at 1905-01-01
```

The correction's effective date is an author declaration recorded in the revision
log. This does not implement unrestricted as-of historical reasoning or determine
which historical assertion is true. Repeated or missing spans, invalid dates,
stale source heads and unavailable sources are rejected. Expert crawling never
invokes a source correction implicitly.

## Versioned results and measurement limits

Fixture record time is fixed in the public manifest so regenerated sealed source bytes are reproducible. Final per-case HTML hashes are retained, including explicit revision history. Each results file records the case-manifest hash, implementation module hashes,
available Git revision/dirty state, model settings and budgets, per-case input
outcomes, and measured wall/CPU time, peak Python allocations and source-text bytes
read. Repeated source reads count repeatedly. This is not total OS I/O or process
RSS. Human labeling/correction time is explicitly unknown; there are no human
participants or operator-burden claims.

Source count and inspected output are visible per case. False supported bridges
are scored separately from missing coverage. Receipt tests distinguish local
execution success from evidence of delivery, reading or acknowledgement.

An earlier implementation can run the same public evaluator under its own
`PYTHONPATH`; absent expert interfaces are reported as gaps. Compare exact source
inventories and the same case hash. Improvements in interface coverage are not
claims of general historical accuracy. New results must not replace dated frozen
reports. Archive-first, full regression and deployed-browser checks remain
separate requirements before publication is described as verified.

See the [expert crawl guide](HISTORICAL_EXPERT_PATH.md) and
[public evaluation scope](../evaluation/historical-experts/README.md).

> Update 2026-11-16: The [public 52-case evidence suite](PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.
