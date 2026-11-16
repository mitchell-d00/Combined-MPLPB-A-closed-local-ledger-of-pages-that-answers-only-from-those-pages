"""Randomized fictional controls. Execution-payload blind, not independent humans."""
import argparse
import json
import os
from pathlib import Path
import random
import secrets
from tools.unprepared_sources import save,sha,import_corpus
from tools.unprepared_challenge import read,freeze

TOPICS=['lichen photometry','abyssal tribology','cryogenic palynology','muonic interferometry',
        'lunar speleometry','exoplanet rheology','archaeal magnetometry','hadal acoustics',
        'tephra chronometry','polar glycomics','silicate spintronics','mesopelagic optics']


def prepare(directory,private_directory,n=12,seed_file=None):
    if type(n) is not int or not 1<=n<=12:raise ValueError('Choose 1–12 fictional rare-topic domains')
    directory=Path(directory);directory.mkdir(exist_ok=False,parents=True);(directory/'originals').mkdir()
    private=Path(private_directory).resolve()
    if private.is_relative_to(Path(__file__).resolve().parents[1]):raise ValueError('Private seed must remain outside repository')
    private.mkdir(mode=0o700,exist_ok=False,parents=True)
    material=read(seed_file) if seed_file else {'seed':secrets.token_hex(32),'salt':secrets.token_hex(32)}
    seed=material['seed'];salt=material['salt'];rng=random.Random(seed)
    seed_path=private/'seed.json';save(seed_path,{'seed':seed,'salt':salt});os.chmod(seed_path,0o600)
    topics=rng.sample(TOPICS,n);colors=['blue','red','green','amber','purple','teal'];sources=[];cases=[];gold=[]
    for index,topic in enumerate(topics,1):
        entity=''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(9))+' '+topic
        color=rng.choice(colors);body='The '+entity+' color is '+color+'.'
        conflict=index%4==0
        contents=[body]
        if conflict:contents.append('The '+entity+' color is '+rng.choice([c for c in colors if c!=color])+'.')
        ids=[]
        for text in contents:
            sid='CONTROL-%04d'%(len(sources)+1);path='originals/'+sid+'.txt';(directory/path).write_text(text+'\n');raw=(directory/path).read_bytes()
            sources.append({'id':sid,'url':'https://example.invalid/fictional-control/'+sid,'path':path,'bytes':len(raw),'sha256':sha(raw),
                'encoding':'utf-8','media_type':'text/plain','rights_basis':'Developer-authored fictional randomized test control; CC0; not historical source material'})
            ids.append('ORIGINAL-%04d'%len(sources))
        positive='S%02d-COLOR'%index;negative='S%02d-CAUSE'%index
        cases.extend([{'id':positive,'category':'randomized_positive_or_conflict','question':'What is the '+entity+' color?'},
                      {'id':negative,'category':'unsupported_causality','question':'Did '+entity+' cause a distant archive collapse?'}])
        citations=[]
        for rid,text in zip(ids,contents):citations.append({'source_id':rid,'start':0,'end':len(text),'quote':text})
        gold.extend([{'id':positive,'expected_kind':'conflict' if conflict else 'supported_answer','expected_support':not conflict,
                      'expected_quote':body,'expectation_draft':'Fictional native finite-grammar control','citations':citations},
                     {'id':negative,'expected_kind':'abstain','expected_support':False,'expected_quote':None,
                      'expectation_draft':'No causal relation was declared in the fictional sources','citations':citations}])
    manifest={'schema':'synthetic-control-corpus-v1','baseline_commit':'614b18cc34f5270d4cb7dfbbf8239391a9f83b31',
        'generator_sha256':sha(Path(__file__).read_bytes()),
        'source_kind':'synthetic fictional controls','sources':sources,'provenance_files':[],
        'independent_human_blinding':False,'private_seed_commitment':sha((salt+seed).encode()),
        'purpose':'Random withheld-answer controls; not authentic historical evaluation or independent question authorship'}
    save(directory/'corpus-manifest.json',manifest)
    save(directory/'questions.json',{'authorship':'Developer-generated randomized; not independently unseen','cases':cases})
    save(directory/'reference-draft.json',{'synthetic_expected_outcomes':True,'cases':gold})
    save(directory/'baseline-inventory.json',{'git_commit':manifest['baseline_commit']})
    save(directory/'protocol.json',{'schema':'randomized-controls-protocol-v1','topics':topics,'n':n,
        'scoring':'Exact native contract kind/support plus source quote for positives; no semantic historical claim.',
        'same_corpus_for_baseline_and_updated':True,'independent_review':'NOT RUN',
        'blinding_scope':'Only runtime input separation; developer authored generator and sees source facts.',
        'seed_release':'After all planned baseline/updated executions, append released-seed.json; never claim human independence.'})
    freeze(directory)


