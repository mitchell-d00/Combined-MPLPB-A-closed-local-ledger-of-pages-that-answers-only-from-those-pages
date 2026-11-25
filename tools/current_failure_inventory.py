"""Read-only current-reader replay of selected, unchanged historical packets."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
import zipfile

BASELINE = '851de6c093394060ce624eb63ba72400b047a7ce'
MISSED = {'partial_correction','earliest_observed','negated_statement','wording_change',
          'header_location','field_compound','date_roles','instruction_statement',
          'identical_wording','explicit_chain','reported_statement'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def prepare(a):
    sys.path.insert(0, str(a.implementation.resolve()))
    from tools.dpercent import FAMILIES
    from tools.unprepared_challenge import code_pins
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.implementation,text=True).strip()==BASELINE
    a.output.mkdir(); a.custody.mkdir(mode=0o700)
    origin=a.implementation/'evaluation/dpercent-known-weaknesses/2026-11-20/synthetic-packets.zip'
    selected=[]; keys=[]; counts=Counter()
    with zipfile.ZipFile(origin) as z:
        candidates=[]
        for name in z.namelist():
            if name.startswith('expected/') and name.endswith('/key.json'):
                shard=name.split('/')[1]
                candidates.extend((row,shard) for row in json.loads(z.read(name))['cases'])
        for key,shard in sorted(candidates,key=lambda r:r[0]['id']):
            family=key['family']
            if family not in set(FAMILIES)|{'field_compound'} or counts[family]>=2:
                continue
            counts[family]+=1; ident=key['id']; prefix=f'public/{shard}/packets/{ident}/'
            path=a.output/'inputs'/'known'/ident; path.mkdir(parents=True)
            file_hashes={}
            for name in z.namelist():
                if name.startswith(prefix) and not name.endswith('/'):
                    rel=name[len(prefix):]; raw=z.read(name);target=path/rel
                    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                    file_hashes[rel]=sha(raw)
            selected.append({'suite':'known','id':ident,'family':family,'expected':key['expected'],
                'historical_miss':family in MISSED,'origin_shard':shard,
                'input_path':str(path.relative_to(a.output)),'files':file_hashes})
            keys.append({'suite':'known',**key})
    assert len(selected)==64 and len(counts)==32
    archive=a.implementation/'evaluation/pole/open-items/focus-extend/frozen-operator-packets.tar.gz'
    diagnostics=read(a.implementation/'evaluation/pole/open-items/focus-extend/receipts/focus-diagnostics.json')
    positives={r['case_id']:r for r in diagnostics}
    with tarfile.open(archive) as t:
        protocol=json.load(t.extractfile('focus/protocol.json'))
        for ident in protocol['cases']:
            path=a.output/'inputs'/'focus'/ident;path.mkdir(parents=True);prefix='focus/packets/'+ident+'/'
            hashes={}
            for member in t.getmembers():
                if member.isfile() and member.name.startswith(prefix):
                    rel=member.name[len(prefix):];raw=t.extractfile(member).read();target=path/rel
                    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);hashes[rel]=sha(raw)
            selected.append({'suite':'focus','id':ident,
                'family':positives[ident]['family'] if ident in positives else 'preserved_negative_control',
                'expected':'answer' if ident in positives else 'no_full_support',
                'historical_miss':ident in positives,'input_path':str(path.relative_to(a.output)),'files':hashes})
    save(a.output/'selection.json',{'baseline_commit':BASELINE,'baseline_runtime_sha256':code_pins(a.implementation),
        'selection_rule':'Two lowest original case IDs per original D% family plus field_compound; all 32 Focus cases. Fixed before current-reader replay. No language or result filtering.',
        'known_archive_sha256':sha(origin.read_bytes()),'focus_archive_sha256':sha(archive.read_bytes()),
        'original_known_reader':'2427d80e777b9cc76e071b2529e91a14b9bdb991',
        'historical_605_status':'Historical full-study count only; this sample is not a new 4096-case census.',
        'worker':'Unchanged tools/pole_worker.py, same <pre> source admission, source policies, question, budgets and native reader calls as original D% worker; OS isolation differs and speed is not compared.',
        'worker_sha256':sha((a.implementation/'tools/pole_worker.py').read_bytes()),
        'os_isolated':False,'independent_historical_accuracy':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN',
        'outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN','cases':selected})
    save(a.custody/'known-keys.json',keys)
    print('Frozen selection: 64 known-weakness cases and all 32 Focus cases; no native implementation changed.')


def run(a):
    selection=read(a.packet/'selection.json')
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.implementation,text=True).strip()
    assert revision==BASELINE
    sys.path.insert(0,str(a.implementation.resolve()))
    from tools.unprepared_challenge import code_pins
    pins=code_pins(a.implementation);assert pins==selection['baseline_runtime_sha256']
    worker=a.implementation.resolve()/'tools/pole_worker.py'
    assert sha(worker.read_bytes())==selection['worker_sha256']
    a.output.mkdir();rows=[]
    for case in selection['cases']:
        src=a.packet/case['input_path']
        actual={str(p.relative_to(src)):sha(p.read_bytes()) for p in src.rglob('*') if p.is_file()}
        assert actual==case['files']
        dest=a.output/case['suite']/case['id'];dest.mkdir(parents=True)
        with TemporaryDirectory(prefix='inventory-') as tmp:
            tmp=Path(tmp);r=tmp/'result.json'
            try:
                with (dest/'worker.log').open('xb') as log:
                    p=subprocess.run([sys.executable,'-I','-B',str(worker),str(a.implementation.resolve()),
                        str(src.resolve()),str(tmp/'ledger'),str(r)],cwd=tmp,stdout=log,stderr=subprocess.STDOUT,timeout=45)
                if p.returncode:raise ValueError('worker exited '+str(p.returncode))
                raw=r.read_bytes();assert len(raw)<=8*1024**2
                (dest/'result.json').write_bytes(raw)
                rows.append({'suite':case['suite'],'id':case['id'],'status':'completed','sha256':sha(raw)})
            except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
                rows.append({'suite':case['suite'],'id':case['id'],'status':'failed','error':str(exc)})
        (a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
    assert code_pins(a.implementation)==pins
    save(a.output/'receipt.json',{'baseline_commit':BASELINE,'runtime_sha256':pins,
        'selection_sha256':sha((a.packet/'selection.json').read_bytes()),'os_isolated':False,'cases':rows})
    print('Executed',len(rows),'selected frozen cases; failures',sum(r['status']!='completed' for r in rows))


def summarize(a):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    selection=read(a.packet/'selection.json');receipt=read(a.run/'receipt.json')
    from tools.unprepared_challenge import code_pins
    assert code_pins(Path(__file__).resolve().parents[1])==receipt['runtime_sha256']
    keys={k['id']:k for k in read(a.custody/'known-keys.json')};rows=[]
    from mplpb_answers.documentary import plan
    from mplpb_answers.reference_identity import parse_request
    for selected,entry in zip(selection['cases'],receipt['cases'],strict=True):
        assert selected['id']==entry['id']
        row={k:selected[k] for k in ['suite','id','family','expected','historical_miss']}
        if entry['status']!='completed':row.update(status='NOT_RUN',error=entry.get('error'));rows.append(row);continue
        path=a.run/row['suite']/row['id']/'result.json';raw=path.read_bytes();assert sha(raw)==entry['sha256']
        data=json.loads(raw);answer=data['answer'];claims=answer['claims']
        records={r['source_id']:r for r in data['source_receipts']};valid=True
        for claim in claims:
            if claim.get('source_support_established') and not claim['citations']:valid=False
            for c in claim['citations']:
                r=records.get(c['source_id'])
                if not r or r['hash']!=c['hash'] or r['canonical_body'][c['body_start']:c['body_end']]!=c['quote']:valid=False
        facts=keys.get(row['id'],{}).get('source_facts',[])
        pack=data['retrieval']['native_facets'];passages=pack['passages']
        coverage=[any(p['source_id']==f['source_id'] and ' '.join(f['evidence_text'].split()) in ' '.join(p['text'].split()) for p in passages) for f in facts]
        code=answer['diagnostic']['code']
        stage=('budget' if 'budget' in code or 'limit' in code else 'question_interpretation' if code=='interpretation_unsupported'
               else 'verification_or_attribution' if not answer['answer_supported'] and row['expected']=='answer' else 'decision_returned')
        key=keys.get(row['id'],{})
        targets=key.get('required_propositions',[])
        props=[c.get('proposition',{}) for c in claims if c.get('source_support_established')]
        normal=lambda x:' '.join(str(x).casefold().strip(' .').split())
        matches=bool(targets) and all(any(all(k in p and (p[k] is v if type(v) is bool else isinstance(p[k],str) and normal(p[k])==normal(v))
            for k,v in target.items()) for p in props) for target in targets)
        if key.get('automatic_answer_matcher')=='literal_field_set_v1':
            matches={c['text'] for c in claims}==set(key['required_field_quotes'])
        if key.get('automatic_answer_matcher')=='quotation_location':
            matches=any(c.get('source_id') in key['reference_sources'] and key['literal_anchor'] in ' '.join(c['quote'].split())
                        for claim in claims for c in claim['citations'])
        row.update(status='completed',question=answer['question'],kind=answer['kind'],diagnostic=code,
            native_complete=answer['answer_supported'],native_partial=answer['kind']=='partial_answer',
            propositions=len(claims),citations_valid=valid,missing=answer.get('missing',[]),
            source_key_match=bool(matches and valid) if row['suite']=='known' and answer['answer_supported'] else None,
            native_documentary_goals=[g['kind'] for g in (plan(answer['question']) or [])],
            native_reference_request=bool(parse_request(answer['question'])),
            sorter_complete=data['sorter']['complete'],
            source_key_full_discovery=all(coverage) if facts else None,
            required_source_statements=len(facts),discovered_statements=sum(coverage),
            observed_failure_stage=stage,trace=answer.get('trace'),
            unsupported_complete=answer['answer_supported'] and row['expected']!='answer',
            semantic_correctness='NOT_RUN for unsupported authored matcher shapes; native support is not independent accuracy',
            measurements=data['measurements'])
        rows.append(row)
    groups={}
    for row in rows:
        group=groups.setdefault(row['suite']+'/'+row['family'],Counter());group['selected']+=1
        if row['status']!='completed':group['not_run']+=1;continue
        for k in ['native_complete','native_partial','unsupported_complete']:
            group[k]+=int(row[k])
        group['remaining_misses']+=int(row['expected']=='answer' and not row['native_complete'] and not row['native_partial'])
        group['budget_stops']+=int(row['observed_failure_stage']=='budget')
    save(a.output,{'baseline_commit':BASELINE,'selection_sha256':sha((a.packet/'selection.json').read_bytes()),
        'groups':groups,'cases':rows,'scope':'Selected software baseline; neither a current 605-miss census nor independent semantic adjudication.',
        'independent_historical_accuracy':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN',
        'outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'})
    print(json.dumps({'groups':groups},indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name,fields in [('prepare',['implementation','output','custody']),('run',['packet','implementation','output']),
                        ('summarize',['packet','run','custody','output'])]:
        q=sub.add_parser(name)
        for field in fields:q.add_argument('--'+field,type=Path,required=True)
    a=p.parse_args();return {'prepare':prepare,'run':run,'summarize':summarize}[a.command](a)


if __name__=='__main__':
    main()
