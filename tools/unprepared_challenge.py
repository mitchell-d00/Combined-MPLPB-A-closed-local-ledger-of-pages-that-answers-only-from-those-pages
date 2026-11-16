"""Frozen original-record challenge. Retrieval coverage is not historical accuracy."""
import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import html
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())


def read(path):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('Duplicate JSON key')
            d[k]=v
        return d
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def code_pins(implementation):
    root=Path(implementation).resolve()
    return {str(p.relative_to(root)):sha(p.read_bytes()) for package in ('mplpb_combined','mplpb_answers','mplpb_work')
            for p in sorted((root/package).glob('*.py'))}


def freeze(directory,receipt_name='freeze.json'):
    directory=Path(directory)
    if '/' in receipt_name or not receipt_name.startswith('freeze') or not receipt_name.endswith('.json'):raise ValueError('Invalid freeze receipt name')
    if (directory/receipt_name).exists():raise FileExistsError('Refusing to replace a frozen evaluation')
    cases=read(directory/'questions.json')['cases']
    import re
    if not cases or len(cases)>100 or len({c['id'] for c in cases})!=len(cases):raise ValueError('Invalid case coverage')
    if any(not re.fullmatch(r'[A-Z0-9_-]{1,50}',c['id']) or not isinstance(c['question'],str) or not c['question'].strip() or len(c['question'])>4000 for c in cases):raise ValueError('Invalid runtime case')
    references=read(directory/'reference-draft.json')['cases']
    if len(references)!=len(cases) or {c['id'] for c in references}!={c['id'] for c in cases}:raise ValueError('Reference coverage differs from questions')
    files=['corpus-manifest.json','questions.json','reference-draft.json','protocol.json']
    value={'schema':'unprepared-frozen-v1','files':{p:sha((directory/p).read_bytes()) for p in files},
        'corpus_namespace':read(directory/'corpus-manifest.json')['schema'],
        'baseline_commit':read(directory/'baseline-inventory.json')['git_commit'],
        'baseline_native_sha256':code_pins(ROOT),'harness_sha256':sha(Path(__file__).read_bytes()),
        'importer_sha256':sha((ROOT/'tools/unprepared_sources.py').read_bytes()),
        'question_authorship':'Codex/developer-authored development questions; not independently unseen',
        'independent_human_evaluation':'NOT RUN','historical_reference_completeness':'incomplete_unreviewed_draft'}
    save(directory/receipt_name,value);return value


def frozen(directory,receipt_name='freeze.json'):
    directory=Path(directory);value=read(directory/receipt_name)
    for path,pin in value['files'].items():
        if sha((directory/path).read_bytes())!=pin:raise ValueError('Frozen evidence/rules changed: '+path)
    if sha(Path(__file__).read_bytes())!=value['harness_sha256']:raise ValueError('Evaluation harness changed after freeze')
    if sha((ROOT/'tools/unprepared_sources.py').read_bytes())!=value['importer_sha256']:raise ValueError('Importer changed after freeze')
    from tools.unprepared_sources import verify
    verify(directory)
    return value


@contextmanager
def source_reads(ledger):
    original=Path.read_text;counts={'source_html_bytes_read':0,'source_read_calls':0,'documents':set()}
    root=Path(ledger).resolve()
    def wrapped(path,*args,**kwargs):
        text=original(path,*args,**kwargs)
        if path.suffix=='.html' and path.resolve().is_relative_to(root):
            counts['source_html_bytes_read']+=len(text.encode());counts['source_read_calls']+=1;counts['documents'].add(path.name)
        return text
    Path.read_text=wrapped
    try:yield counts
    finally:Path.read_text=original


