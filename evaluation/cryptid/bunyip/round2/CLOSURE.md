# Bunyip Round 2 / C3 evaluation closed

The evaluated C3 native source is `3bf9657c7b956623f07ed4b94765e0edd5cd3f02`.
Freeze and evidence are recoverable at PR #106 checkpoint
`d3d34c4e95e79f38e9da524af60c4ae95600d485`. The evaluation closed with a
narrow routing claim. C3 is unmerged and undeployed.

- The exposed development replay moved from 57/128 to 128/128 positives,
  recovering 71 executions across 34 original question strings. This is
  consumed development. The public inputs and outputs are retained, but the
  original key and dice for the 572-case development score are unavailable.
  The original 22 strict-key failures and rejected C1/C2 remain retained.
- On the separate frozen replacement comparison, three fresh routing questions
  recovered and 17 fresh targets missed on both readers. Four expected
  checked partials also missed on both. Neither reader emitted unsupported
  claims on that draw. See [raw outputs, runtime hashes, and scores](replacement/RESULTS.md).
- [Public preservation](public-replay-rerun-receipt.json) retained 832/832
  matching contracts. BB is consumed external regression: 900 positives,
  900 exact eligible citation checks, and 200 withholding controls.
- The original 17 private checks remain incomplete. The original 100 held
  cases remain NOT_RUN. Recovery is INTERRUPTED / UNRECOVERED. The
  [publication incident](custody-containment-v2.json) remains open in Git
  history. Closing the evaluation leaves those records and release gates open.

The next work uses these results as consumed study and preservation evidence.
