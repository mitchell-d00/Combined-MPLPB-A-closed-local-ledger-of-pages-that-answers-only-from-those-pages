"""Versioned metadata-aware attribution; original diagnostic/reader scores stay.

Finite literal claims historically omit a redundant per-claim support tag.
Complete strict contract + exact literal witnesses establish correspondence;
adding that tag is neither a language gain nor a missing source proof.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools import bunyip_language_attribution as v1
def assess(a):
    original=v1.read(a.diagnostic/'assessment.json');frozen=v1.read(a.diagnostic/'frozen-diagnostic.json');keys=v1.read(a.packet/'key.json');reg=v1.read(a.packet/'registry.json');variant=v1.read(a.variant_score);variant={r['id']:r for r in variant['rows']};old_scores={n:{r['id']:r for r in v1.read(p)['rows']} for n,p in [('main',a.main_score),('pr105',a.pr105_score)]};rows=[]
    assert v1.sha(a.packet/'registry.json')==frozen['original_packet_sha256'] and v1.sha(a.packet/'key.json')==frozen['original_key_sha256']
    for old in original['rows']:
        row=json.loads(json.dumps(old));key=keys[row['variant_id']];checks={}
        for name,prior in old['canonical_source_checks'].items():
            path=a.diagnostic/prior['raw'];assert v1.sha(path)==prior['raw_sha256'];raw=v1.read(path);okay,errors=v1.source_checked(raw,key);removed=False
            if ('support_status' in errors and key.get('literal_claim') and raw['answer']['verification'].get('structural') is True
                    and all(c.get('source_support_established',True) is True for c in raw['answer']['claims'])):
                errors=[e for e in errors if e!='support_status'];removed=True
            checks[name]={**prior,'complete_source_checked':not errors,'errors':errors,'v1_support_tag_requirement_removed_after_exact_literal_check':removed}
        row['canonical_source_checks_v2']=checks;row['variant']=variant[row['variant_id']];row['classifications']={}
        for name in ['main','pr105']:
            before=old_scores[name][row['variant_id']];after=row['variant'];canonical_ok=checks[name]['complete_source_checked'];ambiguous='opening hours' in row['variant_question'].casefold()
            if ambiguous:kind='retained_policy_disagreement'
            elif after['complete'] and before['complete']:kind='preserved_variant_support'
            elif after['complete'] and canonical_ok:kind='new_question_wording_support'
            elif after['complete']:kind='new_source_language_or_proof_operation_not_question_only'
            elif canonical_ok:kind='remaining_question_wording_miss'
            else:kind='remaining_source_or_proof_operation_miss'
            row['classifications'][name]=kind
        rows.append(row)
    counts={}
    for name in ['main','pr105']:
        groups=sorted({r['classifications'][name] for r in rows});counts[name]={g:{'executions':sum(r['classifications'][name]==g for r in rows),'unique_question_strings':len({r['variant_question'] for r in rows if r['classifications'][name]==g})} for g in groups}
    result={'policy':'source-matched-wording-attribution-v2','scope':'Post-run same-operator mechanism attribution, not new fresh cases, independent scoring or changed reader acceptance. Original fresh/strict scores and diagnostic v1 remain unchanged.','original_diagnostic_sha256':v1.sha(a.diagnostic/'assessment.json'),'scorer_sha256':v1.sha(Path(__file__)),'original_variant_score_sha256':v1.sha(a.variant_score),'counts':counts,'rows':rows,'tag_layout_infrastructure_counts_as_wording_gain':False,'independent_semantic_adjudication':'NOT_RUN'}
    v1.save(a.output,result);print(counts)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['packet','diagnostic','variant-score','main-score','pr105-score','output']:p.add_argument('--'+n,type=Path,required=True)
    assess(p.parse_args())
