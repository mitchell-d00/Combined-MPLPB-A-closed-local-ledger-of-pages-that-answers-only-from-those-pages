"""Automatic source-linked layout proposals; never facts or host permissions.

Only a separately checked closed metadata block supplies a new reader boundary.
Entity and relation nodes are inspection proposals, with native answer proof
still required. Every public validation rereads the current eligible source.
"""
import hashlib,html,re
from html.parser import HTMLParser
from .body_text import body_text
from . import documentary_verify as kernel
VERSION='source-linked-layout-v1'
_TAGS={'p':'paragraph','pre':'pre','blockquote':'quotation','q':'quotation','article':'section','section':'section'}
_FIELDS=re.compile(r'(From|To|Date(?: written| sent| received)?|Subject|Message-ID|Cc): (.+)',re.I)

def definition_header(record):
    """Reread a closed, leading definition list as layout only.

    Exact source projection stays unchanged. Unknown, duplicate, nested or
    incomplete fields cannot authorize a prose boundary or a source actor.
    """
    raw=record.body_html
    opening=re.search(r'<dl\b[^>]*>',raw,re.I)
    if not opening or body_text(raw[:opening.start()]):return None
    invalid={'status':'unresolved','fields':[],'end':0}
    match=re.match(r'<dl\b[^>]*>([\s\S]{1,2200}?)</dl\s*>',raw[opening.start():],re.I)
    if not match:return invalid
    inner=match[1];field=re.compile(r'\s*<dt\s*>([^<>]{1,40})</dt\s*>\s*<dd\s*>([^<>]{1,300})</dd\s*>',re.I)
    fields=[];cursor=0
    for item in field.finditer(inner):
        if item.start()!=cursor:return invalid
        parsed=_FIELDS.fullmatch(html.unescape(item[1]).strip()+': '+html.unescape(item[2]).strip())
        if not parsed:return invalid
        fields.append((parsed[1].casefold(),parsed[2]));cursor=item.end()
    if inner[cursor:].strip():return invalid
    labels=[label for label,_ in fields]
    if not {'from','to'}<=set(labels) or len(labels)!=len(set(labels)):return invalid
    for label,value in fields:
        if label in {'from','to'} and (not kernel.named_actor(value) or re.search(r'\b(?:if|unless|not|never|only|conditional|reported|quoted)\b',value,re.I)):return invalid
    end_raw=opening.start()+match.end();prefix=body_text(raw[:end_raw]);body=body_text(raw)
    if not prefix or not body.startswith(prefix) or not body[len(prefix):].startswith('\n'):return invalid
    return {'status':'closed','fields':fields,'end':len(prefix)+1}

def _pin(record):return {'id':record.id,'path':record.path,'hash':record.hash_actual,'body_html_sha256':hashlib.sha256(record.body_html.encode()).hexdigest()}
def closed_header(record):
    """Check the physical end of a complete leading preformatted header.

    Folded, duplicate, qualified and ambiguous fields remain unresolved. The
    caller still retains all outer quotation, heading and subject governors.
    """
    raw=record.body_html;match=re.search(r'<pre\b[^>]*>(?P<inner>[\s\S]{1,2200}?)</pre\s*>',raw,re.I)
    if not match or body_text(raw[:match.start()]):return False
    class Text(HTMLParser):
        def __init__(self):super().__init__();self.parts=[]
        def handle_data(self,value):self.parts.append(value)
    parser=Text();parser.feed(match['inner']);physical=''.join(parser.parts).lstrip('\r\n\ufeff')
    if len(physical)>2000:return False
    lines=physical.splitlines();fields=[]
    for line in lines:
        m=_FIELDS.fullmatch(line)
        if not m or line[:1].isspace():return False
        fields.append((m[1].casefold(),m[2]))
    labels=[f for f,_ in fields]
    if not {'from','to'}<=set(labels) or len(labels)!=len(set(labels)):return False
    for label,value in fields:
        if label in {'from','to'} and (not kernel.named_actor(value) or re.search(r'\b(?:if|unless|not|never|only|conditional|reported|quoted)\b',value,re.I)):return False
    quote=body_text(raw[match.start():match.end()]);body=body_text(raw)
    return bool(quote and body.startswith(quote) and body[len(quote):].startswith('\n'))

class _Blocks(HTMLParser):
    def __init__(self,raw):
        super().__init__(convert_charrefs=True);self.raw=raw;self.lines=[0];self.stack=[];self.spans=[]
        for m in re.finditer('\n',raw):self.lines.append(m.end())
    def position(self):line,col=self.getpos();return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        if tag in _TAGS:self.stack.append((tag,self.position()))
    def handle_endtag(self,tag):
        if tag in _TAGS and self.stack and self.stack[-1][0]==tag:
            _,start=self.stack.pop();end=self.raw.find('>',self.position())+1
            self.spans.append((start,end,tag,any(t in {'q','blockquote'} for t,_ in self.stack)))

