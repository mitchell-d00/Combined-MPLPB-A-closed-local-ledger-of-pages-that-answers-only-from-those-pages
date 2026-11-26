# Bunyip BB — Ben Gelhaus external adversarial benchmark

Last reviewed: 2026-11-26.

Ben Gelhaus authored the external benchmark and analysis. Mitchell authored the
MPLPB implementation being exercised. “Hostile” describes deliberately challenging
the reader and seeking failures; it implies no bad faith by the author.

The [released package](../../../field-question-normalization/2026-11-20/public-reproduction.zip),
questions, original results and expectations remain unchanged. Its SHA-256 is
`f4d1c8263dbb8dcf9f7ddbc9fc85be5d005864db4c74fce1a93cda1bb4865718`.
The original reproduction script runs 900 positives and generates 200 negatives;
the positive CSV alone is not the full 1,100-question denominator.

| Arm | Canonical | Paraphrases | Negative controls |
|---|---:|---:|---:|
| Original published reader `bbf6690…` | 150/150 | 0/750 | 200/200 withheld |
| Released main `c01021c…` | 150/150 | 750/750 | 200/200 withheld |
| Current Bunyip candidate | 150/150 | 750/750 | 200/200 withheld |

The existing exact evaluator retains all 900 positive claims for each matched
revision. The unchanged citation checker rereads all 900 exact eligible citations
on each revision. No supported answer was lost; no incorrect supported answer or
citation failure was observed. These are preservation results, not new coverage.

[Summary and pins](summary.json) · [raw matched replays](matched-replays.tar.xz).
Reproduce by extracting the original package and running its unchanged
`reproduce.py --output NEW_DIRECTORY` with the pinned engine on `PYTHONPATH`.
Then use `tools/evaluate_field_questions.py` and the retained original
`evaluation/field-question-normalization/2026-11-20/verify_citations.py`.

Classification is separate from the score:

- **Contract failure:** behavior promised by that exact revision breaks.
- **Coverage gap:** a useful task lies outside that revision's supported behavior.
- **Feature request:** a proposal to expand the supported behavior.

The original revision's README and pipeline describe bounded finite proof rules;
they do not promise arbitrary paraphrase coverage. Its 750 paraphrase misses are
coverage gaps against that documented scope. The subsequent expansion is a feature
request; later authorization does not rewrite the old release's promises.
The 750 positive expectations still require correct answers: none of the original
misses has been relabelled a pass. Canonical support and unsupported-request
withholding are regression requirements.

This published, consumed benchmark is regression evidence, not unseen transfer.
Its results are reported separately from generated Bunyip development and fresh
transfer. No combined accuracy number or independent historical-accuracy claim is
made. The local replay and source checks are same-operator work.

Primary owner: Testing and Evaluation; protected implementation: Reader, Ledger.
[Authoritative Test Index](../../../../docs/TEST_INDEX.md).
