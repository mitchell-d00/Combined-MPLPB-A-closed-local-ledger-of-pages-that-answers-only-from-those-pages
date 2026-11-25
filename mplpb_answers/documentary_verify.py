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

VERSION = 'documentary-assertion-kernel-v11'
PAST = {'appointed':'appoint','sent':'send','received':'receive','wrote':'write',
        'surveyed':'survey','published':'publish','revised':'revise','canceled':'cancel',
         'ordered':'order','requested':'request','instructed':'instruct'}
BASE = {v:k for k,v in PAST.items()}
PASSIVE = {form:PAST[form] for form in ('appointed','sent','received','surveyed','published','revised','canceled')}
PASSIVE['written']='write'
META = re.compile(r'\b(?:fictional|hypothetical|example|suppose|quotation|alleged)\b',re.I)
NAME = re.compile(r"[^\W\d_](?:[^\W\d_]|[’'\-])*(?:\.(?=\s|$))?(?:\s+[^\W\d_](?:[^\W\d_]|[’'\-])*\.?){0,7}")
DATE = re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th|d)?[,]?\s+\d{4}\b')
DATE_LOCATOR_CHARS = 2*1024**2
DATE_DOCUMENT_CHARS = 16000
MONTHS = ('January February March April May June July August September October November December').split()
DATE_EXPRESSION = r'(?:'+'|'.join(MONTHS)+r')\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?'
SITE_KINDS = ('fort', 'harbour', 'harbor', 'city', 'town', 'port')
DATE_ROLES = {'bombardment','surrender','evacuation','departure','arrival','publication','revision','sending','receipt','writing','catalogue','review',
              'telegram','letter','report','memorandum','dispatch'}


def date_inventory_request(question):
    """A complete, source-bounded date question; factual additions never vanish."""
    q=source_question(question).strip().rstrip('? .')
    # Documentary role labels are an inspection plan. Keep the full original
    # question on the index for policy, proof and final current-state checks.
    q=re.sub(r'\.\s+Keep unknown matters unresolved$', '', q, flags=re.I)
    paired=re.fullmatch(r'Distinguish the (reported sending date) and the (writing date) for (.{2,120})',q,re.I)
    if paired:
        subject=re.sub(r'^the\s+', '', paired[3], flags=re.I)
        if re.search(r'\b(?:and|or|if|unless|because|prove|establish|not)\b|[;:?!]',subject,re.I):return None
        return {'roles':['sending','writing'],'subject_text':subject,
                'require_unique_requested_roles':True,
                'scope':'explicit statements in one eligible source record'}
    m=re.fullmatch(r'Distinguish (?:the )?([a-z, ]{3,160}) dates in (?:the )?(.{2,120}) record'
                  r'(?:, without treating (?:the )?webpage review date as an event date)?',q,re.I)
    if m:
        role_text, subject = m.groups()
        phrases = split_date_roles(role_text)
        roles = phrases
        constraints = {}
    else:
        natural = re.fullmatch(
            r'What separate dates does (?:the )?([^,.!?;:]{2,120}?) (?:page|record) '
            r'(?:give|list|report) for ([a-z, ]{3,220})', q, re.I)
        if not natural:
            return None
        subject, role_text = natural.groups()
        if re.search(r'\b(?:only|except|before|after|first|last|according)\b', subject, re.I):
            return None
        phrases = split_date_roles(role_text)
        roles, constraints = natural_date_roles(phrases, subject)
        if len(roles) < 2:
            return None
    if not 1 <= len(roles) <= 6 or len(set(roles)) != len(roles) or not set(roles) <= DATE_ROLES:
        return None
    subject = subject.strip()
    if re.search(r'\b(?:and|or|if|unless|because|caused|prove|establish|not)\b|[;:?!]', subject, re.I):
        return None
    request = {'roles':roles,'subject_text':subject,'scope':'explicit statements in one eligible source record'}
    if constraints:
        request['constraints'] = constraints
    return request


def split_date_roles(text):
    return [x.strip().lower() for x in re.split(r',\s*(?:and\s+)?|\s+and\s+', text) if x.strip()]


def natural_date_roles(phrases, subject):
    roles, constraints = [], {}
    for phrase in phrases:
        if phrase in DATE_ROLES:
            role = phrase
        elif phrase == 'opening fire':
            role = 'bombardment'
            constraints[role] = 'opened_fire'
        elif (site := re.fullmatch(r'giving up the (' + '|'.join(SITE_KINDS) + ')', phrase)) and (
                re.search(r'\b' + site[1] + r'\b', subject, re.I)):
            role = 'surrender'
            constraints[role] = 'surrendered_subject'
        elif phrase == 'leaving it' and roles[-1:] == ['surrender'] and constraints.get('surrender'):
            role = 'evacuation'
            constraints[role] = 'same_clause_evacuation'
        elif (document := re.fullmatch(
                r'the (telegram|letter|report|memorandum|dispatch) date listed in the catalog(?:ue)?', phrase)):
            role = document[1]
            constraints[role] = 'catalogue_date'
        else:
            return [], {}
        roles.append(role)
    return roles, constraints


def date_link_matches_request(link, constraint, subject):
    if not constraint:
        return True
    statement = normalized(link['statement_text'])
    if constraint == 'catalogue_date':
        return link['date_role'] == 'source_catalogue_document_date'
    if constraint == 'opened_fire':
        targets = [subject, 'the ' + subject]
        targets.extend('the ' + kind for kind in SITE_KINDS if kind in subject.split())
        return bool(re.search(r'\bopened fire on (?:' + '|'.join(map(re.escape, targets))
                              + r')(?=\s*,|$)', statement))
    surrender = bool(re.search(r'\bsurrendered (?:the )?' + re.escape(subject) + r'(?=\s*,|$)', statement))
    if constraint == 'same_clause_evacuation':
        return surrender and link['date_role'] == 'explicit_same_clause_relative_date'
    return constraint == 'surrendered_subject' and surrender


