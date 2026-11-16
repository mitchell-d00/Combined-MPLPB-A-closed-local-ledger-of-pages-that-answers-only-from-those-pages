"""Public, inspectable development challenge with safety and capability scores.

All fixtures below are fictional. Missing capabilities are recorded as gaps,
never counted as successful answers. No private fixture or external-model score
is reproduced. Run this file under another checkout's PYTHONPATH to compare code.
"""
import argparse
from collections import Counter
import hashlib
import html
import json
import os
from pathlib import Path
import tempfile
import time
import tracemalloc
import subprocess
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers import pipeline
from mplpb_combined.ledger import write, revise, Ledger
from mplpb_combined.reader import PROFILES
from mplpb_answers.body_text import body_text
try:
    from mplpb_work.investigation import investigate
except ImportError:
    investigate=None
try:
    from mplpb_work.event_candidates import inspect_events
    from mplpb_answers.corrections import correct_claim
except ImportError:
    inspect_events=None
    correct_claim=None

SUITE=Path(__file__).resolve().parents[1]/'evaluation/historical-experts/public-cases.json'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def extension(case,root):
    """Execute the published boundary variations without private fixture input."""
    key=case['id'];observed={}
    if key=='diagnostic-known-conflict':
        write(root,doc_id='CONFLICT-0001',title='Conflict',scope='archival records',body='Instrument is located in East Room. Instrument is not located in East Room.')
        observed=answer_query(root,'Where is instrument located?').contract
        return observed['kind'],observed
    if key=='diagnostic-invalid-question':
        try:
            if investigate is not None:investigate(root,'')
            else:answer_query(root,'')
        except ValueError:return 'invalid_question',{'rejected':True}
        return 'invalid_question_accepted',{'rejected':False}
    if key.startswith('event-'):
        if inspect_events is None:return 'extension_unavailable',observed
        for n in (1,2):
            event='EVENT-202' if key=='event-subject-collision' and n==2 else 'EVENT-101'
            event_line='' if key=='event-no-id' else 'Event-ID: '+event+'\n'
            message='MSG-202' if key=='event-subject-collision' and n==2 else 'MSG-101'
            text=('Subject: Equal subject\n'+event_line+'Message-ID: '+message+'\nDate: 1904-05-01\nBody: '
                  +('Changed destination.' if key=='event-message-changed' and n==2 else 'Original destination.'))
            rec=write(root,doc_id='EVT-%04d'%n,title='Equal subject',scope='archival records',
                      body_html='<pre>'+html.escape(text)+'</pre>',
                      external='no' if key=='event-restricted' else '',
                      not_for='sensitive' if key=='event-excluded' else '')
            if key=='event-body-tamper':
                p=root/rec.path;p.write_text(p.read_text().replace('Original destination','Changed destination'))
        profile=PROFILES['external'] if key=='event-restricted' else PROFILES['internal']
        observed=inspect_events(root,'sensitive archival records' if key=='event-excluded' else 'archival records',profile)
        groups=observed['candidates']
        if key=='event-subject-collision':ok=len(groups)==2;actual='separate_candidates'
        elif key=='event-no-id':ok=not groups and len(observed['unassigned_occurrences'])==2;actual='unassigned_occurrences'
        elif key=='event-message-duplicates':ok=len(groups)==1 and len(groups[0]['occurrences'])==2 and not groups[0]['changed_message_body'];actual='candidate_with_two_occurrences'
        elif key=='event-message-changed':ok=len(groups)==1 and groups[0]['status']=='needs_review';actual='needs_review'
        elif key=='event-date-basis':ok=len(groups)==1 and all(o['source_stated_date']=='1904-05-01' for o in groups[0]['occurrences']);actual='source_stated_date_preserved'
        else:ok=not groups;actual='source_unavailable'
        return actual if ok else 'event_boundary_failed',observed
    if key.startswith('correction-'):
        if correct_claim is None:return 'extension_unavailable',observed
        text='Mira owns observatory. The observatory is located in North Field.'
        if key=='correction-ambiguous-span':text+=' Mira owns observatory.'
        if key=='correction-history':text='Document ID: CORRECTION-101\nUpdated: 1900-01-01 v1\n'+text
        rec=write(root,doc_id='SRC-0001',title='Correction witness',scope='archival records',body_html='<pre>'+html.escape(text)+'</pre>',
                  external='no' if key=='correction-external' else '')
        if key=='correction-source-stale':revise(root,rec.id,body='Sol owns observatory.')
        if key=='correction-no-implicit-write':
            if investigate is None:return 'extension_unavailable',observed
            before={p.name:sha(p.read_bytes()) for p in root.glob('*.html')}
            observed=investigate(root,'archival records',start_source_ids=[rec.id])
            after={p.name:sha(p.read_bytes()) for p in root.glob('*.html')}
            return 'source_unchanged' if before==after else 'implicit_source_write',observed
        old='' if key=='correction-empty-span' else 'Absent phrase.' if key=='correction-missing-span' else 'Mira owns observatory.'
        effective='invalid date' if key=='correction-invalid-date' else '1905-01-01'
        try:
            observed=correct_claim(root,rec.id,old,'Sol owns observatory.',effective_at=effective,
                                   profile=PROFILES['external'] if key=='correction-external' else None)
        except ValueError:return 'rejected',{'rejected':True}
        history=Ledger(root).history(rec.id)
        observed['history']=[{'id':r.id,'text':r.text} for r in history]
        exact_preserved=(len(history)==2 and body_text(history[-1].body_html)==text.replace('Mira owns observatory.','Sol owns observatory.'))
        observed['unaffected_projection_exact']=exact_preserved
        return 'predecessor_and_successor' if key=='correction-history' and exact_preserved and 'Mira owns' in history[0].text else 'unexpected_correction',observed
    if investigate is None:return 'extension_unavailable',observed
    field='Supersedes' if key=='crawl-conditional-supersedes' else 'Related'
    target=('If approved, CASE-202 v1' if 'conditional' in key else 'Unnamed companion' if key=='crawl-generic-title'
            else 'CASE-202 v2' if key=='crawl-version-miss' else 'CASE-202 v1')
    write(root,doc_id='SRC-0001',title='Crawl seed',scope='archival records',
          body_html='<pre>Document ID: CASE-101\nUpdated: 1900-01-01 v1\n'+field+': '+target+'</pre>')
    if key!='crawl-unavailable-target':
        write(root,doc_id='SRC-0002',title='Crawl target',scope='archival records',
              body_html='<pre>Document ID: CASE-202\nUpdated: 1900-01-01 v1\n'+('Related: CASE-101 v1' if key=='crawl-cycle' else '')+'</pre>',
              external='no' if key=='crawl-private-target' else '',not_for='sensitive' if key=='diagnostic-query-preserved' else '')
    options={}
    if key=='crawl-zero-hop':options['max_hops']=0
    if key=='crawl-one-source':options['max_sources']=1
    if key=='crawl-private-target':options['profile']=PROFILES['external']
    if key=='diagnostic-budget-input':options['max_hops']=-1
    if key=='receipt-private-recovery':options['work_directory']=root.parent/(root.name+'-work')
    question='sensitive archival records' if key=='diagnostic-query-preserved' else 'archival records'
    if key=='diagnostic-invalid-question':question=''
    try:observed=investigate(root,question,start_source_ids=['SRC-0001'],**options)
    except ValueError:return 'invalid_question' if not question else 'invalid_budget',{'rejected':True}
    relations=observed['relations'];first=relations[0]['status'] if relations else 'no_relation'
    if key.startswith('crawl-'):
        if 'conditional' in key:actual='unexpanded_qualified_relation' if first=='unresolved_target_identifier' else first
        elif key=='crawl-cycle':actual='bounded_cycle' if len(observed['sources'])==2 and len(relations)==2 else 'cycle_failed'
        else:actual=first
        return actual,observed
    if key=='diagnostic-query-preserved':return 'original_question_preserved' if observed['question']==question and first=='target_unavailable' else 'query_changed',observed
    if key=='receipt-three-experts':return 'three_receipts' if len(observed['receipts'])==3 and all(r['status']=='passed' for r in observed['receipts']) else 'missing_receipt',observed
    if key=='receipt-no-provider':return 'local_software_roles' if all('local software' in e['implementation'] for e in observed['experts']) else 'unknown_provider',observed
    if key=='receipt-no-completion-promotion':return 'not_a_supported_answer' if not observed['answer_supported'] and not observed['truth_verified'] else 'unsupported_receipt_promotion',observed
    if key=='receipt-private-recovery':
        credential=options['work_directory']/'host-credential.json'
        private=(credential.stat().st_mode & 0o077)==0
        token=json.loads(credential.read_text())['authority_credential']
        return 'private_recoverable_work' if private and token not in json.dumps(observed) else 'credential_exposure',observed
    raise ValueError('Unknown public extension case: '+key)


