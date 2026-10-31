"""Adversarial development tests, not independent specialist performance data."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

from mplpb_work import WorkStore, WorkError, Conflict, Denied, IntegrityError
from mplpb_work.store import digest
from mplpb_work.model import OPERATIONS
from mplpb_combined.ledger import write, Ledger


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.now = [1000.0]
        self.corpus = self.base/'corpus'
        write(self.corpus, doc_id='SRC-0001', title='Supplier', scope='supplier availability',
              body='Configuration AX-14 is discontinued. Component X remains available.')
        self.source = Ledger(self.corpus).by_id['SRC-0001'][0]
        self.store, self.host = WorkStore.create(self.base/'work', {'research': self.corpus}, clock=lambda: self.now[0])
        self.calls = []
        self.store.executors['fixture.run.v1'] = self.adapter
        self.tokens = {}
        self.roles = ['finder', 'critic', 'builder', 'reviewer']
        for role in self.roles:
            self.assign(role, role+'-1')
        self.put('finder', 'T1', 'task', self.task())

    def adapter(self, request):
        self.calls.append(request)
        return {'result': 'passed', 'validation': {'test passes': True}, 'artifact': 'fixture passed'}

    def assign(self, seat, instance, operations=None, tools=None, share=None, profile='internal', predecessor=None):
        contract = {'operations': sorted(OPERATIONS if operations is None else operations),
                    'tools': ['fixture.run.v1'] if tools is None else tools,
                    'scopes': ['T1', 'T2'], 'share_with': self.roles if share is None else share,
                    'profile': profile, 'expires_at': 10000.0}
        result = self.store.assign(self.host, seat=seat, instance=instance,
                    model={'name': 'same-model', 'provider': 'fixture', 'version': '1', 'context_policy_hash': digest({'policy': 'fixture'})},
                    contract=contract, continues_work_of=predecessor, expected_head=self.store.head(self.host)['hash'])
        self.tokens[seat] = result['credential']
        return result

    def task(self):
        return {'goal': 'Test component availability', 'criteria': ['test passes'], 'review_budget': 4, 'state': 'open', 'acceptance': {}}

    def evidence(self, quote='Configuration AX-14 is discontinued.'):
        return {'task': 'T1', 'corpus': 'research', 'source_id': self.source.id,
                'source_hash': self.source.hash, 'quote': quote, 'query': 'supplier availability'}

    def claim(self, **changes):
        p = {'task': 'T1', 'proposition': 'Component X is discontinued', 'basis': 'inference',
             'assessment': 'supported_under_scope', 'assumptions': ['Configuration covers component'],
             'alternatives': ['Other configurations may remain'], 'revisit_when': 'Check component catalog'}
        p.update(changes)
        return p

    def action(self, **changes):
        p = {'task': 'T1', 'task_revision': 1, 'operation': 'fixture.run.v1', 'arguments': {'case': 'availability'},
             'side_effect': 'local', 'executor_seat': 'builder', 'state': 'proposed', 'retry_of': {}, 'retry_reason': ''}
        p.update(changes)
        return p

    def review(self, **changes):
        p = {'task': 'T1', 'target': {'C1': 1}, 'target_variable': 'component-level availability',
             'regime': 'supplier catalog 2026', 'finding': 'Configuration is narrower than component',
             'outcome': 'challenge', 'resolution': ''}
        p.update(changes)
        return p

    def put(self, seat, id, kind, payload, deps=None, visible=None, revision=0):
        return self.store.put(self.tokens[seat], id=id, kind=kind, payload=payload,
                    dependencies=deps or {}, visibility=visible or list(self.roles),
                    expected_revision=revision, expected_head=self.store.snapshot(self.tokens[seat])['head'])

    def rows(self, seat='builder'):
        return {r['id']: r for r in self.store.snapshot(self.tokens[seat])['records']}

    def prepare(self):
        self.put('finder', 'E1', 'evidence', self.evidence())
        self.put('finder', 'C1', 'claim', self.claim(), {'E1': 1})
        self.put('builder', 'A1', 'action', self.action(), {'C1': 1})

    def execute(self, id='A1', revision=1):
        token = self.tokens['builder']
        return self.store.execute(token, id=id, expected_revision=revision, expected_head=self.store.snapshot(token)['head'])

    def test_five_instances_recover_and_revise_inherited_premise(self):
        self.prepare()
        self.store.executors['fixture.run.v1'] = lambda _: {'result': 'failed', 'validation': {'test passes': False}, 'artifact': 'wrong configuration'}
        failed = self.execute()
        self.put('finder', 'E2', 'evidence', self.evidence('Component X remains available.'))
        self.put('critic', 'R1', 'review', self.review(), {'E2': 1})
        for role in ('finder', 'critic'):
            token = self.tokens[role]
            self.store.end(token, self.store.snapshot(token)['head'])
        old = self.tokens['builder']
        self.assign('builder', 'builder-2', predecessor='builder-1')
        with self.assertRaises(Denied):
            self.store.snapshot(old)
        # New process/store, same work, a new instance, and the old failed attempt.
        reopened = WorkStore(self.base/'work', {'fixture.run.v1': self.adapter}, clock=lambda: self.now[0])
        handoff = reopened.handoff(self.tokens['builder'])
        rows = {r['id']: r for r in handoff['records']}
        self.assertEqual(handoff['instance']['continues_work_of'], 'builder-1')
        self.assertEqual(rows['C1']['effective_status'], 'contested')
        self.assertEqual(rows[failed['attempt']]['payload']['result'], 'failed')
        self.assertNotIn('A1', handoff['next_actions'])
        self.put('reviewer', 'C1', 'claim', self.claim(proposition='Component X remains available', assumptions=[]), {'E2': 1}, revision=1)
        self.assertEqual(self.rows()['C1']['effective_status'], 'contested')
        self.put('reviewer', 'R1', 'review', self.review(outcome='resolved', resolution='Corrected component-level proposition using catalog statement'), {'E2': 1}, revision=1)
        self.assertEqual(self.rows()['C1']['effective_status'], 'supported_under_scope')
        self.store.executors['fixture.run.v1'] = self.adapter
        self.put('builder', 'A2', 'action', self.action(arguments={'case': 'corrected availability'}, retry_of={failed['attempt']: 1}, retry_reason='Corrected component scope and inputs'), {'C1': 2})
        success = self.execute('A2')
        done = self.task(); done.update(state='done', acceptance={success['attempt']: 1})
        self.put('reviewer', 'T1', 'task', done, revision=1)
        rows = self.rows()
        self.assertEqual(rows['T1']['effective_status'], 'done')
        self.assertEqual(rows['C1']['history'][0]['payload']['proposition'], 'Component X is discontinued')
        audit = self.store.audit(self.host)
        identities = [e['payload']['instance'] for e in audit['events'] if e['type'] == 'assign']
        self.assertEqual(len(identities), 5)
        self.assertEqual(len({i['id'] for i in identities}), 5)
        self.assertEqual(len({i['model']['name'] for i in identities}), 1)

    def test_plaintext_private_content_absent_from_live_and_handoff_views(self):
        before = self.store.snapshot(self.tokens['builder'])
        self.put('finder', 'PRIVATE-SECRET', 'claim', self.claim(proposition='nonce-ultraviolet-947', assessment='proposed'), visible=['finder'])
        for result in (self.store.snapshot(self.tokens['builder']), self.store.handoff(self.tokens['builder'])):
            self.assertEqual(result['head'], before['head'])
            self.assertNotIn('nonce-ultraviolet', json.dumps(result))
            self.assertNotIn('PRIVATE-SECRET', json.dumps(result))
            self.assertNotIn('redacted', json.dumps(result))

    def test_visibility_cannot_be_laundered_through_reference(self):
        self.put('finder', 'E1', 'evidence', self.evidence(), visible=['finder'])
        with self.assertRaises(Denied):
            self.put('finder', 'C1', 'claim', self.claim(), {'E1': 1})

    def test_explicit_transfer_includes_history_but_requires_rights(self):
        self.put('finder', 'C1', 'claim', self.claim(assessment='proposed'), visible=['finder'])
        token = self.tokens['finder']
        result = self.store.transfer(token, id='C1', to=['builder'], include_history=True, expected_revision=1, expected_head=self.store.snapshot(token)['head'])
        self.assertIn('C1', self.rows())
        self.assertEqual(len(self.rows()['C1']['history']), 2)
        self.assertEqual(result['records'][-1]['kind'] in {'claim', 'task'}, True)

    def test_no_capability_self_promotion_or_ungranted_write(self):
        self.assign('builder', 'builder-2', operations=['create:attempt'], tools=[], share=[])
        with self.assertRaises(Denied):
            self.put('builder', 'C1', 'claim', self.claim(assessment='proposed'))
        with self.assertRaises(WorkError):
            self.put('builder', 'grant', 'seat', {'operations': ['*']})
        with self.assertRaises(Denied):
            self.store.head(self.tokens['builder'])

    def test_private_writer_cannot_create_shared_content(self):
        self.assign('finder', 'finder-2', share=[])
        with self.assertRaises(Denied):
            self.put('finder', 'C1', 'claim', self.claim(assessment='proposed'))
        self.put('finder', 'C1', 'claim', self.claim(assessment='proposed'), visible=['finder'])

    def test_expiry_revocation_and_fencing_are_checked_at_write(self):
        self.prepare()
        stale = self.tokens['builder']
        old_view = self.store.snapshot(stale)['head']
        self.assign('builder', 'builder-2', predecessor='builder-1')
        with self.assertRaises(Denied):
            self.store.execute(stale, id='A1', expected_revision=1, expected_head=old_view)
        self.store.revoke(self.host, 'builder', self.store.head(self.host)['hash'])
        with self.assertRaises(Denied):
            self.store.snapshot(self.tokens['builder'])
        self.now[0] = 10001.0
        with self.assertRaises(Denied):
            self.store.snapshot(self.tokens['finder'])
        self.assertEqual(self.calls, [])

    def test_stale_head_and_target_revision_reject_without_appending(self):
        self.prepare()
        token = self.tokens['builder']; head = self.store.snapshot(token)['head']
        self.put('finder', 'E2', 'evidence', self.evidence('Component X remains available.'))
        before = self.store.head(self.host)
        with self.assertRaises(Conflict):
            self.store.execute(token, id='A1', expected_revision=1, expected_head=head)
        with self.assertRaises(Conflict):
            self.store.execute(token, id='A1', expected_revision=9, expected_head=self.store.snapshot(token)['head'])
        self.assertEqual(self.store.head(self.host), before)

    def test_challenge_blocks_transitive_dependents_and_owner_cannot_erase_it(self):
        self.prepare()
        decision = {'task': 'T1', 'choice': 'Redesign', 'alternatives': ['Check catalog'], 'reason': 'Unavailable component', 'assessment': 'accepted', 'recheck_when': 'Source scope changes', 'failed_attempts': {}}
        self.put('finder', 'D1', 'decision', decision, {'C1': 1})
        self.put('critic', 'R1', 'review', self.review(), {'E1': 1})
        self.assertEqual(self.rows()['D1']['effective_status'], 'needs_recheck')
        self.put('finder', 'C1', 'claim', self.claim(), {'E1': 1}, revision=1)
        self.assertEqual(self.rows()['C1']['effective_status'], 'contested')
        with self.assertRaises(Denied):
            self.put('critic', 'R1', 'review', self.review(target={'C1': 2}, outcome='support'), {'E1': 1}, revision=1)
        with self.assertRaises(Denied):
            self.execute()

    def test_copied_review_adds_no_evidence_roots_or_truth(self):
        self.prepare()
        self.put('critic', 'R1', 'review', self.review(outcome='support'), {'E1': 1})
        self.put('reviewer', 'R2', 'review', self.review(outcome='support'), {'E1': 1})
        rows = self.rows()
        self.assertEqual(len(rows['R1']['new_evidence_roots']), 1)
        self.assertEqual(rows['R2']['new_evidence_roots'], [])
        self.assertEqual(rows['R2']['discrimination'], 'unmeasured')
        for n in (3, 4):
            self.put('critic', 'R'+str(n), 'review', self.review(outcome='inconclusive'), {'E1': 1})
        with self.assertRaises(WorkError):
            self.put('critic', 'R5', 'review', self.review(), {'E1': 1})

    def test_no_terminal_truth_and_no_forged_pass_or_completion(self):
        with self.assertRaises(WorkError):
            self.put('finder', 'C1', 'claim', self.claim(assessment='true'))
        fake = {'task': 'T1', 'method': 'claim', 'result': 'passed', 'failure': 'none', 'retry_when': 'none', 'artifact': 'I did it'}
        with self.assertRaises(WorkError):
            self.put('builder', 'F1', 'attempt', fake)
        done = self.task(); done['state'] = 'done'
        with self.assertRaises(WorkError):
            self.put('builder', 'T1', 'task', done, revision=1)
        self.assertEqual(self.rows()['T1']['payload']['state'], 'open')

    def test_heading_scope_and_tampered_source_cannot_supply_evidence(self):
        for bad in ('Supplier', 'supplier availability', 'An invented source sentence.'):
            with self.assertRaises(WorkError):
                self.put('finder', 'E1', 'evidence', self.evidence(bad))
        page = self.corpus/self.source.path
        page.write_text(page.read_text().replace('is discontinued', 'is available'))
        with self.assertRaises(WorkError):
            self.put('finder', 'E1', 'evidence', self.evidence())

    def test_source_change_invalidates_claim_decision_action_and_completed_task(self):
        self.prepare()
        success = self.execute()
        done = self.task(); done.update(state='done', acceptance={success['attempt']: 1})
        self.put('reviewer', 'T1', 'task', done, revision=1)
        page = self.corpus/self.source.path
        page.write_text(page.read_text().replace('is discontinued', 'is available'))
        rows = self.rows()
        for id in ('E1', 'C1', 'A1', 'T1', success['attempt']):
            self.assertEqual(rows[id]['effective_status'], 'needs_recheck', id)
        self.assertEqual(rows['E1']['payload']['quote'], 'Configuration AX-14 is discontinued.')
        self.assertEqual(rows['C1']['history'][0]['payload']['basis'], 'inference')

    def test_crash_reopen_is_indeterminate_and_never_auto_retries(self):
        self.prepare()
        def crash(request):
            raise SystemExit('simulated lost runtime')
        self.store.executors['fixture.run.v1'] = crash
        with self.assertRaises(SystemExit):
            self.execute()
        reopened = WorkStore(self.base/'work', {'fixture.run.v1': self.adapter}, clock=lambda: self.now[0])
        rows = {r['id']: r for r in reopened.snapshot(self.tokens['builder'])['records']}
        self.assertEqual(rows['A1']['effective_status'], 'indeterminate')
        with self.assertRaises(Denied):
            self.execute()
        self.put('builder', 'A2', 'action', self.action(), {'C1': 1})
        self.assertEqual(self.rows()['A2']['permission'], 'blocked')
        audit = self.store.audit(self.host)
        receipt = next(e['payload']['receipt']['id'] for e in audit['events'] if e['type'] == 'start')
        reconciled = self.store.reconcile(self.host, receipt=receipt, result='failed', validation={}, artifact='External fixture did not commit', reason='Operator inspected fixture output', expected_head=self.store.head(self.host)['hash'])
        self.assertEqual(reconciled['receipt']['status'], 'failed')
        self.assertEqual(self.calls, [])

    def test_adapter_error_is_indeterminate_not_a_clean_failure(self):
        self.prepare()
        def error(_):
            raise RuntimeError('could have completed a side effect')
        self.store.executors['fixture.run.v1'] = error
        result = self.execute()
        self.assertEqual(result['receipt']['status'], 'indeterminate')
        self.assertEqual(self.rows()[result['attempt']]['payload']['result'], 'indeterminate')
        self.assertNotIn('could have completed', json.dumps(self.rows()))

    def test_dispatch_idempotency_and_missing_adapter(self):
        self.prepare()
        fresh = WorkStore(self.base/'work', clock=lambda: self.now[0])
        self.assertEqual(fresh.snapshot(self.tokens['builder'])['next_actions'], [])
        self.execute()
        with self.assertRaises(Denied):
            self.execute(revision=2)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(self.calls[0]['idempotency_key']), 32)

    def test_concurrent_writers_have_one_winner_and_no_partial_event(self):
        token = self.tokens['finder']; head = self.store.snapshot(token)['head']
        barrier = threading.Barrier(2)
        def write_claim(n):
            other = WorkStore(self.base/'work', clock=lambda: self.now[0])
            barrier.wait()
            try:
                other.put(token, id='C'+str(n), kind='claim', payload=self.claim(assessment='proposed'), dependencies={}, visibility=list(self.roles), expected_revision=0, expected_head=head)
                return 'ok'
            except Conflict:
                return 'conflict'
        with ThreadPoolExecutor(2) as pool:
            self.assertCountEqual(pool.map(write_claim, [1, 2]), ['ok', 'conflict'])
        audit = self.store.audit(self.host)
        self.assertEqual(audit['head']['seq'], len(audit['events']))

    def test_chain_corruption_and_independent_truncation_checkpoint(self):
        checkpoint = self.store.head(self.host)
        self.put('finder', 'C1', 'claim', self.claim(assessment='proposed'))
        self.store.audit(self.host, checkpoint)
        with sqlite3.connect(str(self.store.path)) as db:
            db.execute("UPDATE events SET body=replace(body,'Component X','Component Y') WHERE seq=(SELECT max(seq) FROM events)")
        with self.assertRaises(IntegrityError):
            self.store.snapshot(self.tokens['builder'])

    def test_new_process_can_recover_without_original_runtime(self):
        self.prepare()
        code = 'import json,sys; from mplpb_work import WorkStore; p=json.load(sys.stdin); print(json.dumps(WorkStore(p["path"],clock=lambda:1000).handoff(p["credential"])))'
        output = subprocess.check_output([sys.executable, '-c', code], input=json.dumps({'path': str(self.base/'work'), 'credential': self.tokens['builder']}).encode())
        recovered = json.loads(output)
        self.assertIn('C1', {r['id'] for r in recovered['records']})
        self.assertFalse(recovered['answer_supported'])
        self.assertNotIn(self.host, output.decode())

    def test_external_profile_cannot_recover_private_source_via_old_claim_history(self):
        self.prepare()
        # Explicitly sealed external restriction, including historical derivatives.
        write(self.corpus, doc_id='SRC-0002', title='Private supplier', scope='private supplier', body='A private fixture fact.', external='no')
        rec = Ledger(self.corpus).by_id['SRC-0002'][0]
        ev = {'task': 'T1', 'corpus': 'research', 'source_id': rec.id, 'source_hash': rec.hash, 'quote': 'A private fixture fact.', 'query': 'private supplier'}
        self.put('finder', 'E2', 'evidence', ev)
        self.put('finder', 'C1', 'claim', self.claim(proposition='nonce-private-fact'), {'E2': 1}, revision=1)
        self.put('finder', 'C1', 'claim', self.claim(proposition='public-scope proposition'), {'E1': 1}, revision=2)
        self.assign('builder', 'builder-2', profile='external')
        output = json.dumps(self.store.handoff(self.tokens['builder']))
        self.assertNotIn('nonce-private-fact', output)
        self.assertNotIn('A private fixture fact', output)
        self.assertNotIn('SRC-0002', output)

    def test_task_dependency_graph_cannot_cycle(self):
        self.put('finder', 'T2', 'task', self.task(), {'T1': 1})
        self.assertEqual(self.rows()['T2']['effective_status'], 'needs_recheck')
        with self.assertRaises(WorkError):
            self.put('finder', 'T1', 'task', self.task(), {'T2': 1}, revision=1)

    def test_changed_criteria_do_not_inherit_old_passing_receipt(self):
        self.prepare(); passed = self.execute()
        task = self.task(); task.update(state='done', acceptance={passed['attempt']: 1}, criteria=['a different criterion'])
        with self.assertRaises(WorkError):
            self.put('reviewer', 'T1', 'task', task, revision=1)

    def test_failed_attempts_immutable_and_failed_route_not_repeated(self):
        self.prepare()
        self.store.executors['fixture.run.v1'] = lambda _: {'result': 'failed', 'validation': {}, 'artifact': 'broken fixture'}
        failed = self.execute()
        attempt = self.rows()[failed['attempt']]
        with self.assertRaises(Denied):
            self.put('builder', failed['attempt'], 'attempt', attempt['payload'], {'C1': 1}, revision=1)
        self.put('builder', 'A2', 'action', self.action(), {'C1': 1})
        with self.assertRaises(Denied):
            self.execute('A2')
        self.put('builder', 'A3', 'action', self.action(arguments={'case': 'different configuration'}, retry_of={failed['attempt']: 1}, retry_reason='Try a different configuration'), {'C1': 1})
        self.assertEqual(self.rows()['A3']['permission'], 'allowed')

    def test_seat_cannot_resolve_challenge_without_resolution_right(self):
        self.prepare()
        self.put('critic', 'R1', 'review', self.review(), {'E1': 1})
        self.assign('critic', 'critic-2', operations=['revise:review'])
        with self.assertRaises(Denied):
            self.put('critic', 'R1', 'review', self.review(outcome='resolved', resolution='The owner agreed'), {'E1': 1}, revision=1)
        self.assertEqual(self.rows()['C1']['effective_status'], 'contested')

    def test_different_spans_same_root_are_not_called_independent_sources(self):
        self.prepare()
        self.put('finder', 'E2', 'evidence', self.evidence('Component X remains available.'))
        self.put('critic', 'R1', 'review', self.review(outcome='support'), {'E1': 1})
        self.put('reviewer', 'R2', 'review', self.review(), {'E2': 1})
        self.assertEqual(self.rows()['R2']['new_evidence_roots'], [])
        self.assertEqual(len(self.rows()['R2']['new_evidence_spans']), 1)

    def test_checkpoint_detects_history_rewrite_even_if_local_head_replaced(self):
        self.prepare()
        trusted = self.store.head(self.host)
        audit = self.store.audit(self.host)
        previous = audit['events'][-2]
        with sqlite3.connect(str(self.store.path)) as db:
            db.execute('DELETE FROM events WHERE seq=?', (trusted['seq'],))
            db.execute('UPDATE head SET seq=?,hash=?', (previous['seq'], digest(previous)))
        with self.assertRaises(IntegrityError):
            self.store.audit(self.host, trusted)

    def test_transfer_does_not_launder_historical_dependencies(self):
        self.put('finder', 'E1', 'evidence', self.evidence(), visible=['finder'])
        self.put('finder', 'C1', 'claim', self.claim(), {'E1': 1}, visible=['finder'])
        token = self.tokens['finder']
        with self.assertRaises(Denied):
            self.store.transfer(token, id='C1', to=['builder'], include_history=True, expected_revision=1, expected_head=self.store.snapshot(token)['head'])

    def test_dispatched_action_cannot_be_rewritten_or_transferred(self):
        self.prepare(); self.execute()
        action = self.rows()['A1']
        with self.assertRaises((Denied, WorkError)):
            self.put('builder', 'A1', 'action', self.action(), {'C1': 1}, revision=action['revision'])
        token = self.tokens['builder']
        with self.assertRaises(Denied):
            self.store.transfer(token, id='A1', to=['reviewer'], include_history=True, expected_revision=action['revision'], expected_head=self.store.snapshot(token)['head'])

    def test_public_seat_api_cannot_invoke_administration(self):
        from mplpb_work.api import request
        with self.assertRaises(WorkError):
            request(self.store, self.host, {'op': 'audit'})
        with self.assertRaises(WorkError):
            request(self.store, self.tokens['builder'], {'op': 'snapshot', 'authority': self.host})

    def test_task_revision_is_rechecked_at_dispatch_and_acceptance(self):
        self.prepare()
        changed = self.task(); changed['goal'] = 'Revised task contract'
        self.put('reviewer', 'T1', 'task', changed, revision=1)
        self.assertEqual(self.rows()['A1']['permission'], 'blocked')
        with self.assertRaises(Denied):
            self.execute()
        self.put('builder', 'A2', 'action', self.action(task_revision=2), {'C1': 1})
        passed = self.execute('A2')
        self.put('reviewer', 'T1', 'task', changed, revision=2)
        done = copy.deepcopy(changed); done.update(state='done', acceptance={passed['attempt']: 1})
        with self.assertRaises(WorkError):
            self.put('reviewer', 'T1', 'task', done, revision=3)

    def test_host_effect_class_cannot_be_downgraded_by_action(self):
        self.prepare()
        self.store.executors['fixture.run.v1'] = {'run': self.adapter, 'side_effect': 'external'}
        self.assertEqual(self.rows()['A1']['permission'], 'blocked')
        with self.assertRaises(Denied):
            self.execute()
        self.put('builder', 'A1', 'action', self.action(side_effect='external'), {'C1': 1}, revision=1)
        self.execute(revision=2)
        self.assertEqual(len(self.calls), 1)

    def test_task_input_pins_travel_into_execution_attempt(self):
        self.put('finder', 'E1', 'evidence', self.evidence())
        self.put('finder', 'C1', 'claim', self.claim(), {'E1': 1})
        self.put('finder', 'T1', 'task', self.task(), {'C1': 1}, revision=1)
        self.put('builder', 'A1', 'action', self.action(task_revision=2))
        passed = self.execute()
        self.assertEqual(self.rows()[passed['attempt']]['dependencies'], {'C1': 1})
        self.put('finder', 'C1', 'claim', self.claim(assessment='withdrawn'), {'E1': 1}, revision=1)
        self.assertEqual(self.rows()[passed['attempt']]['effective_status'], 'needs_recheck')

    def test_local_http_rpc_requires_bearer_and_excludes_host_operations(self):
        from http.server import ThreadingHTTPServer
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        from tools.ledger_ui import App, handler
        app = App(topic_base=self.base/'topics', work_store=self.store)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        url = 'http://127.0.0.1:'+str(server.server_port)+'/api/work'
        def post(payload, token=None):
            headers = {'Content-Type': 'application/json'}
            if token:
                headers['Authorization'] = 'Bearer '+token
            return json.loads(urlopen(Request(url, data=json.dumps(payload).encode(), headers=headers)).read())
        with self.assertRaises(HTTPError):
            post({'op': 'snapshot'})
        with self.assertRaises(HTTPError):
            post({'op': 'audit'}, self.host)
        view = post({'op': 'handoff'}, self.tokens['builder'])
        self.assertEqual(view['instance']['id'], 'builder-1')
        self.assertFalse(view['answer_supported'])
        self.assertNotIn(self.host, json.dumps(view))
        # The work host must not expose the ordinary unauthenticated source API.
        for path in ('/api/query', '/api/page?corpus=studio&path=kiln/studio-0004.html', '/api/state', '/'):
            with self.assertRaises(HTTPError):
                urlopen(url.replace('/api/work', path))
        with self.assertRaises(HTTPError):
            urlopen(Request(url.replace('/api/work', '/api/query'), data=b'{}', headers={'Content-Type': 'application/json'}))

    def test_cli_is_installed_in_supported_entrypoint(self):
        from mplpb_answers.__main__ import main
        import contextlib, io
        credential = self.base/'host.json'; credential.write_text(json.dumps({'authority_credential': self.host}))
        query = self.base/'request.json'; query.write_text(json.dumps({'op': 'head'}))
        with contextlib.redirect_stdout(io.StringIO()) as output:
            status = main(['work', 'request', str(self.base/'work'), '--credential-file', str(credential), '--input', str(query)])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue()), self.store.head(self.host))

    def test_review_revisions_cannot_bypass_declared_budget(self):
        self.prepare()
        self.put('critic', 'R1', 'review', self.review(outcome='inconclusive'), {'E1': 1})
        for revision in (1, 2, 3):
            self.put('critic', 'R1', 'review', self.review(outcome='inconclusive', finding='Round '+str(revision+1)), {'E1': 1}, revision=revision)
        with self.assertRaises(WorkError):
            self.put('critic', 'R1', 'review', self.review(outcome='support'), {'E1': 1}, revision=4)

    def test_scope_and_tool_allowlists_are_enforced_independently(self):
        self.prepare()
        self.assign('builder', 'builder-2', operations=['execute'], tools=[])
        self.assertEqual(self.rows()['A1']['permission'], 'requires_authorization')
        with self.assertRaises(Denied):
            self.execute()
        contract = {'operations': ['create:claim'], 'tools': [], 'scopes': ['T2'], 'share_with': [], 'profile': 'internal', 'expires_at': 10000}
        outsider = self.store.assign(self.host, seat='outsider', instance='outsider-1', model={'name': 'same-model', 'provider': 'fixture', 'version': '1', 'context_policy_hash': digest({'policy': 'fixture'})}, contract=contract, expected_head=self.store.head(self.host)['hash'])
        self.assertEqual(self.store.snapshot(outsider['credential'])['records'], [])
        with self.assertRaises(Denied):
            self.store.put(outsider['credential'], id='orphan', kind='claim', payload=self.claim(assessment='proposed'), dependencies={}, visibility=['outsider'], expected_revision=0, expected_head=self.store.snapshot(outsider['credential'])['head'])

    def test_concurrent_processes_use_database_compare_and_swap(self):
        head = self.store.snapshot(self.tokens['finder'])['head']
        code = '''import json,sys
from mplpb_work import WorkStore,Conflict
p=json.load(sys.stdin)
try:
 WorkStore(p.pop('directory'),clock=lambda:1000).put(**p)
 print('committed')
except Conflict:
 print('conflict')
'''
        def process(n):
            params = {'directory': str(self.base/'work'), 'credential': self.tokens['finder'], 'id': 'P'+str(n), 'kind': 'claim', 'payload': self.claim(assessment='proposed'), 'dependencies': {}, 'visibility': self.roles, 'expected_revision': 0, 'expected_head': head}
            return subprocess.check_output([sys.executable, '-c', code], input=json.dumps(params).encode()).decode().strip()
        with ThreadPoolExecutor(2) as pool:
            self.assertCountEqual(list(pool.map(process, [1, 2])), ['committed', 'conflict'])
        self.store.audit(self.host)

    def test_failed_attempt_is_context_for_decision_not_a_success_prerequisite(self):
        self.prepare()
        self.store.executors['fixture.run.v1'] = lambda _: {'result': 'failed', 'validation': {}, 'artifact': 'Unsuccessful route'}
        failed = self.execute()
        decision = {'task': 'T1', 'choice': 'Try the component-specific fixture', 'alternatives': ['Repeat configuration fixture'], 'reason': 'The recorded route failed under the old assumptions', 'assessment': 'accepted', 'recheck_when': 'Inputs or acceptance criteria change', 'failed_attempts': {failed['attempt']: 1}}
        self.put('reviewer', 'D1', 'decision', decision)
        self.assertEqual(self.rows()['D1']['effective_status'], 'accepted')
        self.assertIn(failed['attempt'], self.rows()['D1']['payload']['failed_attempts'])
