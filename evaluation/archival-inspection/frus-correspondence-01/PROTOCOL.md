# FRUS Correspondence 01 — frozen public diagnostic

Last reviewed: 2026-11-28.

The released runtime is main `cb7ed70a57d3fab38c458f278a42ffd040108d98`
(tree `8573ed26b24aa5336b72c0ce3d3b7512eb7059b3`). PR #132 lab results and
their original boundaries remain unchanged. The reader and effect code are
outside the study change. The diagnostic runs native Strict Ask and the
existing investigation path in the original-record study runner. No network,
models, evaluator files or production effect dispatch in the worker.

## Sources and limits

Seven documents from Foreign Relations of the United States, 1969–1976,
Volume III, US State Department Office of the Historian, official TEI edition.
The [source map](source-map.json) records pinned acquisition, parent XML
digest, exact fragment coordinates and digests, edition URLs, TEI printed
page offsets and references. [Publisher rights](sources/publisher-license.log)
provide the public-domain basis and CC0 dedication. The seven records span
17 distinct printed pages. Page numbers are printed edition markers.
They are neither manuscript sheets nor whole pages reproduced in this
selection. Some printed pages are shared and some are absent between
records. The volume is larger. The retained cluster is smaller than the
515-page target to keep the documentary relationships coherent.

The unchanged UTF-8 TEI fragments are preserved. The [projector](project.py)
uses published character data with whitespace normalization and block
boundaries. Editorial note text is explicitly marked. Figures and graphics
are omitted. Publisher anchor targets and physical page offsets remain
in the map. The ledger contains projected text, not HTML rendering,
facsimile, publisher navigation or inferred event fields. Editorial framing
and main-text wording remain distinguishable. Page mapping verifies publisher
layout coordinates; it does not establish historical truth.

Use the existing internal profile, native scan limits, investigation maximum
two hops, 12 sources and 200,000 characters, and the sealed study sandbox
limits. No budget or enablement changes. Preserve raw native and investigation
output and failures. A recorded dispatch field establishes only what the
record says. Delivery, reading, agreement and execution require their
own evidence.

## Freeze and custody

This study tests comparable failure classes on public historical sources.
Gelhaus’s private experiment retains its own dataset and score. Record who
authored the questions, ran the baseline, scored the outputs, and reviewed
the results, along with what each person saw and when. A same-operator
baseline measures performance on the frozen cases. Independent semantic
accuracy requires a separate assessment.

Keep held fresh answers and any parameters that could reconstruct the fresh
packet out of public files, including generators and manifests. Publish only
approved artifacts and non-revealing integrity hashes. Verify that the
permitted checkpoint can be recovered from remote storage while the
evaluator material remains in approved private custody. Report public
recoverability and private-custody verification separately.

Mitchell directed the study, Al received a progress update, and Betty authored
the cases and scored the baseline using a local evaluator key. The author
saw corpus and both question sets before scoring. GitHub Actions receives
public corpus and development questions only. No external reviewer has
seen or scored outputs. Hold fresh cases and answers for a separate run.
See [packet seals](packet-seals.json) and [freeze checksums](FREEZE-SHA256SUMS).
Fresh runtime inputs, authoring parameters, questions, expected anchors and
scorer stay outside the public tree. Independent and human metrics NOT_RUN.

## Rubric and order

| Track | Cases | Interpretation target |
| --- | ---: | --- |
| Location | 42 + 15 controls | Exact location and header anchors. Nine invented missing phrases have separate labels. Six evidence-absence prompts use the authentic records. |
| Direct relationship | 6 | Four positives and two missing or contrary evidence contrasts. |
| Two-link relationship | 5 | Two positives, three withheld missing/ambiguous/contrary bridge contrasts. |
| Documentary interpretation | 9 | Four supported interpretations and five withholds. |
| Smoke | 3 executions | Predeclared consumed subset, excluded from the 77 diagnostic cases. |

Preflight verifies actual Bubblewrap with the repository tests, including
lack of private mounts. Run smoke first, then current baseline only
after successful isolation and smoke execution. An older pinned comparison,
if executed, runs the same public packets and limits with independently
rebound runtime seals. Output timing measures worker wall and CPU time,
not reviewer effort. Keep source visits, exact anchor retrieval, exact page
citation correspondence, supported literal proof, meaningful attribution
or bridges, complete answers, partials, conflicts, uncertainty, unsupported
assertions, misses and execution errors separate. Require claim-level
semantic review for nonliteral positives that emit claims. The initial
mechanical grade can verify exact spans and classify no-claim misses.
It supplies no independent adjudication. Retain any review-required
claims individually.
