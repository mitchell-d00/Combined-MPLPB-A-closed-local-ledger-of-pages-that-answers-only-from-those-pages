"""Bounded, quote-linked propositions from ordinary prose; no semantic proof.

These rules propose actor/action/object, scope and modality. They do not certify
historical truth or resolve identity by vocabulary overlap. Every result retains
its complete source sentence and an explicit candidate status.
"""
import difflib
import re
from collections import Counter
from html.parser import HTMLParser
from html import escape
from mplpb_answers.body_text import body_text
from mplpb_answers.prose_retrieval import metadata
from mplpb_combined.reader import terms
from .source_mapping import anchor,_item as _source_item


def _item(*args,**kwargs):
    return _source_item(*args,operation='finite-prose-interpretation-v5',**kwargs)

VERSION='source-propositions-v5'
VERBS={
 'called off':'cancel','call off':'cancel','cancelled':'cancel','canceled':'cancel','cancel':'cancel',
 'responded':'respond','respond':'respond',
 'appoint':'appoint','appointed':'appoint','decided':'decide','decide':'decide','proceed':'proceed',
 'wrote':'write','write':'write','written':'write','scribbled':'write','drafting':'draft','drafted':'draft',
 'distributed':'distribute','published':'publish','publishing':'publish','read':'read',
 'told':'tell','instructed':'instruct','ordered':'order','order':'order','designate':'designate',
 'sent':'send','send':'send','sending':'send','received':'receive','receive':'receive',
 'surveyed':'survey','provided':'provide','provide':'provide','lobbied':'lobby','supported':'support',
 'correcting':'correct','corrected':'correct','correct':'correct','reconsidered':'reconsider',
 'retracted':'retract','retract':'retract','withdrawn':'withdraw','withdrew':'withdraw',
 'revised':'revise','amended':'amend','denied':'deny','disagreed':'disagree',
 'repealed':'repeal','repeal':'repeal','prohibited':'prohibit','prohibit':'prohibit',
 'issued':'issue','containing':'quote_or_contain','quote':'quote','quoted':'quote',
 'grant':'grant','allowed':'allow','authorized':'authorize','aborted':'abort',
 'defended':'defend','surrendered':'surrender','evacuated':'evacuate','marched':'march',
 'failed':'fail','fail':'fail','caused':'cause','cause':'cause',
}
ACTION=re.compile(r'\b('+'|'.join(re.escape(v).replace(r'\ ',r'\s+') for v in sorted(VERBS,key=len,reverse=True))+r')\b',re.I)
LETTER=re.compile(r"(?m)^([A-Z][A-Z .’'\-]{2,70}?)\s+TO\s+([A-Z][A-Z .’'\-]{2,70}?)(?=\.\s+[A-Z][a-z]|\.\s*\n|\s*\n)")
NAMES=re.compile(r"\b(?:[A-Z][a-z]+(?:[’'][a-z]+)?(?:\s+(?:[A-Z]\.\s*)?[A-Z][a-z]+){0,2}|I|[Hh]e|[Ss]he|[Tt]hey|[Ww]e|[Yy]ou)\b")
MONTH_NAMES='January|February|March|April|May|June|July|August|September|October|November|December'
DATE=re.compile(r'\b(?:\d{4}-\d{2}-\d{2}|(?:'+MONTH_NAMES+r')(?:\s+(?:\d{4}(?!\d)|\d{1,2}(?:st|nd|rd|th|d)?(?:,)?(?:\s+\[?\d{4}\]?)?))?|(?:eve|afternoon|morning)\s+of\s+[^.;!?]{1,50})(?!\w)',re.I)
BARE_MONTH=re.compile(r'(?:'+MONTH_NAMES+r')',re.I)


def date_cues(quote):
    """Calendar cues require calendar context; may/march are also ordinary words.

    No normalized event time is inferred. Full source wording stays in evidence
    even when an ambiguous lexical cue is rejected.
    """
    for match in DATE.finditer(quote):
        if BARE_MONTH.fullmatch(match[0]):
            before=quote[max(0,match.start()-70):match.start()]
            temporal=bool(re.search(r'\b(?:in|on|by|during|until|since|before|after|for|from)\s*$',before,re.I)
                          or re.search(r'\b(?:month|day|end|beginning|middle|start|close|first|second|third|last)\s+of\s*$',before,re.I))
            if not temporal:continue
        yield match

