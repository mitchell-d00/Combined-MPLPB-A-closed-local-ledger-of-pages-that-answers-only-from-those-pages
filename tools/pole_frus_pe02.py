"""Freeze and replay the PE-02 signed-letter cycle with separate local key custody."""
import argparse
from collections import Counter
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

BASELINE = '7618be370c334b082cb91c50eaf665f979ce5c1e'
RESTRICTED = {'FRUS-D2', 'FRUS-D3'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def prepare(args):
    sys.path.insert(0, str(args.baseline.resolve()))
    from tools import pole_authentic as a
    from tools.pole_focus_extend import frus_rendered
    from mplpb_answers.body_text import body_text
    from tools.unprepared_challenge import code_pins
    a.seal_for(args.inherited)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.baseline,text=True).strip()==BASELINE
    assert not args.packet.exists() and not args.custody.exists()
    assert args.packet.resolve() not in args.custody.resolve().parents
    assert args.custody.resolve() not in args.packet.resolve().parents
    shutil.copytree(args.inherited,args.packet)
    args.custody.mkdir(parents=True,mode=0o700)
    shutil.copyfile(args.packet/'seal.json',args.packet/'inherited-seal.json')
    shutil.copyfile(args.packet/'questions.json',args.packet/'inherited-questions.json')
    shutil.copyfile(args.packet/'sources.json',args.packet/'inherited-sources.json')
    questions=read(args.packet/'questions.json');sources=read(args.packet/'sources.json')
    prior={row['id']:row for row in read(args.prior)['rows']}
    assert len(questions)==11 and {q['id'] for q in questions}==set(prior)
    key=[]
    for q in questions:
        key.append({'id':q['id'],'cohort':'inherited','expected_before':prior[q['id']]['strict_after'],
                    'expected_after':'partial' if q['id']=='PE-02' else 'unchanged'})
    question='What task did Elena Moreno give the river survey delegation in the letter to Patel?'
    directive='The task of the river survey delegation is to inspect the northern levees and report any cracks before Friday.'
    for kind in ['positive','wrong-signer','initials-only','quoted','negated','unavailable']:
        ident='SIGNED-'+kind.upper()
        signer={'wrong-signer':'Adrian Voss','initials-only':'E. M.'}.get(kind,'Elena Moreno')
        sentence=directive.replace(' is to ',' is not to ') if kind=='negated' else directive
        paragraph='<p>'+escape(sentence)+'</p>'
        if kind=='quoted':paragraph='<blockquote><p>“'+escape(sentence)+'”</p></blockquote>'
        html=('<html><body><div class="tei-div3" id="letter">'
              '<h2>Archival letter</h2><p>Dear Director Patel:</p>'
              '<p>These are my instructions for the river survey delegation.</p>'
              +paragraph+'<p>Respectfully,</p><p>'+signer+'</p></div></body></html>')
        raw=html.encode();relative='sources/'+ident+'.html';(args.packet/relative).write_bytes(raw)
        sources.append({'id':ident,'path':relative,'filename':ident+'.html','encoding':'utf-8',
                        'sha256':digest(raw),'media_type':'text/html','document_id':'letter',
                        'url':'synthetic:independently-worded-signed-letter','withdraw':kind=='unavailable'})
        questions.append({'id':ident,'question':question,'sources':[ident],
                          'budget':{'passages':12,'characters':8000}})
        key.append({'id':ident,'cohort':'synthetic','expected_before':'miss' if kind=='positive' else 'expected_withhold',
                    'expected_after':'complete' if kind=='positive' else 'withhold',
                    'signer':'Elena Moreno','addressee':'Director Patel','directive':directive,'source_id':ident})
    target=next(s for s in sources if s['id']=='FRUS-D16')
    body=body_text(frus_rendered((args.packet/target['path']).read_bytes(),target))
    task=next(line for line in body.splitlines() if line.startswith('The task of the Delegation'))
    row=next(k for k in key if k['id']=='PE-02')
    row.update(signer='Richard Nixon',addressee='Ambassador Smith',directive=task,source_id='FRUS-D16',
               missing_question=questions[2]['question'].split(', and what task',1)[0]+'?')
    for path,value in [(args.packet/'questions.json',questions),(args.packet/'sources.json',sources)]:
        path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    save(args.custody/'key.json',key);(args.custody/'key.json').chmod(0o600)
    (args.packet/'seal.json').unlink()
    save(args.packet/'seal.json',{'public_files':a.inventory(args.packet),
         'key_sha256':digest((args.custody/'key.json').read_bytes()),
         'harness_sha256':digest(Path(__file__).read_bytes()),
         'inherited_seal_sha256':digest((args.packet/'inherited-seal.json').read_bytes())})
    save(args.custody/'seal-copy.json',read(args.packet/'seal.json'))
    save(args.freeze,{'baseline_commit':BASELINE,'baseline_runtime_sha256':code_pins(args.baseline),
         'packet_seal_sha256':digest((args.packet/'seal.json').read_bytes()),
         'key_sha256':digest((args.custody/'key.json').read_bytes()),'rule_sha256':digest(args.rule.read_bytes()),
         'harness_sha256':digest(Path(__file__).read_bytes()),'inherited_cases':[q['id'] for q in questions[:11]],
         'new_cases':[q['id'] for q in questions[11:]],'budgets':{'records':8,'scan_characters':200000,
         'scan_units':1000,'passages':12,'output_characters':8000},'worker_receives_key_path':False,
         'os_isolated':False,'same_operator_prepared_local_key':True,
         'outside_custodian_scoring':'NOT_RUN','independent_historical_accuracy':'NOT_RUN',
         'independent_semantic_adjudication':'NOT_RUN','native_oocc':'NOT_RUN'})
    print('Frozen seventeen cases, unchanged original bytes, rule, harness and separate local key.')


