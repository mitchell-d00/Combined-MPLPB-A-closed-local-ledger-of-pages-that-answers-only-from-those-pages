"""Pinned original-source study phases; never invent independent human results."""
import argparse
import hashlib
import html
import json
import math
import os
import secrets
from pathlib import Path
import tempfile
import time

from mplpb_combined.ledger import write
from mplpb_answers.body_text import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_work.investigation import investigate

ROOT=Path(__file__).resolve().parents[1]
KEYS=('local-web','smart-paper','combined-v3','combined-v1')


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')


def read(path):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate JSON field')
            result[key]=value
        return result
    raw=Path(path).read_text(encoding='utf-8')
    if len(raw)>20000000:raise ValueError('Study file budget exceeded')
    value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    digest(value)
    return value


def implementation_pins():
    paths=[p for package in ('mplpb_answers','mplpb_combined','mplpb_work') for p in (ROOT/package).glob('*.py')]
    paths.append(Path(__file__))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def prepare(directory):
    directory=Path(directory);directory.mkdir(mode=0o700,parents=True,exist_ok=False)
    manifest=read(ROOT/'docs/research/mplpb-originality/mplpb-sources.json')['sources']
    sources=[]
    for number,key in enumerate(KEYS,1):
        entry=manifest[key];raw=(ROOT/entry['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('Original source pin changed')
        sources.append({'id':'ORIGINAL-%04d'%number,'original_path':entry['path'],
                        'original_ref':entry['revision'],'sha256':entry['sha256'],'text':raw.decode('utf-8')})
    corpus={'schema':'original-record-study-corpus-v1','sources':sources,
            'status':'awaiting_external_questions','independence_verified':False}
    save(directory/'corpus.json',corpus)
    save(directory/'questions-template.json',{'cases':[],
        'instructions':'Supply separately authored questions and gold source expectations before sealing. Do not call developer-inspected questions held out.'})
    return corpus


def validate_corpus(corpus):
    if not isinstance(corpus,dict) or corpus.get('schema')!='original-record-study-corpus-v1':raise ValueError('Unknown corpus schema')
    sources=corpus.get('sources')
    if not isinstance(sources,list) or not 1<=len(sources)<=32:raise ValueError('Invalid source budget')
    ids=set()
    for source in sources:
        if not isinstance(source.get('id'),str) or not source['id'] or source['id'] in ids:raise ValueError('Duplicate or invalid source ID')
        ids.add(source['id'])
        if not isinstance(source.get('text'),str) or len(source['text'])>1000000:raise ValueError('Invalid source text')
        if hashlib.sha256(source['text'].encode()).hexdigest()!=source['sha256']:raise ValueError('Source bytes changed')
    return ids


def seal(directory,questions_path):
    directory=Path(directory);corpus=read(directory/'corpus.json');ids=validate_corpus(corpus)
    cases=read(questions_path).get('cases')
    if not isinstance(cases,list) or not 1<=len(cases)<=200:raise ValueError('Supply 1–200 externally authored questions')
    seen=set();runtime=[];gold=[]
    for case in cases:
        if set(case)!={'id','question','required_source_ids'}:raise ValueError('Unexpected case fields')
        if not isinstance(case['id'],str) or not case['id'] or case['id'] in seen:raise ValueError('Duplicate or invalid case ID')
        seen.add(case['id'])
        if not isinstance(case['question'],str) or not case['question'].strip() or len(case['question'])>4000:raise ValueError('Invalid question')
        required=case['required_source_ids']
        if not isinstance(required,list) or any(not isinstance(i,str) for i in required) or len(set(required))!=len(required) or not set(required)<=ids:raise ValueError('Invalid gold source IDs')
        runtime.append({'id':case['id'],'question':case['question']})
        gold.append({'id':case['id'],'required_source_ids':required})
    private=directory/'private';private.mkdir(mode=0o700,exist_ok=False)
    committed_gold={'salt':secrets.token_hex(32),'cases':gold}
    save(private/'gold.json',committed_gold);os.chmod(private/'gold.json',0o600)
    save(directory/'runtime-questions.json',runtime)
    receipt={'schema':'original-record-study-seal-v1','corpus_sha256':digest(corpus),
             'questions_sha256':digest(runtime),'gold_sha256':digest(committed_gold),
             'implementation_sha256':implementation_pins(),
             'configuration':{'profile':'internal','max_hops':2,'max_sources':12,'max_source_chars':200000,
                              'models_enabled':False,'fixture_record_time':'2026-11-16T00:00Z'},
             'independence_verified':False,'blindness_basis':'gold excluded from runtime payload; filesystem access is not sandboxed'}
    save(directory/'seal.json',receipt)
    return receipt


def pinned(directory):
    directory=Path(directory);corpus=read(directory/'corpus.json');validate_corpus(corpus)
    questions=read(directory/'runtime-questions.json');receipt=read(directory/'seal.json')
    if receipt['schema']!='original-record-study-seal-v1' or digest(corpus)!=receipt['corpus_sha256'] or digest(questions)!=receipt['questions_sha256']:raise ValueError('Sealed inputs changed')
    return corpus,questions,receipt


def execute(directory):
    directory=Path(directory);corpus,questions,receipt=pinned(directory)
    if implementation_pins()!=receipt['implementation_sha256']:raise ValueError('Implementation changed after sealing')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='mplpb-sealed-study-') as root:
        for source in corpus['sources']:
            write(root,doc_id=source['id'],title=source['original_path'],scope='original historical document',origin='machine',
                  body_html='<pre>'+html.escape(source['text'])+'</pre>',when=receipt['configuration']['fixture_record_time'])
        for case in questions:
            start=time.perf_counter();cpu=time.process_time()
            strict=answer_query(root,case['question']).contract
            research=investigate(root,case['question'],max_hops=2,max_sources=12,max_chars=200000)
            rows.append({'id':case['id'],'question':case['question'],'strict':strict,'investigation':research,
                         'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu})
    if pinned(directory)[2]!=receipt or implementation_pins()!=receipt['implementation_sha256']:raise ValueError('Study or implementation changed during execution')
    result={'schema':'original-record-study-run-v1','seal_sha256':digest(receipt),'rows':rows,
            'independence_verified':False,'status':'awaiting_external_review'}
    save(directory/'run.json',result)
    template={'run_sha256':digest(result),'reviewer_id':'',
              'cases':[{'id':r['id'],'complete':None,'false_bridge':None,'source_accurate':None,
                        'labeling_seconds':None,'correction_seconds':None,'citations':[],'rationale':''} for r in rows]}
    save(directory/'review-template.json',template)
    return result


def score(directory,review_paths):
    directory=Path(directory);corpus,questions,receipt=pinned(directory);result=read(directory/'run.json')
    if result['seal_sha256']!=digest(receipt):raise ValueError('Run/seal mismatch')
    expected_questions={q['id']:q['question'] for q in questions}
    if (not isinstance(result.get('rows'),list) or len(result['rows'])!=len(questions)
            or {r.get('id'):r.get('question') for r in result['rows']}!=expected_questions):
        raise ValueError('Run case coverage changed')
    committed_gold=read(directory/'private/gold.json')
    if digest(committed_gold)!=receipt['gold_sha256']:raise ValueError('Gold changed')
    gold=committed_gold['cases']
    if len(review_paths)<2:raise ValueError('At least two separate reviewer submissions required')
    bodies={s['id']:body_text('<pre>'+html.escape(s['text'])+'</pre>') for s in corpus['sources']}
    ids={q['id'] for q in questions};reviewers=set();reviews=[]
    for path in review_paths:
        review=read(path)
        if not isinstance(review,dict):raise ValueError('Expected a review object')
        reviewer=review.get('reviewer_id')
        if not isinstance(reviewer,str) or not reviewer.strip() or reviewer in reviewers:raise ValueError('Distinct named reviewer IDs required')
        reviewers.add(reviewer)
        if review.get('run_sha256')!=digest(result):raise ValueError('Review is for another run')
        cases=review.get('cases')
        if not isinstance(cases,list) or len(cases)!=len(ids) or {c.get('id') for c in cases}!=ids:raise ValueError('Incomplete or duplicate review cases')
        for case in cases:
            if any(type(case.get(k)) is not bool for k in ('complete','false_bridge','source_accurate')):raise ValueError('Explicit reviewer judgments required')
            for field in ('labeling_seconds','correction_seconds'):
                value=case.get(field)
                if type(value) not in (int,float) or not math.isfinite(value) or value<0:raise ValueError('Nonnegative reported review times required')
            if not isinstance(case.get('rationale'),str) or not case['rationale'].strip():raise ValueError('Reviewer rationale required')
            citations=case.get('citations')
            if not isinstance(citations,list) or len(citations)>32 or (case['complete'] and not citations):raise ValueError('Completed answers require source citations')
            for cite in citations:
                if not isinstance(cite,dict) or set(cite)!={'source_id','start','end','quote'}:raise ValueError('Invalid citation fields')
                body=bodies.get(cite['source_id']);a,b=cite['start'],cite['end']
                if body is None or type(a) is not int or type(b) is not int or not 0<=a<b<=len(body) or body[a:b]!=cite['quote']:raise ValueError('Reviewer citation must match pinned source bytes')
        reviews.append({c['id']:c for c in cases})
    disagreements=[i for i in sorted(ids) if len({tuple(r[i][k] for k in ('complete','false_bridge','source_accurate')) for r in reviews})!=1]
    expected={g['id']:set(g['required_source_ids']) for g in gold}
    coverage={}
    for row in result['rows']:
        got={s['id'] for s in row['investigation']['sources']}
        coverage[row['id']]=len(got & expected[row['id']])/len(expected[row['id']]) if expected[row['id']] else None
    output={'schema':'original-record-study-score-v1','seal_sha256':digest(receipt),'run_sha256':digest(result),
            'scorer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'review_sha256':[digest(read(p)) for p in review_paths],
            'status':'adjudication_required' if disagreements else 'review_submissions_agree',
            'disagreements':disagreements,'required_source_coverage':coverage,
            'reviewer_reported_rates':[{'complete':sum(c['complete'] for c in r.values())/len(ids),
                'false_bridge':sum(c['false_bridge'] for c in r.values())/len(ids),
                'source_accurate':sum(c['source_accurate'] for c in r.values())/len(ids)} for r in reviews],
            'reviewer_reported_labeling_seconds':sum(c['labeling_seconds'] for r in reviews for c in r.values()),
            'reviewer_reported_correction_seconds':sum(c['correction_seconds'] for r in reviews for c in r.values()),
            'reviewer_identity_attested':False,'independence_verified':False,
            'notice':'Submission IDs/times are self-reported. Agreement and exact quotations do not attest reviewer independence or certify historical truth.'}
    save(directory/'score.json',output)
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    for command in ('prepare','seal','run','score'):
        p=sub.add_parser(command);p.add_argument('directory',type=Path)
        if command=='seal':p.add_argument('questions',type=Path)
        if command=='score':p.add_argument('reviews',nargs='+',type=Path)
    args=parser.parse_args()
    try:
        value=prepare(args.directory) if args.command=='prepare' else seal(args.directory,args.questions) if args.command=='seal' else execute(args.directory) if args.command=='run' else score(args.directory,args.reviews)
    except (ValueError,OSError,KeyError,TypeError) as exc:parser.exit(2,str(exc)+'\n')
    print(json.dumps({'status':value.get('status','sealed'),'independence_verified':False},indent=2))


if __name__=='__main__':main()
