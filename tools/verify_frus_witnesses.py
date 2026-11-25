"""Independently map native instruction witnesses back to sealed original HTML."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from mplpb_answers.body_text import body_text
from tools.pole_focus_extend import frus_fragment, frus_rendered


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class Blocks(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.text=text;self.stack=[];self.spans=[]
        self.offsets=[0]+[m.end() for m in re.finditer('\n',text)]

    def position(self):
        row,column=self.getpos();return self.offsets[row-1]+column

    def handle_starttag(self,tag,attrs):
        if tag in {'p','div'}:self.stack.append((tag,self.position()))

    def handle_endtag(self,tag):
        if self.stack and self.stack[-1][0]==tag:
            _,start=self.stack.pop();end=self.text.index('>',self.position())+1
            self.spans.append((start,end,tag))


def original_span(raw,source,quote):
    text=raw.decode(source['encoding']);fragment=frus_fragment(raw,source)
    assert text.count(fragment)==1
    base=text.index(fragment);parser=Blocks(fragment);parser.feed(fragment);parser.close()
    candidates={(a,b) for a,b,_ in parser.spans}
    if len(parser.spans)>512:raise ValueError('Original block mapping budget exceeded')
    # A closing phrase and its signature can occupy adjacent p/div elements.
    # Keep the complete contiguous original bytes between structural endpoints.
    for start,_,_ in parser.spans:
        for _,end,_ in parser.spans:
            if start<end and end-start<=20000:candidates.add((start,end))
    normalize=lambda s:' '.join(s.split())
    matching=[(a,b) for a,b in candidates if normalize(body_text(fragment[a:b]))==normalize(quote)]
    if not matching:raise ValueError('No exact original block maps to the native witness')
    a,b=min(matching,key=lambda v:(v[1]-v[0],v[0]));a+=base;b+=base
    begin,end=len(text[:a].encode(source['encoding'])),len(text[:b].encode(source['encoding']))
    assert raw[begin:end].decode(source['encoding'])==text[a:b]
    return {'original_byte_span':[begin,end],'original_character_span':[a,b],
            'original_span_sha256':digest(raw[begin:end]),'canonical_quote_sha256':digest(quote.encode())}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['packet','receipt','output']:p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();sources={s['id']:s for s in json.loads((args.packet/'sources.json').read_text())}
    receipt=json.loads(args.receipt.read_text());rows=[];bodies=0
    for case in receipt['cases']:
        records={r['id']:r for r in case['records']}
        for record in records.values():
            source=sources[record['id']];raw=(args.packet/source['path']).read_bytes()
            assert digest(raw)==source['sha256']==record['original_sha256']
            assert record['body']==body_text(frus_rendered(raw,source));bodies+=1
        for claim in case['answer']['claims']:
            if claim['proposition'].get('relation')!='source_signed_letter_instruction':continue
            for cite in claim['citations']:
                record=records[cite['source_id']];source=sources[cite['source_id']]
                assert record['body'][cite['body_start']:cite['body_end']]==cite['quote']
                rows.append({'case':case['id'],'source_id':cite['source_id'],'original_sha256':source['sha256'],
                    **original_span((args.packet/source['path']).read_bytes(),source,cite['quote'])})
    with args.output.open('x') as stream:
        stream.write(json.dumps({'status':'PASS','source_instances_checked':bodies,
            'instruction_witnesses_mapped':len(rows),'witnesses':rows,
            'scope':'Source bytes and projection only; independent historical truth is NOT_RUN.'},indent=2)+'\n')
    print('PASS',bodies,'original projections and',len(rows),'instruction witness mappings')


if __name__=='__main__':main()