def worker(implementation,ledger,case_path,output,mode):
    import resource
    implementation=Path(implementation).resolve();sys.path.insert(0,str(implementation))
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.passages import PassageIndex
    from mplpb_work.investigation import investigate
    from mplpb_combined.reader import terms,PROFILES
    import mplpb_answers.pipeline as pipeline
    if not Path(pipeline.__file__).resolve().is_relative_to(implementation):raise ValueError('Wrong implementation imported')
    case=read(case_path);before=code_pins(implementation)
    start=time.perf_counter();cpu=time.process_time()
    result={'case_id':case['id'],'question':case['question'],'arm':mode,'implementation_sha256':before}
    def checkpoint(stage):
        payload=dict(result,completed_stage=stage,phase_state='provisional_complete_phase_outputs',
            partial_wall_seconds=time.perf_counter()-start,partial_cpu_seconds=time.process_time()-cpu)
        temporary=Path(output).parent/'checkpoint.tmp'
        temporary.write_text(json.dumps(payload,ensure_ascii=False,allow_nan=False))
        temporary.replace(Path(output).parent/'checkpoint.json')
    with source_reads(ledger) as scans:
        if mode in {'baseline','updated'}:
            answer=answer_query(ledger,case['question']).contract
            result['answer']=answer;checkpoint('native_answer')
            if mode=='updated':
                from mplpb_work.prose_evidence import discover
                result['investigation']={'prose_candidates':discover(ledger,case['question'],PROFILES['internal'],max_passages=12,max_chars=12000)}
                checkpoint('candidate_contexts')
            args={'max_hops':2,'max_sources':12,'max_chars':200000}
            if mode=='updated':args['prose_candidates']=True
            investigation=investigate(ledger,case['question'],**args)
            result.update(answer=answer,investigation=investigation)
        else:
            index=PassageIndex(ledger,case['question'],PROFILES['internal'])
            if mode=='bm25':pack=index.retrieve([case['question']],12,12000)
            elif mode=='keyword':
                wanted=terms(case['question']);selected=[];size=0
                for passage in index.passages:
                    if wanted and wanted<=terms(passage['text']) and len(selected)<12 and size+len(passage['text'])<=12000:
                        selected.append(passage);size+=len(passage['text'])
                pack={'passages':selected,'ranking':'conjunctive-keyword-source-order','index_built_from_all_eligible_pages':True}
            else:raise ValueError('Unknown arm')
            result.update(retrieval=pack,answer_supported=False,notice='Actual gated source search execution, not a reconstructed answer or human workflow.')
    wall=time.perf_counter()-start;cpu_seconds=time.process_time()-cpu
    if before!=code_pins(implementation):raise ValueError('Native code changed during execution')
    result.update(case_id=case['id'],question=case['question'],arm=mode,implementation_sha256=before,
        measurements={'wall_seconds':wall,'cpu_seconds':cpu_seconds,'peak_python_allocated_bytes':None,'allocation_tracing':'disabled in primary v2 runs; pilot retained separately',
        'peak_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'rss_scope':'fresh Linux worker including imports; not incremental phase memory',
        'source_html_bytes_read':scans['source_html_bytes_read'],'source_read_calls':scans['source_read_calls'],
        'source_documents_examined':len(scans['documents']),'source_document_paths':sorted(scans['documents']),
        'model_calls':0,'api_charge_usd':0,'compute_charge_usd':None,
        'whole_worker_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
        'human_labeling_seconds':None,'human_correction_seconds':None,'human_review_seconds':None,'human_adjudication_seconds':None})
    save(output,result)