def run(args):
    implementation=args.implementation.resolve();sys.path.insert(0,str(implementation))
    from tools import pole_authentic as a
    from tools.pole_focus_extend import frus_rendered
    from tools.unprepared_challenge import code_pins
    from mplpb_combined.ledger import write,withdraw
    from mplpb_combined.reader import PROFILES
    from mplpb_answers.body_text import body_text
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.passages import PassageIndex
    seal=a.seal_for(args.packet)
    assert seal['harness_sha256']==digest(Path(__file__).read_bytes())
    pins=code_pins(implementation);sources={s['id']:s for s in read(args.packet/'sources.json')}
    rows=[]
    for q in read(args.packet/'questions.json'):
        with TemporaryDirectory(prefix='pe02-') as folder:
            root=Path(folder);records=[]
            for ident in q['sources']:
                s=sources[ident];raw=(args.packet/s['path']).read_bytes();assert digest(raw)==s['sha256']
                html=frus_rendered(raw,s)
                r=write(root,doc_id=ident,title=ident,scope='public documentary originals',origin='machine',
                        body_html=html,external='yes',when='2026-11-24T00:00Z')
                if s.get('withdraw'):withdraw(root,ident,when='2026-11-25T00:00Z')
                records.append({'id':ident,'original_sha256':s['sha256'],'path':r.path,
                                'hash':r.hash_actual,'body':body_text(r.body_html)})
            b=q['budget'];answer=answer_query(root,q['question'],PROFILES['internal'],
                                             max_passages=b['passages'],max_chars=b['characters']).contract
            discovery=PassageIndex(root,q['question'],PROFILES['internal']).retrieve(
                [q['question']],b['passages'],b['characters'])
            rows.append({'id':q['id'],'question':q['question'],'records':records,'answer':answer,
                         'discovery':discovery['passages']})
    assert pins==code_pins(implementation);a.seal_for(args.packet)
    save(args.output,{'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=implementation,text=True).strip(),
        'runtime_sha256':pins,'packet_seal_sha256':digest((args.packet/'seal.json').read_bytes()),
        'worker_receives_key_path':False,'os_isolated':False,'cases':rows})
    print('Replayed',len(rows),'cases without a key path.')


def normalized(value):
    if isinstance(value,dict):return {k:normalized(v) for k,v in value.items() if k!='code_sha256'}
    if isinstance(value,list):return [normalized(v) for v in value]
    return value


def category(answer,positive):
    return ('complete' if answer['answer_supported'] else 'partial' if answer['claims']
            else 'miss' if positive else 'expected_withhold')