def _date_value(text):
    from datetime import date
    m=re.fullmatch(r'('+'|'.join(MONTHS)+r')\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?',text,re.I)
    if not m:return None
    month=next(i+1 for i,x in enumerate(MONTHS) if x.lower()==m[1].lower())
    year=int(m[3]) if m[3] else None
    try:date(year or 2000,month,int(m[2]))
    except ValueError:return None
    return {'month':month,'day':int(m[2]),'year':year}


def _following_day(anchor):
    from datetime import date,timedelta
    if not anchor:return None
    try:
        candidates=[date(y,anchor['month'],anchor['day'])+timedelta(days=1)
                    for y in ([anchor['year']] if anchor['year'] else [2000,2001])]
    except (ValueError,OverflowError):return None
    if len({(v.month,v.day) for v in candidates})!=1:return None
    d=candidates[0]
    return {'resolved_month_day':MONTHS[d.month-1]+' '+str(d.day),
            'year':d.year if anchor['year'] else None}


def dated_statements(quote):
    """Finite literal date/predicate links; never resolve a historical event.

    Catalogue dates are explicitly source-body catalogue statements, not proof
    of sending. Relative arithmetic is confined to a syntactically governed
    action in the same sentence. Unknown years are never borrowed from a title,
    citation, preceding paragraph or page review date.
    """
    links=[]
    def add(role,date_text,kind,statement,**extra):
        value=_date_value(date_text)
        if value is None:return
        links.append(dict(requested_role=role,date_text=date_text,date_role=kind,
                          statement_text=statement,literal_identity_context=statement,
                          event_identity=None,normalized_event_time=None,**value,**extra))
    catalogue=re.search(r'(?im)^Citation:\s*(Telegram|Letter|Report|Memorandum|Dispatch)\b[^\n;]*;\s*('+DATE_EXPRESSION+r')\s*;[^\n]*',quote)
    if catalogue and not META.search(quote[:catalogue.start()]):
        add(catalogue[1].lower(),catalogue[2],'source_catalogue_document_date',catalogue[0],
            dispatch_verified=False,receipt_verified=False,field_span=[catalogue.start(),catalogue.end()])
        add('catalogue',catalogue[2],'source_catalogue_document_date',catalogue[0],
            dispatch_verified=False,receipt_verified=False,field_span=[catalogue.start(),catalogue.end()])
    writing=re.fullmatch(r'This\s+record\s+was\s+written\s+on\s+('+DATE_EXPRESSION+r')\.',quote,re.I)
    if writing:
        add('writing',writing[1],'explicit_record_writing_date',quote,
            sending_established=False,receipt_established=False,event_occurrence_established=False)
    review=re.fullmatch(r'This page was last reviewed on ('+DATE_EXPRESSION+r')\.',quote,re.I)
    if review:
        add('webpage_review',review[1],'webpage_review',quote,support_scope='textual_occurrence')
        add('review',review[1],'webpage_review',quote,support_scope='textual_occurrence')
    m=re.fullmatch(r'(?:On |At (\d{1,2}:\d{2}\s*[ap]\.m\.),\s*)('+DATE_EXPRESSION+r'),\s*(.{2,500})\.',quote,re.I|re.S)
    if not m:return links
    time_text,date_text,predicate=m.groups(); tail=predicate
    if (re.search(r'[:;!?“”"]',predicate) or
        re.search(r'\b(?:if|unless|would|could|might|may|maybe|perhaps|alleged|allegedly|reported|reportedly|apparently|possibly|supposedly|claimed|said|denied|never|not|planned|intended|requested|only|except|almost|nearly|purportedly|suspected|believed|feared|expected|hoped|thought|imagined|suggested|seemed|uncertain|whether|plan|proposal|scenario|draft|forecast|prediction|hypothesis)\b',predicate,re.I)):return links
    predicates={'surrender':'surrendered','evacuation':'evacuated','departure':'departed','arrival':'arrived',
                'publication':'published','revision':'revised','sending':'sent','receipt':'received',
                'bombardment':'bombarded|opened fire on'}
    relative=re.fullmatch(r'(.{2,300}?), evacuating (.{2,120}) on the following day',tail,re.I)
    if relative:tail=relative[1]
    # Additional coordinated predicates cannot hide behind the object slot.
    if re.search(r'\b(?:and|or|then|before|after|because)\b',tail,re.I):return links
    for role,verb in predicates.items():
        parsed=re.fullmatch(r'(.{2,120}?)\s+('+verb+r')\s+(.{2,250})',tail,re.I|re.S)
        if not parsed:continue
        actor,action,obj=parsed.groups()
        # An actor is a literal name or one small declared collective-noun
        # phrase. Arbitrary words before a verb cannot become an actor: that
        # previously swallowed reporting clauses and near-miss adverbs.
        collective=re.fullmatch(r'(?:[Tt]he|[Aa]|[Aa]n) (?:(?:[A-Z][A-Za-z]+|coastal|naval|shore|local|federal|royal|enemy|defending|attacking|northern|southern|eastern|western) ){0,3}'
                                r'(?:batteries|artillery|cannons|guns|forces|garrison|crew|troops|committee|council|assembly|publisher|press|office|company|depot|vessel|ship|fleet|army)',actor)
        named=(named_actor(actor) and not normalized(actor).split()[0].endswith('ly') and
               not set(normalized(actor).split()) & {'i','he','she','it','they','we','you','no','none','nobody','neither','nothing'})
        if not (collective or named):continue
        if action.lower()=='opened fire on' and not re.search(r'\b(?:batteries|artillery|cannons|guns)\b',actor,re.I):continue
        if parsed:
            add(role,date_text,'source_reported_action_date',quote,time_text=time_text or '')
            if relative:
                anchor=_date_value(date_text); resolved=_following_day(anchor)
                if anchor:
                    links.append(dict(requested_role='evacuation',date_text='the following day',
                        date_role='explicit_same_clause_relative_date',statement_text=quote,literal_identity_context=quote,
                        anchor_date_text=date_text,calendar_rule='one_day_after_same_clause_anchor',
                        calendar_assumption='proleptic Gregorian arithmetic only; historical calendar not authenticated',
                        resolved_month_day=resolved['resolved_month_day'] if resolved else None,
                        year=resolved['year'] if resolved else None,event_identity=None,normalized_event_time=None,
                        calendar_resolution_complete=resolved is not None))
    return links