def run(directory,implementation,output,mode,commit,case_limit=None,seal_file='freeze.json'):
    from tools.unprepared_sources import import_corpus
    from tools.study_sandbox import command,_limits
    directory=Path(directory).resolve();implementation=Path(implementation).resolve();output=Path(output).resolve()
    seal=frozen(directory,seal_file);pins=code_pins(implementation)
    if mode=='baseline' and pins!=seal['baseline_native_sha256']:raise ValueError('Baseline implementation is not the pinned unchanged code')
    if not shutil.which('bwrap'):raise ValueError('Real runs require Linux bubblewrap; no direct fallback')
    output.mkdir(exist_ok=False,parents=True)
    cases=read(directory/'questions.json')['cases']
    if case_limit is not None:cases=cases[:case_limit]
    rows=[]
    with tempfile.TemporaryDirectory(prefix='mplpb-unprepared-run-') as temp:
        temp=Path(temp);code=temp/'code';code.mkdir();inputs=temp/'inputs';inputs.mkdir()
        for package in ('mplpb_combined','mplpb_answers','mplpb_work'):
            shutil.copytree(implementation/package,code/package,ignore=shutil.ignore_patterns('__pycache__'))
        (code/'tools').mkdir();shutil.copyfile(__file__,code/'tools/unprepared_challenge.py')
        import_start=time.perf_counter();import_cpu=time.process_time()
        imported=import_corpus(directory,inputs/'ledger')
        import_metrics={'wall_seconds':time.perf_counter()-import_start,'cpu_seconds':time.process_time()-import_cpu,
                        'native_records':len(imported['records']),'raw_source_bytes':sum(s['bytes'] for s in read(directory/'corpus-manifest.json')['sources'])}
        save(output/'import-receipt.json',imported)
        (inputs/'ledger/import-receipt.json').unlink()  # Audit mapping stays outside the execution view.
        for case in cases:
            q=inputs/'question.json';q.write_text(json.dumps({'id':case['id'],'question':case['question']}))
            out=temp/('out-'+case['id']);out.mkdir()
            program="import sys,runpy;sys.argv=['challenge','worker','--implementation','/app','--ledger','/study/ledger','--case','/study/question.json','--output','/output/result.json','--mode',"+repr(mode)+"];runpy.run_path('/app/tools/unprepared_challenge.py',run_name='__main__')"
            started=time.perf_counter();row=None
            try:
                with tempfile.TemporaryFile() as log:
                    process=subprocess.run(command(shutil.which('bwrap'),code,inputs,out,program),stdin=subprocess.DEVNULL,
                        stdout=log,stderr=log,timeout=180,close_fds=True,preexec_fn=_limits)
                    log.seek(0);logtext=log.read(100000).decode(errors='replace')
                (output/(case['id']+'.log')).write_text(logtext)
                if process.returncode:raise ValueError('Worker failed with exit '+str(process.returncode))
                path=out/'result.json'
                if path.is_symlink() or not path.is_file():raise ValueError('Invalid worker output')
                row=read(path)
                if row['implementation_sha256']!=pins or row['case_id']!=case['id']:raise ValueError('Worker identity mismatch')
                row['execution_status']='completed'
            except Exception as exc:
                checkpoint_path=out/'checkpoint.json'
                partial=read(checkpoint_path) if checkpoint_path.is_file() and not checkpoint_path.is_symlink() else {}
                if partial and (partial.get('implementation_sha256')!=pins or partial.get('case_id')!=case['id']):partial={}
                row=dict(partial,**{'case_id':case['id'],'question':case['question'],'arm':mode,'execution_status':'failed',
                    'error':type(exc).__name__+': '+str(exc),'parent_wall_seconds':time.perf_counter()-started,
                    'measurements':None,'answer_supported':False})
                row['execution_status']='partial' if partial else 'failed'
                row['partial_output_notice']='Completed phase output retained; whole investigation did not finish. No semantic success follows from this checkpoint.'
            row['parent_wall_seconds']=time.perf_counter()-started
            if row.get('measurements'):
                scanned=set(row['measurements']['source_document_paths'])
                row['measurements']['original_source_documents_examined']=len({r['original_id'] for r in imported['records'] if r['path'] in scanned})
            save(output/(case['id']+'.json'),row);rows.append(row)
        frozen(directory,seal_file)
        if pins!=code_pins(implementation):raise ValueError('Implementation changed during challenge')
    receipt={'schema':'unprepared-run-v1','arm':mode,'implementation_commit':commit,'implementation_sha256':pins,
        'corpus_namespace':seal['corpus_namespace'],
        'freeze_file':seal_file,'freeze_sha256':sha((directory/seal_file).read_bytes()),'harness_sha256':sha(Path(__file__).read_bytes()),
        'protocol_sha256':seal['files']['protocol.json'],'corpus_sha256':seal['files']['corpus-manifest.json'],
        'questions_sha256':seal['files']['questions.json'],'import':import_metrics,'case_count':len(rows),
        'import_receipt_sha256':sha((output/'import-receipt.json').read_bytes()),
        'cases':[{'id':r['case_id'],'sha256':sha((output/(r['case_id']+'.json')).read_bytes()),'status':r['execution_status']} for r in rows],
        'execution_isolation':{'mechanism':'Linux bubblewrap via existing study sandbox command','network_isolated':True,'private_gold_mounted':False,
            'worker_wall_timeout_seconds':180,'host_admin_trusted':True,'independence_verified':False},
        'independent_human_evaluation':'NOT RUN','evaluation_class':'public_developer_authored_development'}
    from datetime import datetime,timezone
    receipt['completed_at_utc']=datetime.now(timezone.utc).isoformat()
    save(output/'run-receipt.json',receipt);return receipt


