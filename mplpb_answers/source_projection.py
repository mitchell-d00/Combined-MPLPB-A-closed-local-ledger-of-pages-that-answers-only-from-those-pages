"""Shared reversible canonical-body projection for runtime and study tools.

Coordinates map unchanged source text to the existing body_text projection;
quote fidelity does not certify any interpreted relationship.
"""
from array import array
from html.parser import HTMLParser
import html
import re
from .body_text import body_text


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

