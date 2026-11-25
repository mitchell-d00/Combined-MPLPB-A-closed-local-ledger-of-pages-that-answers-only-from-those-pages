"""Derived documentary units over the unchanged canonical body projection.

Layers and section names are inspection cues, never factual source evidence.
Only immutable parsing is cached. Serving decisions are always made elsewhere.
"""
from functools import lru_cache
from html import escape
from html.parser import HTMLParser
import re
from .body_text import body_text, VERSION as BODY_VERSION
from .evidence_contract import pin

VERSION = 'documentary-source-units-v3'
CHROME = {'nav', 'header', 'footer', 'aside', 'form'}


def comparison_units(record):
    """Complete existing paragraph units for literal wording comparison.

    A semicolon-separated paragraph need not end in a full stop. This rule
    compares text, not whether any assertion in that paragraph is true.
    """
    from .passages import _passage_units, _preformatted_spans
    body=body_text(record.body_html)
    class PreText(HTMLParser):
        def __init__(self):super().__init__();self.depth=0;self.values=[];self.current=[]
        def handle_starttag(self,tag,attrs):
            if tag=='pre':
                if not self.depth:self.current=[]
                self.depth+=1
        def handle_endtag(self,tag):
            if tag=='pre' and self.depth:
                self.depth-=1
                if not self.depth:self.values.append(''.join(self.current))
        def handle_data(self,value):
            if self.depth:self.current.append(value)
    parser=PreText();parser.feed(record.body_html);parser.close()
    mapped={}
    for (start,end),raw in zip(_preformatted_spans(record.body_html,body),parser.values):
        parts=[body_text('<pre>'+escape(p)+'</pre>') for p in re.split(r'\n[ \t]*\n+',raw)]
        parts=[p for p in parts if p]
        # Only use physical paragraph boundaries if they reproduce the exact
        # existing projection. Neither OCR correction nor whitespace rewriting
        # is allowed to move canonical evidence coordinates.
        if len(parts)>1 and '\n'.join(parts)==body[start:end]:
            cursor=start
            for q in parts:mapped[cursor]=(cursor+len(q),q);cursor+=len(q)+1
    emitted=set()
    for a,q,truncated in _passage_units(record.body_html,body):
        if mapped and any(x<a+len(q) and y>a for x,(y,_) in mapped.items()):
            for x,(y,text) in mapped.items():
                if x<a+len(q) and y>a and (x,y) not in emitted and y-x<=2200 and not re.match(r'^Source capture:\s*\{',text,re.I):
                    emitted.add((x,y));yield x,y,text
            continue
        if not truncated and q.strip() and len(q)<=2200 and not re.match(r'^Source capture:\s*\{',q,re.I):
            yield a,a+len(q),q