def passages(row):
    if 'retrieval' in row:return row['retrieval'].get('passages',[])
    report=row.get('investigation',{})
    return report.get('prose_candidates',{}).get('candidates',[])+report.get('observations',[])


def projections(directory,receipt):
    from tools.unprepared_sources import projected,inside,verify
    from mplpb_answers.body_text import body_text
    sources={s['id']:s for s in verify(directory)['sources']};texts={};out={}
    for record in receipt['records']:
        source=sources[record['original_id']]
        if source['id'] not in texts:texts[source['id']]=projected(source,inside(directory,source['path']).read_bytes())[0]
        full=texts[source['id']];a,b=record['projection_character_start'],record['projection_character_end']
        text=body_text('<pre>'+html.escape(full[a:b])+'</pre>')
        if sha(text.encode())!=record['projection_sha256']:raise ValueError('Projection reconstruction mismatch')
        out[record['id']]=(record,text)
    return out


def covers(passage,reference):
    start=passage.get('body_start',passage.get('start'))
    end=passage.get('body_end',passage.get('end'))
    if end is None and type(start) is int:end=start+len(passage.get('text',passage.get('quote','')))
    return (passage.get('source_id')==reference['source_id'] and type(start) is int and type(end) is int
            and start<=reference['start'] and end>=reference['end'])


