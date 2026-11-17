"""Small proof checker for explicitly attributed documentary assertions.

Accepts source coordinates, not extractor votes or inferred graph edges. Reloads
eligibility under the complete question and derives roles from complete source
units itself. Support concerns a source assertion, never historical truth.
"""
import re
import html
from html.parser import HTMLParser
from .body_text import body_text, VERSION as BODY_VERSION
from .passages import PassageIndex

VERSION = 'documentary-assertion-kernel-v2'
PAST = {'appointed':'appoint','sent':'send','received':'receive','wrote':'write',
        'surveyed':'survey','published':'publish','revised':'revise','canceled':'cancel',
         'ordered':'order','requested':'request','instructed':'instruct'}
BASE = {v:k for k,v in PAST.items()}
META = re.compile(r'\b(?:fictional|hypothetical|example|suppose|quotation|alleged)\b',re.I)
NAME = re.compile(r"[A-Z][A-Za-z’'\-]*(?:\.(?=\s|$))?(?:\s+[A-Z][A-Za-z’'\-]*\.?){0,7}")
DATE = re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th|d)?[,]?\s+\d{4}\b')


def context_ranges(record):
    """Conservatively exclude quotation/chrome and qualified heading scopes.

    Position through the unchanged canonical projection. A page containing a
    navigation menu is not thereby wholly unavailable as documentary evidence.
    """
    class Context(HTMLParser):
        def __init__(self):super().__init__();self.parts=[];self.stack=[];self.ranges=[];self.headings=[];self.heading=None
        def position(self):return len(body_text(''.join(self.parts)))
        def handle_starttag(self,tag,attrs):
            if tag in {'blockquote','q','nav','header','footer','aside','form'}:self.stack.append((tag,self.position()))
            if re.fullmatch('h[1-6]',tag):self.heading=[self.position(),int(tag[1]),[]]
            self.parts.append('<'+tag+'>')
        def handle_endtag(self,tag):
            self.parts.append('</'+tag+'>')
            if self.stack and tag==self.stack[-1][0]:
                _,start=self.stack.pop();self.ranges.append((start,self.position()+1))
            if self.heading and tag=='h'+str(self.heading[1]):
                self.headings.append((self.heading[0],self.heading[1],''.join(self.heading[2])));self.heading=None
        def handle_data(self,value):
            self.parts.append(html.escape(value,quote=False))
            if self.heading:self.heading[2].append(value)
    parser=Context();parser.feed(record.body_html);parser.close();full=body_text(record.body_html)
    if body_text(''.join(parser.parts))!=full:return [(0,len(full)+1)]
    for _,start in parser.stack:parser.ranges.append((start,len(full)+1))
    for i,(start,level,heading) in enumerate(parser.headings):
        if META.search(heading) or re.search(r'\b(?:if|unless|conditional|plans?|planned|planning|proposals?|proposed|draft|scenario|forecast|prediction|hypothesis|intention|intended)\b',heading,re.I):
            end=next((a for a,l,_ in parser.headings[i+1:] if l<=level),len(full)+1)
            parser.ranges.append((start,end))
    return parser.ranges


def normalized(text):
    return re.sub(r'\s+',' ',text).strip().casefold().rstrip('.')


def quoted_context(prefix):
    """Distinguish quotation delimiters from contractions/plural possessives."""
    single=double=uncertain=False
    for match in re.finditer(r'''['"‘’“”]''',prefix):
        i=match.start();c=match[0];before=prefix[i-1] if i else '';after=prefix[i+1] if i+1<len(prefix) else ''
        if c in {"'",'’'} and before.isalnum() and after.isalnum():continue
        if c=='“':uncertain|=double;double=True
        elif c=='”':uncertain|=not double;double=False
        elif c=='"':double=not double
        elif c=='‘':uncertain|=single;single=True
        elif single:single=False
        elif before in {'s','S'} and not after.isalnum():continue
        elif c=="'" and not before.isalnum() and after.isalnum():single=True
        else:uncertain=True
    return single or double or uncertain