def statement_units(body):
    """Complete literal units, with original all-capital section boundaries.

    Layout labels supply boundaries, not answer facts. Wrapped source lines
    remain together. A cut scan still needs its caller's completeness check.
    """
    boundaries = {0, len(body)}
    # A leading correspondence header and salutation are layout units, not
    # part of the first sentence's actor. Keep every character and the prefix
    # available to the checker for quotation/conditional scope tests.
    lines=list(re.finditer(r'[^\n]+(?:\n|$)',body[:2000]))
    end=None
    if lines:
        first=lines[0][0].rstrip('\n')
        heading=re.fullmatch(r'([^\n]{2,70}) TO ([^\n]{2,70})\. [^\n]{4,120}',first)
        if heading and heading[1].isupper() and heading[2].isupper():
            end=lines[0].end()
        elif first.startswith('From: '):
            names=[]
            for line in lines[:16]:
                match=re.fullmatch(r'(From|To|Date(?: written| sent| received)?|Subject|Message-ID|Cc): [^\n]+\n?',line[0])
                if not match:break
                names.append(match[1]);end=line.end()
            if 'To' not in names:end=None
    if end is not None:
        boundaries.add(end)
        greeting=re.match(r"(?:Dear [A-Za-z ’'\-]{1,70},|My dear [A-Za-z ’'\-]{1,70},)\n",body[end:])
        if greeting:boundaries.add(end+greeting.end())
    # A printed byline need not end in sentence punctuation. Keep it as a
    # separate layout unit rather than making it the actor of the next clause.
    # This supplies boundaries only: source voice still requires native proof,
    # and the entire prefix remains available for qualification/quotation checks.
    byline = re.match(r'^(?:Meeting minutes\.\n(?:Recorder:|Recorded by)|Report\.\nWritten by) '
                      r'(?P<writer>[^\n]{2,120})\n', body)
    if byline:
        name=byline['writer'].removesuffix('.')
        words=name.split()
        if (re.fullmatch(r"[^\W\d_][^\W\d_’'\-]*(?: [^\W\d_][^\W\d_’'\-]*){1,7}",name)
                and all(w[0].isupper() for w in words)
                and not {w.casefold() for w in words}&{'if','unless','not','never','conditional','hypothetical'}):
            boundaries.add(byline.end())
    for m in re.finditer(r'(?m)^[A-Z][A-Z0-9 /—–:-]{2,79}\n', body):
        boundaries.update((m.start(), m.end()))
    points = sorted(boundaries)
    for lo, hi in zip(points, points[1:]):
        section = body[lo:hi]
        if re.fullmatch(r'[A-Z][A-Z0-9 /—–:\-]{2,79}\n?', section):
            continue
        start = lo
        for m in re.finditer(r'[.!?]["”\)\]]?\s+(?=[A-Z"\[])', section):
            pos = lo + m.start()
            # Inspect a bounded lexical tail. Searching an unbounded prefix
            # ending in OCR punctuation causes quadratic regex backtracking.
            word = re.search(r'([A-Za-z]+)$', body[max(lo,pos-24):pos])
            if word and (len(word[1]) == 1 or word[1].lower() in {'mr','mrs','ms','dr','gen','maj','prof','hon','st','jr','sr'}):
                continue
            end = pos + 1
            if end < hi and body[end] in '"”)]': end += 1
            a = start + len(body[start:end]) - len(body[start:end].lstrip())
            if a < end: yield a, end, body[a:end]
            start = lo + m.end()
        if body[start:hi].strip():
            a = start + len(body[start:hi]) - len(body[start:hi].lstrip())
            b = hi - len(body[start:hi]) + len(body[start:hi].rstrip())
            yield a, b, body[a:b]


@lru_cache(maxsize=4)
def _structure(source_hash, version, source):
    class Structure(HTMLParser):
        def __init__(self):
            super().__init__(); self.parts=[]; self.stack=[]; self.ranges=[]; self.headings=[]; self.heading=None
        def position(self): return len(body_text(''.join(self.parts)))
        def handle_starttag(self, tag, attrs):
            if tag in CHROME | {'blockquote','q','sup'}:
                self.stack.append((tag,self.position()))
            if re.fullmatch(r'h[1-6]',tag): self.heading=[self.position(),int(tag[1]),[]]
            self.parts.append('<'+tag+'>')
        def handle_endtag(self, tag):
            self.parts.append('</'+tag+'>')
            if self.stack and self.stack[-1][0]==tag:
                t,a=self.stack.pop(); self.ranges.append((a,self.position()+1,'site_chrome' if t in CHROME else 'quotation' if t in {'q','blockquote'} else 'annotation'))
            if self.heading and tag=='h'+str(self.heading[1]):
                self.headings.append((self.heading[0],self.heading[1],''.join(self.heading[2])));self.heading=None
        def handle_data(self,value):
            self.parts.append(escape(value,quote=False))
            if self.heading:self.heading[2].append(value)
    parser=Structure();parser.feed(source);parser.close();body=body_text(source)
    aligned=body_text(''.join(parser.parts))==body
    for tag,a in parser.stack:parser.ranges.append((a,len(body)+1,'incomplete_markup'))
    for i,(a,level,label) in enumerate(parser.headings):
        end=next((b for b,l,_ in parser.headings[i+1:] if l<=level),len(body)+1)
        if re.search(r'\b(?:transcript|transcription|original text)\b',label,re.I):layer='documentary_transcript'
        elif re.search(r'\b(?:footnotes?|annotations?|notes)\b',label,re.I):layer='annotation'
        elif re.search(r'\b(?:editorial|introduction|commentary|historical background)\b',label,re.I):layer='editorial_commentary'
        else:layer='unclassified'
        parser.ranges.append((a,end,layer))
    return body,tuple(parser.ranges),aligned


