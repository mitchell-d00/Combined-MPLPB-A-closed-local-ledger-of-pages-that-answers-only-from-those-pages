"""Frozen execution-only adapter. No key, scorer, generator or Git access."""
import json
from pathlib import Path
import resource
import sys


def execute():
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2, 8 * 1024**2))
    inputs, ledger, output = Path('/study'), Path('/scratch/ledger'), Path('/output/result.json')
    case = json.loads((inputs / 'case.json').read_text())
    if case.get('adapter_mode') != 'documentary':
        from tools.pole_worker import execute as pole_execute
        return pole_execute(inputs, ledger, output)
    from mplpb_combined.ledger import write, withdraw
    from mplpb_combined.reader import PROFILES
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.body_text import body_text
    from mplpb_answers.passages import PassageIndex
    from tools.pole_worker import snapshot
    records = []
    for s in case['sources']:
        r = write(ledger, doc_id=s['id'], title=s.get('title', 'Documentary original'),
                  scope=s.get('scope', 'documentary evidence'), origin='machine',
                  external='yes', body_html=s['body_html'],
                  when=s.get('when', '2026-11-25T00:00Z'))
        if s.get('withdraw'):
            withdraw(ledger, s['id'], when='2026-11-25T00:00Z')
        row = {'id': r.id, 'path': r.path, 'hash': r.hash_actual, 'body': body_text(r.body_html)}
        if 'original_sha256' in s:
            row['original_sha256'] = s['original_sha256']
        records.append(row)
    before = snapshot(ledger)
    profile = PROFILES[case.get('profile', 'internal')]
    b = case['budget']
    answer = answer_query(ledger, case['question'], profile,
                         max_passages=b['passages'], max_chars=b['characters']).contract
    result = {'id': case['id'], 'question': case['question'], 'records': records, 'answer': answer}
    if case.get('discovery'):
        result['discovery'] = PassageIndex(ledger, case['question'], profile).retrieve(
            [case['question']], b['passages'], b['characters'])['passages']
    assert before == snapshot(ledger), 'Reader mutated ledger'
    with output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, allow_nan=False)


if __name__ == '__main__':
    execute()