def units(body):
    """Re-derive complete boundaries from native canonical source text."""
    from .source_units import statement_units
    yield from statement_units(body)


def action_assertion(quote):
    """Typed SVO semantics for a deliberately small, closed clause grammar."""
    clean=re.sub(r'\s+',' ',quote).strip()
    if not clean.endswith('.') or any(c in clean for c in '\"“”!?;'):return None
    clean=clean[:-1];temporal=''
    if ',' in clean:
        prefix,tail=clean.split(',',1)
        if not re.match(r'^(?:Shortly after|After|Before|On|In)\b',prefix):return None
        if re.search(r'\b(?:if|unless|not|never|would|could|might)\b',prefix,re.I):return None
        temporal=prefix;clean=tail.strip()
    if ',' in clean:return None
    tokens=clean.split();found=[]
    for i,word in enumerate(tokens):
        if word in PAST:found.append((i,PAST[word],False))
        elif word in BASE and i>=2 and tokens[i-2:i]==['did','not']:found.append((i,word,True))
    if len(found)!=1:return None
    i,action,negative=found[0];actor=' '.join(tokens[:i-2 if negative else i]);obj=' '.join(tokens[i+1:])
    if (not NAME.fullmatch(actor) or normalized(actor) in {'he','she','they','we','i','you','it'}
        or set(normalized(actor).split()) & {'if','unless','not','no','never','only','neither','maybe','perhaps','allegedly','reportedly','apparently','possibly','hypothetically'}
        or normalized(actor).split()[0] in {'yesterday','today','tomorrow','later','earlier','then','now','also','instead','next','once','still','again','first','second','indeed','thereupon','beforehand','forthwith'}
        or normalized(actor).split()[0].endswith('ly')):return None
    if not obj or len(obj)>220:return None
    if re.search(r'\b(?:and|or|if|unless|when|because|not|never|may|might|could|would|should|alleged|reported|claimed|allegedly|apparently|perhaps|probably|possibly|reportedly|supposedly|intended|planned|requested|permitted)\b',obj,re.I):return None
    if any(c in obj for c in '():'):return None
    unresolved=bool(re.search(r'\b(?:that|this|it|him|her|them|those|these|dated|pending|except|only|provided)\b|\bsubject to\b',obj,re.I))
    return {'relation':'source_action_assertion','actor_text':actor,'action':action,
            'object_text':obj,'negative':negative,'temporal_qualification_text':temporal,
            'unresolved_reference':unresolved,'assertion_modality':'qualified_or_referential_unresolved' if unresolved else 'unconditional_source_assertion',
            'event_identity':None}