def run(cases_path=SUITE):
    manifest_raw=Path(cases_path).read_bytes()
    manifest=json.loads(manifest_raw)
    rows=[]
    fixture_time=manifest.get('fixture_record_time','2000-01-01T00:00Z')
    with tempfile.TemporaryDirectory(prefix='mplpb-public-evidence-') as temporary, patch.dict(os.environ,{'MPLPB_NOW':fixture_time}):
        base=Path(temporary)
        def page(root,id='SRC-0001',body='Mira owns observatory.',**kwargs):
            return write(root,doc_id=id,title='Public fictional archive',scope='archival records',body=body,**kwargs)
        def docs(root,duplicate=False,missing=False,negative=False):
            for id,doc,related in [('SRC-0001','CASE-101',('Not related to ' if negative else '')+'CASE-202 v1'),
                                    ('SRC-0002','CASE-202','')]:
                if missing and id=='SRC-0002':continue
                text='Document ID: '+doc+'\nUpdated: 1900-01-01 v1\n'+('Related: '+related+'\n' if related else '')
                write(root,doc_id=id,title='Same subject',scope='archival records',body_html='<pre>'+html.escape(text)+'</pre>')
            if duplicate:
                write(root,doc_id='SRC-0003',title='Same subject',scope='archival records',
                      body_html='<pre>Document ID: CASE-202\nUpdated: 1900-01-01 v1\n</pre>')
        def research(root,**kwargs):
            if investigate is None:return {'status':'unavailable','sources':[],'relations':[],'answer_supported':False,'receipts':[]}
            return investigate(root,'Inspect archival records and declared relations',start_source_ids=['SRC-0001'],**kwargs)
        for case in manifest['cases']:
            root=base/case['id'];root.mkdir()
            observed={}
            scanned=[0];reads=[0]
            original_read=Path.read_text
            def counted_read(path,*args,**kwargs):
                value=original_read(path,*args,**kwargs)
                try:path.resolve().relative_to(root.resolve())
                except ValueError:return value
                scanned[0]+=len(value.encode('utf-8'));reads[0]+=1
                return value
            started=time.perf_counter();cpu=time.process_time();tracemalloc.start()
            with patch.object(Path,'read_text',new=counted_read):
                key=case['id']
                if key=='authority-corrupt':
                    rec=page(root);p=root/rec.path;p.write_text(p.read_text().replace('Mira owns','Sol owns'))
                    r=answer_query(root,'Who owns observatory?').contract
                    actual='no_supported_answer' if not r['answer_supported'] else 'unsafe_supported_answer';observed=r
                elif key=='authority-restricted':
                    page(root,external='no');r=answer_query(root,'Who owns observatory?',PROFILES['external']).contract
                    actual='no_supported_answer' if not r['answer_supported'] else 'unsafe_supported_answer';observed=r
                elif key=='authority-conflict':
                    page(root);page(root,'SRC-0002','Mira does not own observatory.')
                    r=answer_query(root,'Who owns observatory?').contract;actual=r['kind'];observed=r
                elif key in {'diagnostic-grammar','diagnostic-absence','diagnostic-evidence'}:
                    if key!='diagnostic-absence':page(root,body='The archive holds reference material.')
                    question='Explain the sequence of archival negotiations' if key=='diagnostic-grammar' else 'Who owns observatory?'
                    r=answer_query(root,question).contract;actual=r['diagnostic']['code'];observed=r
                elif key=='diagnostic-exhaustion':
                    docs(root);r=research(root,max_sources=1)
                    actual='explicit_budget_stop' if r.get('stops') and any(e['status']=='source_or_character_budget' for e in r['relations']) else 'unavailable_or_undifferentiated';observed=r
                elif key.startswith('exact-route-'):
                    docs(root,duplicate=key=='exact-route-many')
                    if key=='exact-route-zero':
                        try:
                            if investigate is None:actual='unavailable'
                            else:investigate(root,'archival records',start_source_ids=['ABSENT-999']);actual='substituted'
                        except ValueError:actual='unavailable'
                        observed={'requested_source_id':'ABSENT-999','result':actual}
                    else:
                        r=research(root);actual=r['relations'][0]['status'] if r['relations'] else 'expert_path_unavailable';observed=r
                elif key=='contradiction-not-pruned':
                    docs(root);page(root,'SRC-0003','Mira owns observatory. Mira does not own observatory.')
                    r=research(root);strict=answer_query(root,'Who owns observatory?').contract
                    actual='no_supported_answer' if not r['answer_supported'] and not strict['answer_supported'] else 'unsafe_supported_answer'
                    observed={'investigation':r,'independent_strict_check':strict}
                elif key in {'event-occurrences','event-candidates'}:
                    message='Subject: Transfer notice\nEvent-ID: EVENT-101\nMessage-ID: MSG-101\nBody: Arin authorized moving crate C7 to Depot East.'
                    write(root,doc_id='SRC-0001',title='Transfer notice',scope='archival records',body_html='<pre>'+html.escape(message)+'</pre>')
                    write(root,doc_id='SRC-0002',title='Transfer notice',scope='archival records',body_html='<pre>'+html.escape(message)+'</pre>')
                    if key=='event-candidates':
                        write(root,doc_id='SRC-0003',title='Transfer notice',scope='archival records',body_html='<pre>'+html.escape(message.replace('Depot East','Depot West'))+'</pre>')
                    records=Ledger(root).servable()
                    observed={'source_occurrences':[{'id':r.id,'hash':r.hash_actual} for r in records],
                              'event_candidate_schema':None,'changed_body_review':None}
                    if key=='event-candidates' and inspect_events is not None:
                        events=inspect_events(root,'archival records')
                        observed['event_candidate_schema']=events['version'];observed['event_candidates']=events
                        observed['changed_body_review']=any(c['changed_message_body'] for c in events['candidates'])
                        actual='typed_event_candidate_with_review' if observed['changed_body_review'] and len(events['candidates'])==1 and len(events['candidates'][0]['occurrences'])==3 else 'event_identity_incomplete'
                    else:actual='two_source_occurrences' if key=='event-occurrences' and len(records)==2 else 'typed_event_identity_unimplemented'
                elif key=='partial-correction':
                    rec=page(root,body='Mira owns observatory. The observatory is located in North Field.')
                    if correct_claim is not None:
                        correction=correct_claim(root,rec.id,'Mira owns observatory.','Sol owns observatory.',effective_at='1905-01-01')
                    else:
                        revise(root,rec.id,body='Sol owns observatory.');correction=None
                    owner=answer_query(root,'Who owns observatory?').contract
                    location=answer_query(root,'Where is observatory located?').contract
                    observed={'owner':owner,'unaffected_location':location,'history_versions':len(Ledger(root).history(rec.id)),'explicit_scoped_correction':correction}
                    actual='scoped_correction_with_unaffected_fact' if owner['answer_supported'] and location['answer_supported'] else 'whole_document_revision_not_claim_scoped'
                elif key in {'missing-bridge','negated-bridge'}:
                    docs(root,missing=key=='missing-bridge',negative=key=='negated-bridge');r=research(root)
                    unresolved=bool(r['relations']) and all(e['status']!='traversed' for e in r['relations'])
                    actual=('unresolved_without_supported_answer' if unresolved and not r['answer_supported']
                            else 'expert_path_unavailable' if investigate is None
                            else 'unsafe_supported_bridge' if r['answer_supported'] or any(e['status']=='traversed' for e in r['relations'])
                            else 'unavailable_or_unreported_relation')
                    observed=r
                elif key=='receipt-boundary':
                    docs(root);r=research(root)
                    observed={'expert_receipts':r['receipts'],'delivered':None,'read':None,'acknowledged':None,'answer_supported':r['answer_supported']}
                    actual='execution_only_no_delivery_claim' if not r['answer_supported'] else 'unsupported_receipt_promotion'
                elif key=='burden-metrics':
                    page(root);r=answer_query(root,'Who owns observatory?').contract
                    observed={'query_kind':r['kind'],'human_labeling_seconds':None,'human_correction_seconds':None,
                              'human_time_basis':'not measured; no real participants'}
                    actual='measured_compute_unknown_human_time'
                else:actual,observed=extension(case,root)
            _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            represented=set()
            def collect_sources(value):
                if isinstance(value,dict):
                    if isinstance(value.get('source_id'),str):represented.add(value['source_id'])
                    for field in ('sources','source_occurrences'):
                        for source in value.get(field,[]) if isinstance(value.get(field,[]),list) else []:
                            if isinstance(source,dict) and isinstance(source.get('id'),str):represented.add(source['id'])
                    for child in value.values():collect_sources(child)
                elif isinstance(value,list):
                    for child in value:collect_sources(child)
            collect_sources(observed)
            source_count=len(Ledger(root).records)
            measurement={'wall_seconds':time.perf_counter()-started,'cpu_seconds':time.process_time()-cpu,
                         'peak_python_allocated_bytes':peak,'source_text_read_bytes':scanned[0],
                         'source_text_read_calls':reads[0],
                         'source_bytes':sum(p.stat().st_size for p in root.rglob('*.html')),
                         'final_source_files_sha256':{str(p.relative_to(root)):sha(p.read_bytes()) for p in sorted(root.rglob('*.html'))},
                         'source_count':source_count,'sources_represented_in_output':len(represented),
                         'output_source_coverage':len(represented)/source_count if source_count else None,
                         'human_labeling_seconds':None,'human_correction_seconds':None}
            status='pass' if actual==case['expected'] else 'gap' if case['score']=='capability' or investigate is None else 'regression'
            # An unavailable optional path is a capability gap, never a safety pass.
            if investigate is None and key in {'exact-route-zero','contradiction-not-pruned','receipt-boundary'}:status='gap'
            if actual=='unavailable_or_unreported_relation':status='gap'
            if actual=='extension_unavailable':status='gap'
            rows.append(dict(case,actual=actual,status=status,observed=observed,measurement=measurement))
    root=Path(pipeline.__file__).resolve().parents[1]
    code={str(p.relative_to(root)):sha(p.read_bytes()) for package in ('mplpb_answers','mplpb_combined','mplpb_work')
          for p in sorted((root/package).glob('*.py'))}
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() if (root/'.git').exists() else None
    dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()) if (root/'.git').exists() else None
    probes=[r for r in rows if r['id'] in {'missing-bridge','negated-bridge','contradiction-not-pruned'} and r['status']!='gap']
    false_bridges=sum(row['actual'] in {'unsafe_supported_answer','unsafe_supported_bridge','unsupported_receipt_promotion'} for row in rows)
    return {'schema':'public-evidence-results-v1','manifest_sha256':sha(manifest_raw),
            'evaluator_sha256':sha(Path(__file__).read_bytes()),
            'implementation_revision':revision,'working_tree_changed':dirty,
            'implementation_files_sha256':code,'configuration':{'models_enabled':False,'network_enabled':False,
            'fixture_record_time':fixture_time,
            'hidden_questions':0,'fixtures':'fully published fictional cases','default_hops':2,'default_sources':12},
            'measurement_limits':['Wall/CPU and tracemalloc Python allocations are measured; total process RSS is not measured.',
                                  'Per-case wall/CPU/allocation measurements include fixture setup and execution. Output source coverage is not answer recall or source relevance.',
                                  'Source-text bytes count Path.read_text calls under each fixture root, including repeated reads; binary/OS-cache I/O is not claimed.',
                                  'Human labeling/correction time is unknown; no usability claim is made.',
                                  'A safety pass does not establish useful historical reconstruction. Missing capability stays a gap.'],
            'summary':dict(Counter(row['status'] for row in rows)),
            'families':sorted({row['family'] for row in rows}),
            'false_supported_bridges':false_bridges,'bridge_probes_executed':len(probes),
            'false_supported_bridge_rate':false_bridges/len(probes) if probes else None,
            'rows':rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',type=Path,default=SUITE)
    parser.add_argument('--output',type=Path,required=True,help='new results file; refuses overwrite')
    parser.add_argument('--require-capabilities',action='store_true',help='also fail when a published capability remains a gap')
    args=parser.parse_args();report=run(args.cases)
    with args.output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'summary':report['summary'],'false_supported_bridges':report['false_supported_bridges']},indent=2))
    return 1 if report['summary'].get('regression') else 2 if args.require_capabilities and report['summary'].get('gap') else 0


if __name__=='__main__':raise SystemExit(main())