def summary(directory,run_directory):
    directory=Path(directory);run_directory=Path(run_directory)
    receipt=read(run_directory/'run-receipt.json');seal_file=receipt.get('freeze_file','freeze.json');frozen(directory,seal_file)
    if receipt['freeze_sha256']!=sha((directory/seal_file).read_bytes()):raise ValueError('Run uses different frozen inputs')
    if receipt['import_receipt_sha256']!=sha((run_directory/'import-receipt.json').read_bytes()):raise ValueError('Import receipt changed')
    original_bodies=projections(directory,read(run_directory/'import-receipt.json'))
    references={c['id']:c for c in read(directory/'reference-draft.json')['cases']};rows=[]
    for entry in receipt['cases']:
        path=run_directory/(entry['id']+'.json')
        if sha(path.read_bytes())!=entry['sha256']:raise ValueError('Run output changed')
        row=read(path);spans=passages(row);expected=references[entry['id']]['citations']
        evidence=spans+[cite for claim in row.get('answer',{}).get('claims',[]) for cite in claim.get('citations',[])]
        hits=[any(covers(p,e) for p in evidence) for e in expected]
        answer=row.get('answer',{});supported=answer.get('answer_supported',False)
        citations=evidence
        valid=0;invalid=[]
        for cite in citations:
            identity=original_bodies.get(cite.get('source_id'));quote=cite.get('quote',cite.get('text',''))
            start=cite.get('body_start',cite.get('start'));end=cite.get('body_end',cite.get('end',start+len(quote) if type(start) is int else None))
            if (identity and cite.get('hash')==identity[0]['hash'] and type(start) is int and type(end) is int
                    and 0<=start<end<=len(identity[1]) and identity[1][start:end]==quote):valid+=1
            else:invalid.append({'source_id':cite.get('source_id'),'reason':'pin/offset/quote mismatch'})
        rows.append({'id':entry['id'],'execution_status':entry['status'],'answer_kind':answer.get('kind'),
            'diagnostic':answer.get('diagnostic',{}).get('code'),'answer_supported':supported,
            'reference_evidence_spans':len(expected),'reference_evidence_spans_retrieved':sum(hits),
            'reference_evidence_span_coverage':sum(hits)/len(hits) if hits else None,
            'semantic_outcome':'unassessed','incorrect_answer':None,'missed_semantic_relationships':None,
            'false_causal_relationships':None,'semantic_judgment':'NOT RUN: requires separate human review',
            'candidate_count':len(spans),'costs':row.get('measurements')})
        rows[-1].update(citations_checked=len(citations),exact_citations_valid=valid,invalid_citations=invalid,
            exact_quote_fidelity=valid/len(citations) if citations else None,
            unsupported_conclusion_structural=bool(supported and (not citations or invalid)))
    return {'schema':'unprepared-automated-summary-v1','arm':receipt['arm'],'run_receipt_sha256':sha((run_directory/'run-receipt.json').read_bytes()),
        'rows':rows,'native_supported_answers':sum(r['answer_supported'] for r in rows),
        'reference_evidence_spans':sum(r['reference_evidence_spans'] for r in rows),
        'reference_evidence_spans_retrieved':sum(r['reference_evidence_spans_retrieved'] for r in rows),
        'scope':'Evidence-span coverage against incomplete developer references is retrieval only, not event/relationship recall.',
        'event_precision':None,'event_recall':None,'relationship_precision':None,'relationship_recall':None,
        'correction_precision':None,'correction_recall':None,'false_positive_relationship_rate':None,
        'chronological_error_count':None,'appropriate_refusal_rate':None,'unsupported_answer_rate':None,
        'independent_human_evaluation':'NOT RUN','review_status':'PENDING'}


def compare(directory,run_directories):
    receipts=[read(Path(r)/'run-receipt.json') for r in run_directories]
    for field in ('corpus_namespace','freeze_sha256','protocol_sha256','corpus_sha256','questions_sha256','import_receipt_sha256'):
        if len({r[field] for r in receipts})!=1:raise ValueError('Comparison inputs differ: '+field)
    if len({tuple(c['id'] for c in r['cases']) for r in receipts})!=1:raise ValueError('Comparison case coverage differs')
    return {'schema':'unprepared-comparison-v1','conditions_matched':True,
        'arms':[summary(directory,r) for r in run_directories],
        'semantic_conclusion':'UNASSESSED: independent review and complete reference graphs NOT RUN',
        'independent_blinded_evaluation':'NOT RUN'}


DIMENSIONS=['event_identification','chronology','citation_fidelity','correction_reconstruction','relationships',
    'unsupported_causality','missing_evidence','refusal_uncertainty','completeness']