def letter_assertion(body,start,end):
    """An original heading + unquoted first-person opening supplies all bindings.

    Reject quoted/conditional openings; never bind I/you across another letter.
    The heading date is not a sending, receipt or action date.
    """
    if start and body[start-1]!='\n':return None
    line_end=body.find('\n',start)
    if line_end<0:return None
    line=body[start:line_end]
    if ' TO ' not in line or len(line)>240:return None
    writer,right=line.split(' TO ',1)
    if not re.fullmatch(r"[A-Z][A-Z .’'\-]{2,70}",writer):return None
    separator=re.search(r'\.\s+(?=[A-Z][a-z])',right)
    if separator:
        addressee=right[:separator.start()].strip();dateline=right[separator.end():]
    else:addressee=right.rstrip('.');dateline=''
    if not re.fullmatch(r"[A-Z][A-Z .’'\-]{2,70}",addressee):return None
    cursor=line_end+1;greeting=None
    for _ in range(3):
        stop=body.find('\n',cursor)
        if stop<0:return None
        text=body[cursor:stop]
        if re.fullmatch(r'(?:My dear|Dear) [^,\n]{1,70},|Sir,|Madam,',text):greeting=stop+1;break
        if not DATE.search(text) or len(text)>120:return None
        dateline+=' '+text;cursor=stop+1
    if greeting is None or end-start>1400:return None
    first=next(units(body[greeting:min(len(body),greeting+1400)]),None)
    if not first or greeting+first[1]!=end:return None
    quote=body[greeting:end];note=''
    following=re.fullmatch(r'([\s\S]+?\.)\s+(\([^()]{1,300}\))',quote)
    if following:
        quote,note=following.groups()
        if re.search(r'\b(?:if|unless|not|no|never|only|above|foregoing|statement|request|instruction|joke|joking|fiction|fictional|send|sent|post|deliver|forward|told|asked|instructed|requested|ordered|canceled|withdrawn)\b',note,re.I):return None
    clean=re.sub(r'\s+',' ',quote[:-1])
    if any(c in clean for c in '\"“”') or not quote.endswith('.'):return None
    main,*hope=clean.split(', and I hope ',1)
    prefix=re.match(r'I (have )?(told|asked|instructed|requested|ordered) (.+?) to (send|deliver|forward|post) (.+)$',main)
    if not prefix:return None
    intermediary=prefix[3];obj=prefix[5]
    if not NAME.fullmatch(intermediary):return None
    conditions=re.findall(r'\((if possible|if practicable|when possible)\)',obj)
    if len(conditions)>1:return None
    condition=conditions[0] if conditions else ''
    obj=re.sub(r'\((?:if possible|if practicable|when possible)\)',' ',obj);obj=re.sub(r'\s+',' ',obj).strip()
    if obj.startswith('you '):obj=obj[4:]
    elif obj.endswith(' to you'):obj=obj[:-7]
    else:return None  # Never infer that a named or omitted recipient is you.
    delivery=''
    route=re.match(r'(by (?:post|mail|courier)) (.+)$',obj)
    tail=re.fullmatch(r'(.+) (by (?:post|mail|courier))',obj)
    if route:delivery,obj=route[1],route[2]
    elif tail:obj,delivery=tail[1],tail[2]
    if not re.fullmatch(r'(?:a copy of my|my|the|a|an) [A-Za-z][A-Za-z0-9 ’\'\-]{0,100}',obj):return None
    if re.search(r'\b(?:if|unless|not|never|and|or|may|might|would|should|shall|will|canceled|withdrawn|retracted)\b',obj):return None
    if hope and (len(hope[0])>180 or re.search(r'\b(?:if|unless|not|never|and I)\b',hope[0])):return None
    if META.search(body[max(0,start-180):start]):return None
    date=DATE.findall(dateline)
    if len(date)>1:return None
    return {'relation':'source_reports_instruction','writer_text':writer,'addressee_text':addressee,
            'intermediary_text':intermediary,'request_verb':prefix[2],'request_aspect':'perfect' if prefix[1] else 'past',
            'requested_action':prefix[4],'object_text':obj,
            'object_owner_text':writer if obj.startswith(('my ','a copy of my ')) else None,'requested_recipient_text':addressee,
            'condition_text':condition,'condition_scope':'literal_clause_context_unresolved' if condition else None,
            'delivery_text':delivery,'hope_text':'I hope '+hope[0] if hope else '','literal_following_note':note,
            'heading_date_text':date[0] if date else None,'date_role':'letter_heading_date_role_unresolved',
            'instruction_event_truth_verified':False,'dispatch_verified':False,'receipt_verified':False,
            'event_identity':None,'header_end':line_end,'statement_start':greeting}


def citation(record,body,a,b):
    return {'source_id':record.id,'path':record.path,'hash':record.hash_actual,
            'body_start':a,'body_end':b,'start':a,'end':b,'quote':body[a:b],'body_projection':BODY_VERSION}


