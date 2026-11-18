"""Compose checked source assertions; extraction never awards support.

Question decomposition is an inspection plan. Every gate and verifier retains
the complete question/profile. Only the independent assertion kernel can produce
source-support certificates, with historical truth explicitly unverified.
"""
import re
from .body_text import body_text
from .evidence_contract import pin
from . import documentary_verify as kernel
from mplpb_combined.reader import terms

VERSION='documentary-composition-v1'
ACTIONS={'appointed':'appoint','sent':'send','received':'receive','wrote':'write',
         'surveyed':'survey','published':'publish','revised':'revise','canceled':'cancel',
         'ordered':'order','requested':'request','instructed':'instruct'}


def _proposal_units(text):
    start=0
    for m in re.finditer(r'[.!?]["”\)\]]?\s+(?=[A-Z"\[])',text):
        word=re.search(r'(\w+)$',text[:m.start()])
        if word and (len(word[1])==1 or word[1].lower() in {'mr','mrs','ms','dr','gen','maj','prof','hon','st','jr','sr'}):continue
        end=m.start()+1
        if end<len(text) and text[end] in '\"”)]':end+=1
        a=start+len(text[start:end])-len(text[start:end].lstrip())
        if a<end:yield a,end,text[a:end]
        start=m.end()
    if text[start:].strip():
        a=start+len(text[start:])-len(text[start:].lstrip());yield a,len(text),text[a:]


