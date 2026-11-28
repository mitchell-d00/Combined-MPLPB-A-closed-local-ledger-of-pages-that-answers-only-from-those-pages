"""Frozen evaluator for an exact subject reference, qualified output and actual stop."""
import hashlib
import json
from pathlib import Path
import sys

raw, key, output = map(Path, sys.argv[1:])
captured = json.loads(raw.read_bytes())
expected = json.loads(key.read_bytes())
assert captured['input_sha256'] == expected['input_sha256']
assert [r['id'] for r in captured['rows']] == list(expected['cases'])
results = []
for row in captured['rows']:
    want = expected['cases'][row['id']]
    if 'error' in row:
        results.append({'id':row['id'], 'pass':False, 'execution_failure':row['error']})
        continue
    answer = row['answer']
    support = answer.get('documentary_support', {})
    diagnostic = answer['diagnostic']
    got_stage = support.get('subject_stage', support.get('response_stage', diagnostic.get('stage')))
    if diagnostic['code'] == 'source_changed':
        got_stage = 'state_recheck'
    if diagnostic['code'] == 'interpretation_unsupported':
        got_stage = 'interpretation'
    observed_claims = answer['claims']
    records = {r['id']:r for r in row['records']}
    exact = []
    citations = [c for claim in observed_claims for c in claim['citations']]
    for c in citations:
        rec = records[c['source_id']]
        lo, hi = c['body_start'], c['body_end']
        if (c['hash']==rec['hash'] and c['path']==rec['path'] and not rec['withdrawn']
                and 0<=lo<hi<=len(rec['body']) and rec['body'][lo:hi]==c['quote']):
            exact.append([c['source_id'], lo, hi, c['quote']])
    complete = answer['kind']=='supported_answer' and answer['answer_supported']
    if want['kind']=='subject':
        claim = observed_claims[0] if len(observed_claims)==1 else {}
        qualifiers = ' '.join(claim.get('qualifiers', [])).casefold()
        passed = (complete and got_stage=='proved' and claim.get('proposition')==want['proposition']
                  and sorted(exact)==sorted(want['witnesses']) and len(exact)==len(citations)
                  and all(term in qualifiers for term in ('submission', 'receipt', 'agreement', 'execution', 'unverified')))
    elif want['kind']=='guard':
        passed = complete == want['complete'] and (not want['complete'] or bool(exact)) and diagnostic['code']==want['code']
        if 'witnesses' in want:
            passed = passed and sorted(exact)==sorted(want['witnesses'])
        if 'stage' in want:
            passed = passed and got_stage==want['stage']
    else:
        passed = (answer['kind']=='abstain' and not complete and not observed_claims and got_stage==want['stage']
                  and ('target_count' not in want or support.get('eligible_target_count')==want['target_count'])
                  and ('mutation' not in want or [x['withdrawn'] for x in row['mutations']]==[want['mutation']]))
    results.append({'id':row['id'], 'pass':bool(passed), 'kind':answer['kind'], 'stage':got_stage,
                    'code':diagnostic['code'], 'expected_stage':want.get('stage', 'proved' if want['kind']=='subject' else None),
                    'target_count':support.get('eligible_target_count'), 'exact_citations':len(exact),
                    'claims':len(observed_claims), 'mutations':len(row['mutations']),
                    'unsupported_completion':bool(complete and not passed and want['kind']!='guard')})
with output.open('x') as stream:
    json.dump(results, stream, indent=2)
    stream.write('\n')