def check(index,proposals,*,max_scan_chars=200000):
    """Reload and certify only explicit source assertions, not historical events."""
    if type(max_scan_chars) is not int or not 1000<=max_scan_chars<=1000000:raise ValueError('Invalid assertion scan budget')
    fresh=PassageIndex(index.root,index.question,index.profile)
    records={r.path:r for r in fresh.records};bodies={p:body_text(r.body_html) for p,r in records.items()}
    regions={p:context_ranges(r) for p,r in records.items()}
    certified=[];rejected=[];scanned=[];contexts=[];used=0;complete=True;limits_reached=set()
    for path,record in records.items():
        body=bodies[path];remaining=max_scan_chars-used;limit=min(len(body),max(0,remaining))
        used+=limit
        if limit<len(body):complete=False;limits_reached.add('source_characters')
        prefix=body[:limit]
        # A cut unit is never inspected as a complete contradictory statement.
        for a,b,q in units(prefix):
            if limit<len(body) and b==limit:continue
            if len(contexts)>=1000:complete=False;limits_reached.add('source_units');break
            value=action_assertion(q)
            prior=body[:a]
            safe=(not any(lo<b and hi>a for lo,hi in regions[path]) and not quoted_context(prior) and not META.search(prior)
                  and not re.search(r'\b(?:if|unless)\b',prior[-180:],re.I)
                  and not re.search(r'\b(?:the|a) (?:plan|proposal|scenario|draft|forecast|prediction|hypothesis) (?:was|is|reads|follows|stated)\b',prior[-240:],re.I)
                  and not re.search(r'(?:^|\n)\s*(?:plan|proposal|draft|scenario|forecast|prediction|hypothesis)[.:]?\s*$',prior[-240:],re.I))
            contexts.append((record,a,b,q,value if safe else None))
            if value and safe:
                if len(scanned)>=64:complete=False;limits_reached.add('source_assertions');continue
                scanned.append((record,a,b,value))
    for proposal in proposals[:12]:
        record=records.get(proposal.get('path'));a=proposal.get('start');b=proposal.get('end')
        if (not record or record.id!=proposal.get('source_id') or record.hash_actual!=proposal.get('hash')
            or record.fields.get('corrects-field') or type(a) is not int or type(b) is not int
            or not 0<=a<b<=len(bodies[record.path]) or b-a>2200
            or bodies[record.path][a:b]!=proposal.get('quote')):
            rejected.append('source_or_scope_changed');continue
        body=bodies[record.path];kind=proposal.get('kind');value=None;citations=[]
        if kind=='letter_instruction':
            value=letter_assertion(body,a,b) if not any(lo<b and hi>a for lo,hi in regions[record.path]) else None
            if value:
                h=value.pop('header_end');s=value.pop('statement_start')
                citations=[citation(record,body,a,h),citation(record,body,s,b)]
        elif kind in {'relationship_statement','wording_comparison'}:
            # Re-read complete native units; an exact substring alone cannot
            # hide a leading negation, attribution or conditional governor.
            from .source_units import comparison_units
            native=comparison_units(record) if kind=='wording_comparison' else units(body)
            unit=next(((lo,hi,q) for lo,hi,q in native if (lo,hi)==(a,b)),None)
            def safe_unit(record,a,b,body):
                prior=body[:a]
                return (not record.fields.get('corrects-field')
                    and not any(lo<b and hi>a for lo,hi in regions[record.path])
                    and not quoted_context(prior) and not META.search(prior)
                    and not re.search(r'\b(?:if|unless)\b',prior[-180:],re.I)
                    and not re.search(r'\b(?:the|a) (?:plan|proposal|scenario|draft|forecast|prediction|hypothesis) (?:was|is|reads|follows|stated)\b',prior[-240:],re.I)
                    and not re.search(r'(?:^|\n)\s*(?:plan|proposal|draft|scenario|forecast|prediction|hypothesis)[.:]?\s*$',prior[-240:],re.I))
            if unit and (kind=='wording_comparison' or safe_unit(record,a,b,body)):
                if kind=='relationship_statement':
                    value=relationship_assertion(unit[2])
                    if value:citations=[citation(record,body,a,b)]
                else:
                    other=proposal.get('other',{});r=records.get(other.get('path'));lo=other.get('start');hi=other.get('end')
                    if (r and r.path!=record.path and r.id==other.get('source_id') and r.hash_actual==other.get('hash')
                        and type(lo) is int and type(hi) is int and 0<=lo<hi<=len(bodies[r.path]) and hi-lo<=2200
                        and bodies[r.path][lo:hi]==other.get('quote') and not r.fields.get('corrects-field')
                        and any((x,y)==(lo,hi) for x,y,_ in comparison_units(r))):
                        value=wording_difference(unit[2],bodies[r.path][lo:hi])
                        if value:citations=[citation(record,body,a,b),citation(r,bodies[r.path],lo,hi)]
        elif kind=='action_statement':
            matches=[v for r,lo,hi,v in scanned if r.path==record.path and (lo,hi)==(a,b)]
            if len(matches)==1:
                value=matches[0];citations=[citation(record,body,a,b)]
        if value is None:rejected.append('assertion_grammar_or_context_unresolved');continue
        certified.append({'proposition':value,'citations':citations,'source_support_established':True,
            'support_scope':'source_attributed_assertion','verification':VERSION,
            'historical_truth_independently_verified':False})
    if not fresh.unchanged() or not index.unchanged():
        return {'proofs':[],'status':'source_changed','scan_complete':False,'rejected':[],'scanned':[],'examined_characters':used}
    observations=[{'proposition':v,'citations':[citation(r,bodies[r.path],a,b)],
                   'source_support_established':True,'support_scope':'source_attributed_assertion',
                   'verification':VERSION,'historical_truth_independently_verified':False} for r,a,b,v in scanned]
    return {'proofs':certified,'status':'checked','scan_complete':complete,'rejected':rejected,
            'observations':observations,'contexts':contexts,'examined_characters':used,
            'examined_units':len(contexts),'limits_reached':sorted(limits_reached),
            'limits':{'max_proposals':12,'max_scan_characters':max_scan_chars,'max_units':1000,'max_assertions':64}}