def date_inventory(index,record):
    """Independently locate a unique source owner and inspect all its units.

    The locator has a separate transparent bound. No eligible match is pruned
    by rank, filename or source title. Body catalogue statements are date claims
    of that source, never authenticated event or transmission evidence.
    """
    request=date_inventory_request(index.question)
    if not request or len(index.records)>64:return None
    subject=normalized(request['subject_text']); owners=[]; used=0
    subject_pattern=re.compile(r'(?<!\w)'+re.escape(subject)+r'(?!\w)')
    for r in index.records:
        body=body_text(r.body_html);used+=len(body)
        if used>DATE_LOCATOR_CHARS:return None
        if len(body)>DATE_DOCUMENT_CHARS:
            # A long source containing the literal target cannot be silently
            # skipped in favour of a shorter, more convenient owner.
            if subject_pattern.search(normalized(body)):return None
            continue
        rows=[]; regions=context_ranges(r); named_date_context=False
        for ordinal,(a,b,q) in enumerate(units(body)):
            if ordinal>=256:return None
            if subject_pattern.search(normalized(q)) and re.search(DATE_EXPRESSION,q,re.I) and not q.startswith('Source capture:'):
                named_date_context=True
            parsed=dated_statements(q)
            prior=body[:a]
            safe_values=[]
            for value in parsed:
                lo,hi=value.get('field_span',[0,len(q)]);start,end=a+lo,a+hi
                before=body[:start]
                # Catalogue fields have their own complete line boundaries;
                # unrelated navigation in a coarse sentence unit is context,
                # not the field. Review mentions are textual annotations only
                # and never supply event dates, including inside a footer.
                safe=(not r.fields.get('corrects-field') and
                      (value['requested_role']=='webpage_review' or not any(x<end and y>start for x,y in regions))
                      and not quoted_context(before) and not META.search(before) and not META.search(q)
                      and not re.search(r'\b(?:the|a) (?:plan|proposal|scenario|draft|forecast|prediction|hypothesis) (?:was|is|reads|follows|stated)\b',before,re.I)
                      and not re.search(r'(?:^|\n)\s*(?:plan|proposal|draft|scenario|forecast|prediction|hypothesis)[.:]?\s*$',before[-240:],re.I)
                      and not re.search(r'\b(?:if|unless)\b',before[-180:],re.I))
                if safe:safe_values.append(value)
            if safe_values:rows.append((a,b,q,safe_values))
        if named_date_context:
            grounded=any(subject_pattern.search(normalized(v['literal_identity_context'])) for a,b,q,vs in rows for v in vs
                         if v['requested_role']!='webpage_review')
            owners.append((r,body,rows,grounded))
    if len(owners)!=1 or owners[0][0].path!=record.path or not owners[0][3]:return None
    r,body,rows,_=owners[0];links=[];reviews=[];citations=[];unresolved=[]
    for a,b,q,values in rows:
        wanted=[v for v in values if v['requested_role'] in request['roles'] or v['requested_role']=='webpage_review']
        if wanted:
            for v in wanted:
                lo,hi=v.get('field_span',[0,b-a]);cite=citation(r,body,a+lo,a+hi)
                if cite not in citations:citations.append(cite)
                v=dict(v,evidence_citation_index=citations.index(cite))
                (reviews if v['requested_role']=='webpage_review' else links).append(v)
                if (lo,hi)!=(0,b-a):
                    context=citation(r,body,a,b)
                    if context not in citations:citations.append(context)
    for role in request['roles']:
        found=[v for v in links if v['requested_role']==role]
        if (len(found) != 1 or found[0].get('calendar_resolution_complete') is False
                or not date_link_matches_request(found[0], request.get('constraints', {}).get(role), subject)):
            unresolved.append(role)
    # Any unparsed relevant dated predicate, including negation and modality,
    # prevents a conveniently selected positive subset from completing.
    accepted={(a,b) for a,b,q,vs in rows}
    for a,b,q in units(body):
        correction=bool(re.search(r'\b(?:correction|corrected|erratum|retracted|withdrawn|superseded|amended|rescinded)\b',q,re.I))
        if (a,b) in accepted and not possible_refutation(q) and not correction:continue
        if possible_refutation(q) or correction or (re.search(DATE_EXPRESSION,q,re.I) and
            re.search(r'\b(?:surrender(?:ed)?|evacuat\w*|bombard\w*|open(?:ed)? fire|depart\w*|arriv\w*|publish\w*|revis\w*|sent|send|receiv\w*)\b',q,re.I)):
            # A demanded surrender is a different source assertion; it does
            # not certify actual surrender and is not an opposing event date.
            if re.search(r'\b(?:demanded|requested) the surrender\b',q,re.I):continue
            if possible_refutation(q) or correction or re.search(r'\b(?:surrender\w*|evacuat\w*|bombard\w*|fire|depart\w*|arriv\w*|publish\w*|revis\w*|sent|send|receiv\w*)\b',q,re.I):
                for role in request['roles']:
                    if role not in unresolved:unresolved.append(role)
                cite=citation(r,body,a,b)
                if cite not in citations:citations.append(cite)
    if not links:return None
    # A paired role-disambiguation question needs both uniquely witnessed
    # dates. Do not emit a convenient subset as the requested comparison.
    # Existing inventory forms retain their checked-partial behavior.
    if unresolved and request.get('require_unique_requested_roles'):return None
    complete=not unresolved
    value={'relation':'source_event_date_inventory','date_links':links,'review_dates':reviews,
           'subject_text':request['subject_text'],'unresolved_roles':unresolved,
           'question_obligations_verified':complete,'verified_question':index.question,
           'question_completion_rule':'explicit_source_date_relations_v1',
           'reference_scope':'Explicit source-reported date relationships in one eligible record; partial years stay unknown and catalogue dates do not prove sending.',
           'event_coreference_established':False,'causation_established':False,
           'historical_truth_independently_verified':False,
           'date_scan':{'locator_characters':used,'max_locator_characters':DATE_LOCATOR_CHARS,
                        'selected_source_characters':len(body),'max_selected_source_characters':DATE_DOCUMENT_CHARS,
                        'selected_source_fully_examined':True,'max_sources':64}}
    return {'proposition':value,'citations':citations}


