"""Assemble the dated source-reconstruction follow-up without overwriting results."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from tools.unprepared_challenge import read,save,summary,compare,covers,passages

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'evaluation/unprepared-originals/2026-11-16-followup'
OLD=ROOT/'evaluation/unprepared-originals/2026-11-16'


def costs(s):
    known=[x['costs'] for x in s['rows'] if x.get('costs')]
    return {'cases':len(s['rows']),'completed':sum(x['execution_status']=='completed' for x in s['rows']),
        'measured_cases':len(known),'cpu_seconds':sum(x['cpu_seconds'] for x in known),
        'worker_wall_seconds':sum(x['wall_seconds'] for x in known),
        'max_worker_rss_bytes':max((x['peak_process_rss_bytes'] for x in known),default=None),
        'logical_source_html_bytes_read':sum(x['source_html_bytes_read'] for x in known),
        'api_charge_usd':sum(x['api_charge_usd'] for x in known),'compute_price_usd':None,
        'human_labeling_seconds':None,'human_correction_seconds':None,'human_review_seconds':None,
        'native_supported':s['native_supported_answers'],'draft_spans_retrieved':s['reference_evidence_spans_retrieved'],
        'draft_spans':s['reference_evidence_spans']}


def main():
    if (R/'REPORT.md').exists():raise FileExistsError('Never replace a dated research result')
    old=summary(OLD,OLD/'conversion-repair');intermediate=summary(OLD,R/'historical-updated');final=summary(OLD,R/'historical-final')
    save(R/'historical-final-summary.json',final)
    save(R/'historical-comparison.json',compare(OLD,[OLD/'conversion-repair',R/'historical-updated',R/'historical-final']))
    refs={c['id']:c for c in read(OLD/'reference-draft.json')['cases']};missed=[]
    for case in final['rows']:
        out=read(R/'historical-final'/(case['id']+'.json'));shown=passages(out)+[e for c in out['answer'].get('claims',[]) for e in c.get('citations',[])]
        for ref in refs[case['id']]['citations']:
            if not any(covers(p,ref) for p in shown):missed.append({'case_id':case['id'],'reference':ref,'native_kind':case['answer_kind'],'diagnostic':case['diagnostic']})
    save(R/'remaining-missed-draft-spans.json',{'count':len(missed),'scope':'Unchanged incomplete draft references; not complete historical omissions. Negative-control excerpts need not establish a relationship.','rows':missed})
    measures={'historical_prior':costs(old),'historical_intermediate':costs(intermediate),'historical_final':costs(final)}
    for c in ['unfamiliar','legal-transfer','cold-transfer']:
        for arm in ['prior','final']:measures[c+'_'+arm]=costs(summary(R/c,R/c/arm))
    quality={n:read(R/(n+'.json')) for n in ['intermediate-semantic-score-v2','final-semantic-score-v2','cold-prior-score','cold-final-score']}
    facets=read(R/'reference-facet-assessment.json')
    receipt_cases=[]
    for c,case in [('unfamiliar','U08'),('legal-transfer','L03'),('cold-transfer','T03')]:
        o=read(R/c/'final'/(case+'.json'));receipt_cases.append({'case_id':case,'kind':o['answer']['kind'],'diagnostic':o['answer']['diagnostic']['code'],
            'developer_assessment':'justified refusal within this corpus','rationale':'Frozen question asks for causal or individual evidentiary support absent from the selected originals. No global impossibility claim.'})
    result={'schema':'prose-followup-results-v1','baseline_commit':'ee9975a9c6d3a6413a9295763e7cbea068195f17','intermediate_commit':'6499338f00377181a8ffc169b9977d4be31841e1',
        'final_native_commit':'01f128bc6022ff64c2edf5c363f05f173ac95972','runtime_budget_seconds':180,'frozen_original_inputs_preserved':True,
        'costs':measures,'semantic_assessments':quality,'draft_reference_facets':{'scope':facets['method'],'counts':facets['counts'],'denominator':facets['denominator']},
        'scoped_negative_refusal_controls':receipt_cases,'independent_human_evaluation':'NOT RUN','global_historical_relationship_precision':None,
        'global_historical_relationship_recall':None,'global_historical_false_positive_rate':None,
        'conclusion':'Reduced false candidate associations while retaining useful ones in finite developer source review; general historical reconstruction is not established.'}
    save(R/'results.json',result)
    lines=['# Reducing false relationships while retaining useful ones — 2026-11-16','',
    'The engineering priority is fewer false relationships without discarding useful correct ones. This iteration improves that tradeoff in source-linked developer assessment. It does **not** establish reliable general historical reconstruction. Independent human review remains **NOT RUN**.','',
    '## What changed and why','',
    'Starting code: `ee9975a9c6d3a6413a9295763e7cbea068195f17`. The [13-span diagnosis](missing-13-diagnosis.json) found ranking/navigation/context-budget failures, not lost imports. Several relevant passages ranked 18–63; others were outside the first 64. Generic context expansion consumed almost all 12,000 characters before reaching them. Query-facet retrieval now separates document discovery from the requested subject, uses source headings only for discovery, retains declared transcript appearances and reduces navigation dominance. Eligibility, exact-field unranked routing, restrictions, hashes, origin/depth and supersession remain governing.','',
    'The first source-proposition prototype (`6499338f00377181a8ffc169b9977d4be31841e1`) exposed genuine interpretation errors even though software regressions passed: Order/title nouns became actions; Union cause and well-received were misread; jurisdictional nouns became actors; shared website templates became proposed historical connections. All failures are retained. [The launch metadata correction](execution-metadata-correction.json) documents a mistyped descriptive commit label, `8ae`; actual executed native hashes bind those unchanged outputs to the stated intermediate commit.','',
    'The final native revision is `01f128bc6022ff64c2edf5c363f05f173ac95972`. It rejects common nominal/adjectival matches, respects source HTML paragraphs/site chrome, distinguishes reporting speech from instructions, leaves uncertain/passive roles unresolved and proposes bounded actor-continuity and decision-to-planned-action links. Full source quotations and qualification language stay attached. Every connection remains `answer_supported=false` and `content_truth_verified=false`. No inferred event identity, causality, correction or receipt becomes source authority.','',
    '## Actual semantic assessment','',
    'All proposed actor/action/modality associations and typed textual connections from the unfamiliar sets were inspected against their original source-linked quotes by Codex, the developer. These are **developer/AI judgments**, not independent human review or authenticated historical truth. Every label, rationale, mistake and unresolved case is public. Correct means a source-consistent candidate association within this finite scope.','',
    '| Evaluated code/set | Correct | Incorrect | Unresolved | Irrelevant | Distinct proposals |','|---|---:|---:|---:|---:|---:|']
    names={'intermediate-semantic-score-v2':'First prototype, reused unfamiliar records','final-semantic-score-v2':'Corrected code, same records','cold-prior-score':'First prototype, cold transfer','cold-final-score':'Corrected code, cold transfer'}
    for n,s in quality.items():
        c=s['unique_labels'];lines.append(f"| {names[n]} | {c.get('correct',0)} | {c.get('incorrect',0)} | {c.get('unresolved',0)} | {c.get('irrelevant',0)} | {s['unique_interpretations']} |")
    lines+=['','Useful correct proposals rise from **15 to 18**, while incorrect proposals fall from **38 to 1** in the reused unfamiliar-source set. Unresolved proposals increase from **17 to 37**. This is an explicit coverage/uncertainty tradeoff, not unconditional success. The final code retains a known error: United States is assigned an appointing action whose subject is the District. [Final assessment](final-developer-assessment-v2.json) retains that wrong proposal and its evidence.','',
    'Examples of useful candidate reconstruction: Roosevelt appoints Eisenhower; Eisenhower decides to proceed without proving a completed operation; he scribbled is tentatively connected to Eisenhower in the same paragraph; Hayden is tentatively connected to writing, supplying photographs and lobbying; the Secretary’s discretionary permission remains distinct from completed leases. These are interpretable, source-linked propositions and connections, not just passage matches. Their semantic status stays unverified.','',
    'The original [80-proposal review](intermediate-developer-assessment.json) remains unchanged. Version 2 analysis applies semantic-unit deduplication to both implementations: question-scoped proposition IDs no longer multiply one connection, and reversed directionless pairs collapse. The same correctness judgments are retained. This post-run analytical refinement is disclosed rather than presented as a preregistered independent metric. [Comparable intermediate score](intermediate-semantic-score-v2.json), [final score](final-semantic-score-v2.json).','',
    '## Unfamiliar originals and cold transfer','',
    'Three separately frozen NARA records cover the Order of the Day, Yellowstone legislation and the Emancipation Proclamation, followed by a separate constitutional repeal/scope record. Their ordinary prose was not rewritten into Event-ID/Related/Corrects fields. Exact original bytes, rights notice, hashes, generic import wrappers, frozen questions/rules and prior outputs are in [unfamiliar](unfamiliar/) and [legal-transfer](legal-transfer/). Published transcriptions and modern archival framing are retained together and distinguished where possible; no autograph authentication is claimed.','',
    'A further [Executive Order 8802 record](cold-transfer/) was acquired **after the final native code was committed**. Prior/final executions used the same frozen record, questions, budget and evaluator, with no parser changes after seeing its output. This is a cold transfer check for the code changes, not independent human blinding: Codex read the source and authored the questions. Both versions retain 3 source-consistent proposals; incorrect proposals fall from 14 to 0. Six final proposals remain unresolved. The final parser still misses Randolph’s called off the march response and fails to connect the complex June 25 issuance clause fully to Roosevelt. No zero-error generalization claim follows.','',
    f"[Finite reference-facet assessment](reference-facet-assessment.json): **{facets['counts'].get('matched',0)} matched, {facets['counts'].get('partial',0)} partial, {facets['counts'].get('missing',0)} missing**, across {facets['denominator']} post-run developer-atomized facets from the unchanged pre-run expectations. Partial is not success. Missing examples include the Order of the Day’s distribution relationship and Randolph’s response. This is not complete historical recall or independent gold accuracy.",'',
    'All fourteen unfamiliar/transfer questions still receive native strict refusals. Developer review finds refusal justified for the three prespecified causal/individual-finding negatives (U08, L03, T03); this is **3/3 scoped negative controls**, not overall answer accuracy. The remaining eleven refusals include answerable source facets and incomplete reconstruction. Receiving a complaint never proves its truth; normative committee duties do not prove completed enforcement.','',
    '## Frozen original historical questions','',
    f"All 14 final questions completed within the unchanged 180-second budget. Draft-reference coverage improves from **{old['reference_evidence_spans_retrieved']}/23 to {final['reference_evidence_spans_retrieved']}/23**. Eight of the original thirteen missing spans are recovered; [five remain](remaining-missed-draft-spans.json). The original questions, references, source corpus and scoring rules are unchanged. Native supported answers remain **0/14**. Coverage is against incomplete developer references, not historical relationship accuracy.",'',
    'Remaining misses occur in H06, H10, H11, H12 and H14. In particular, an opening paragraph of the final Declaration cannot establish whole-document absence, and background excerpts do not themselves prove a requested causal link or personal authorization. Those limitations do not excuse the retrieval misses; the frozen score still counts them. The larger original 14-question proposal set has mechanical evidence auditing but no exhaustive semantic review; its overall relationship error rate remains unknown.','',
    '## Processing costs and authority regressions','',
    '| Execution | Cases completed | CPU s | Worker wall s | Peak RSS MiB | Logical native HTML read GB |','|---|---:|---:|---:|---:|---:|']
    for n,c in measures.items():lines.append(f"| {n} | {c['completed']}/{c['cases']} | {c['cpu_seconds']:.2f} | {c['worker_wall_seconds']:.2f} | {c['max_worker_rss_bytes']/1048576:.2f} | {c['logical_source_html_bytes_read']/1e9:.3f} |")
    lines+=['','CPU/wall/RSS and repeated logical reads are actual measurements. Logical reads are not physical disk I/O. Source import and parent-launch costs are in receipts; concurrent testing can affect wall times. Compute price, human labeling/correction/review/adjudication time and engineering model costs are unknown. Runtime model/API calls are absent; zero API charges are not zero computation. No efficiency improvement is claimed.','',
    'The final full regression suite passed **1003 tests**; [receipt/log](final-full-regression.json). The intermediate suite passed 1000 despite its semantic failures, demonstrating that test counts are not reconstruction evidence. Existing tests are unchanged. New controls cover actual correspondence requests, passive legal scope, nominal/adjectival errors, candidate antecedents, corrupted/stale evidence and permission boundaries. The public prepared suite passed **52/52** and the separate published synthetic controls passed **24/24**; neither is independent historical validation.','',
    'Every proposed proposition/connection/scope object was checked for current source/policy state, native pins, exact canonical quote coordinates, digest and non-authoritative flags. See each study’s final-evidence-audit.json and [the historical audit](historical-final-evidence-audit.json). Mechanical fidelity is separate from semantic correctness. Final native code passed the archive-first, regression/browser, isolation, infrastructure and handoff CI checks on commit 01f128b; subsequent evidence-only publication commits have their own CI status. No deployment is claimed.','',
    '## Reproduce and review','',
    'See [the operational guide](../../../docs/PROSE_RECONSTRUCTION_FOLLOWUP.md) for frozen run commands. Existing results refuse overwrite. Use exact implementation commits and the same frozen evaluator/importer and 180-second question budget. `tools/prose_quality_study.py inventory --version 2` generates comparable proposal units; `score` binds all developer judgments to the exact inventory/evidence. `tools/audit_prose_study.py` checks every rich mapping’s mechanical evidence. Independent-review packets contain complete outputs, source projections and blank submissions in each study directory. They remain **NOT RUN**; no reviewer identities, signatures or durations are invented.','',
    'The next research question is whether correct useful associations survive broader independent source/question selection while unresolved and false proposals remain manageable. Current evidence supports bounded assistance with source reconstruction, not autonomous historical understanding.','']
    (R/'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps({'historical_coverage':final['reference_evidence_spans_retrieved'],'remaining':len(missed),'semantic':{n:s['unique_labels'] for n,s in quality.items()}},indent=2))


if __name__=='__main__':main()