def score(args):
    frozen=read(args.freeze);key=read(args.custody/'key.json');before=read(args.before);after=read(args.after)
    assert digest((args.custody/'key.json').read_bytes())==frozen['key_sha256']
    assert digest(args.rule.read_bytes())==frozen['rule_sha256']
    assert before['revision']==frozen['baseline_commit']
    assert before['runtime_sha256']==frozen['baseline_runtime_sha256']
    assert digest(Path(__file__).read_bytes())==frozen['harness_sha256']
    assert before['packet_seal_sha256']==after['packet_seal_sha256']==frozen['packet_seal_sha256']
    assert [r['id'] for r in before['cases']]==[r['id'] for r in after['cases']]==[k['id'] for k in key]
    rows=[];failures=[];false_support=0;counts={'before':Counter(),'after':Counter()}
    for expected,left,right in zip(key,before['cases'],after['cases'],strict=True):
        first,last=left['answer'],right['answer'];errors=[]
        positive=expected['expected_before'] in {'miss','complete'}
        baseline_expected=expected['expected_before']
        if baseline_expected=='expected_presentation_withhold':baseline_expected='partial'
        if category(first,positive)!=baseline_expected:errors.append('baseline differs from frozen published expectation')
        for label,row in [('before',left),('after',right)]:
            answer=row['answer'];counts[label][category(answer,positive)]+=1
            records={r['id']:r for r in row['records']}
            for claim in answer['claims']:
                for cite in claim['citations']:
                    record=records[cite['source_id']];lo,hi=cite['body_start'],cite['body_end']
                    if not (record['hash']==cite['hash'] and record['path']==cite['path']
                            and record['body'][lo:hi]==cite['quote']):errors.append(label+': citation mismatch')
        mode=expected['expected_after']
        if mode=='unchanged':
            if normalized(first)!=normalized(last):errors.append('inherited answer changed')
        elif mode=='withhold':
            if last['claims'] or last['answer_supported']:errors.append('claim on withhold')
        else:
            if (last['kind']!=('partial_answer' if mode=='partial' else 'supported_answer')
                    or last['answer_supported']!=(mode=='complete') or len(last['claims'])!=1):
                errors.append('expected signed-instruction decision missing')
            elif last['claims']:
                claim=last['claims'][0];p=claim['proposition'];cites=claim['citations']
                if not (p.get('relation')=='source_signed_letter_instruction'
                    and p.get('signer')==expected['signer'] and p.get('addressee')==expected['addressee']
                    and p.get('directive')==expected['directive'] and p.get('modality')=='instruction_only'
                    and all(c['source_id']==expected['source_id'] for c in cites)
                    and any(c['quote']==expected['directive'] for c in cites)):
                    errors.append('signed instruction or witness differs from key')
                if mode=='partial' and expected['missing_question'] not in last['missing']:
                    errors.append('unresolved first obligation lost')
        if (last['claims'] and any(e!='baseline differs from frozen published expectation' for e in errors)) or (mode=='partial' and last['answer_supported']):
            false_support+=1
        row={'id':expected['id'],'cohort':expected['cohort'],'before':category(first,positive),
             'after':category(last,positive),'propositions_before':len(first['claims']),
             'propositions_after':len(last['claims']),'errors':errors}
        rows.append(row);failures.extend({'id':row['id'],'reason':e} for e in errors)
    save(args.output,{'freeze':frozen,'counts':{k:dict(v) for k,v in counts.items()},'rows':rows,
         'failures':failures,'acceptance_passed':not failures,
         'false_support_decisions':false_support,
         'before_sha256':digest(args.before.read_bytes()),'after_sha256':digest(args.after.read_bytes()),
         'outside_custodian_scoring':'NOT_RUN','independent_historical_accuracy':'NOT_RUN',
         'independent_semantic_adjudication':'NOT_RUN','native_oocc':'NOT_RUN'})
    print(json.dumps({'failures':len(failures),'before':dict(counts['before']),'after':dict(counts['after'])}))
    return 1 if failures else 0


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    fields={'prepare':['inherited','packet','custody','baseline','prior','freeze','rule'],
            'run':['packet','implementation','output'],
            'score':['custody','freeze','rule','before','after','output']}
    for command,names in fields.items():
        c=sub.add_parser(command)
        for name in names:c.add_argument('--'+name,required=True,type=Path)
    args=p.parse_args();return {'prepare':prepare,'run':run,'score':score}[args.command](args)


if __name__=='__main__':
    raise SystemExit(main())
