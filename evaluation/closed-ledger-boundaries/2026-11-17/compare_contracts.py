"""Same fictional inputs in two imports; no historical accuracy scoring."""
import hashlib
import html
import json
import os
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, sys.argv[1])
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
os.environ['MPLPB_NOW'] = '2026-11-17T00:00Z'
rows=[]
cases=[('single-coherent-original', ['Record-ID: CASE-1\nOwner: Alice'], 12),
       ('conflicting-claims', ['Record-ID: CASE-1\nOwner: Alice\nOwner: Bob'], 12),
       ('conflict-exceeds-budget', ['Record-ID: CASE-1\nOwner: Alice\nOwner: Bob'], 1),
       ('missing-field', ['Record-ID: CASE-1\nLocation: archive'], 12),
       ('missing-record', [], 12),
       ('nonconflict-exceeds-budget', ['Record-ID: CASE-1\nOwner: Alice\nOwner: Alice'], 1)]
for key,bodies,budget in cases:
    with tempfile.TemporaryDirectory() as name:
        root=Path(name)
        sources=[]
        for i,body in enumerate(bodies):
            rec=write(root,doc_id='SRC-'+str(i+1),title='Witness',scope='archive record owner location',
                      body_html='<pre>'+html.escape(body)+'</pre>')
            raw=(root/rec.path).read_bytes()
            sources.append({'id':rec.id,'hash':rec.hash,'raw_sha256':hashlib.sha256(raw).hexdigest(),
                            'path':rec.path,'fictional_body':body})
        c=answer_query(root,'What is Owner for record CASE-1?',max_passages=budget).contract
        rows.append({'case':key,'fictional_development_fixture':True,'inputs':sources,'contract':c})
Path(sys.argv[2]).write_text(json.dumps(rows,indent=2)+'\n')