def score(directory,run_directory):
    directory=Path(directory);run_directory=Path(run_directory)
    expected={c['id']:c for c in read(directory/'reference-draft.json')['cases']};receipt=read(run_directory/'run-receipt.json')
    if receipt['corpus_namespace']!='synthetic-control-corpus-v1':raise ValueError('Authentic results cannot be scored as synthetic controls')
    if receipt['arm'] not in {'baseline','updated'}:raise ValueError('Search comparators are not answer-generating control arms')
    if receipt['freeze_sha256']!=sha((directory/receipt.get('freeze_file','freeze.json')).read_bytes()):raise ValueError('Synthetic inputs changed')
    rows=[]
    for entry in receipt['cases']:
        if sha((run_directory/(entry['id']+'.json')).read_bytes())!=entry['sha256']:raise ValueError('Synthetic output changed')
        row=read(run_directory/(entry['id']+'.json'));gold=expected[entry['id']];answer=row.get('answer',{})
        correct=(answer.get('kind')==gold['expected_kind']
                 and answer.get('answer_supported')==gold['expected_support'])
        if gold['expected_support']:correct=correct and gold['expected_quote'] in answer.get('text','')
        rows.append({'id':entry['id'],'expected_kind':gold['expected_kind'],'observed_kind':answer.get('kind'),
                     'expected_support':gold['expected_support'],'observed_support':answer.get('answer_supported'),
                     'native_contract_matches':bool(correct),'whole_pipeline_completed':row['execution_status']=='completed',
                     'control_outcome':'successful' if correct and row['execution_status']=='completed' else 'partially_successful' if correct else 'unsuccessful','semantic_historical_accuracy':None})
    return {'scope':'Randomized synthetic finite-contract controls only; NOT independently blinded historical evaluation',
        'arm':receipt['arm'],'rows':rows,'successful':sum(r['control_outcome']=='successful' for r in rows),'total':len(rows),
        'independent_human_evaluation':'NOT RUN'}


def release_seed(directory,private_directory,run_directories):
    directory=Path(directory)
    for run in run_directories:
        receipt=read(Path(run)/'run-receipt.json')
        if receipt['corpus_namespace']!='synthetic-control-corpus-v1':raise ValueError('Wrong evaluation arm')
    if {read(Path(r)/'run-receipt.json')['arm'] for r in run_directories}!={'baseline','updated'}:
        raise ValueError('Both baseline and updated executions are required before seed release')
    seed=read(Path(private_directory)/'seed.json');manifest=read(directory/'corpus-manifest.json')
    if sha((seed['salt']+seed['seed']).encode())!=manifest['private_seed_commitment']:raise ValueError('Seed commitment mismatch')
    save(directory/'released-seed.json',dict(seed,release_basis='Baseline/updated runs completed; synthetic control material is now public',
        run_receipts_sha256=[sha((Path(r)/'run-receipt.json').read_bytes()) for r in run_directories]))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','score','release'])
    p.add_argument('directory');p.add_argument('--private');p.add_argument('--runs',nargs='+');p.add_argument('--n',type=int,default=12);p.add_argument('--output');p.add_argument('--seed-file');a=p.parse_args()
    if a.command=='prepare':prepare(a.directory,a.private,a.n,a.seed_file)
    elif a.command=='score':save(a.output,score(a.directory,a.runs[0]))
    else:release_seed(a.directory,a.private,a.runs)


if __name__=='__main__':main()