def context_ranges(record, *, document_draft=False):
    """Conservatively exclude quotation/chrome and qualified heading scopes.

    Position through the unchanged canonical projection. A page containing a
    navigation menu is not thereby wholly unavailable as documentary evidence.
    """
    qualifiers=r'if|unless|conditional(?:ly)?|plans?|planned|planning|proposals?|proposed|scenarios?|forecasts?|predictions?|hypothes(?:is|es)|intentions?|intended'
    if not document_draft:qualifiers+='|draft'
    class Context(HTMLParser):
        def __init__(self):
            super().__init__();self.parts=[];self.stack=[];self.ranges=[];self.headings=[];self.heading=None
            self.pre_depth=0;self.pre_prefix='';self.pre_start=None;self.pre_finished=False
        def position(self):return len(body_text(''.join(self.parts)))
        def handle_starttag(self,tag,attrs):
            if tag=='pre':
                if self.pre_start is None:self.pre_start=self.position()
                self.pre_depth+=1
            hint=' '.join(value or '' for key,value in attrs if key in {'class','role','aria-label','data-layer'}).replace('_',' ')
            qualified_hint=bool(META.search(hint) or re.search(r'\b(?:'+qualifiers+r'|reported|quoted|forwarded)\b',hint,re.I))
            if tag in {'blockquote','q','nav','header','footer','aside','form'} or (tag in {'pre','div','section','article'} and qualified_hint):
                self.stack.append((tag,self.position()))
            if re.fullmatch('h[1-6]',tag):self.heading=[self.position(),int(tag[1]),[hint+' '] if qualified_hint else []]
            self.parts.append('<'+tag+'>')
        def handle_endtag(self,tag):
            self.parts.append('</'+tag+'>')
            if self.stack and tag==self.stack[-1][0]:
                _,start=self.stack.pop();self.ranges.append((start,self.position()+1))
            if self.heading and tag=='h'+str(self.heading[1]):
                self.headings.append((self.heading[0],self.heading[1],''.join(self.heading[2])));self.heading=None
            if tag=='pre':
                self.pre_depth=max(0,self.pre_depth-1)
                if not self.pre_depth:self.pre_finished=True
        def handle_data(self,value):
            self.parts.append(html.escape(value,quote=False))
            if self.heading:self.heading[2].append(value)
            if self.pre_depth and not self.pre_finished:self.pre_prefix+=value[:max(0,2001-len(self.pre_prefix))]
    parser=Context();parser.feed(record.body_html);parser.close();full=body_text(record.body_html)
    if body_text(''.join(parser.parts))!=full:return [(0,len(full)+1)]
    opened=None
    for m in re.finditer(r'(?m)^\ufeff?[ \t]*(?:>[ \t]*)*(`{3,}|~{3,})([^\r\n]*)',full):
        if opened is None:opened=(m.start(),m[1])
        elif m[1][0]==opened[1][0] and len(m[1])>=len(opened[1]) and not m[2].strip():
            parser.ranges.append((opened[0],m.end()));opened=None
        if len(parser.ranges)>1000:return [(0,len(full)+1)]
    if opened:parser.ranges.append((opened[0],len(full)+1))
    # The projection removes physical blank lines. A Markdown quote with an
    # uncertain lazy-continuation end cannot authorize subsequent bare actions.
    quote=re.search(r'(?m)^\ufeff?[ \t]*>',full)
    if quote:parser.ranges.append((quote.start(),len(full)+1))
    # A source explicitly ascribing a hypothetical/documentary layer to itself
    # leaves attachment unresolved, including retrospective declarations. Keep
    # the complete record inspectable but do not certify bare action predicates.
    # Merely mentioning a plan is not such an ascription.
    if re.search(r'\b(?:this|the following|what follows|these) (?:is|was|are|were) (?:(?:merely|only|just) )?(?:an? |the )?(?:plans?|proposals?|drafts?|scenarios?|forecasts?|predictions?|hypothesis|hypotheses|quotations?|examples?|reported (?:accounts?|statements?|instructions?))\b',full,re.I):
        parser.ranges.append((0,len(full)+1))
    # Independently retain modality in leading documentary headers. The layout
    # extractor's new sentence boundaries must never erase these governors.
    # This restricts semantic assertions; literal text-location remains allowed.
    labels=[];lines=full[:2000].lstrip('\ufeff').splitlines()[:16];header_uncertain=False
    if lines and re.match(r'From: ',lines[0],re.I):
        fields=[]
        for line in lines:
            m=re.fullmatch(r'(From|To|Date(?: written| sent| received)?|Subject|Message-ID|Cc): (.+)',line,re.I)
            if not m:break
            fields.append((m[1].casefold(),m[2]))
        if any(k=='to' for k,_ in fields):labels=[v for k,v in fields if k=='subject']
        else:header_uncertain=True
        # Canonical projection strips indentation. Re-read original leading
        # preformatted layout before treating a folded field as body prose.
        # Unmapped, folded or over-budget headers stay candidates, not facts.
        physical=parser.pre_prefix.lstrip('\r\n\ufeff');transition=False
        if parser.pre_start!=0 or not re.match(r'From: ',physical,re.I):header_uncertain=True
        else:
            for raw_line in physical.splitlines(keepends=True)[:17]:
                if not raw_line.endswith(('\r','\n')) and not (parser.pre_finished and len(parser.pre_prefix)<2001):
                    header_uncertain=True;break
                line=raw_line.rstrip('\r\n')
                if not line.strip():transition=True;break
                if line[:1].isspace():header_uncertain=True;break
                if not re.fullmatch(r'(?:From|To|Date(?: written| sent| received)?|Subject|Message-ID|Cc): .+',line,re.I):
                    if re.match(r'[^:\n]{1,80}:',line):header_uncertain=True
                    else:transition=True
                    break
            if not transition:header_uncertain=True
    elif lines:
        h=re.fullmatch(r'([^\n]{2,70}) TO ([^\n]{2,70})\. ([^\n]{4,120})',lines[0])
        if h and h[1].isupper() and h[2].isupper():labels=[h[3]]
    if header_uncertain or any(META.search(label) or re.search(r'\b(?:'+qualifiers+r'|reported|quoted|forwarded|alleged|denied|instructions?|orders?)\b',label,re.I) for label in labels):
        parser.ranges.append((0,len(full)+1))
    for _,start in parser.stack:parser.ranges.append((start,len(full)+1))
    for i,(start,level,heading) in enumerate(parser.headings):
        if META.search(heading) or re.search(r'\b(?:'+qualifiers+r')\b',heading,re.I):
            end=next((a for a,l,_ in parser.headings[i+1:] if l<=level),len(full)+1)
            parser.ranges.append((start,end))
    return parser.ranges