QUALIFICATION=re.compile(r'\b(?:not|never|no|if|unless|except(?:ed)?|only|all|every|may|might|could|should|shall|will|possible|hope|intended|discretion|as if|in violation|not exceeding|subject to|provided that)\b',re.I)
ABBREVIATIONS={'mr','mrs','ms','dr','prof','gen','maj','hon','st','secy','jr','sr','s','ss'}


def sentences(text):
    start=0
    for m in re.finditer(r'[.!?]["”\)\]]?\s+(?=[A-Z"\[])',text):
        prefix=text[max(0,m.start()-80):m.start()];last=re.search(r'(\w+)$',prefix)
        if last and (len(last[1])==1 or last[1].casefold() in ABBREVIATIONS):continue
        end=m.start()+1
        if end<len(text) and text[end] in '"”)]':end+=1
        if text[start:end].strip():
            a=start+len(text[start:end])-len(text[start:end].lstrip());yield a,end,text[a:end]
        start=m.end()
    if text[start:].strip():
        a=start+len(text[start:])-len(text[start:].lstrip());yield a,len(text),text[a:]


def _modality(quote,position):
    # Clause-local qualifiers are retained alongside the full sentence. A later
    # conditional clause must not turn a preceding writing event into a defeat.
    prefix=quote[:position];clause=re.split(r';|\b(?:but|and)\b',prefix,flags=re.I)[-1][-180:]
    if re.search(r'\b(?:if|should|would|might|could|were to)\b',clause,re.I):return 'conditional_or_uncertain'
    if re.search(r'\b(?:not|never|no)\b',clause,re.I):return 'negated_or_scope_limited'
    if re.search(r'\bmay\b',clause,re.I):return 'permission_or_possibility'
    if re.search(r'\b(?:will|shall|to|about to|hope|intended)\s+(?:\w+\s+){0,3}$',clause,re.I):return 'future_request_or_intention'
    return 'source_reports_action'


def _predicate(quote,match):
    """Reject common nominal/adjectival uses without asserting full POS parsing."""
    word=match[0].lower();prefix=quote[:match.start()];suffix=quote[match.end():]
    if match.start() and quote[match.start()-1] in '-‐‑':return False
    if word=='written':return bool(re.search(r'\b(?:has|have|had|was|were|is|been|be)\s*$',prefix,re.I))
    if word=='appointed' and re.match(r'\s*(?:;|,|$)',suffix):return False
    if word=='provided' and (re.search(r'\b(?:as|hereinafter|hereinbefore)\s*$',prefix,re.I) or re.match(r'\s*,?\s*that\b',suffix,re.I)):return False
    if word in {'order','cause','grant','quote'}:
        # Base forms need a grammatical cue; titles and nominal "cause of" do not.
        return bool(re.search(r'\b(?:I|we|you|they|do|did|will|shall|may|might|would|could|should|to)\s+(?:(?:also|hereby|not)\s+|in\s+his\s+discretion,?\s+)?$',prefix,re.I))
    return True


def _actor(prefix):
    # Prefer an immediately attached grammatical actor, never the nearest proper
    # noun anywhere in a long prepositional phrase.
    apposition=re.search(r"\bI,\s*([A-Z][A-Za-z .’'\-]{2,65}?),",prefix)
    if apposition:return apposition[1].strip()
    tail=re.sub(r'\b(?:have|has|had|did|do|does|will|shall|would|could|should|may|might|not|never|quickly|also|began|in his discretion)\b[, ]*',' ',prefix,flags=re.I).strip()
    tail=re.sub(r'\bto\s*$','',tail,flags=re.I).strip()
    pronoun=re.search(r'\b(I|[Hh]e|[Ss]he|[Tt]hey|[Ww]e|[Yy]ou)\s*$',tail)
    if pronoun:return pronoun[1]
    compound=re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$",tail)
    if compound:
        before=tail[:compound.start()]
        if re.search(r'\b(?:of|in|at|from|for|to)\s+(?:the\s+)?$',before,re.I):return None
        return compound[1]
    names=list(NAMES.finditer(tail))
    if names:
        name=names[-1]
        if not tail[name.end():].strip() and name[0].casefold() not in {'much','in','during','even','this','that','the','later','december','january','february','march','april','may','june','july','august','september','october','november'}:
            if re.search(r'\b(?:of|in|at|from|for|to)\s+(?:the\s+)?$',tail[:name.start()],re.I):return None
            return re.sub(r'^(?:If|When|Whenever|Unless|Although)\s+','',name[0])
    if re.search(r'\b[Ss]uch regulations\s*$',tail):return 'Such regulations'
    return None