def packets(directory,run_directories,output):
    output=Path(output);output.mkdir(exist_ok=False,parents=True);directory=Path(directory)
    first_receipt=read(Path(run_directories[0])/'run-receipt.json');frozen(directory,first_receipt.get('freeze_file','freeze.json'))
    from tools.unprepared_sources import import_corpus
    from mplpb_combined.ledger import Ledger
    from mplpb_answers.body_text import body_text
    (output/'source-projections').mkdir()
    with tempfile.TemporaryDirectory() as temp:
        imported=import_corpus(directory,Path(temp)/'ledger')
        for record in Ledger(Path(temp)/'ledger').records:
            (output/'source-projections'/(record.id+'.txt')).write_text(body_text(record.body_html))
    rows=[]
    for run_dir in run_directories:
        run_dir=Path(run_dir);receipt=read(run_dir/'run-receipt.json');summary(directory,run_dir)
        arm=receipt['arm'];(output/arm).mkdir()
        for entry in receipt['cases']:
            row=read(run_dir/(entry['id']+'.json'))
            packet={'case_id':entry['id'],'arm':arm,'question':row['question'],'output':row,
                'source_manifest':read(directory/'corpus-manifest.json'),'import_receipt':read(run_dir/'import-receipt.json'),
                'reference_draft':next(c for c in read(directory/'reference-draft.json')['cases'] if c['id']==entry['id']),
                'reference_notice':'Incomplete developer draft; reviewer must inspect originals and may reject it.'}
            save(output/arm/(entry['id']+'.packet.json'),packet)
            rows.append({'case_id':entry['id'],'arm':arm,'output_sha256':entry['sha256'],
                'packet_sha256':digest(packet),'judgments':{d:None for d in DIMENSIONS},
                'event':{'tp':None,'fp':None,'fn':None},'relationship':{'tp':None,'fp':None,'fn':None,'negative_opportunities':None},
                'correction':{'tp':None,'fp':None,'fn':None},'reference_scope':None,'reference_complete_within_scope':None,
                'chronological_errors':None,'appropriate_refusal':None,'unsupported_answer':None,'outcome':None,
                'labeling_seconds':None,'correction_seconds':None,'review_seconds':None,'rationale':'','citations':[]})
    template={'schema':'unprepared-human-review-v1','reviewer_id':'','reviewer_is_human':None,
        'independence_attestation':'','items':rows,'status':'NOT RUN'}
    save(output/'review-template.json',template)
    save(output/'STATUS.json',{'independent_review':'NOT RUN','adjudication':'NOT RUN','question_authorship':'developer; not independently unseen',
        'instruction':'Two genuinely separate humans must supply complete judgments; no model personas count as human reviewers.'})
    return template


