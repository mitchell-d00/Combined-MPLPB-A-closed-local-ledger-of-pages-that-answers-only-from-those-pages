"""Publish completed recovery executions without replacing historical artifacts."""
from pathlib import Path
from tools.unprepared_challenge import read, save, summary, compare
from tools.report_prose_followup import costs

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'evaluation/unprepared-originals/2026-11-16-recovery'
F = R.parent / '2026-11-16-followup'
OLD = R.parent / '2026-11-16'
FINAL = 'f12540c73d15ee81248e9eb4fe07f5b12242a312'


def main():
    if (R / 'REPORT.md').exists():
        raise FileExistsError('Preserve dated reports; publish a new experiment instead')
    measures = {}
    studies = [('historical', OLD, F/'historical-final', R/'final-historical'),
               ('unfamiliar', F/'unfamiliar', F/'unfamiliar/final', R/'final-unfamiliar'),
               ('legal-transfer', F/'legal-transfer', F/'legal-transfer/final', R/'final-legal-transfer'),
               ('cold-transfer', F/'cold-transfer', F/'cold-transfer/final', R/'final-cold-transfer'),
               ('transfer', R/'transfer', R/'transfer/prior', R/'transfer/final')]
    for name, corpus, prior, final in studies:
        save(R/(name+'-final-comparison.json'), compare(corpus, [prior, final]))
        for label, run in [('prior', prior), ('final', final)]:
            s = summary(corpus, run)
            if any(row['execution_status'] != 'completed' for row in s['rows']):
                raise ValueError('Report requires completed executions: '+str(run))
            measures[name+'_'+label] = costs(s)
            if label == 'final':
                save(R/(name+'-final-summary.json'), s)
    quality = {n: read(R/('final-'+n+'-score.json')) for n in ['reused', 'eo8802', 'transfer']}
    targets = {n: read(R/(n+'-final.json')) for n in ['distribution', 'cancellation']}
    date = read(R/'date-cue-comparison.json')
    regressions = read(R/'final-full-regression.json')
    public = read(R/'final-public-52.json')
    synthetic = read(R/'final-synthetic-score.json')
    audits = {n: read(R/('final-'+n+'-evidence-audit.json')) for n, _, _, _ in studies}
    if any(a['objects_checked'] != a['valid_objects'] for a in audits.values()):
        raise ValueError('Evidence audit failed')
    data = dict(schema='historical-recovery-results-v1', prior_native_commit='01f128bc6022ff64c2edf5c363f05f173ac95972',
                final_native_commit=FINAL, runtime_budget_seconds=180, costs=measures,
                targeted_recovery=targets, developer_semantic_assessments=quality,
                date_cue_comparison=date, regression=regressions,
                public_prepared_summary=public['summary'], synthetic_regression=synthetic,
                evidence_audit_objects=sum(a['objects_checked'] for a in audits.values()),
                independent_human_evaluation='NOT RUN', global_historical_precision=None,
                global_historical_recall=None, global_false_positive_relationship_rate=None,
                conclusion='Targeted recovery improved with retained useful associations; broad consistent reconstruction remains unestablished.')
    save(R/'results.json', data)
    h = measures['historical_final']
    lines = [
        '# Recovering missed relationships without reintroducing false ones — 2026-11-16', '',
        'MPLPB now consistently proposes two targeted missing source relationships when their complete evidence is retrieved. All 21 previously useful reviewed associations are retained, three useful associations are added, and the known incorrect actor association becomes unresolved. This is a **partial engineering success**, not evidence of general historical understanding. The additional two-record transfer still yields no fully resolved correct associations. Independent human evaluation is **NOT RUN**.', '',
        '## Frozen comparison and preservation', '',
        'The prior native revision is `01f128bc6022ff64c2edf5c363f05f173ac95972`; final native code is `'+FINAL+'`. Original strict baseline `614b18cc34f5270d4cb7dfbbf8239391a9f83b31`, all original five documents, 14 questions, 23 incomplete draft reference spans, scores and old outputs remain unchanged. The same frozen v2 importer/evaluator, native gates and 180-second per-question budget govern the paired runs. Raw originals are never rewritten with answer-bearing fields. Runtime sandboxes do not receive reference answers. [Results](results.json) bind actual runs and costs; each run retains code hashes, phase checkpoints, stdout/stderr and receipts.', '',
        'All semantic labels here are **Codex developer/AI source inspection**, with source quotes and rationales. These are not independent human judgments or complete historical gold labels. Frozen questions are developer-authored. Synthetic public-key regression controls remain in a separate corpus and are not independent blind evaluation.', '',
        '## Earliest demonstrated bottlenecks and repairs', '',
        'Import and canonical passage preservation had already succeeded. The first recovery attempt still missed distribution in three of four retrieved contexts: rejected lexical predicates consumed local extraction slots, and the six-proposition per-context limit excluded relevant later clauses. The final repair counts accepted predicates under the existing global 48-proposition bound instead. It does not expand permissions or turn candidates into claims. Generic cancellation phrases now work across physical line breaks while retaining conditional and negative scope. A prepositional place name is no longer guessed to be a grammatical actor; bounded same-clause coordinated actions carry quoted evidence and remain candidate connections.', '',
        'A separate source review found modal “may” and protest “march” being proposed as dates. Calendar cues now require explicit date syntax or temporal context; the original wording and offsets remain intact. The existing reverse-mapping CLI can select rich proposition/connection/scope objects and rechecks current source/policy state before reconstructing quotes. Reversible quotation verifies fidelity, not the truth of an inferred relationship.', '',
        '## Targeted consistency, with unsuccessful intermediate results retained', '',
        '| Target | Prior 01f128b | First recovery a2597bf | Final f12540c |',
        '|---|---:|---:|---:|',
        '| Order distribution with “eve of the invasion” date cue | 0/4 | 1/4 | 4/4 |',
        '| Randolph called off the march | 0/3 | 3/3 | 3/3 |', '',
        'Denominators are existing question/context opportunities containing the complete target passage: **two relationships across seven contexts**, not seven independent historical events. Distribution still has an unresolved agent. These checks measure candidate recovery, not verified event identity, truth, causality or overall recall. [Distribution](distribution-final.json) and [cancellation](cancellation-final.json) expose every success and miss. The failed 1/4 run, allocation correction and all terminal outputs remain public.', '',
        '## Correct associations, errors and uncertainty', '',
        '| Developer-reviewed set | Prior correct / incorrect / unresolved | Final correct / incorrect / unresolved |',
        '|---|---:|---:|',
        '| Reused unfamiliar originals and amendments | 18 / 1 / 37 | 18 / 0 / 40 |',
        '| Executive Order 8802 source | 3 / 0 / 6 | 6 / 0 / 6 |',
        '| Two additional transfer originals | 0 / 0 / 5 | 0 / 0 / 5 |', '',
        'All 21 previously source-consistent associations are retained. New useful candidates describe Roosevelt responding, Randolph cancelling, and the explicit same-clause coordination of responding and issuing. The wrong United States/District actor assignment is now unresolved. Increased uncertainty remains visible: across the final 75 distinct reviewed actor/action or textual associations, 24 are source-consistent and 51 unresolved. Zero labeled incorrect in this limited assessment is **not a global false-positive rate**. It does not count unresolved proposals as correct or certify every metadata field. Actor/action retention excludes only date-cue metadata, which is separately reviewed and fully disclosed in [the retention record](date-guard-association-retention.json).', '',
        'The [date-cue comparison](date-cue-comparison.json) retains all 16 genuine reviewed calendar/relative cues while reducing 12 false cues to zero. A genuine date expression does not establish its role as event, publication, observation or revision time; normalized event time remains unknown.', '',
        'The two additional originals are the Zimmermann Telegram and Germany’s surrender records. They were acquired after the a2597bf recovery code freeze and unchanged prior code ran first. Their originals, questions and rules were frozen before execution. Later allocation/date revisions reused these sources, so they are not newly unseen tests of final code. The frozen transfer protocol’s no-post-reading-change statement describes its initial a2597bf comparison, not those later revisions. Important conditional-alliance, intent/publication, signing/ceasefire and prospective-supersession relationships remain missed or unresolved. All five unique proposed transfer associations remain unresolved; no broad consistent recovery is demonstrated.', '',
        '## Retrieval, refusals and incomplete historical reference scope', '',
        f'The final historical execution returns **{h["draft_spans_retrieved"]}/{h["draft_spans"]}** draft reference spans, versus the earlier conversion repair’s 10/23. Native supported answers remain **{h["native_supported"]}/14**. The five previously missing draft cases H06/H10/H11/H12/H14 remain a discovery limitation; some negative-control excerpts are weak reference proxies, but no score is silently revised. Draft coverage is not independent historical accuracy or semantic reconstruction.', '',
        'Strict native refusals remain visible even where useful candidate evidence was retrieved. Frozen negative controls U08, L03 and T03 ask for unsupported causal or individual conclusions; refusal is appropriate within the selected corpus. Transfer Z02, G03 and X01 similarly test unsupported acceptance, appearance identity or connection. Positive questions also still abstain: those are answer-coverage limitations, not evidence that all refusals are desirable. No candidate, operational receipt or source quotation is promoted to semantic support merely to improve a score.', '',
        '## Authority, regression and review evidence', '',
        f'All **{data["evidence_audit_objects"]}** final rich proposition/connection/scope objects passed digest, current policy/source state, native pin, exact quote-coordinate and non-authority checks across the five studies. Each case also exercises a fresh gated inverse reconstruction. See final-*-evidence-audit.json and [the fresh-process rich CLI round trip](rich-cli-roundtrip.json). These mechanical checks do not validate semantic correctness.', '',
        f'The complete Python suite passed **{regressions["tests"]} tests in {regressions["seconds"]} seconds**. The 105 test files present at the starting ee9975a revision remain byte-identical; [comparison](existing-tests-preserved.json). New targeted controls exercise actual failure shapes, negative/conditional scope, multiline phrases, source corruption/change and permission boundaries. The prepared public suite passed **52/52**; separate released synthetic controls passed **24/24**. Those are regression evidence, not historical reconstruction scores. The earlier premature test statement and actual failure/correction are retained in validation-correction.json.', '',
        'All candidate nodes keep `answer_supported=false` and `content_truth_verified=false`. Source integrity, eligibility, origin/depth, restrictions, supersession, conflict handling, source-change invalidation, fencing, failed-work history and independent receipt boundaries remain governing. No model-generated assertions, causal bridges or candidate corrections alter the native ledger’s authority state.', '',
        'Complete final human review packets are prepared in final-*-review-packets. They contain outputs, exact citations and blank review templates, not invented reviewers or results. Independent review and adjudication are **NOT RUN**. No deployment or external validation is claimed.', '',
        '## Measured processing costs', '',
        '| Final study | Cases | CPU seconds | Worker wall seconds | Peak worker RSS bytes | Logical source bytes read |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for name, _, _, _ in studies:
        c = measures[name+'_final']
        lines.append(f'| {name} | {c["cases"]} | {c["cpu_seconds"]:.3f} | {c["worker_wall_seconds"]:.3f} | {c["max_worker_rss_bytes"]} | {c["logical_source_html_bytes_read"]} |')
    lines += ['', 'Prior-versus-final measurements are retained in results.json, along with complete per-case costs in run outputs. Logical bytes include repeated reads, not unique corpus size or physical disk I/O; parallel runs and host scheduling limit wall-time comparisons. No efficiency improvement is claimed. Runtime model/API charges are zero because runtime uses no model calls; compute pricing, human labeling/correction/review/adjudication time and development/model-assistance costs are unknown or not measured. Zero API charges do not mean zero computational cost.', '',
              '## Reproduction', '', 'Use an exact checkout of the desired native revision and a new output directory; existing outputs refuse overwrite. The historical frozen v2 seal is required. New original studies use their own freeze.json. The post-run target evaluator receives the key only after runtime execution.', '', '```sh',
              'python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16 --implementation CHECKOUT --mode updated --commit EXACT_SHA --seal freeze-v2.json --output NEW_HISTORICAL_RUN',
              'python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-followup/unfamiliar --implementation CHECKOUT --mode updated --commit EXACT_SHA --output NEW_UNFAMILIAR_RUN',
              'python -m tools.unprepared_challenge run evaluation/unprepared-originals/2026-11-16-recovery/transfer --implementation CHECKOUT --mode updated --commit EXACT_SHA --output NEW_TRANSFER_RUN',
              'python -m tools.audit_prose_study CORPUS RUN --output NEW_AUDIT.json',
              'python -m tools.evaluate_recovery_targets CORPUS PRIOR_RUN NEW_RUN --target distribution --output NEW_TARGET.json',
              'python -m tools.unprepared_challenge packets CORPUS NEW_RUN --output NEW_PACKETS',
              'python -m unittest discover -s tests -q', '```', '',
              'The same commands with legal-transfer and cold-transfer corpora reproduce those arms. Synthetic controls use the separate original synthetic-controls directory with --seal freeze-v2.json. Source hashes, acquisition links and rights are in each corpus manifest. Historical results are immutable; changed code or measurement conditions require new output paths and a new dated report.']
    (R/'REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