def _non_event_ranges(record):
    """Source-marked site chrome is not an event, while original bytes remain."""
    if not re.search(r'<(?:nav|header|footer|aside|form)\b',record.body_html,re.I):return []
    class Chrome(HTMLParser):
        def __init__(self):super().__init__();self.parts=[];self.depth=0;self.ranges=[]
        def handle_starttag(self,t,attrs):
            if t in {'nav','header','footer','aside','form'}:
                if not self.depth:
                    prefix=body_text(''.join(self.parts));self.begin=len(prefix)+bool(prefix)
                self.depth+=1
            self.parts.append('<'+t+'>')
        def handle_endtag(self,t):
            self.parts.append('</'+t+'>')
            if t in {'nav','header','footer','aside','form'} and self.depth:
                self.depth-=1
                if not self.depth:self.ranges.append((self.begin,len(body_text(''.join(self.parts)))))
        def handle_data(self,t):self.parts.append(escape(t,quote=False))
    p=Chrome();p.feed(record.body_html);p.close();return p.ranges


def _sentence_index(record,text):
    if '<pre' in record.body_html.casefold():return list(sentences(text))
    # Canonical HTML block lines are already source-defined paragraph boundaries.
    result=[];offset=0;ranges=_non_event_ranges(record)
    for line in text.splitlines(keepends=True):
        for a,b,q in sentences(line.rstrip('\n')):
            if not any(lo<=offset+a<hi for lo,hi in ranges):result.append((offset+a,offset+b,q))
        offset+=len(line)
    return result


