from pathlib import Path
from collections import Counter,defaultdict
import hashlib,html,json,re,sys,zipfile
root=Path('evaluation/cryptid/bunyip/round2/replacement')
sha=lambda b:hashlib.sha256(b).hexdigest()
norm=lambda s:' '.join(str(s).casefold().split())
def require(b,m):
    if not b:raise ValueError(m)
z=zipfile.ZipFile(sys.argv[1]); arms=sys.argv[2:]
rows=[]
for arm in arms:
    home=root/arm
    registry=json.loads((home/'registry.json').read_text())
    keys=json.loads((home/'custodian-key.json').read_text())
    seal=json.loads((home/'freeze.json').read_text())
    for name,digest in [('registry.json',seal['registry_sha256']),('custodian-key.json',seal['key_sha256'])]:
        require(sha((home/name).read_bytes())==digest,name)
    for name in ('released','candidate'):
        require(sha(z.read(f'{name}-runtime.zip'))==seal[f'{name}_runtime_zip'],name)
    for desc in registry['cases']:
        id=desc['id']; path=Path(desc['packet'])/'case.json'
        packet=json.loads(path.read_text()); key=keys[id]; marks={}
        require(sha(path.read_bytes())==desc['files']['case.json'],id)
        src={s['id']:s for s in packet['sources']}
        for w in key['witnesses']:
            b=src[w['source']]['body_html'].encode()
            require(sha(b)==w['body_html_sha256'] and html.unescape(b[w['start_byte']:w['end_byte']].decode())==w['quote'],id)
        for reader in ('released','candidate'):
            base=f'{arm}-{reader}/{id}'
            run=json.loads(z.read(f'{arm}-{reader}/run.json'))
            require(run['reader_commit']==seal[f'{reader}_commit'] and run['registry_sha256']==seal['registry_sha256'],base)
            rr=next(x for x in run['cases'] if x['id']==id)
            if rr['execution_status']!='completed':
                marks[reader]={'execution':rr['execution_status'],'reason':rr.get('error'),'status':'NOT_RUN'}
                continue
            raw=z.read(f'{base}/result.json')
            ex=json.loads(z.read(f'{base}/execution.json'))
            require(sha(raw)==rr['raw_sha256']==ex['result_sha256'] and ex['inputs']==desc['files'] and ex['worker_receives_key'] is False and ex['network_namespace_isolated'] is True,base)
            r=json.loads(raw)
            require(r['id']==id and r['question']==packet['question'],base)
            a=r['answer']; claims=a['claims']; citations=[]; cite_errors=[]
            records={x['id']:x for x in r['records']}
            for claim in claims:
                if not claim.get('citations'):cite_errors.append('uncited claim')
                for c in claim.get('citations',[]):
                    sid=c.get('source_id'); source=src.get(sid); record=records.get(sid)
                    if not source or not record or source['withdraw'] or (packet['profile']=='external' and source['external']!='yes'):
                        cite_errors.append('ineligible or unavailable source');continue
                    start,end=c.get('body_start'),c.get('body_end')
                    if not (isinstance(start,int) and isinstance(end,int) and 0<=start<end<=len(record['body']) and record['body'][start:end]==c.get('quote') and record['hash']==c.get('hash') and record['path']==c.get('path')):
                        cite_errors.append('canonical citation disagrees with sealed record');continue
                    if 'original_witness' in c:
                        w=c['original_witness']
                        title=html.escape(' '.join(source['title'].split()),quote=False)
                        body=(f'<h1>{title}</h1>\n'+source['body_html']).replace('\r\n','\n').strip().encode()
                        x,y=w.get('start_byte'),w.get('end_byte')
                        if not (w.get('coordinate_space')=='admitted_record_body_html_utf8' and w.get('body_html_sha256')==sha(body) and isinstance(x,int) and isinstance(y,int) and 0<=x<y<=len(body) and html.unescape(body[x:y].decode())==c['quote']):
                            cite_errors.append('original HTML witness mismatch')
                    citations.append((sid,c['quote']))
            witnesses=[w['quote'] for w in key['witnesses'] if any(sid==w['source'] and norm(w['quote']) in norm(q) for sid,q in citations)]
            covered=len(witnesses)==len(key['witnesses'])
            attributed=all(norm(x) in norm(json.dumps(claims,ensure_ascii=False)) and any(norm(x) in norm(q) for _,q in citations) for x in key['attribution'])
            condition_ok=all(any(norm(s) in norm(q) for _,q in citations) and norm(s) in norm(json.dumps([c.get('text') for c in claims],ensure_ascii=False))+norm(json.dumps([c.get('proposition') for c in claims],ensure_ascii=False)) for s in key['conditions'])
            props=[c.get('proposition',{}) or {} for c in claims]
            neg=any(p.get('inner_negative') is True or p.get('polarity')=='negative' or p.get('outer_polarity')=='negative' for p in props)
            pos=any(p.get('inner_negative') is False or p.get('polarity') in {'positive','affirmative'} or p.get('outer_polarity')=='affirmative' for p in props)
            literal_negative=any(re.search(r'\b(not|never)\b',norm(q)) for q in witnesses)
            polarity_ok=(key['polarity'] is None or (key['polarity']=='negative' and (neg or literal_negative)) or (key['polarity']=='positive' and not neg and (pos or bool(witnesses) and not literal_negative)))
            layer_ok=not any(p.get(k) is True or p.get('time',{}).get(k) is True for p in props for k in ('completion_established','completion_asserted_by_source','actual_authorship_established','historical_truth_independently_verified') if isinstance(p.get('time',{}),dict))
            supplied_missing=norm(' '.join(str(x) for x in a.get('missing',[])))
            missing_ok=all(norm(x) in supplied_missing for x in key['missing'])
            proof=covered and attributed and condition_ok and polarity_ok and layer_ok and not cite_errors
            complete=bool(a['answer_supported'])
            is_partial=a['kind']=='partial_answer' and bool(claims) and not complete
            if key['status']=='complete':match=complete and bool(claims) and proof
            elif key['status']=='partial':match=is_partial and proof and missing_ok
            else:match=not complete and (not claims or key['conflict_allowed'] and a['kind']=='conflict' and proof)
            unsupported_complete=complete and not match
            unsafe_claim=bool(claims and (cite_errors or not layer_ok or key['status']=='withhold' and not match or key['status']=='partial' and (not proof or complete) or key['status']=='complete' and complete and not match))
            marks[reader]={'execution':'completed','status':a['kind'],'claim_count':len(claims),'support':match,'unsupported_completion':unsupported_complete,'unsupported_claim_case':unsafe_claim,'dimensions':{'source_support':covered and bool(claims),'attribution':attributed if key['attribution'] else None,'polarity':polarity_ok if key['polarity'] else None,'conditions':condition_ok if key['conditions'] else None,'citation_correctness':not cite_errors if claims else None,'readable_yes_no':a['text'].lstrip().startswith(key['presentation']) if key['presentation'] and complete else None,'missing_obligation':missing_ok if key['missing'] else None},'required_witnesses_covered':witnesses,'citation_errors':cite_errors,'diagnostic':a['diagnostic']['code'],'raw_output_sha256':sha(raw)}
        rows.append({'packet':arm,'id':id,'family':desc['family'],'question':packet['question'],'expected':key['status'],'membership':'target' if id.endswith('-A') else 'control',**marks})