def propose(record):
    raw=record.body_html;body=body_text(raw);encoded=raw.encode();errors=[]
    root={'id':'N0','kind':'document','parent':None,'body_start':0,'body_end':len(body),'original_start_byte':0,'original_end_byte':len(encoded),'role':'container_only'}
    packet={'schema':VERSION,'source':_pin(record),'nodes':[root],'relations':[],'extraction_errors':errors,'authoritative':False,'source_support_established':False,'identity_expansion':False,'host_policy_fields':False}
    if len(raw)>200000:errors.append('source_extraction_character_budget');return packet
    parser=_Blocks(raw);parser.feed(raw);parser.close()
    if parser.stack:errors.append('unclosed_layout_blocks')
    def add(kind,parent,a,b,lo,hi,role,quoted=False):
        if len(packet['nodes'])>=64:errors.append('node_budget');return None
        quote=body[a:b]
        if not quote or len(quote)>2200:errors.append('node_phrase_budget');return None
        value={'id':'N'+str(len(packet['nodes'])),'kind':kind,'parent':parent,'body_start':a,'body_end':b,'quote':quote,'original_start_byte':len(raw[:lo].encode()),'original_end_byte':len(raw[:hi].encode()),'role':role,'inside_quotation':quoted};packet['nodes'].append(value);return value
    blocks=[]
    for lo,hi,tag,quoted in sorted(parser.spans,key=lambda s:(s[0],-s[1])):
        fragment=raw[lo:hi];quote=body_text(fragment);prefix=body_text(raw[:lo]);a=len(prefix)+bool(prefix);b=a+len(quote)
        if not quote:continue
        if body[a:b]!=quote:errors.append('unmapped_layout_block');continue
        parents=[n for n in packet['nodes'] if n['kind'] in {'document','section','quotation','pre','paragraph'} and n['body_start']<=a and b<=n['body_end'] and n['original_start_byte']<=len(raw[:lo].encode()) and len(raw[:hi].encode())<=n['original_end_byte']]
        parent=parents[-1]['id'] if parents else 'N0';node=add(_TAGS[tag],parent,a,b,lo,hi,'layout_candidate',quoted or tag in {'q','blockquote'})
        if node:blocks.append((node,fragment,lo))
    def entity(node,fragment,lo,value,kind,role):
        # Exact canonical occurrence plus exact raw encoding, no guessed spans.
        candidates=list(re.finditer(re.escape(value),node['quote']))
        locations={(m.start(),m.end()) for encoded_value in {value,html.escape(value),html.escape(value,quote=False)} for m in re.finditer(re.escape(encoded_value),fragment)}
        if len(candidates)!=1 or len(locations)!=1:errors.append('unmapped_or_ambiguous_entity');return None
        m=candidates[0];x,y=next(iter(locations));return add(kind,node['id'],node['body_start']+m.start(),node['body_start']+m.end(),lo+x,lo+y,role,node['inside_quotation'])
    for node,fragment,lo in blocks:
        if node['kind'] not in {'pre','paragraph'}:continue
        for m in re.finditer(r'(?m)^(From|To): ([^\n]+)$',node['quote']):entity(node,fragment,lo,m[2],'person','declared_header_'+m[1].lower())
        byline=re.fullmatch(r'(?:Written by|Recorded by|Recorder:) ([^.\n]+)\.?',node['quote'])
        if byline:entity(node,fragment,lo,byline[1],'person','printed_byline_candidate')
        for date in re.finditer(kernel.DATE_EXPRESSION,node['quote'],re.I):entity(node,fragment,lo,date[0],'date','date_mention_only')
        action=kernel.action_assertion(node['quote'])
        if action:
            actor=entity(node,fragment,lo,action['actor_text'],'person','proposed_action_actor');obj=entity(node,fragment,lo,action['object_text'],'object','proposed_action_object')
            if actor and obj:packet['relations'].append({'witness':node['id'],'actor':actor['id'],'object':obj['id'],'action':action['action'],'negative':action['negative'],'status':'unverified_source_claim_proposal'})
    return packet

def verify_proposals(root,question,packet,profile=None):
    from .passages import PassageIndex
    base={'schema':VERSION,'authoritative':False,'source_support_established':False,'changes_host_access':False,'historical_truth_independently_verified':False}
    import json
    if type(packet) is not dict or len(json.dumps(packet,ensure_ascii=False).encode())>64000:
        return dict(base,status='rejected',reason='proposal_byte_budget_or_schema')
    index=PassageIndex(root,question,profile)
    if not index.profile.prose:return dict(base,status='rejected',reason='profile_no_prose')
    if len(index.records)>8 or sum(len(r.body_html) for r in index.records)>200000:return dict(base,status='rejected',reason='scan_budget')
    source=packet.get('source',{}) if isinstance(packet,dict) else {}
    records=[r for r in index.records if _pin(r)==source and r.kind=='page' and not r.derived_from and not r.fields.get('corrects-field')]
    if len(records)!=1:return dict(base,status='rejected',reason='no_unique_current_eligible_source')
    if sum(sum(1 for _ in kernel.units(body_text(r.body_html))) for r in index.records)>1000:return dict(base,status='rejected',reason='unit_budget')
    # The native validator derives every proposed field again from reread bytes.
    # Equality retains exact types, source hashes, source voice and coordinates.
    import json
    expected=propose(records[0]);same=json.dumps(expected,sort_keys=True,ensure_ascii=False)==json.dumps(packet,sort_keys=True,ensure_ascii=False)
    if not index.unchanged():return dict(base,status='rejected',reason='source_changed')
    return dict(base,status='accepted' if same else 'rejected',reason='non_authoritative_source_layout_only' if same else 'proposal_does_not_match_original_bytes')