def extract(index,passages,state,*,max_propositions=48,max_connections=16):
    bodies={r.path:body_text(r.body_html) for r in index.records};meta={r.path:metadata(r) for r in index.records}
    records={r.path:r for r in index.records}
    sentence_index={path:_sentence_index(records[path],text) for path,text in bodies.items()}
    frames=[];seen=set();truncated=False;contexts=[];context_seen=set()
    for p in passages:
        text=bodies[p['path']];begin=p['body_start'];end=begin+len(p['text'])
        # A header is usable only within its documentary appearance; no global
        # I->author binding across documents or following letter boundaries.
        all_headers=list(LETTER.finditer(text))
        per_context=0
        for a,b,quote in sentence_index[p['path']]:
            if not (a<end and b>begin) or b-a>2200:continue
            e=anchor(dict(p,body_start=a,text=quote));ck=(e['path'],a,b)
            if ck not in context_seen and len(contexts)<80:contexts.append(e);context_seen.add(ck)
            relevant=[m for m in all_headers if m.start()<=a and a-m.end()<10000]
            header=relevant[-1] if relevant else None
            if header and any(m.start()>header.start() and m.start()<b for m in all_headers):header=None
            for match in ACTION.finditer(quote):
                key=(p['path'],a,match.start())
                if key in seen:continue
                if not _predicate(quote,match):continue
                if len(frames)>=max_propositions:truncated=True;break
                per_context+=1
                seen.add(key);action=VERBS[re.sub(r'\s+',' ',match[0].lower())];prefix=quote[:match.start()]
                if action=='tell':action='instruct' if re.search(r'\bto\s+(?:send|write|publish|correct|retract)\b',quote[match.end():],re.I) else 'report_speech'
                subject=_actor(prefix)
                unresolved=[];bindings=[]
                apposition=re.search(r"\bI,\s*([A-Z][A-Za-z .’'\-]{2,65}?),",prefix)
                if apposition:subject=apposition[1].strip()
                # Do not guess a person for a title, unresolved pronoun or passive.
                if subject and subject.lower() in {'i','we','you','he','she','they'}:
                    if header and subject.lower() in {'i','you'}:
                        bindings=[{'pronoun':subject,'resolved_candidate':header[1 if subject.lower()=='i' else 2],
                                   'basis':'explicit documentary AUTHOR TO RECIPIENT heading'}]
                        subject=bindings[0]['resolved_candidate']
                    else:unresolved.append('pronoun_actor_unresolved')
                object_bindings=[]
                if header and re.match(r'\s+you\b',quote[match.end():],re.I):
                    object_bindings=[{'pronoun':'you','resolved_candidate':header[2],'basis':'explicit documentary addressee heading'}]
                if re.search(r'\b(?:is|are|was|were|been|be)(?:\s+\w+){0,4}\s*$',prefix,re.I):
                    subject=None;unresolved.append('passive_agent_unresolved')
                following=quote[match.end():];object_text=following.strip()
                next_action=ACTION.search(quote,match.end())
                role_end=next_action.start() if next_action else len(quote)
                dates=[{'raw_text':m[0],'candidate_role':('creation' if action in {'write','draft'} else 'distribution' if action in {'send','distribute'} else 'action_time_unresolved') if match.end()<=m.start()<role_end else 'context_date_role_unresolved',
                        'start':a+m.start(),'end':a+m.end(),'normalized_time':None} for m in date_cues(quote)]
                evidence=[anchor(dict(p,body_start=a,text=quote))]
                if bindings or object_bindings:
                    stop=min(len(text),header.end()+200)
                    following_header=next((m.start() for m in all_headers if m.start()>header.start()),len(text))
                    stop=min(stop,following_header)
                    evidence.append(anchor(dict(p,body_start=header.start(),text=text[header.start():stop])))
                ts=meta[p['path']]['transcript_start']
                layer='unresolved' if ts is None else 'after_source_transcript_heading' if a>=ts else 'before_source_transcript_heading'
                modality=_modality(quote,match.start())
                if subject is None and modality=='source_reports_action':modality='actor_or_passive_agent_unresolved'
                frame=_item('source_proposition_candidate',evidence,
                    {'actor':subject,'action':action,'predicate_text':match[0],
                     'object_text':object_text,'affected_subject_text':prefix.strip()[-220:] if subject is None else None,'modality':modality,
                     'documentary_bindings':bindings,'object_bindings':object_bindings,'date_candidates':dates,'source_layer_hint':layer},state,
                    operation_basis='ordinary-prose actor/action/object rules; finite and fallible',
                    qualification_cues=[m[0] for m in QUALIFICATION.finditer(quote)],
                    predicate_start=a+match.start(),predicate_end=a+match.end(),
                    unresolved_actor_or_scope=unresolved,event_identity=None,conflicting_evidence=[],
                    conflict_search='Only bounded candidate contexts compared; not exhaustive')
                frames.append(frame)
    qualifications=[]
    for e in contexts:
        cues=[m[0] for m in QUALIFICATION.finditer(e['quote'])]
        if cues and len(qualifications)<12:
            qualifications.append(_item('scope_or_modality_candidate',[e],{'literal_qualifiers':cues},state,
                operation_basis='explicit qualification language; scope requires review',scope_resolved=False))
    connections=[]
    for i,left in enumerate(frames):
        lv=left['value'];le=left['evidence'][0]
        for right in frames[i+1:]:
            rv=right['value'];re_=right['evidence'][0]
            if le['path']==re_['path'] and le['body_start']==re_['body_start']:
                bridge=le['quote'][left['predicate_end']-le['body_start']:right['predicate_start']-le['body_start']]
                clause=le['quote'][le['quote'].rfind(',',0,left['predicate_start']-le['body_start'])+1:right['predicate_start']-le['body_start']]
                if lv['actor'] and rv['actor'] is None and lv['action']=='respond' and rv['action']=='issue' and re.search(r'\band\s*$',bridge,re.I) and not re.search(r'\b(?:that|which|who|whether|if|unless)\b',clause,re.I):
                    connections.append(_item('possible_coordinated_actor',[le],{'prior_action_proposition':left['mapping_id'],'following_action_proposition':right['mapping_id'],'actor_candidate':lv['actor']},state,operation_basis='same-clause respond-and-issue with no intervening subject or relative marker; candidate only',identity_verified=False,direction='shared_actor_candidate',causality='NOT ESTABLISHED'))
                if lv['action']=='decide' and rv['action']=='proceed' and left['predicate_start']<right['predicate_start'] and re.search(r'\bto\s+proceed\b',le['quote'],re.I):
                    connections.append(_item('planned_action_candidate',[le],{'decision_proposition':left['mapping_id'],'planned_action_proposition':right['mapping_id'],'actor_candidate':lv['actor']},state,operation_basis='explicit decision with to-proceed complement; plan is not completion',action_completed=False,direction='decision_to_planned_action',causality='NOT ESTABLISHED'))
                if lv['action']=='instruct' and rv['action']=='send' and left['predicate_start']<right['predicate_start']:
                    connections.append(_item('reported_request_candidate',[le],{'request_proposition':left['mapping_id'],'requested_action_proposition':right['mapping_id']},state,
                        operation_basis='instruction and nested send action in the same quoted sentence; not completion',requested_action_completed=False,direction='request_to_requested_action',causality='NOT ESTABLISHED'))
                continue
            kind=None;basis=None
            # Exact candidate actor/action/object agreement with opposite polarity
            # is narrower than a vocabulary-similarity contradiction detector.
            la,ra=lv['actor'],rv['actor'];lo=terms(lv['object_text']);ro=terms(rv['object_text'])
            same_actor=la and ra and la.casefold()==ra.casefold() and la.lower() not in {'i','we','you','he','she','they'}
            if same_actor and lv['action']==rv['action'] and lo and lo==ro and (lv['modality']=='negated_or_scope_limited')!=(rv['modality']=='negated_or_scope_limited'):
                kind='possible_statement_conflict';basis='same candidate actor/predicate/object; opposite local polarity'
            elif lv['action'] in {'correct','reconsider','retract','revise','amend'} or rv['action'] in {'correct','reconsider','retract','revise','amend'}:
                if same_actor and len(lo&ro)>=3:
                    kind='possible_correction_link';basis='explicit correction action with candidate actor and shared object terms; scope unresolved'
            if kind:
                connections.append(_item(kind,[le,re_],{'left_proposition':left['mapping_id'],'right_proposition':right['mapping_id']},state,
                    operation_basis=basis,direction=None,causality='NOT ESTABLISHED',predecessor_resolved=False))
    # A bounded same-paragraph antecedent proposal is exposed separately; it
    # does not silently replace the unresolved pronoun in the proposition.
    ordered=sorted(frames,key=lambda f:(f['evidence'][0]['path'],f['predicate_start']))
    for n,current in enumerate(ordered):
        cv=current['value'];ce=current['evidence'][0]
        if str(cv['actor']).casefold() not in {'he','she'}:continue
        prior=[f for f in ordered[:n] if f['evidence'][0]['path']==ce['path']
               and ce['body_start']-f['evidence'][0]['body_start'] in range(1,1001)
               and f['value']['actor'] and str(f['value']['actor']).casefold() not in {'i','we','he','she','they','you'}
               and '\n' not in bodies[ce['path']][f['evidence'][0]['body_start']:ce['body_start']]]
        if prior:
            antecedent=prior[-1]
            connections.append(_item('possible_pronoun_antecedent',[antecedent['evidence'][0],ce],
                {'pronoun_proposition':current['mapping_id'],'antecedent_proposition':antecedent['mapping_id'],'actor_candidate':antecedent['value']['actor']},state,
                operation_basis='nearest explicit acting subject in the same paragraph within 1000 characters; ambiguity remains',
                identity_verified=False,direction='candidate_actor_to_unresolved_pronoun',causality='NOT ESTABLISHED'))
    # A parallel wording candidate connects explicit shared wording, not events.
    compare_wording=bool(terms(index.question)&terms('wording compare correction revise reconsider retract changed difference contradiction'))
    for i,left in enumerate(contexts) if compare_wording else []:
        for right in contexts[i+1:]:
            if left['path']==right['path']:continue
            a=left['quote'];b=right['quote'];wa=re.findall(r'\w+',a.casefold());wb=re.findall(r'\w+',b.casefold())
            grams=lambda w:{tuple(w[n:n+4]) for n in range(len(w)-3)}
            if len(grams(wa)&grams(wb))<2:continue
            similarity=difflib.SequenceMatcher(None,wa,wb,autojunk=False).ratio()
            if similarity<.45 or a==b:continue
            connections.append(_item('parallel_wording_candidate',[left,right],{'token_similarity':similarity,
                'left_only_words':sorted(set(wa)-set(wb)),'right_only_words':sorted(set(wb)-set(wa))},state,
                operation_basis='shared literal four-word sequences and token alignment; not a verified correction',
                direction=None,causality='NOT ESTABLISHED',predecessor_resolved=False))
    return {'schema':VERSION,'propositions':frames,'qualifications':qualifications,'connections':connections[:max_connections],
        'answer_supported':False,'content_truth_verified':False,
        'semantic_verification':'NOT RUN','budget_truncated':truncated or len(connections)>max_connections,
        'limits':{'max_propositions':max_propositions,'max_connections':max_connections,'max_sentence_characters':2200},
        'notice':'Actor, object, modality, date role and connections are candidate interpretations; inspect full evidence and unresolved bindings.'}
