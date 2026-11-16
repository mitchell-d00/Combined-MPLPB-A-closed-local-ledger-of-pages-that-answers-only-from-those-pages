"""Verify frozen originals and reverse canonical citation coordinates to raw bytes.

Canonical text normalizes layout. raw_excerpt is the untouched contiguous source
slice, with markup/layout retained. These are distinct outputs, never conflated.
"""
from array import array
from html.parser import HTMLParser
import html
import re
from tools.unprepared_sources import verify, inside, sha, projected
from mplpb_answers.body_text import body_text


def projection_offsets(text,is_html):
    chars=[];starts=array('q');ends=array('q')
    def emit(value,a,b=None):
        for i,c in enumerate(value):
            chars.append(c);starts.append(a+i if b is None else a);ends.append(a+i+1 if b is None else b)
    if not is_html:
        emit(text,0)
    else:
        line_starts=[0]+[m.end() for m in re.finditer('\n',text)]
        class Mapped(HTMLParser):
            SKIP={'h1','h2','h3','h4','h5','h6','script','style','head','title','noscript'}
            BLOCK={'p','div','li','tr','br','pre','section','ul','ol','table'}
            def __init__(self):super().__init__(convert_charrefs=False);self.blocked=[]
            def position(self):
                line,col=self.getpos();return line_starts[line-1]+col
            def handle_starttag(self,tag,attrs):
                if tag in self.SKIP:self.blocked.append(tag)
                elif not self.blocked and tag in self.BLOCK:emit('\n',-1,-1)
            def handle_endtag(self,tag):
                if tag in self.blocked:
                    i=len(self.blocked)-1-self.blocked[::-1].index(tag);del self.blocked[i:]
                    if not self.blocked:emit('\n',-1,-1)
                elif not self.blocked and tag in self.BLOCK:emit('\n',-1,-1)
            def handle_data(self,value):
                if not self.blocked:emit(value,self.position())
            def handle_entityref(self,name):
                if not self.blocked:
                    a=self.position();raw='&'+name+(';' if text[a+len(name)+1:a+len(name)+2]==';' else '')
                    emit(html.unescape(raw),a,a+len(raw))
            def handle_charref(self,name):
                if not self.blocked:
                    a=self.position();raw='&#'+name+(';' if text[a+len(name)+2:a+len(name)+3]==';' else '')
                    emit(html.unescape(raw),a,a+len(raw))
        parser=Mapped();parser.feed(text);parser.close()
    raw=''.join(chars);out=[];aout=array('q');bout=array('q');cursor=0
    for line in raw.splitlines(keepends=True):
        # Match the existing canonical projection exactly, including Unicode trim.
        content=line.rstrip('\r\n\v\f\x1c\x1d\x1e\x85\u2028\u2029')
        groups=list(re.finditer(r'[ \t]+|[^ \t]',content));normal=[]
        for m in groups:
            normal.append((' ' if m[0][0] in ' \t' else m[0],cursor+m.start(),cursor+m.end()-1))
        while normal and normal[0][0].isspace():normal.pop(0)
        while normal and normal[-1][0].isspace():normal.pop()
        if normal:
            if out:out.append('\n');aout.append(-1);bout.append(-1)
            for c,a,b in normal:out.append(c);aout.append(starts[a]);bout.append(ends[b])
        cursor+=len(line)
    projection=''.join(out)
    expected=body_text(text if is_html else '<pre>'+html.escape(text)+'</pre>')
    if projection!=expected:raise ValueError('Projection mapping cannot reproduce existing canonical text')
    return projection,aout,bout


def original_passage(directory,receipt,evidence):
    manifest=verify(directory)
    matches=[r for r in receipt['records'] if r['id']==evidence['source_id'] and r['path']==evidence['path'] and r['hash']==evidence['hash']]
    if len(matches)!=1:raise ValueError('No unique imported original mapping')
    record=matches[0];sources=[s for s in manifest['sources'] if s['id']==record['original_id']]
    if len(sources)!=1:raise ValueError('No original source')
    source=sources[0];raw=inside(directory,source['path']).read_bytes();text=raw.decode(source['encoding'])
    if sha(raw)!=record['original_sha256']:raise ValueError('Original revision changed')
    fragment=text;offset=0
    if source['media_type']=='text/html':
        m=re.search(r'<body\b[^>]*>([\s\S]*)</body\s*>',text,re.I)
        if not m:raise ValueError('Missing body envelope')
        fragment=m[1];offset=m.start(1)
    projection,starts,ends=projection_offsets(fragment,source['media_type']=='text/html')
    a=record['projection_character_start']+evidence['body_start'];b=record['projection_character_start']+evidence['body_end']
    if type(a) is not int or type(b) is not int or not 0<=a<b<=len(projection) or projection[a:b]!=evidence['quote']:raise ValueError('Canonical evidence changed')
    positions=[i for i in range(a,b) if starts[i]>=0 and ends[i]>=0]
    if not positions:raise ValueError('No raw source characters')
    ca=offset+min(starts[i] for i in positions);cb=offset+max(ends[i] for i in positions)
    ba=len(text[:ca].encode(source['encoding']));bb=len(text[:cb].encode(source['encoding']))
    excerpt=raw[ba:bb].decode(source['encoding'])
    return {'original_id':source['id'],'original_sha256':sha(raw),'original_url':source['url'],
        'original_character_start':ca,'original_character_end':cb,'original_byte_start':ba,'original_byte_end':bb,
        'raw_excerpt':excerpt,'raw_excerpt_sha256':sha(raw[ba:bb]),'canonical_quote':projection[a:b],
        'projection_version':record['projection_version'],'round_trip_quote_fidelity':True,
        'semantic_relationship_verified':False,'answer_supported':False,
        'notice':'Raw excerpt retains source markup and layout; canonical quote uses the existing normalized projection.'}