def normalized(text):
    return re.sub(r'\s+',' ',text).strip().casefold().rstrip('.')


def named_actor(text):
    """Literal capitalized name spelling, including Unicode; no entity binding."""
    return bool(NAME.fullmatch(text) and all(word[0].isupper() for word in text.split()))


def source_question(question):
    """A finite inspection view; never replace the original policy question.

    Only non-factual request scaffolding and generic documentary attribution
    are removed. Named speakers, conditions and additional factual requests stay.
    """
    q=question.strip()
    q=re.sub(r'^Please (?:assess|answer|evaluate|examine|consider) (?:this|the question) (?:from|using|based on) (?:the )?(?:provided|supplied|eligible|available) (?:records|sources|documents):\s*','',q,flags=re.I)
    q=re.sub(r'(?<=\?)\s+(?:Keep|Leave) (?:unknown|unverified|unresolved) (?:matters|claims|parts|issues) (?:unresolved|unverified)\.?$','',q,flags=re.I)
    return re.sub(r'^According to the (?:record|report|source|letter),\s*','',q,flags=re.I)


def action_forms(action):
    """All finite active/passive spellings, including irregular participles."""
    return {action}|{word for word,value in {**PAST,**PASSIVE}.items() if value==action}


def possible_refutation(text):
    """Unresolved self-reference to an error/denial is alternative evidence.

    This does not identify its target or establish an authored correction.
    """
    return bool(re.search(r'\b(?:this|that|it|above|earlier|previous|preceding|prior|i|he|she|they)\b[^.!?\n]{0,100}\b(?:false|untrue|incorrect|mistaken|wrong|inaccurate|lied|a mistake|an error|not true|isn[’\']t true|wasn[’\']t true|never happened|never occurred|didn[’\']t happen|didn[’\']t occur)\b',text,re.I))


def metadata_values(text):
    """Recognize layout-only units without treating labels as predicates."""
    lines=text.splitlines()
    if not lines or len(lines)>16:return None
    values=[]
    for line in lines:
        m=re.fullmatch(r'(?:From|To|Date(?: written| sent| received)?|Subject|Message-ID|Cc): (.+)',line,re.I)
        if not m:return None
        values.append(m[1])
    return ' '.join(values)


def literal_request(question):
    """Whole-request literal location, with no historical/execution obligation."""
    q=source_question(question)
    match=re.fullmatch(r'(?:Which|What) (?:source|record|document) (?:contains|includes|records) (?:the )?exact (?:words|wording|text) ["“]([^"“”]{2,240})["”]\??(?:\s*(?:(?:Locate|Find|Identify) (?:the )?(?:words|wording|text) only|(?:Keep|Leave) (?:unknown|unverified|unresolved) (?:matters|claims|parts|issues) (?:unresolved|unverified))\.){0,2}',q,re.I)
    anchor=match[1].strip() if match else ''
    return anchor if len(anchor)>=2 and any(c.isalnum() for c in anchor) else None


def literal_pattern(anchor):
    pattern=r'\s+'.join(re.escape(word) for word in anchor.split())
    return re.compile(r'(?<!\w)'+pattern+r'(?!\w)')


def literal_occurrence(question,quote):
    anchor=literal_request(question)
    if not anchor or not literal_pattern(anchor).search(quote):return None
    return {'relation':'source_literal_occurrence','requested_words':anchor,
            'matching_basis':'Exact code points and word boundaries; source whitespace may wrap.',
            'text_only':True,'event_identity':None,'historical_truth_independently_verified':False}


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
    if (not named_actor(actor) or normalized(actor) in {'he','she','they','we','i','you','it'}
        or set(normalized(actor).split()) & {'if','unless','not','no','never','only','neither','maybe','perhaps','allegedly','reportedly','apparently','possibly','hypothetically'}
        or normalized(actor).split()[0] in {'yesterday','today','tomorrow','later','earlier','then','now','also','instead','next','once','still','again','first','second','indeed','thereupon','beforehand','forthwith'}
        or normalized(actor).split()[0].endswith('ly')):return None
    if not obj or len(obj)>220:return None
    if re.search(r'\b(?:and|or|if|unless|when|because|not|never|may|might|could|would|should|alleged|reported|claimed|allegedly|apparently|perhaps|probably|possibly|reportedly|supposedly|intended|planned|requested|permitted)\b',obj,re.I):return None
    if any(c in obj for c in '():'):return None
    unresolved=bool(re.search(r'\b(?:that|this|it|him|her|them|those|these|dated|pending|except|only|provided)\b|\bsubject to\b|\bthe (?:area|region|place|book|letter|report)\b',obj,re.I))
    return {'relation':'source_action_assertion','actor_text':actor,'action':action,
            'object_text':obj,'negative':negative,'temporal_qualification_text':temporal,
            'unresolved_reference':unresolved,'assertion_modality':'qualified_or_referential_unresolved' if unresolved else 'unconditional_source_assertion',
            'event_identity':None}


