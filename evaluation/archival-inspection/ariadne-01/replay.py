"""Capture the original public 77-case cohort under the selected native reader."""
import gzip
import hashlib
import html
import io
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write

BASE = '6942df4670196405797114cbe25317577c3118e1'
PATH = 'evaluation/archival-inspection/frus-correspondence-01/public-first.zip'
fields = ('kind','answer_supported','claims','missing','verification','diagnostic','documentary_support')
artifact = subprocess.check_output(['git','show',BASE+':'+PATH])
assert hashlib.sha256(artifact).hexdigest() == '895ef4181460bd58ec446c47818860a482ba70276d3a05487dbd0a93767a3331'
capture, archived = {}, {}
with ZipFile(io.BytesIO(artifact)) as archive, TemporaryDirectory() as root:
    for source in json.loads(archive.read('location/corpus.json'))['sources']:
        write(root, doc_id=source['id'],title=source['original_path'],scope='original historical document',
              origin='machine',body_html='<pre>'+html.escape(source['text'])+'</pre>',when='2026-11-16T00:00Z')
    for track in ('location','relation','documentary'):
        for row in json.loads(archive.read(track+'/run.json'))['rows']:
            native = answer_query(root,row['question']).contract
            capture[row['id']] = {name:native.get(name) for name in fields}
            archived[row['id']] = {name:row['strict'].get(name) for name in fields}
assert len(capture)==77
out = Path(sys.argv[1])
with out.open('xb') as f:
    f.write(gzip.compress(json.dumps(capture,ensure_ascii=False,separators=(',', ':')).encode(),mtime=0))
prior = json.loads(gzip.decompress(Path(sys.argv[2]).read_bytes())) if len(sys.argv)>2 else archived
assert set(prior)==set(capture)
changes = {}
for old, name in ((prior,'comparison'),(archived,'historical')):
    changes[name] = [{'id':key,'fields':[f for f in fields if capture[key][f]!=old[key][f]],
                      'before':old[key]['kind'],'after':capture[key]['kind'],
                      'target':[c['proposition'].get('target_source_id') for c in capture[key]['claims']]}
                     for key in capture if capture[key]!=old[key]]
print(json.dumps({'compared':len(capture),'fields':fields,'changes':changes},indent=2))