def summarize(data):
    result=Counter()
    for r in data:
        result['cases']+=1
        a,b=r['released'],r['candidate']
        for name,side in [('released',a),('candidate',b)]:
            if side['execution']!='completed':result[f'{name}_execution_failures']+=1;continue
            result[f'{name}_executed']+=1
            result[f'{name}_unsupported_completions']+=side['unsupported_completion']
            result[f'{name}_unsupported_claim_cases']+=side['unsupported_claim_case']
            result[f'{name}_correct_controls']+=int(r['membership']=='control' and side['support'])
            if side['dimensions']['readable_yes_no'] is False: result[f'{name}_formatting_disagreements']+=1
        if r['membership']=='target' and a['execution']==b['execution']=='completed':
            result[{(True,True):'both', (False,True):'candidate_only', (True,False):'released_only', (False,False):'neither'}[a['support'],b['support']]]+=1
    return dict(result)
families=defaultdict(list); questions=defaultdict(list)
for r in rows:families[r['family']].append(r);questions[r['question']].append(r['id'])
out={'comparison_format':'bunyip-round2-replacement-readout-v1','packet_arms':arms,'artifact_sha256':sha(Path(sys.argv[1]).read_bytes()),'summary':summarize(rows),'by_family':{f:summarize(data) for f,data in families.items()},'distinct_original_questions':len(questions),'question_memberships':dict(questions),'rows':rows}
print(json.dumps(out,ensure_ascii=False,indent=2))