def local_referent_context(record,body,a,b,value):
    """Retain topic context for a referential assertion without resolving it.

    A paragraph mentioning a question topic is discovery evidence, never an
    identity binding. The complete paragraph is independently re-located and
    cited; completion still requires the literal requested argument.
    """
    if not value or not value.get('unresolved_reference'):return value,[]
    from .source_units import comparison_units
    from mplpb_combined.reader import terms
    for lo,hi,text in comparison_units(record):
        if lo<=a<b<=hi and hi-lo<=2200:
            return dict(value,context_topic_terms=sorted(terms(text)),
                        context_identity_resolved=False),[citation(record,body,lo,hi)]
    return value,[]


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
    if not named_actor(intermediary):return None
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


def arrangement_request(question):
    """Closed question about a recorded request, never actual delivery.

    Retain the raw full question: additional actions, motives and dates do not
    inherit support. An explicit possessive must bind to the printed writer.
    """
    m = re.fullmatch(r"Who arranged for (.{1,100}?) to receive (.{1,100}?)['’]s "
                     r"([A-Za-z][A-Za-z \-]{0,60}?),? and which dated letter records the arrangement\?", question)
    if not m or not named_actor(m[1]) or not named_actor(m[2]):return None
    if re.search(r'\b(?:actual|completed|delivered|not|never|if|unless|and|or|only)\b', m[3], re.I):return None
    return {'recipient_reference':m[1], 'writer_reference':m[2], 'object_reference':m[3],
            'scope':'source-reported instruction and printed letter heading; no actual dispatch or receipt'}


