# Implementation and verification status — 2026-10-31

This review covers current documentation entry points after the general-reader and
researcher-pilot merges. It is not a new full-system audit, independent accuracy
evaluation, or certification of every historical document. Original papers, sealed
inputs, captured responses and dated JSON reports retain their original bytes.

## Merged implementation

The distribution declares **2.1.0rc1**. The legacy core's 1.0.0 version, JavaScript
API version and provenance/retrieval contracts are separate version identifiers.

| Change | Merged state | Scope |
| --- | --- | --- |
| General answer pipeline, PR #21 | Merge `684097101b460a84c1216add1036b05acbf763c5` | Strict default; optional native local-model reading; citations, partial answers, diagnostic abstention and human-scored evaluation |
| Synthetic researcher pilot, PR #22 | Merge `bfba98786e54b45d7a18a9396517b61726ed97b7` | Six native scripted research journeys, one real Chromium journey, literal working-note routing/replay fixes and retained failure evidence |

The [pipeline guide](GENERAL_ANSWER_PIPELINE.md), [capability matrix](RELEASE_2_1_RC1.md),
[specialist API](SPECIALIST_CONTINUITY_API.md) and [pilot guide](../evaluation/researcher-pilot/README.md)
describe their respective operational boundaries. Assisted reading is configured
on a native host; the standalone browser has no model reader or specialist work UI.

## Tests and exact revisions

At PR #22's tested head `3f160ffacb6545e30a0c2752359c2bf15d0dafee`:

- The local full Python suite passed **764 tests** in 266.779 seconds; a focused
  pilot/routing/replay/context run passed **49 tests**.
- The synthetic native pilot passed **108/108 workflow checks** across six personas.
- The fast actual Chromium/WebAssembly journey passed **8/8 UI checks**.
- [PR validation run 41218141218](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/41218141218)
  passed both `regression` and `researcher-browser`.
- [Extracted-ZIP run 41218141042](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/41218141042)
  passed `archive-first`, including Python, native pilot, JavaScript, pinned
  WebAssembly, Chromium, persistence, offline API and layout checks.

These passed before PR #22 merged. They are results for that tested revision,
not blanket approval of future revisions. PR #21's earlier 755-test local result
and its build-time `evaluation/general-reader/validation.json` remain historical;
the latter's original CI-pending field is not a current deployment-status source.

## Answer coverage and product gaps

The pilot's deliberately simple developer fixtures returned **12/18 answerable
questions**, with six unnecessary refusals, 18/18 gold passages retrieved, and
12/12 citations validated. Six further conflict queries are checked separately
from its 24 scored questions. The first failed baseline and intermediate repair
remain alongside [the final pinned run](../evaluation/researcher-pilot/strict-after-replay.json).
Workflow passes, literal quotations and model confidence are not human semantic
correctness judgments. The strict pottery result remains **6/59**.

Live-model quality and calibration are unmeasured. Independent questions and
human usability sessions remain necessary. Dedicated investigation overview UI,
portable end-user backup/restore, schema upgrades and long-duration storage are
unfinished or unmeasured. A harness directory copy does not implement a backup
product feature. See the pilot's seven-goal table for the complete distinction.

## Deployment is separate

The last completed Pages run observed during this review was
[41211720842](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/41211720842),
which passed for the PR #21 merge `6840971`.
The post-PR #22 Pages run
[41219098810](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/41219098810)
was still running when inspected. Consult that run for its eventual outcome;
do not infer deployed-live verification from the passed premerge checks.

The [release procedure](RELEASE_EVIDENCE.md) requires the actual public-site
postdeployment Chromium check. The current commit, a generated build identifier,
an archive checksum and a historical successful workflow answer different questions.