def _contexts(index,passages,max_chars,max_passages):
    bodies={r.path:body_text(r.body_html) for r in index.records};result=[];used=0
    for p in passages:
        a=p['body_start'];b=a+len(p['text']);remaining=max_chars-used
        if len(result)>=max_passages or b-a>remaining:continue
        if any(q['path']==p['path'] and q['body_start']<=a and q['body_start']+len(q['text'])>=b for q in result):continue
        margin=min(500,(remaining-(b-a))//2);lo=max(0,a-margin);hi=min(len(bodies[p['path']]),b+margin)
        item=dict(p,body_start=lo,text=bodies[p['path']][lo:hi]);result.append(item);used+=hi-lo
    return result


def plan(question):
    clauses=re.split(r'\?\s+(?=[A-Z])|,?\s+and\s+(?=(?:who|which|what|when|how|why|did|does|can)\b)',question,flags=re.I)
    if len(clauses)>4:return None
    goals=[]
    for clause in clauses:
        clause=clause.strip().rstrip('? .')
        q=re.sub(r'^According to [^,]{1,120},\s*','',clause,flags=re.I)
        who=re.fullmatch(r'Who ('+'|'.join(ACTIONS)+r') (.{1,240})',q,re.I)
        if who:
            goals.append({'question':clause,'kind':'who_action','action':ACTIONS[who[1].lower()],'object_text':who[2]})
        elif re.match(r'Who (?:arranged|asked|requested|instructed)\b',q,re.I):
            goals.append({'question':clause,'kind':'reported_instruction'})
        elif re.match(r'Which (?:dated )?letter\b',q,re.I):
            goals.append({'question':clause,'kind':'letter_context'})
        elif re.match(r'(?:Why (?:was|were|did)|what (?:spacecraft|vehicle|resource|equipment|system)|what .*provide)',q,re.I):
            goals.append({'question':clause,'kind':'explicit_cause' if q.lower().startswith('why') else 'resource_support'})
        elif re.match(r'(?:Compare|What (?:wording|words|text)|How .*differ)',q,re.I):
            goals.append({'question':clause,'kind':'wording_comparison'})
        elif re.fullmatch(r'(?:what|which) (?:wording |words )?(?:remained|remains|is shared|was retained)',q,re.I):
            goals.append({'question':clause,'kind':'wording_shared'})
        elif re.match(r'(?:When |What happened (?:before|after)|Did .* (?:before|after))',q,re.I):
            goals.append({'question':clause,'kind':'temporal_statement'})
        else:goals.append({'question':clause,'kind':'unresolved'})
    return goals if any(g['kind'] not in {'unresolved','letter_context'} for g in goals) else None


def propose(index,passages):
    """Opaque exact-source proposals only; no authoritative actor/event fields."""
    bodies={r.path:body_text(r.body_html) for r in index.records};result=[];seen=set()
    def add(p,a,b,kind):
        key=(p['path'],a,b,kind)
        if key in seen or len(result)>=12:return
        seen.add(key);result.append({'kind':kind,'source_id':p['source_id'],'path':p['path'],
          'hash':p['hash'],'start':a,'end':b,'quote':bodies[p['path']][a:b]})
    for p in passages:
        body=bodies[p['path']];a=p['body_start'];b=a+len(p['text'])
        # Letter openings need both the original heading and complete statement.
        for heading in re.finditer(r"(?m)^[A-Z][A-Z .’'\-]{2,70} TO ",p['text']):
            h=a+heading.start()
            opening=re.search(r'\bI\s+(?:have\s+)?(?:told|asked|instructed|requested|ordered)\s+',body[h:min(b,h+400)])
            if not opening:continue
            start=h+opening.start();first=next(_proposal_units(body[start:b]),None)
            if first:add(p,h,start+first[1],'letter_instruction')
        for lo,hi,q in _proposal_units(p['text']):
            if hi-lo<=2200 and re.search(r'\b(?:'+'|'.join(ACTIONS)+r'|did\s+not\s+(?:'+'|'.join(ACTIONS.values())+r'))\b',q):
                add(p,a+lo,a+hi,'action_statement')
        for lo,hi,q in kernel.units(body):
            if lo>=b or hi<=a or hi-lo>2200:continue
            if kernel.relationship_assertion(q):add(p,lo,hi,'relationship_statement')
    if any(g['kind']=='wording_comparison' for g in plan(index.question) or []):
        import difflib
        from .source_units import comparison_units
        records={r.path:r for r in index.records}
        candidates=[];candidate_seen=set();comparison_plan=kernel.comparison_request(index.question)
        for p in passages:
            for lo,hi,q in comparison_units(records[p['path']]):
                if lo<p['body_start']+len(p['text']) and hi>p['body_start'] and 8<=hi-lo<=2200:
                    key=(p['path'],lo,hi)
                    if key not in candidate_seen:candidates.append((p,lo,hi,q));candidate_seen.add(key)
        pairs=[]
        minimum_shared=2 if comparison_plan else 4
        for i,left in enumerate(candidates[:60]):
            for right in candidates[i+1:60]:
                if left[0]['path']==right[0]['path']:continue
                x,y=terms(left[3]),terms(right[3]);shared=x&y
                if len(shared)<minimum_shared:continue
                common=difflib.SequenceMatcher(None,left[3].split(),right[3].split(),autojunk=False).find_longest_match().size
                if common<minimum_shared:continue
                score=10*len(terms(index.question)&shared)+common/max(1,min(len(left[3].split()),len(right[3].split())))
                if comparison_plan:score+=100*len(set(comparison_plan['topic_terms'])&shared)
                pairs.append((score,left,right))
        for _,left,right in sorted(pairs,key=lambda x:-x[0])[:4 if comparison_plan else 2]:
            p,a,b,q=left;r,lo,hi,t=right
            # Comparisons share the same 12-proposal bound as all other rules.
            if len(result)>=12:break
            result.append({'kind':'wording_comparison','source_id':p['source_id'],'path':p['path'],'hash':p['hash'],'start':a,'end':b,'quote':q,
                'other':{'source_id':r['source_id'],'path':r['path'],'hash':r['hash'],'start':lo,'end':hi,'quote':t}})
            if len(result)<12 and kernel.comparison_request(index.question):
                result.append(dict(result[-1],kind='comparison_completion'))
    return result


def _relevant(goal,proof,question):
    v=proof['proposition']
    relation={'explicit_cause':'source_causal_assertion','resource_support':'source_resource_assertion',
              'wording_comparison':'exact_wording_comparison','wording_shared':'exact_wording_comparison','temporal_statement':'source_temporal_assertion'}.get(goal['kind'])
    if relation:
        if v['relation']!=relation:return False
        if relation=='exact_wording_comparison':return True
        return bool(terms(goal['question']) & terms(' '.join(str(x) for x in v.values() if isinstance(x,str))))
    if goal['kind']=='who_action':
        if v['relation']=='source_reports_instruction' and goal['action'] in {'request','instruct','order'}:
            return bool(terms(goal['object_text']) & terms(v['intermediary_text']+' '+v['object_text']+' '+v['requested_recipient_text']))
        if v['relation'] not in {'source_action_assertion','source_passive_action_assertion'} or v['action']!=goal['action']:return False
        return bool(terms(goal['object_text']) & terms(v['object_text'])) or (
            v.get('unresolved_reference') is True and v.get('context_identity_resolved') is False
            and bool(terms(goal['object_text']) & set(v.get('context_topic_terms',[]))))
    if goal['kind'] in {'reported_instruction','letter_context'} and v['relation']=='source_reports_instruction':
        wanted=terms(question)-terms('who arranged asked requested instructed which dated letter records arrangement receive send copy book report')
        observed=terms(' '.join(str(x) for x in v.values() if isinstance(x,str)))
        return bool(wanted & observed) or bool(terms(question)&terms(v['object_text']))
    return False


def _claim(proof):
    v=proof['proposition']
    if v['relation']=='source_action_assertion':
        prefix=(v['temporal_qualification_text']+', ') if v['temporal_qualification_text'] else ''
        text='Source assertion: '+prefix+v['actor_text']+' '+('did not '+v['action'] if v['negative'] else next(k for k,a in ACTIONS.items() if a==v['action']))+' '+v['object_text']+'.'
        qualifiers=['Source-attributed statement; event/person identity and historical truth are not independently verified.']
        if v['action'] in {'order','request','instruct'}:qualifiers.append('A directive or request does not establish its execution.')
        if v['unresolved_reference']:qualifiers.append('An object, role or date reference remains unresolved.')
        if v.get('context_identity_resolved') is False:qualifiers.append('Shared local topic wording does not resolve the object or establish an event identity.')
    elif v['relation']=='source_reports_instruction':
        text=('The letter headed '+v['writer_text']+' TO '+v['addressee_text']+
              (' ('+v['heading_date_text']+')' if v['heading_date_text'] else '')+
              ' reports that its writer '+('had ' if v['request_aspect']=='perfect' else '')+v['request_verb']+' '+v['intermediary_text']+
              ' to '+v['requested_action']+' its addressee the item described as “'+v['object_text']+'”.')
        qualifiers=['The I/you/my bindings refer only to this documentary appearance; authorship is source-declared, not authenticated.',
                    'Reported instruction does not establish actual dispatch or receipt.',
                    'Heading date does not establish when the instruction, dispatch or receipt occurred.']
        if v['condition_text']:qualifiers.append('Literal action/delivery qualification (exact scope unresolved): '+v['condition_text'])
        if v['delivery_text']:qualifiers.append('Requested delivery method: '+v['delivery_text'])
        if v['hope_text']:qualifiers.append('Additional hope stated by writer: '+v['hope_text'])
        if v['literal_following_note']:qualifiers.append('Following source note retained without a separate historical claim: '+v['literal_following_note'])
        if v.get('question_obligations_verified'):
            qualifiers.append('Complete only as the recorded arrangement request and printed letter date; the complete local letter is cited. Actual fulfillment and outside-world truth remain unverified.')
    else:
        if v['relation']=='exact_wording_comparison':
            parts=[]
            for change in v['alignment'][:12]:
                if change['operation']=='equal':parts.append('Shared wording: “'+change['left_text']+'”.')
                else:parts.append('Source A: “'+change['left_text']+'”; source B: “'+change['right_text']+'”.')
            text='Exact comparison of the two cited units. '+' '.join(parts)
            if len(v['alignment'])>12:text+=' Further differences and shared text are retained in the complete structured alignment.'
        else:text='Source assertion: '+re.sub(r'\s+',' ',proof['citations'][0]['quote'])
        qualifiers=['Only the complete cited wording is checked; historical truth and event/person identity are not independently verified.']
        if v['relation']=='source_causal_assertion':qualifiers.append('The source explicitly attributes a cause; this does not independently establish historical causation.')
        if v['relation']=='exact_wording_comparison':
            qualifiers.append('No version order, correction, motive, responsible person or whole-document absence is established by this local comparison.')
            if v.get('question_obligations_verified'):
                qualifiers.append('Complete only for the supplied source-declared reconstruction/transcription and their cited opening topic. Historical authenticity and finality are not independently verified.')
    return {'text':text,'qualifiers':qualifiers,'citations':proof['citations'],
            'proposition':v,'source_support_established':True,'support_scope':'source_attributed_assertion',
            'verification':proof['verification'],'historical_truth_independently_verified':False,
            'proof_sha256':pin(proof)}


def compose(index,max_passages,max_chars):
    goals=plan(index.question)
    if goals is None:return None
    from .prose_retrieval import retrieve
    pack=retrieve(index,max_passages,max_chars)
    from .passage_admission import Budget,comparison_plan,candidate_allowed,admit_proposals,pending_suggestions
    admission=Budget(index,max_passages,max_chars)
    planned=comparison_plan(index,admission)
    located=pack['passages']+pack.get('sorter_candidates',[])+pending_suggestions()
    ordinary=[p for p in located if candidate_allowed(index,p,goals,admission,closed_plan=planned is not None)]
    # Reader-selected rule dependencies survive reranking and final cutoff.
    # Sorter search-only suggestions remain separate locators for review.
    if planned:ordinary=planned['passages']
    elif not ordinary:
        # Older retrieval adapters can tag every source passage as a hint.
        # Recover through this index's own native question search, never through
        # a synonym score, hinted endpoint or class supplied by the sorter.
        native=index.retrieve([index.question],max_passages,max_chars)
        ordinary=native['passages']
        admission.discovery['native_fallback_passages']=len(ordinary)
    from .source_units import expand
    passages,context_limits=expand(index,ordinary,max_passages,max_chars)
    if any(g['kind']=='wording_comparison' for g in goals):
        # Literal comparisons retain complete native paragraphs, including
        # semicolon-separated originals that are longer than a sentence.
        passages=ordinary
    if not passages:passages=_contexts(index,ordinary,max_chars,max_passages)
    proposals=propose(index,passages)
    proposals=admit_proposals(index,proposals,goals,_relevant,admission,planned['proposal'] if planned else None)
    checked=kernel.check(index,proposals)
    if checked['status']=='source_changed':return {'kind':'abstain','code':'source_changed'}
    proofs=checked['proofs'];selected=[];statuses=[];missing=[];conflict=False;ambiguous=False;alternatives=[]
    closures=[p for p in proofs if p['proposition'].get('question_obligations_verified')
              and p['proposition'].get('verified_question')==index.question]
    comparison_completion=(len(closures)==1 and all(g['kind'] in {'wording_comparison','wording_shared'} for g in goals))
    arrangement_completion=(len(closures)==1 and all(g['kind'] in {'reported_instruction','letter_context'} for g in goals)
        and closures[0]['proposition'].get('question_completion_rule')=='document_local_arrangement_reference_v1')
    literal_completion=comparison_completion or arrangement_completion
    if literal_completion:proofs=closures
    for goal in goals:
        matches=[p for p in proofs if _relevant(goal,p,index.question)]
        status={'question':goal['question'],'kind':goal['kind'],'status':'unresolved'}
        if goal['kind'] in {'explicit_cause','resource_support','wording_comparison','wording_shared','temporal_statement'}:
            if matches:status['status']='supported_source_assertion' if literal_completion else 'checked_relationship_scope_partial'
        elif goal['kind']=='who_action':
            exact=[p for p in matches if p['proposition']['relation']=='source_action_assertion' and not p['proposition']['unresolved_reference']
                   and kernel.normalized(p['proposition']['object_text'])==kernel.normalized(goal['object_text'])]
            # Scan all eligible source units, not only retrieval winners. A
            # qualified/unparsed relevant unit prevents complete acceptance.
            competing=[p for p in checked['observations'] if p['proposition']['action']==goal['action']
                       and kernel.normalized(p['proposition']['object_text'])==kernel.normalized(goal['object_text'])]
            if exact:
                matches=competing
                actors={kernel.normalized(p['proposition']['actor_text']) for p in competing if not p['proposition']['negative']}
                polarities={p['proposition']['negative'] for p in competing}
                scopes={p['proposition']['temporal_qualification_text'] for p in competing}
                unknown_contexts=[(r,a,b,q) for r,a,b,q,value in checked['contexts']
                    if (value is None and (terms(goal['object_text'])&terms(q) or re.search(r'\b(?:he|she|it|they|that|this|those|these)\b',q,re.I))
                    and (re.search(r'\b'+re.escape(goal['action'])+r'\w*\b',q,re.I)
                         or any(re.search(r'\b'+re.escape(w)+r'\b',q,re.I) for w,act in ACTIONS.items() if act==goal['action'])))
                    or (re.search(r'\b(?:retracted|withdrawn|corrected|superseded|amended|revoked|rescinded|denied|canceled)\b',q,re.I)
                        and (value is None or value['action']!=goal['action']))]
                unknown=bool(unknown_contexts)
                for r,a,b,q in unknown_contexts:
                    e=kernel.citation(r,body_text(r.body_html),a,b)
                    if e not in alternatives:alternatives.append(e)
                if len(polarities)>1 and len(scopes)==1:conflict=True;status['status']='opposed_source_statements_event_identity_unverified'
                elif len(actors)>1 or len(scopes)>1:ambiguous=True;status['status']='event_or_actor_scope_unresolved'
                elif actors and checked['scan_complete'] and not unknown:
                    status['status']='supported_source_assertion'
                else:status['status']='partial_source_assertion'
            elif matches:status['status']='partial_source_assertion'
        elif matches:
            status['status']='supported_source_assertion' if arrangement_completion else 'supported_documentary_context' if goal['kind']=='letter_context' and all(p['proposition']['heading_date_text'] for p in matches) else 'partial_source_assertion'
            for record,a,b,q,value in checked['contexts']:
                if re.search(r'\b(?:canceled|cancelled|withdrawn|retracted|corrected|denied)\b',q,re.I) and any(terms(q)&terms(p['proposition']['object_text']) for p in matches):
                    e=kernel.citation(record,body_text(record.body_html),a,b)
                    if e not in alternatives:alternatives.append(e)
        for proof in matches:
            if proof not in selected:selected.append(proof)
        if status['status'] not in {'supported_source_assertion','supported_documentary_context'}:
            reason=('Exact requested identity/object and actual arrangement, dispatch and receipt are not established by a reported instruction.' if goal['kind']=='reported_instruction'
                    else 'Exact requested argument, reference, qualification, or complete contrary-evidence search is not established.')
            missing.append(goal['question']+': '+reason)
        status['evidence_proof_sha256'] = list(dict.fromkeys(pin(p) for p in matches))
        statuses.append(status)
    if not checked['scan_complete'] and not literal_completion:missing.append('Contrary-evidence scan reached its explicit character/unit/assertion budget; absence of contradiction is not established.')
    if context_limits and not literal_completion:missing.append('Some complete source units exceeded the context budget; search/context is incomplete.')
    request_scope=any(p['proposition']['relation']=='source_reports_instruction' for p in selected)
    if request_scope and not arrangement_completion:missing.append('Request occurrence, later correction/cancellation and execution are outside this source-attribution certificate.')
    shown=[]
    for proof in selected:
        if not admission.offer(proof['citations'],'verified_question_evidence_or_counterevidence'):
            if conflict:admission.counter_did_not_fit=True
            missing.append('Verified/competing statements exceed the display budget; no pruned subset establishes a complete answer.');continue
        shown.append(proof)
    displayed_alternatives=[]
    for e in alternatives:
        if not admission.offer([e],'relevant_unresolved_counterevidence'):
            admission.counter_did_not_fit=True;continue
        displayed_alternatives.append(e)
    if len(displayed_alternatives)!=len(alternatives):missing.append('Some unresolved alternative evidence cannot fit the display budget.')
    claims=[_claim(p) for p in shown]
    for part,status in enumerate(statuses):
        hashes = set(status['evidence_proof_sha256'])
        status['evidence_claim_indices'] = [i for i, claim in enumerate(claims) if claim['proof_sha256'] in hashes]
        unadmitted=sum(1 for row in admission.blocked
            if row['role'].startswith('native_rule_candidates_for_question_parts:')
            and str(part) in row['role'].split(':',1)[1].split(','))
        status['unadmitted_witness_candidate_count']=unadmitted
        status['undisplayed_evidence_count'] = len(hashes)-len(status['evidence_claim_indices'])+unadmitted
        status['unadmitted_candidates_verified']=False
    all_supported=bool(claims) and not missing and all(g['status']=='supported_source_assertion' for g in statuses)
    kind='conflict' if conflict else 'clarify' if ambiguous else 'supported_answer' if all_supported else 'partial_answer' if claims else 'abstain'
    text='\n'.join(c['text']+' '+ ' '.join(c['qualifiers']) for c in claims)
    if conflict:text='The sources make opposed assertions; event co-reference and a historical contradiction are not established.\n'+text
    if missing:text+=('\nUnresolved: '+'; '.join(missing))
    sources=[]
    for c in claims:
        for e in c['citations']:
            s={'id':e['source_id'],'path':e['path'],'hash':e['hash']}
            if s not in sources:sources.append(s)
    return {'kind':kind,'code':'contradictory_passages_pruned' if admission.counter_did_not_fit and conflict else 'reader_budget_exceeded' if admission.counter_did_not_fit or admission.blocked and not all_supported else 'documentary_statement_conflict' if conflict else 'documentary_scope_ambiguous' if ambiguous else 'supported_documentary_assertion' if all_supported else 'partial_documentary_evidence' if claims else 'documentary_assertion_not_established',
            'text':text,'claims':claims,'sources':sources,'missing':missing,'answer_supported':all_supported,
            'verification':{'structural':bool(claims),'semantic':kernel.VERSION,'truth_verified':False,'independence_verified':False},
            'documentary_support':{'schema':VERSION,'original_question':index.question,'profile':index.profile.name,
                'obligations':statuses,'source_support_claims':len(claims),'historical_truth_independently_verified':False,
                'admission':admission.report(),
                'composition_rule':'Conjunction of independently checked source assertions; no person/event co-reference inferred.',
                'historical_conflict_verified':False,'event_coreference_established':False,
                'contrary_evidence_scan_complete':checked['scan_complete'] and not request_scope,
                'scan_scope':'Finite literal action assertions; request occurrence/correction/execution not certified.',
                'examined_characters':checked['examined_characters'],'examined_units':checked['examined_units'],'limits_reached':checked['limits_reached'],
                'limits':checked['limits'],'rejected_proposals':checked['rejected'],
                'context_limits':context_limits,
                'comparison_completion_scope':closures[0]['proposition'].get('reference_scope') if comparison_completion else None,
                'question_completion_scope':closures[0]['proposition'].get('reference_scope') if literal_completion else None,
                'alternative_evidence':displayed_alternatives,'unshown_alternative_evidence_count':len(alternatives)-len(displayed_alternatives),
                'retrieval_limits':{'max_passages':max_passages,'max_characters':max_chars}}}