def arrangement_completion(question, record, body, start, end, value):
    request = arrangement_request(question)
    if not request or not value['heading_date_text'] or not value['object_owner_text']:return None
    def local_name(reference, name):
        clean = lambda s: re.sub(r'[^a-z ]', '', normalized(s))
        ref, full = clean(reference), clean(name)
        return ref == full or (' ' not in ref and ref == full.split()[-1])
    if (not local_name(request['writer_reference'], value['writer_text'])
            or not local_name(request['recipient_reference'], value['addressee_text'])
            or local_name(request['writer_reference'], value['addressee_text'])
            or local_name(request['recipient_reference'], value['writer_text'])):return None
    obj = re.sub(r'^(?:a copy of my|my) ', '', value['object_text'])
    if normalized(obj) != normalized(request['object_reference']):return None
    # Examine and cite the complete local letter. A long/missing boundary stops
    # closure. Other letters are separate appearances, never merged events.
    maximum = min(len(body), start+4001)
    next_heading = re.search(r"(?m)^[A-Z][A-Z .’'\-]{1,70} TO ", body[end:maximum])
    stop = end+next_heading.start() if next_heading else len(body)
    if stop-start>4000:return None
    context = body[start:stop]
    if re.search(r'\b(?:cancell?ed|withdrawn|withdrew|retracted|rescinded|revoked|denied|correction|corrected)\b', context, re.I):return None
    return {'question_obligations_verified':True, 'verified_question':question,
            'question_completion_rule':'document_local_arrangement_reference_v1',
            'reference_bindings':request, 'reference_scope':request['scope'],
            'complete_letter_start':start, 'complete_letter_end':stop,
            'source_correction_search_scope':'this complete letter only; no global absence claim',
            'actual_arrangement_independently_verified':False}


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
            if value is None:
                passive=relationship_assertion(q)
                # Positive passive actions can be checked as exact assertions.
                # Passive denials remain conservative alternative evidence.
                if passive and passive['relation']=='source_passive_action_assertion' and not passive['negative']:
                    value=dict(passive,temporal_qualification_text='')
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
        if kind=='date_inventory':
            inventory=date_inventory(fresh,record)
            if inventory:
                value=inventory['proposition'];citations=inventory['citations']
        elif kind=='letter_instruction':
            value=letter_assertion(body,a,b) if not any(lo<b and hi>a for lo,hi in regions[record.path]) else None
            if value:
                h=value.pop('header_end');s=value.pop('statement_start')
                citations=[citation(record,body,a,h),citation(record,body,s,b)]
                closure=arrangement_completion(fresh.question,record,body,a,b,value)
                if closure:
                    value.update(closure)
                    citations.append(citation(record,body,closure['complete_letter_start'],closure['complete_letter_end']))
        elif kind in {'relationship_statement','wording_comparison','comparison_completion'}:
            # Re-read complete native units; an exact substring alone cannot
            # hide a leading negation, attribution or conditional governor.
            from .source_units import comparison_units
            native=comparison_units(record) if kind in {'wording_comparison','comparison_completion'} else units(body)
            unit=next(((lo,hi,q) for lo,hi,q in native if (lo,hi)==(a,b)),None)
            def safe_unit(record,a,b,body):
                prior=body[:a]
                return (not record.fields.get('corrects-field')
                    and not any(lo<b and hi>a for lo,hi in regions[record.path])
                    and not quoted_context(prior) and not META.search(prior)
                    and not re.search(r'\b(?:if|unless)\b',prior[-180:],re.I)
                    and not re.search(r'\b(?:the|a) (?:plan|proposal|scenario|draft|forecast|prediction|hypothesis) (?:was|is|reads|follows|stated)\b',prior[-240:],re.I)
                    and not re.search(r'(?:^|\n)\s*(?:plan|proposal|draft|scenario|forecast|prediction|hypothesis)[.:]?\s*$',prior[-240:],re.I))
            if unit and (kind in {'wording_comparison','comparison_completion'} or safe_unit(record,a,b,body)):
                if kind=='relationship_statement':
                    value=relationship_assertion(unit[2])
                    if value:
                        citations=[citation(record,body,a,b)]
                        closure=causal_completion(fresh.question,value,contexts,record,a,b,complete)
                        if closure:value.update(closure)
                else:
                    other=proposal.get('other',{});r=records.get(other.get('path'));lo=other.get('start');hi=other.get('end')
                    if (r and r.path!=record.path and r.id==other.get('source_id') and r.hash_actual==other.get('hash')
                        and type(lo) is int and type(hi) is int and 0<=lo<hi<=len(bodies[r.path]) and hi-lo<=2200
                        and bodies[r.path][lo:hi]==other.get('quote') and not r.fields.get('corrects-field')
                        and any((x,y)==(lo,hi) for x,y,_ in comparison_units(r))):
                        value=wording_difference(unit[2],bodies[r.path][lo:hi])
                        if value:citations=[citation(record,body,a,b),citation(r,bodies[r.path],lo,hi)]
                        if value and kind=='comparison_completion':
                            closure=comparison_completion(fresh,record,a,b,r,lo,hi)
                            if closure:
                                value.update(closure['proposition']);citations.extend(closure['citations'])
                            else:value=None;citations=[]
        elif kind=='action_statement':
            matches=[v for r,lo,hi,v in scanned if r.path==record.path and (lo,hi)==(a,b)]
            if len(matches)==1:
                value,context=local_referent_context(record,body,a,b,matches[0])
                citations=[citation(record,body,a,b)]+context
        elif kind=='literal_location':
            value=literal_occurrence(fresh.question,body[a:b])
            if value:
                # Word boundaries belong to the source, not to a clipped
                # extractor window. One surrounding character suffices for
                # the finite word-boundary predicate, without an unbounded read.
                lo=max(0,a-1);hi=min(len(body),b+1)
                pattern=literal_pattern(value['requested_words'])
                if not any(a<=lo+m.start() and lo+m.end()<=b for m in pattern.finditer(body[lo:hi])):value=None
            if value:
                # Re-search all eligible bodies independently of proposal rank.
                owners=set();remaining=max_scan_chars;whole=True
                pattern=literal_pattern(value['requested_words'])
                for path,text in bodies.items():
                    inspected=text[:max(0,remaining)];remaining-=len(inspected)
                    if len(inspected)<len(text):whole=False
                    if pattern.search(inspected):owners.add(path)
                citations=[citation(record,body,a,b)]
                if whole and complete and owners=={record.path}:
                    value.update(question_obligations_verified=True,verified_question=fresh.question,
                        question_completion_rule='eligible_literal_location_v1',
                        reference_scope='Textual occurrence in one current eligible source; no event or historical assertion.')
                value['eligible_source_ambiguity']=len(owners)>1
        if value is None:rejected.append('assertion_grammar_or_context_unresolved');continue
        certified.append({'proposition':value,'citations':citations,'source_support_established':True,
            'support_scope':'textual_occurrence' if kind=='literal_location' else 'source_attributed_assertion','verification':VERSION,
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
    passive=re.fullmatch(r'(.{2,160}?) was (not )?('+'|'.join(PASSIVE)+r') by (.{2,100})\.',clean)
    if passive:
        obj,neg,action,actor=passive.groups()
        if (named_actor(actor) and not re.search(r'\b(?:he|she|they|it|we|i|you|if|unless|and|or|not|never|perhaps|maybe|possibly|apparently|allegedly|reportedly|planned|requested|reported)\b',actor+' '+obj,re.I)
            and not normalized(actor).split()[0].endswith('ly')):
            value={'relation':'source_passive_action_assertion','actor_text':actor,'action':PASSIVE[action],
                   'object_text':obj,'negative':bool(neg),'unresolved_reference':bool(re.search(r'\b(?:that|this|it|him|her|them|those|these|dated|pending|except|only|provided)\b|\bsubject to\b|\bthe (?:area|region|place|book|letter|report)\b',obj,re.I))}
    if value is not None:
        value.update(assertion_modality='source_attributed_assertion',event_identity=None,
                     historical_truth_independently_verified=False)
    return value


def causal_completion(question,value,contexts,record,a,b,complete):
    """Close one exact source-reported because-of question, never event truth.

    Independently derived source arguments must match the entire request.
    Any other relevant appearance, even with similar wording, stops closure;
    neither event co-reference nor absence outside this bounded scan is inferred.
    """
    if not complete or value['relation']!='source_causal_assertion' or value['negative']:return None
    q=source_question(question).strip().rstrip('? .')
    request=re.fullmatch(r'why was (.{2,350}?) (aborted|cancelled|canceled|delayed|postponed|halted|withdrawn|terminated)',q,re.I)
    if not request or normalized(request[1])!=normalized(value['subject_text']) or request[2].lower()!=value['action_text']:return None
    subject=re.sub(r'^(?:the|a|an) ','',normalized(value['subject_text']))
    for other,lo,hi,text,_ in contexts:
        if other.path==record.path and (lo,hi)==(a,b):continue
        if possible_refutation(text):return None
        fields=metadata_values(text)
        if fields is not None and not re.search(r'\b'+re.escape(value['action_text'])+r'\b',fields,re.I):continue
        if subject in normalized(text):return None
        if (re.search(r'\b(?:it|this|that|they|those|these)\b',text,re.I)
            and re.search(r'\b(?:'+re.escape(value['action_text'])+r'|not|never|denied|cancelled|canceled)\b',text,re.I)):return None
    return {'question_obligations_verified':True,'verified_question':question,
            'question_completion_rule':'literal_source_cause_v1',
            'reference_scope':'One explicit source-attributed cause; event identity and historical causation unverified.'}


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


def comparison_request(question):
    """Closed literal-comparison questions; extra factual obligations stop closure."""
    from mplpb_combined.reader import terms
    if not re.match(r'^(?:Compare\b|How (?:does|do)\b)',question):return None
    if re.search(r'\b(?:not|never|unless|if|only|except|whether|alleged|possibly|supposed|hypothetical|assume|imagine|denied)\b',question,re.I):return None
    owner=re.search(r"\b(?:in|between|from)\s+([A-Z][A-Za-z .’'\-]{0,80}?)['’]s\s+rough\s+(?:draft|draught)\b",question)
    if not owner:return None
    tail=question[owner.end():]
    work=re.search(r'\b([A-Z][A-Za-z \-]{1,100}?)\s+transcript\b',tail)
    if not work:return None
    middle=tail[:work.start()];suffix=tail[work.end():]
    if set(re.findall(r'[A-Za-z]+',middle.lower()))-set('and differs differ from the final to versus vs with'.split()):return None
    if set(re.findall(r'[A-Za-z]+',suffix.lower()))-set('what which wording words changed changes remained remains shared retained is was and describe differs differ'.split()):return None
    if re.sub(r'[A-Za-z\s?.;,]','',middle+suffix):return None
    prefix=question[:owner.start()]
    if not re.search(r'\b(?:opening|initial|first)\b',prefix):return None
    focus=terms(prefix)-terms('compare how does do the opening initial first wording words claim statement in between differ difference and')
    if not 1<=len(focus)<=5:return None
    return {'author_reference':owner[1].strip(),'work_reference':work[1].strip(),'topic_terms':sorted(focus),
            'operations':['changed_wording','shared_wording'],'scope':'the supplied source-declared reconstruction and transcription; not historical authenticity or finality'}


def comparison_completion(index,left,a,b,right,lo,hi):
    """Independently bind source references and close literal comparison goals.

    Framing is cited body prose, never a filename/title or model label. This
    proves selection of two supplied documentary appearances and text operations,
    not manuscript authenticity, event identity or a last-ever historical version.
    """
    from .source_units import comparison_units
    from mplpb_combined.reader import terms
    request=comparison_request(index.question)
    if request is None or len(index.records)>32:return None
    frames=[]
    for record in index.records:
        # A document headed Draft may still explicitly identify its own rough
        # reconstruction for a literal comparison. This exception never applies
        # to action/execution proofs; plan/conditional/quotation scopes still stop it.
        body=body_text(record.body_html);regions=context_ranges(record,document_draft=True)
        for start,end,q in comparison_units(record):
            if start>=6000:break
            clean=re.sub(r'\s+',' ',q).strip();prior=body[:start]
            if (META.search(clean) or re.search(r'\b(?:not|never|if|unless|may|might|perhaps|probably|possibly|supposed|purported|allegedly|reportedly)\b',clean,re.I)
                or quoted_context(prior) or re.search(r'\b(?:if|unless)\b',prior[-180:],re.I)
                or any(x<end and y>start for x,y in regions)):continue
            rough=re.search(r"reconstruction of ([^\n\"“”]{2,120}?)['’]s [\"“](?:original )?Rough (?:draft|draught)[\"”] of (?:the )?(.{2,100}?) before it was revised\b",clean,re.I)
            trans=re.match(r'(?:Note: )?The following text is a transcription of (.{2,220}?)(?:\.| \()',clean)
            if rough and re.match(r'\(?This is ',clean):
                frames.append({'role':'rough_reconstruction','author':rough[1],'work':rough[2],
                               'record':record,'start':start,'end':end})
            elif trans:
                frames.append({'role':'source_declared_transcription','artifact':trans[1],
                               'record':record,'start':start,'end':end})
    drafts=[f for f in frames if f['role']=='rough_reconstruction'
            and (normalized(f['author'])==normalized(request['author_reference'])
                 or normalized(f['author']).endswith(' '+normalized(request['author_reference'])))
            and list(terms(request['work_reference']))
            and normalized(f['work']).startswith(normalized(request['work_reference']))]
    if len(drafts)!=1:return None
    draft=drafts[0]
    transcripts=[f for f in frames if f['role']=='source_declared_transcription'
                 and normalized(draft['work']) in normalized(f['artifact']) and f['record'].path!=draft['record'].path]
    if len(transcripts)!=1:return None
    transcript=transcripts[0];wanted={left.path:(a,b),right.path:(lo,hi)}
    if set(wanted)!={draft['record'].path,transcript['record'].path}:return None
    for frame in (draft,transcript):
        eligible=[(x,y,q) for x,y,q in comparison_units(frame['record'])
                  if x>=frame['end'] and set(request['topic_terms'])<=terms(q)]
        if not eligible or eligible[0][:2]!=wanted[frame['record'].path]:return None
        if '?' in eligible[0][2] or not eligible[0][2].rstrip().endswith('.'):return None
    roles=[{'role':f['role'],'source_id':f['record'].id,'hash':f['record'].hash_actual,
            'work_reference':draft['work'],'declaration_only':True} for f in (draft,transcript)]
    return {'proposition':{'question_obligations_verified':True,'verified_question':index.question,
            'completion_rule':'source-framed-literal-comparison-v1','document_roles':roles,
            'document_authenticity_verified':False,'historical_finality_verified':False,
            'reference_scope':request['scope'],'topic_terms':request['topic_terms'],
            'completed_operations':request['operations']},
        'citations':[citation(f['record'],body_text(f['record'].body_html),f['start'],f['end']) for f in (draft,transcript)]}