def relationship_assertion(quote):
    """Finite literal causal/order/resource/passive assertions, not event truth.

    All arguments are retained verbatim, including appositions and time phrases.
    A cause explicitly attributed by a source is not an independently true cause.
    """
    clean=re.sub(r'\s+',' ',quote).strip()
    if not clean.endswith('.') or len(clean)>1800 or any(c in clean for c in '\"“”!?;'):return None
    if re.search(r'\b(?:if|unless|would|could|might|allegedly|reportedly|perhaps|supposedly|claimed|denied|hypothetical)\b',clean,re.I):return None
    value=None
    causal=re.fullmatch(r'((?:The|A|An) [A-Za-z0-9][A-Za-z0-9 ,’\'()\-]{1,350}?) was (not )?(aborted|cancelled|canceled|delayed|postponed|halted|withdrawn|terminated) because of ([^.;:]{2,1000})\.',clean)
    if causal:
        subject,neg,action,cause=causal.groups()
        # Apposition describes the intended goal; never read planned action as
        # execution. Other commas/relative clauses are outside this proof rule.
        if ',' in subject and not re.fullmatch(r'[^,]+, planned as [^,]+,',subject):return None
        value={'relation':'source_causal_assertion','subject_text':subject,'action_text':action,
               'cause_text':cause,'negative':bool(neg),'causal_basis':'literal because-of assertion',
               'date_role':'event_relative_or_elapsed_expression_unresolved'}
    resource=re.fullmatch(r'((?:The|A|An) [A-Za-z][A-Za-z0-9 ’\'\-]{1,100}?) provided ([^.;:]{2,500}?) (for|to) ([^.;:]{2,500})\.',clean)
    if resource:
        subject,obj,prep,purpose=resource.groups()
        if any(re.search(r'\b(?:and|or|not|never|planned|intended|requested|only|except)\b',s,re.I) for s in (subject,obj)):return None
        value={'relation':'source_resource_assertion','resource_text':subject,'provided_text':obj,
               'purpose_preposition':prep,'purpose_text':purpose,'negative':False}
    temporal=re.fullmatch(r'(.{2,160}?) (occurred|was completed|was published|was revised|was received) (before|after) (.{2,160}?)\.',clean)
    if temporal and ',' not in clean:
        left,action,order,right=temporal.groups()
        if not re.search(r'\b(?:and|or|not|never|planned|intended|requested)\b',left+' '+right,re.I):
            value={'relation':'source_temporal_assertion','subject_text':left,'action_text':action,'ordering':order,
                   'reference_text':right,'date_role':'publication' if action=='was published' else 'revision' if action=='was revised' else 'receipt' if action=='was received' else 'reported_event',
                   'reference_date_role':'unresolved','normalized_event_time':None,'causality_established':False,'negative':False}
    passive=re.fullmatch(r'(.{2,160}?) was (not )?(appointed|sent|received|surveyed|published|revised|canceled) by (.{2,100})\.',clean)
    if passive:
        obj,neg,action,actor=passive.groups()
        if NAME.fullmatch(actor) and not re.search(r'\b(?:he|she|they|it|if|unless|and|or|not)\b',actor+' '+obj,re.I):
            value={'relation':'source_passive_action_assertion','actor_text':actor,'action':PAST[action],
                   'object_text':obj,'negative':bool(neg),'unresolved_reference':bool(re.search(r'\b(?:this|that|him|her|it|them)\b',obj,re.I))}
    if value is not None:
        value.update(assertion_modality='source_attributed_assertion',event_identity=None,
                     historical_truth_independently_verified=False)
    return value


