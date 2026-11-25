"""Versioned scoring amendment: reconstruct the frozen worker's full written HTML.

Original role keys and source contracts are unchanged. Frozen v1 and its failed
certificate checks remain retained. This version restores ledger.write's H1
wrapper and CRLF normalization when independently checking original coordinates.
"""
import argparse
import json
import sys
from collections import Counter
import hashlib
import html
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.bubble_wrap_trial import (read, save, normal, sha, citations,
    source_claim_errors, digest, verify_frozen, HOME, ROOT)


def original_citations(result, descriptor):
    packet=ROOT/descriptor['packet'];case=read(packet/'case.json');sources={}
    for number,source in enumerate(case['sources'],1):
        if case.get('adapter_mode')=='documentary':
            ident=source['id'];title=source.get('title','Documentary original');inner=source['body_html']
        else:
            ident=f'SOURCE-{number:04d}';title=f'Synthetic source {number}'
            inner='<pre>'+html.escape((packet/source['path']).read_bytes().decode())+'</pre>'
        # Exact documented write/render admission, not candidate semantic parsing.
        body=('<h1>'+html.escape(' '.join(title.split()),quote=False)+'</h1>\n'+inner).strip()
        sources[ident]=body.replace('\r\n','\n').strip().encode()
    errors=[]
    for claim in result['answer']['claims']:
        if claim.get('proposition',{}).get('relation')!='source_attributed_report_content':continue
        for c in claim['citations']:
            raw=sources[c['source_id']];w=c.get('original_witness',{})
            selected=raw[w.get('start_byte',0):w.get('end_byte',0)]
            if (w.get('coordinate_space')!='admitted_record_body_html_utf8'
                or w.get('body_html_sha256')!=hashlib.sha256(raw).hexdigest()
                or html.unescape(selected.decode())!=c['quote']):
                errors.append('original HTML witness coordinates/hash mismatch')
    return errors


def score(a):
    registry = read(a.transfer_manifest) if a.transfer_manifest else verify_frozen()
    selected = {r['id']: r for r in registry['cases']}
    keys = read(a.transfer_key) if a.transfer_key else read(HOME / 'scoring-key.json')
    run_record = read(a.run / 'run.json'); rows, totals = [], Counter()
    for entry in run_record['rows']:
        ident = entry['id']; descriptor = selected[ident]
        if entry['execution_status'] != 'completed':
            totals['failed_execution'] += 1
            rows.append(dict(entry, score='NOT_RUN')); continue
        raw = a.run / ident / 'result.json'; assert sha(raw) == entry['result_sha256']
        result = read(raw); answer = result['answer']; errors = citations(result)+original_citations(result,descriptor)
        if ident in keys:
            errors += source_claim_errors(result, keys[ident])
        else:
            before = read(ROOT / descriptor['original_output'])
            if normal(answer) != normal(before['answer']): errors.append('unaffected answer contract changed')
            if 'discovery' in before and result.get('discovery') != before['discovery']:
                errors.append('preserved discovery changed')
        totals['scored'] += 1; totals['passed' if not errors else 'failed'] += 1
        totals['complete'] += answer['answer_supported']; totals['partial'] += answer['kind'] == 'partial_answer'
        totals['claims'] += len(answer['claims'])
        totals['false_supported_claim_cases'] += bool(errors and answer['claims'])
        totals['misses'] += bool(errors and not answer['claims'])
        totals['budget_stops'] += 'budget' in answer['diagnostic']['code']
        rows.append({'id': ident, 'family': descriptor['family'], 'case_hash': descriptor['case_hash'],
                     'kind': answer['kind'], 'diagnostic': answer['diagnostic']['code'], 'claim_count': len(answer['claims']),
                     'answer_sha256': digest(normal(answer)), 'errors': errors, 'score': 'PASS' if not errors else 'FAIL',
                     'raw_output_sha256': sha(raw), 'raw_output_public': descriptor['public_raw_output']})
        rows[-1]['known_non_target_incomplete_positive']=(descriptor.get('prior_expected')=='answer'
            and not descriptor['allowed_target_change'] and not answer['answer_supported'])
    save(a.output, {'source_commit': run_record['source_commit'], 'scorer_version':3, 'scorer_amendment_sha256':sha(HOME/'scorer-amendment-v3.json'), 'run_sha256': sha(a.run / 'run.json'),
         'registry_sha256': run_record['registry_sha256'], 'counts': dict(totals), 'rows': rows,
         'acceptance_passed': not totals['failed'] and not totals['failed_execution'],
         'custody': 'Same operator; authored source-role keys, no independent semantic adjudication',
         'independent_historical_accuracy': 'NOT_RUN', 'independent_semantic_adjudication': 'NOT_RUN',
         'outside_custodian_scoring': 'NOT_RUN', 'native_oocc': 'NOT_RUN'})
    print(json.dumps(dict(totals)))
    return int(bool(totals['failed'] or totals['failed_execution']))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('run','output'):p.add_argument('--'+n,type=Path,required=True)
    for n in ('transfer-manifest','transfer-key'):p.add_argument('--'+n,type=Path)
    a=p.parse_args();amendment=read(HOME/'scorer-amendment-v3.json')
    for name,expected in amendment['files'].items():assert sha(ROOT/name)==expected
    raise SystemExit(score(a))
