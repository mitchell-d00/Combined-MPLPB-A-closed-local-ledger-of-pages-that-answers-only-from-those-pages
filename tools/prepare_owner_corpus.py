"""Prepare attributed candidate prose from owner-authorized public repository READMEs.

This does not train a model, approve mixed third-party content, or change MPLPB's
source ledger. Raw prose is not automatically a supervised conversation dataset.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
MAX_SOURCE=2*1024*1024


def fetch(url):
    if not url.startswith(('https://api.github.com/','https://raw.githubusercontent.com/')):
        raise ValueError('Only explicit public GitHub source URLs are supported by this collector')
    with urlopen(Request(url,headers={'User-Agent':'MPLPB-owner-authorized-corpus-preparation'}),timeout=20) as response:
        raw=response.read(MAX_SOURCE+1)
    if len(raw)>MAX_SOURCE:raise ValueError('Source exceeds collection byte budget')
    return raw


def normalized(text):return re.sub(r'\s+',' ',text).casefold().strip()


def frozen_questions(root=ROOT):
    questions=set()
    def walk(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in {'q','question'} and isinstance(item,str) and len(normalized(item))>=20:questions.add(normalized(item))
                else:walk(item)
        elif isinstance(value,list):
            for item in value:walk(item)
    for folder in ('evaluation','killtest','reference_corpus'):
        for path in (Path(root)/folder).rglob('*.json'):
            try:walk(json.loads(path.read_text()))
            except (OSError,ValueError):continue
    return questions


def passages(text,excluded):
    result=[];rejected=0
    for match in re.finditer(r'\S[\s\S]*?(?=\n\s*\n|\Z)',text):
        body=match[0]
        if len(body)>4000:rejected+=1;continue
        if any(question in normalized(body) for question in excluded):rejected+=1;continue
        if len(body.strip())<80:continue
        result.append({'text':body,'start':match.start(),'end':match.end(),
                       'sha256':hashlib.sha256(body.encode()).hexdigest(),
                       'scope':'Exact excerpt; inspect the full source for conditions and context.',
                       'training_status':'candidate_prose_not_reviewed_conversation_data'})
    return result,rejected


def collect(repositories,output,owner,permission,fetcher=fetch,root=ROOT):
    output=Path(output)
    if output.exists():raise ValueError('Choose a new output directory; preserve earlier source snapshots')
    if not permission.strip():raise ValueError('Record the owner permission and scope before collection')
    selected=[r for r in repositories if r.get('owner',{}).get('login')==owner and not r.get('private',r.get('visibility')=='private') and not r.get('fork',False)]
    excluded=frozen_questions(root);output.mkdir(parents=True)
    (output/'sources').mkdir()
    def one(repo):
        name=repo['name'];branch=repo.get('default_branch','main')
        record={'repository':owner+'/'+name,'url':'https://github.com/'+owner+'/'+name,
                'owner_declared_permission':permission,'observed_repository_license':(repo.get('license') or {}).get('spdx_id'),
                'rights_note':'Owner-authorized first-party writing only. Repository ownership/license does not authenticate authorship or approve embedded third-party material.',
                'status':'unavailable'}
        for filename in ('README.md','README.rst'):
            url='https://raw.githubusercontent.com/'+owner+'/'+name+'/'+branch+'/'+filename
            try:raw=fetcher(url)
            except HTTPError as exc:
                if exc.code==404:continue
                record['error']='HTTP '+str(exc.code);return record,[]
            except (OSError,ValueError) as exc:
                record['error']=str(exc);return record,[]
            try:text=raw.decode('utf-8')
            except UnicodeError:
                record['error']='Source is not UTF-8';return record,[]
            chunks,rejected=passages(text,excluded)
            record.update(status='captured_candidate',source_url=url,source_sha256=hashlib.sha256(raw).hexdigest(),
                          bytes=len(raw),branch=branch,filename=filename,excluded_or_oversized_paragraphs=rejected,
                          candidate_passages=len(chunks),text=text)
            return record,[dict(part,source_url=url,source_sha256=record['source_sha256'],repository=record['repository']) for part in chunks]
        record['error']='No supported public root README found';return record,[]
    records=[];all_passages=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for record,chunks in pool.map(one,selected):
            name=hashlib.sha256(record['repository'].encode()).hexdigest()[:16]+'.json'
            (output/'sources'/name).write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
            records.append({k:v for k,v in record.items() if k!='text'});all_passages.extend(chunks)
    with (output/'candidate-passages.jsonl').open('w') as stream:
        for item in all_passages:stream.write(json.dumps(item,ensure_ascii=False)+'\n')
    manifest={'schema':'owner-authorized-candidate-prose-v1','collected_at':datetime.now(timezone.utc).isoformat(),
              'owner':owner,'permission':permission,'repositories_considered':len(selected),
              'sources_captured':sum(r['status']=='captured_candidate' for r in records),'candidate_passages':len(all_passages),
              'frozen_questions_screened':len(excluded),'training_has_run':False,'ready_for_supervised_fine_tuning':False,
              'limitations':['Raw authored prose is not a reviewed conversation dataset.','Exact normalized benchmark overlaps are screened; this is not proof against paraphrase contamination.',
                             'Mixed third-party excerpts and individual rights/attribution still require review.','No existing source ledger, source seal, question, label or historical report is changed.'],
              'sources':records}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner',required=True);p.add_argument('--permission',required=True)
    p.add_argument('--inventory',type=Path,help='Previously fetched public GitHub repositories API JSON')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9-]{1,39}',args.owner):p.error('Invalid owner login')
    if args.inventory:repositories=json.loads(args.inventory.read_text())
    else:
        repositories=[]
        for page in range(1,6):
            rows=json.loads(fetch('https://api.github.com/users/'+args.owner+'/repos?per_page=100&type=owner&page='+str(page)))
            repositories.extend(rows)
            if len(rows)<100:break
    manifest=collect(repositories,args.output,args.owner,args.permission)
    print(json.dumps({k:manifest[k] for k in ('repositories_considered','sources_captured','candidate_passages','frozen_questions_screened','training_has_run','ready_for_supervised_fine_tuning')},indent=2))


if __name__=='__main__':main()