def wording_difference(left,right):
    """Exact token alignment only; never inferred correction, motive or absence."""
    import difflib
    a=list(re.finditer(r'\S+',left));b=list(re.finditer(r'\S+',right))
    if max(len(a),len(b))>600:return None
    changes=[]
    for op,i,j,k,l in difflib.SequenceMatcher(None,[m[0] for m in a],[m[0] for m in b],autojunk=False).get_opcodes():
        changes.append({'operation':op,'left_text':left[a[i].start():a[j-1].end()] if i<j else '',
                        'right_text':right[b[k].start():b[l-1].end()] if k<l else '',
                        'left_relative_start':a[i].start() if i<len(a) else len(left),
                        'right_relative_start':b[k].start() if k<len(b) else len(right)})
    return {'relation':'exact_wording_comparison','alignment':changes,'comparison_scope':'two complete cited source units only',
            'whole_document_absence_established':False,'correction_relationship_established':False,
            'version_order_established':False,'event_identity':None,
            'historical_truth_independently_verified':False}


def check_source_identity(index,left,right):
    """Check ledger appearance/content identity; never person/event identity."""
    fresh=PassageIndex(index.root,index.question,index.profile);records={r.path:r for r in fresh.records};chosen=[]
    for anchor in (left,right):
        record=records.get(anchor.get('path'))
        if not record or record.id!=anchor.get('source_id') or record.hash_actual!=anchor.get('hash'):
            return {'status':'ineligible_or_changed','source_identity_established':False,'historical_truth_independently_verified':False}
        chosen.append(record)
    a,b=chosen
    if not fresh.unchanged() or not index.unchanged():return {'status':'source_changed','source_identity_established':False,'historical_truth_independently_verified':False}
    return {'status':'checked_current_source_identity','sources':[{'source_id':r.id,'path':r.path,'hash':r.hash_actual} for r in chosen],
            'same_ledger_occurrence':a.path==b.path and a.hash_actual==b.hash_actual,
            'same_sealed_hash':a.hash_actual==b.hash_actual,'same_canonical_body':body_text(a.body_html)==body_text(b.body_html),
            'source_identity_established':a.path==b.path and a.hash_actual==b.hash_actual,
            'same_original_bytes':None,'authorship_authenticated':False,'event_identity_established':False,
            'independent_corroboration_established':False,'historical_truth_independently_verified':False,
            'notice':'Canonical equality is not original-byte equality. Use pinned raw captures/import round trips for original bytes.'}
