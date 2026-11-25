"""Check source witnesses against sealed HTML inputs outside the answer worker."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re


def project(raw):
    class Canonical(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True); self.parts=[]
        def handle_starttag(self, tag, attrs):
            # Frozen packets contain plain paragraphs only. Do not silently
            # extend this independent audit to an unknown source encoding.
            if tag != 'p' or attrs:
                raise ValueError('Source shape outside frozen paragraph audit')
            self.parts.append('\n')
        def handle_endtag(self, tag):
            if tag != 'p':
                raise ValueError('Unexpected source close tag')
            self.parts.append('\n')
        def handle_data(self, value):
            self.parts.append(value)
    parser=Canonical(); parser.feed(raw); parser.close()
    return '\n'.join(line for s in ''.join(parser.parts).splitlines()
                     if (line := re.sub(r'[ \t]+',' ',s).strip()))


def audit(inputs, receipt, frozen):
    cases=json.loads(inputs.read_text()); result=json.loads(receipt.read_text())
    seal=json.loads(frozen.read_text())
    digest=hashlib.sha256(inputs.read_bytes()).hexdigest()
    assert digest == seal['cohorts'][result['cohort']]['input_sha256'] == result['input_sha256']
    assert [r['id'] for r in cases] == [r['id'] for r in result['cases']]
    sources=0; witnesses=0
    for case, row in zip(cases,result['cases'],strict=True):
        canonical={s['id']:project(s['body_html']) for s in case['sources']}
        for record in row['records']:
            assert canonical[record['id']] == record['body']; sources+=1
        for claim in row['answer']['claims']:
            for cite in claim['citations']:
                assert canonical[cite['source_id']][cite['body_start']:cite['body_end']] == cite['quote']
                witnesses+=1
    return {'input_sha256':digest, 'sources_verified':sources,'exact_witnesses_verified':witnesses,
            'receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'passed':True,
            'scope':'Separate frozen-input paragraph projection, not independent semantic adjudication.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['inputs','receipt','freeze','output']:
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); result=audit(a.inputs,a.receipt,a.freeze)
    with a.output.open('x') as f:
        f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
