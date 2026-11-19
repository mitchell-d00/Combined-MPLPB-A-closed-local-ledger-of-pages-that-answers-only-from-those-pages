# Archival source/date completeness experiment

Last reviewed: 2026-11-19.

Baseline main: `bc6f25c053dfc1ceb3b0096cca56550041395105`. Existing sources,
questions, expected files and past runs remain unchanged. Scope: finite
source-attributed event/date relationships, an offline tutorial, retained-metric
dashboard and anonymous review preparation. No new model authority or historical
truth claim is added. Independent review is **NOT RUN**.

Before code edits, a sparse detached baseline worktree was created at the pinned
main revision. Full baseline D% completed all 1,240 cases: 200/600 matched complete
answers and 640/640 expected refusals; observed false support 0. The unchanged
original-record baseline has 2 complete, 2 partial, 3 conflicts and 15 abstentions.
The initial independent-vocabulary event/date regression failed 5 of 10 controls
with exit 1; its log is retained. The first implementation passed those controls
but the real record still withheld catalogue/review dates because coarse native
units overlapped unrelated navigation/footer regions. The correction locates the
complete catalogue field, retains parent context, and treats page-review mentions
as textual annotations only. No historical event claim is accepted from chrome.

The current working-tree H07 answer retains four separate links: source-reported
artillery firing on April 12, surrender on April 13 at 2:30 p.m., evacuation on
the following day (calendar display April 14, year unstated), and the source's
catalogue date April 18, 1861. The webpage review date May 10, 2022 is explicitly
not an event date. The source calendar and event identity are not authenticated;
the catalogue date does not prove transmission. No 1861 year is silently added
to narrative clauses. Runtime rules contain no case IDs or historical names.

Final frozen-candidate regression, D%, full unchanged-original comparisons and
packet export have not yet completed at this source freeze. Their exact receipts,
failures, before/after results and costs will be added after execution. No pending
check is claimed as passed. The frozen D% scorer/generator/worker/key remain
unchanged; new unsupported semantic shapes do not get automatic credit.

Commands:

```sh
python -m unittest tests.test_event_date_inventory tests.test_archival_onboarding -q
python -m tools.dpercent run --packets /tmp/dpercent-frozen-public --implementation IMPLEMENTATION --out NEW_RUN
python -m tools.dpercent score --packets /tmp/dpercent-frozen-public --custodian /tmp/dpercent-frozen-private --run NEW_RUN --out NEW_SCORE
python -m tools.article_study --output NEW_ORIGINAL_STUDY
python -m tools.blind_archival_packets --before BASELINE_STUDY --after UPDATED_STUDY --output PUBLIC_REVIEW --custody PRIVATE_CROSSWALK
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/new-archival-public.json
```

Human historical precision/recall, appropriate-refusal rate, candidate-link
accuracy and human intervention costs remain null. External institutional pages
were located for reference context only; they are not human review or independent
corroboration. The primary research use case is archival inspection, not arbitrary
historical narration. See [contract and first use](../../../docs/ARCHIVAL_INSPECTION.md).
