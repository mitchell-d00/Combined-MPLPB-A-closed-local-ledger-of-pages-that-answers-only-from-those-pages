"""Byte-preserving public-source acquisition and non-answer-bearing native import."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'evaluation/unprepared-originals/2026-11-16'


def sha(data):return hashlib.sha256(data).hexdigest()


def load(path):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('Duplicate JSON key')
            out[k]=v
        return out
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,
        parse_constant=lambda v:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def inside(root,relative):
    path=(Path(root)/relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):raise ValueError('Path escapes source package')
    return path


def verify(directory):
    directory=Path(directory);manifest=load(directory/'corpus-manifest.json')
    if manifest['schema'] not in {'unprepared-public-corpus-v1','synthetic-control-corpus-v1'}:raise ValueError('Unknown corpus manifest')
    ids=set()
    for source in manifest['sources']+manifest['provenance_files']:
        if source['id'] in ids:raise ValueError('Duplicate source identity')
        ids.add(source['id'])
        raw=inside(directory,source['path']).read_bytes()
        if len(raw)!=source['bytes'] or sha(raw)!=source['sha256']:raise ValueError('Original bytes changed: '+source['id'])
        if not source.get('rights_basis') or not source['url'].startswith('https://'):raise ValueError('Missing public access/rights record')
    return manifest


def acquire(directory,output):
    """Re-fetch frozen public URLs; never silently accept changed publisher bytes."""
    manifest=verify(directory);output=Path(output);output.mkdir(exist_ok=False,parents=True)
    if manifest['schema']!='unprepared-public-corpus-v1':raise ValueError('Synthetic controls are not public archive acquisitions')
    receipts=[]
    for item in manifest['sources']+manifest['provenance_files']:
        url=item['url'];parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='https' or parsed.username or parsed.password or parsed.hostname not in {
            'raw.githubusercontent.com','www.archives.gov','www.loc.gov','ntrs.nasa.gov'}:
            raise ValueError('Unapproved public acquisition origin')
        request=urllib.request.Request(url,headers={'User-Agent':'MPLPB-unprepared-original-study/1.0'})
        row={'id':item['id'],'url':url,'started_at':datetime.now(timezone.utc).isoformat()}
        try:
            with urllib.request.urlopen(request,timeout=45) as response:
                final=urllib.parse.urlsplit(response.url)
                if final.scheme!='https' or final.hostname!=parsed.hostname:raise ValueError('Cross-origin redirect rejected')
                raw=response.read(8000001)
                if len(raw)>8000000 or sha(raw)!=item['sha256']:raise ValueError('Acquired bytes differ from frozen source')
                path=inside(output,item['path']);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
                row.update(status='verified',sha256=sha(raw),bytes=len(raw))
        except Exception as exc:row.update(status='failed',error=type(exc).__name__+': '+str(exc))
        receipts.append(row)
    save(output/'acquisition-receipt.json',{'attempts':receipts,'all_verified':all(r['status']=='verified' for r in receipts)})
    return receipts


def projected(source,raw):
    from mplpb_answers.body_text import body_text
    text=raw.decode(source['encoding'])
    if source['media_type']=='text/html':
        match=re.search(r'<body\b[^>]*>([\s\S]*)</body\s*>',text,re.I)
        if not match:raise ValueError('HTML source has no unique body envelope')
        fragment=match[1]
        return body_text(fragment),fragment,{'operation':'body envelope selection only; source body markup retained',
            'raw_character_start':match.start(1),'raw_character_end':match.end(1)}
    return body_text('<pre>'+html.escape(text)+'</pre>'),None,{'operation':'declared character decoding, HTML escape and existing canonical body projection'}


def import_corpus(directory,output):
    from mplpb_combined.ledger import write
    from mplpb_answers.body_text import body_text, VERSION
    directory=Path(directory);manifest=verify(directory);output=Path(output);output.mkdir(exist_ok=False,parents=True)
    records=[];ordinal=0
    for source in manifest['sources']:
        text,fragment,operation=projected(source,inside(directory,source['path']).read_bytes())
        # Fixed character cuts, chosen before questions; never a semantic/event split.
        spans=[(0,len(text))] if fragment is not None else [(a,min(a+450000,len(text))) for a in range(0,len(text),450000)]
        for begin,end in spans:
            ordinal+=1;identifier='ORIGINAL-%04d'%ordinal
            inner=fragment if fragment is not None else '<pre>'+html.escape(text[begin:end])+'</pre>'
            title=('Imported original ' if manifest['schema']=='unprepared-public-corpus-v1' else 'Synthetic control ')+identifier
            scope='public historical records' if manifest['schema']=='unprepared-public-corpus-v1' else 'fictional rare topic controls'
            rec=write(output,doc_id=identifier,title=title,scope=scope,
                origin='machine',body_html=inner,when='2026-11-16T00:00Z')
            body=body_text(rec.body_html)
            records.append({'id':rec.id,'path':rec.path,'hash':rec.hash,'original_id':source['id'],
                'original_sha256':source['sha256'],'original_url':source['url'],'projection_sha256':sha(body.encode()),
                'projection_character_start':begin,'projection_character_end':end,'canonical_characters':len(body),
                'transformation':operation,'projection_version':VERSION,
                'wrapper_fields_added':{'document-id':identifier,'title':title,
                    'scope':scope,'origin':'machine','origin-depth':1,'status':'current',
                    'updated':'2026-11-16T00:00Z','hash':rec.hash,'derived-from':'','supersedes':''},
                'wrapper_metadata_is_source_authored':False,'answer_fields_added':False})
    receipt={'schema':'unprepared-native-import-v1','corpus_manifest_sha256':sha((directory/'corpus-manifest.json').read_bytes()),
        'corpus_namespace':manifest['schema'],
        'records':records,'notes':['Titles, scope, IDs, depth and time are import bookkeeping only.',
        'Original content is not rewritten into Event-ID, Related, Corrects or answer labels.',
        'Modern editorial framing, OCR errors, layout loss in canonical text and fixed chunk boundaries are retained limitations.']}
    save(output/'import-receipt.json',receipt);return receipt


def prepare_study(directory,output):
    """Use the existing salted study protocol for separately authored questions."""
    from tools.historical_study import save as study_save
    from mplpb_answers.body_text import body_text
    import tempfile
    output=Path(output);output.mkdir(exist_ok=False,parents=True)
    with tempfile.TemporaryDirectory() as temp:
        ledger=Path(temp)/'ledger';receipt=import_corpus(directory,ledger)
        from mplpb_combined.ledger import Ledger
        by_id={r.id:r for r in Ledger(ledger).records}
        sources=[{'id':r['id'],'original_path':r['original_url'],'original_ref':r['original_sha256'],
            'sha256':r['projection_sha256'],'text':body_text(by_id[r['id']].body_html)} for r in receipt['records']]
    study_save(output/'corpus.json',{'schema':'original-record-study-corpus-v1','sources':sources,
        'status':'awaiting_external_questions','independence_verified':False})
    study_save(output/'questions-template.json',{'cases':[],'instructions':'Separately authored questions only; keep gold private; no synthetic or developer-authored questions may be called independent.'})
    study_save(output/'import-receipt.json',receipt)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['verify','acquire','import','prepare-study'])
    p.add_argument('directory',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.command=='verify':print(json.dumps({'sources':len(verify(a.directory)['sources'])}))
    elif a.output is None:p.error('--output is required')
    elif a.command=='acquire':acquire(a.directory,a.output)
    elif a.command=='import':import_corpus(a.directory,a.output)
    else:prepare_study(a.directory,a.output)


if __name__=='__main__':main()
