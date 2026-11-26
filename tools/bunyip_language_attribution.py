"""Post-run matched canonical diagnostic; never a fresh test or runtime rule.

Separate question-wording recovery from newly admitted source/proof operations.
Source bytes remain identical. Original packets, keys and scores are untouched.
"""
import argparse,copy,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_adapter_v5 import execute,sha,runtime_files
from tools.bunyip_score import norm,subset
def read(p):return json.loads(Path(p).read_text())
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def canonical(k):
    p=k['proposition'];relation=p.get('relation');w=k['complete_witnesses'];text=w[0]
    if relation=='source_attributed_report_content':return 'reporting',f"What does {p['reporter']} report about whether {p['author']} wrote {p['object']}?"
    if relation=='source_modality_assertion':return 'instruction',f"What instruction does the record attribute to {p['actor']} concerning {p['task_object']}?"
    if relation=='source_event_date_inventory':
        subject=re.fullmatch(r'(.+?) was written on .+\.',text)[1]
        return 'writing_date',f'Distinguish the writing dates in {subject} record.'
    if text.startswith('Name: '):return 'opening_time','When does '+text.removeprefix('Name: ')+' open?'
    for pattern in [r'.+? owns (.+)\.',r'(.+?) is owned by .+\.',r'(.+?) belongs to .+\.']:
        m=re.fullmatch(pattern,text)
        if m:return 'ownership','Who owns '+m[1]+'?'
    m=re.fullmatch(r'(.+?) is (?:a|an) .+\.',text);assert m,text
    return 'classification','What is '+m[1]+'?'
def source_checked(raw,k):
    a=raw['answer'];errors=[]
    if not a['answer_supported'] or a['kind']!='supported_answer' or not a['claims']:return False,['canonical_not_complete']
    records={r['id']:r for r in raw['records']};quotes=[]
    if a['verification'].get('truth_verified') is not False:errors.append('truth_scope')
    for c in a['claims']:
        if c.get('source_support_established') is not True:errors.append('support_status')
        expected=copy.deepcopy(k['proposition']);actual=c.get('proposition',{})
        if expected.get('relation')=='source_attributed_report_content' and 'embedded_content_negative' not in actual:
            # Versioned representation assessment, not a changed original score.
            # Only permit the absent literal field after its exact source witness.
            assert expected['embedded_content_negative'] is False
            if not any(norm(expected['author']+' wrote '+expected['object']) in norm(x['quote']) for x in c['citations']):errors.append('literal_polarity_witness')
            expected.pop('embedded_content_negative')
        if not subset(actual,expected):errors.append('proposition')
        if k.get('literal_claim') and norm(c['text']) not in {norm('\n'.join(k['complete_witnesses'])),*(norm(w) for w in k['complete_witnesses'])}:errors.append('literal_claim')
        for f in k.get('qualification_fragments',[]):
            if not any(norm(f) in norm(q) for q in c.get('qualifiers',[])):errors.append('qualification')
        for x in c['citations']:
            r=records.get(x['source_id']);lo,hi=x['body_start'],x['body_end']
            if not r or r['hash']!=x['hash'] or r['body'][lo:hi]!=x['quote']:errors.append('citation')
            quotes.append(norm(x['quote']))
        for role,date in k.get('date_roles',{}).items():
            if not any(x.get('requested_role')==role and norm(x.get('date_text',''))==norm(date) for x in actual.get('date_links',[])):errors.append('date_role')
    for w in k['complete_witnesses']:
        if norm(w) not in quotes:errors.append('complete_witness')
    return not errors,errors
def main(a):
    a.output.mkdir(parents=True,exist_ok=False);reg=read(a.packet/'registry.json');keys=read(a.packet/'key.json');sealed=read(a.packet/'freeze.json');assert sha(a.packet/'registry.json')==sealed['registry_sha256'] and sha(a.packet/'key.json')==sealed['key_sha256']
    items=[];unique={}
    for r in reg['cases']:
        k=keys[r['id']]
        if k['decision']!='complete':continue
        path=(a.packet if r['packet'].startswith('inputs/') else ROOT)/r['packet'];case=read(path/'case.json');group,q=canonical(k);value=copy.deepcopy(case);value['question']=q;value.pop('id',None)
        signature=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest();probe=unique.setdefault(signature,{'case':value,'key':k,'canonical':q,'group':group})
        items.append({'variant_id':r['id'],'variant_question':case['question'],'canonical_question':q,'group':group,'probe_signature':signature,'source_bytes_unchanged':True})
    implementations={'main':a.main,'pr105':a.pr105,'candidate':a.candidate};pins={name:{str(p.relative_to(root)):sha(p) for p in runtime_files(root)} for name,root in implementations.items()}
    save(a.output/'frozen-diagnostic.json',{'purpose':'Post-run source-matched mechanism diagnostic, not fresh/independent evaluation','original_packet_sha256':sha(a.packet/'registry.json'),'original_key_sha256':sha(a.packet/'key.json'),'harness_sha256':sha(Path(__file__)),'canonical_map':items,'reader_pins':pins,'labels':'No original expected results or scores changed; API/tag/layout/infrastructure checks never counted as wording gains'})
    results={}
    for n,(signature,probe) in enumerate(unique.items(),1):
        inputs=a.output/'public'/f'PROBE-{n:04d}';case=copy.deepcopy(probe['case']);case['id']='PROBE-'+str(n);save(inputs/'case.json',case)
        for name,root in implementations.items():
            raw=execute(root,inputs,a.output/'runs'/name/inputs.name);okay,errors=source_checked(raw,probe['key']);results[(signature,name)]={'complete_source_checked':okay,'errors':errors,'raw_sha256':sha(a.output/'runs'/name/inputs.name/'result.json'),'raw':str(Path('runs')/name/inputs.name/'result.json')}
    for row in items:row['canonical_source_checks']={name:results[row['probe_signature'],name] for name in implementations}
    for name,root in implementations.items():assert pins[name]=={str(p.relative_to(root)):sha(p) for p in runtime_files(root)}
    save(a.output/'assessment.json',{'purpose':'Canonical-source support diagnostic; join with original fresh variant score to attribute gains. Same operator; post-run and not blinded.','variant_executions':len(items),'unique_canonical_probes':len(unique),'diagnostic_executions':len(unique)*3,'rows':items,'independent_historical_semantic_adjudication':'NOT_RUN'});print('diagnostic',len(items),'variants',len(unique)*3,'executions')
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['packet','output','main','pr105','candidate']:p.add_argument('--'+name,type=Path,required=True)
    main(p.parse_args())
