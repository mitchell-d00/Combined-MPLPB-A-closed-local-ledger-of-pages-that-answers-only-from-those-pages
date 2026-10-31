"""Offline five-instance continuation demonstration. No AI-provider calls.

Roles use distinct host-issued contracts. The successor reads the durable work
from a fresh process after the first three instances have ended.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from mplpb_combined.ledger import write, Ledger
from mplpb_work import WorkStore, Denied
from mplpb_work.store import implementation_pins, digest


def run():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        corpus = base/'corpus'
        write(corpus, doc_id='CATALOG-0001', title='Catalog bulletin', scope='supplier component availability',
              body='Configuration AX-14 is discontinued. Component X remains available.')
        source = Ledger(corpus).by_id['CATALOG-0001'][0]
        store, authority = WorkStore.create(base/'work', {'catalog': corpus})
        seats = ['finder', 'challenger', 'builder', 'reviewer']
        rights = {
            'finder': ['create:task', 'create:evidence', 'create:claim', 'create:decision'],
            'challenger': ['create:review'],
            'builder': ['create:action', 'execute'],
            'reviewer': ['revise:claim', 'revise:review', 'resolve_review', 'revise:task'],
        }
        tokens = {}
        def assign(seat, instance, previous=None):
            result = store.assign(authority, seat=seat, instance=instance,
                model={'name': 'offline-fixture', 'provider': 'local', 'version': '1', 'context_policy_hash': digest({'projection': 'fixture-isolated-views-v1', 'seat': seat})},
                contract={'operations': rights[seat], 'tools': ['fixture.availability.v1'] if seat == 'builder' else [],
                          'scopes': ['T1'], 'share_with': seats, 'profile': 'internal', 'expires_at': time.time()+3600},
                continues_work_of=previous, expected_head=store.head(authority)['hash'])
            tokens[seat] = result['credential']
        for seat, instance in [('finder', 'A'), ('challenger', 'B'), ('builder', 'C'), ('reviewer', 'E')]:
            assign(seat, instance)
        def put(seat, id, kind, payload, dependencies=None, revision=0):
            store.put(tokens[seat], id=id, kind=kind, payload=payload, dependencies=dependencies or {},
                      visibility=seats, expected_revision=revision, expected_head=store.snapshot(tokens[seat])['head'])
        task = {'goal': 'Test component-level availability', 'criteria': ['catalog fixture passes'], 'review_budget': 3, 'state': 'open', 'acceptance': {}}
        put('finder', 'T1', 'task', task)
        for id, quote in [('E1', 'Configuration AX-14 is discontinued.'), ('E2', 'Component X remains available.')]:
            put('finder', id, 'evidence', {'task': 'T1', 'corpus': 'catalog', 'source_id': source.id, 'source_hash': source.hash, 'quote': quote, 'query': 'supplier component availability'})
        claim = {'task': 'T1', 'proposition': 'Component X is discontinued', 'basis': 'inference', 'assessment': 'supported_under_scope',
                 'assumptions': ['Configuration status implies component status'], 'alternatives': ['Other configurations remain'], 'revisit_when': 'Read component-level catalog statement'}
        put('finder', 'C1', 'claim', claim, {'E1': 1})
        action = {'task': 'T1', 'task_revision': 1, 'operation': 'fixture.availability.v1', 'arguments': {'interpretation': 'configuration implies component'},
                  'side_effect': 'local', 'executor_seat': 'builder', 'state': 'proposed', 'retry_of': {}, 'retry_reason': ''}
        put('builder', 'A1', 'action', action, {'C1': 1})
        store.executors['fixture.availability.v1'] = lambda request: {'result': 'failed', 'validation': {'catalog fixture passes': False}, 'artifact': 'Fixture failed: configuration is not component-level availability'}
        failed = store.execute(tokens['builder'], id='A1', expected_revision=1, expected_head=store.snapshot(tokens['builder'])['head'])
        review = {'task': 'T1', 'target': {'C1': 1}, 'target_variable': 'component-level availability', 'regime': 'synthetic catalog',
                  'finding': 'The inference exceeds the source scope', 'outcome': 'challenge', 'resolution': ''}
        put('challenger', 'R1', 'review', review, {'E2': 1})
        for seat in ('finder', 'challenger', 'builder'):
            store.end(tokens[seat], store.snapshot(tokens[seat])['head'])
        old_builder = tokens['builder']
        assign('builder', 'D', 'C')
        # Credential travels through stdin, never argv or the emitted report.
        code = 'import json,sys; from mplpb_work import WorkStore; r=json.load(sys.stdin); v=WorkStore(r["path"]).handoff(r["credential"]); print(json.dumps(v))'
        successor = json.loads(subprocess.check_output([sys.executable, '-c', code],
                      input=json.dumps({'path': str(base/'work'), 'credential': tokens['builder']}).encode()))
        inherited = {r['id']: r for r in successor['records']}
        try:
            store.snapshot(old_builder)
            fenced = False
        except Denied:
            fenced = True
        claim.update(proposition='Component X remains available', assumptions=[])
        put('reviewer', 'C1', 'claim', claim, {'E2': 1}, revision=1)
        review.update(outcome='resolved', resolution='Revised proposition to the exact component-level source scope')
        put('reviewer', 'R1', 'review', review, {'E2': 1}, revision=1)
        action.update(arguments={'interpretation': 'explicit component-level statement'}, retry_of={failed['attempt']: 1}, retry_reason='Corrected scope and source pin')
        put('builder', 'A2', 'action', action, {'C1': 2})
        store.executors['fixture.availability.v1'] = lambda request: {'result': 'passed', 'validation': {'catalog fixture passes': True}, 'artifact': 'Corrected catalog fixture passed'}
        passed = store.execute(tokens['builder'], id='A2', expected_revision=1, expected_head=store.snapshot(tokens['builder'])['head'])
        task.update(state='done', acceptance={passed['attempt']: 1})
        put('reviewer', 'T1', 'task', task, revision=1)
        final = {r['id']: r for r in store.snapshot(tokens['builder'])['records']}
        checkpoint = store.head(authority)
        audited = store.audit(authority, checkpoint)
        identities = [event['payload']['instance'] for event in audited['events'] if event['type'] == 'assign']
        return {'scenario': 'five specialist instances with process replacement', 'evaluation_status': 'offline developer fixture; not independent multi-agent performance evidence',
                'implementation_sha256': implementation_pins(), 'instances': sorted(i['id'] for i in identities),
                'same_model_distinct_instances': len({i['id'] for i in identities}) == 5 and len({i['model']['name'] for i in identities}) == 1, 'successor_process': 'fresh subprocess', 'successor_continues_work_of': successor['instance']['continues_work_of'],
                'inherited_claim_status': inherited['C1']['effective_status'], 'inherited_failed_attempt': inherited[failed['attempt']]['payload']['result'],
                'ended_writer_rejected': fenced, 'claim_revisions_preserved': len(final['C1']['history']),
                'final_claim_assessment': final['C1']['effective_status'], 'final_task_status': final['T1']['effective_status'],
                'supported_answer_claimed': successor['answer_supported'], 'event_chain_verified': audited['head'] == checkpoint, 'event_count': checkpoint['seq']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