def score_reviews(packet_directory,review_paths,adjudication_path=None):
    packet_directory=Path(packet_directory);template=read(packet_directory/'review-template.json')
    expected={(i['arm'],i['case_id']):i for i in template['items']}
    if len(review_paths)<2:raise ValueError('At least two human review submissions required')
    reviewers=set();reviews=[];pins=[]
    for path in review_paths:
        review=read(path);identity=review.get('reviewer_id','')
        if not isinstance(identity,str) or not identity.strip() or identity in reviewers or review.get('reviewer_is_human') is not True:
            raise ValueError('Distinct declared human reviewers required')
        if not isinstance(review.get('independence_attestation'),str) or not review['independence_attestation'].strip():raise ValueError('Human independence attestation required')
        reviewers.add(identity);pins.append(digest(review));items=review.get('items',[])
        if len(items)!=len(expected) or {(i['arm'],i['case_id']) for i in items}!=set(expected):raise ValueError('Incomplete or duplicate review coverage')
        mapped={}
        for item in items:
            key=(item['arm'],item['case_id']);original=expected[key]
            if item['output_sha256']!=original['output_sha256'] or item['packet_sha256']!=original['packet_sha256']:raise ValueError('Review is bound to different evidence')
            if set(item['judgments'])!=set(DIMENSIONS) or any(item['judgments'][d] not in {'accurate','partial','incorrect','not_applicable','unassessed'} for d in DIMENSIONS):raise ValueError('Explicit per-dimension judgments required')
            if item['outcome'] not in {'successful','partially_successful','unsuccessful','unassessed'}:raise ValueError('Explicit scientific outcome required')
            if not isinstance(item['rationale'],str) or not item['rationale'].strip():raise ValueError('Review rationale required')
            if type(item['reference_complete_within_scope']) is not bool or not isinstance(item['reference_scope'],str) or not item['reference_scope'].strip():raise ValueError('Reference scope/completeness required')
            for kind in ('event','relationship','correction'):
                for field in ('tp','fp','fn'):
                    if item['outcome']=='unassessed' and item[kind].get(field) is None:continue
                    if type(item[kind].get(field)) is not int or item[kind][field]<0:raise ValueError('Nonnegative semantic counts required')
            n=item['relationship'].get('negative_opportunities')
            if item['outcome']!='unassessed':
                if type(n) is not int or n<item['relationship']['fp']:raise ValueError('Relationship false-positive denominator required')
                if type(item['chronological_errors']) is not int or item['chronological_errors']<0:raise ValueError('Chronological count required')
                if any(type(item[k]) is not bool for k in ('appropriate_refusal','unsupported_answer')):raise ValueError('Explicit refusal/unsupported judgments required')
            if item['outcome']=='successful' and (any(v not in {'accurate','not_applicable'} for v in item['judgments'].values())
                    or any(item[k]['fp'] or item[k]['fn'] for k in ('event','relationship','correction'))
                    or item['chronological_errors'] or item['unsupported_answer']):
                raise ValueError('Successful outcome contradicts submitted errors or omissions')
            if item['outcome']=='partially_successful' and (item['unsupported_answer'] or any(item[k]['fp'] for k in ('event','relationship','correction'))):
                raise ValueError('Partial safe coverage cannot hide false assertions')
            for field in ('labeling_seconds','correction_seconds','review_seconds'):
                value=item.get(field)
                if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or value<0):raise ValueError('Invalid human time')
            packet=read(packet_directory/item['arm']/(item['case_id']+'.packet.json'))
            if digest(packet)!=original['packet_sha256']:raise ValueError('Review packet changed')
            sources={r['id']:r for r in packet['import_receipt']['records']}
            for cite in item['citations']:
                source=sources.get(cite.get('source_id'))
                if not source or cite.get('source_hash')!=source['hash']:raise ValueError('Citation source pin mismatch')
                # Citations are checked against exact immutable original projections.
                original_dir=packet_directory/'source-projections'
                body=(original_dir/(source['id']+'.txt')).read_text()
                if sha(body.encode())!=source['projection_sha256']:raise ValueError('Source projection changed')
                a,b=cite.get('start'),cite.get('end')
                if type(a) is not int or type(b) is not int or not 0<=a<b<=len(body) or body[a:b]!=cite.get('quote'):raise ValueError('Review citation mismatch')
            if item['outcome']!='unassessed' and not item['citations']:raise ValueError('Assessed outcomes require source citations')
            mapped[key]=item
        reviews.append(mapped)
    fields=['judgments','event','relationship','correction','chronological_errors','appropriate_refusal','unsupported_answer','outcome','reference_scope','reference_complete_within_scope']
    disagreements=[key for key in expected if len({digest({f:r[key][f] for f in fields}) for r in reviews})!=1]
    if disagreements and adjudication_path is None:return {'status':'adjudication_required','disagreements':[list(k) for k in disagreements], 'review_sha256':pins,'independence_verified':False}
    accepted=reviews[0]
    if disagreements:
        adj=read(adjudication_path)
        if adj.get('review_sha256')!=pins or not adj.get('adjudicator_id') or not adj.get('rationale') or adj.get('adjudicator_is_human') is not True:raise ValueError('Adjudication needs bound reviews, human identity and rationale')
        # Full adjudicated submissions pass the same validators, rather than an unchecked winner flag.
        decisions=adj.get('accepted_review_sha256',{})
        accepted=dict(accepted)
        for key in disagreements:
            selected=decisions.get(key[0]+':'+key[1])
            if selected not in pins:raise ValueError('Adjudication must explicitly resolve every disagreement')
            accepted[key]=reviews[pins.index(selected)][key]
    arms={}
    for arm in sorted({k[0] for k in expected}):
        all_values=[v for k,v in accepted.items() if k[0]==arm]
        values=[v for v in all_values if v['outcome']!='unassessed'];metrics={}
        for kind in ('event','relationship','correction'):
            tp=sum(v[kind]['tp'] for v in values);fp=sum(v[kind]['fp'] for v in values);fn=sum(v[kind]['fn'] for v in values)
            complete=bool(values) and all(v['reference_complete_within_scope'] for v in values)
            metrics[kind]={'tp':tp if values else None,'fp':fp if values else None,'fn':fn if values else None,'precision':tp/(tp+fp) if tp+fp else None,
                'recall':tp/(tp+fn) if complete and tp+fn else None,'reference_complete_within_declared_scopes':complete}
        neg=sum(v['relationship']['negative_opportunities'] for v in values)
        metrics.update(reference_scopes=[v['reference_scope'] for v in values],
            false_positive_relationship_rate=metrics['relationship']['fp']/neg if neg else None,
            chronological_errors=sum(v['chronological_errors'] for v in values) if values else None,
            appropriate_refusal_rate=sum(v['appropriate_refusal'] for v in values)/len(values) if values else None,
            unsupported_answer_rate=sum(v['unsupported_answer'] for v in values)/len(values) if values else None,
            assessed_case_count=len(values),unassessed_case_count=len(all_values)-len(values),outcomes=dict(Counter(v['outcome'] for v in all_values)))
        arms[arm]=metrics
    times={}
    for field in ('labeling_seconds','correction_seconds','review_seconds'):
        supplied=[item[field] for review in reviews for item in review.values()]
        times[field]={'total_seconds':sum(supplied) if all(v is not None for v in supplied) else None,
            'known_reported_seconds':sum(v for v in supplied if v is not None),'missing_count':sum(v is None for v in supplied),'attested':False}
    return {'reported_human_times':times,'adjudication_seconds':None if adjudication_path is None else adj.get('adjudication_seconds'),
        'status':'adjudicated' if disagreements else 'review_submissions_agree','review_sha256':pins,'arms':arms,
        'reviewer_identity_authenticated':False,'independence_verified':False,
        'notice':'Human/independence attestations are supplied by participants, not authenticated by this software; counts describe declared reference scopes only.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    f=sub.add_parser('freeze');f.add_argument('directory',type=Path);f.add_argument('--receipt',default='freeze.json')
    w=sub.add_parser('worker');w.add_argument('--implementation',required=True);w.add_argument('--ledger',required=True);w.add_argument('--case',required=True);w.add_argument('--output',required=True);w.add_argument('--mode',required=True)
    r=sub.add_parser('run');r.add_argument('directory',type=Path);r.add_argument('--implementation',required=True);r.add_argument('--output',required=True);r.add_argument('--mode',choices=['baseline','updated','bm25','keyword'],required=True);r.add_argument('--commit',required=True);r.add_argument('--case-limit',type=int);r.add_argument('--seal',default='freeze.json')
    s=sub.add_parser('summary');s.add_argument('directory');s.add_argument('run_directory');s.add_argument('--output',required=True)
    k=sub.add_parser('packets');k.add_argument('directory');k.add_argument('runs',nargs='+');k.add_argument('--output',required=True)
    c=sub.add_parser('compare');c.add_argument('directory');c.add_argument('runs',nargs='+');c.add_argument('--output',required=True)
    a=sub.add_parser('score');a.add_argument('packets');a.add_argument('reviews',nargs='+');a.add_argument('--adjudication');a.add_argument('--output',required=True)
    args=p.parse_args()
    if args.command=='freeze':freeze(args.directory,args.receipt)
    elif args.command=='worker':worker(args.implementation,args.ledger,args.case,args.output,args.mode)
    elif args.command=='run':run(args.directory,args.implementation,args.output,args.mode,args.commit,args.case_limit,args.seal)
    elif args.command=='summary':save(args.output,summary(args.directory,args.run_directory))
    elif args.command=='packets':packets(args.directory,args.runs,args.output)
    elif args.command=='compare':save(args.output,compare(args.directory,args.runs))
    else:save(args.output,score_reviews(args.packets,args.reviews,args.adjudication))


if __name__=='__main__':main()