def inspect_source(record, *, max_chars=200000, max_units=1000):
    if type(max_chars) is not int or not 1000<=max_chars<=1000000:raise ValueError('Invalid source-unit character budget')
    if type(max_units) is not int or not 1<=max_units<=2000:raise ValueError('Invalid source-unit count budget')
    # Oversized inputs do not enter the bounded immutable cache.
    parse=_structure if len(record.body_html)<=2000000 else _structure.__wrapped__
    body,ranges,aligned=parse(record.hash_actual,VERSION,record.body_html)
    limit=min(len(body),max_chars);items=[];cut=False
    for a,b,q in statement_units(body[:limit]):
        if len(items)>=max_units:cut=True;break
        complete=not (limit<len(body) and b==limit)
        layers=[layer for lo,hi,layer in ranges if lo<b and hi>a and layer!='unclassified']
        layer=('site_chrome' if 'site_chrome' in layers else 'quotation' if 'quotation' in layers else 'annotation' if 'annotation' in layers else layers[-1] if layers else 'unclassified') if aligned else 'structure_unresolved'
        if re.match(r"[A-Z][A-Z .’'\-]{2,70} TO ",q):layer='correspondence_appearance'
        evidence={'source_id':record.id,'path':record.path,'hash':record.hash_actual,'body_start':a,'body_end':b,'quote':q,'body_projection':BODY_VERSION}
        items.append(dict(evidence,unit_id=pin({'version':VERSION,'evidence':evidence}),documentary_layer=layer,
            layer_basis='source layout inspection; identity and historical authority unresolved',
            complete_statement_boundary=complete and aligned,original_byte_mapping=None,
            original_mapping_status='Use tools.source_roundtrip.original_passage with the pinned import receipt when available.',
            source_support_established=False,historical_truth_independently_verified=False))
    return {'schema':VERSION,'source_id':record.id,'hash':record.hash_actual,'units':items,
            'examined_characters':limit,'source_characters':len(body),'complete_source_examined':aligned and limit==len(body) and not cut,
            'limits_reached':(['source_characters'] if limit<len(body) else [])+(['source_units'] if cut else []),
            'authoritative':False,'layer_interpretation_verified':False}


def expand(index, passages, max_passages, max_chars):
    """Recover full source units across passage boundaries under caller budget."""
    by_path={r.path:r for r in index.records};result=[];used=0;seen=set();diagnostics=[]
    for passage in passages:
        record=by_path[passage['path']];body=body_text(record.body_html);lo=passage['body_start'];hi=lo+len(passage['text'])
        overlapping=[(a,b) for a,b,q in statement_units(body) if a<hi and b>lo]
        if not overlapping:continue
        a,b=overlapping[0][0],overlapping[-1][1];key=(record.path,a,b)
        if key in seen:continue
        if len(result)>=max_passages or used+b-a>max_chars:
            diagnostics.append({'path':record.path,'reason':'complete_context_exceeds_budget'});continue
        seen.add(key);used+=b-a
        result.append(dict(passage,body_start=a,text=body[a:b],context_truncated=False,
            id=pin({'source':record.path,'hash':record.hash_actual,'start':a,'text':body[a:b]}),context_operation=VERSION))
    return result,diagnostics
