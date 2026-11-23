"""A user can freeze, tag, and test one rule without editing runtime code."""
import copy
import json
from pathlib import Path
import unittest

from mplpb_work import training


EXAMPLE = Path(__file__).resolve().parents[1] / 'evaluation/d12/coordinator'


class TrainingTests(unittest.TestCase):
    def setUp(self):
        self.fixtures, self.key, self.old, self.new = [
            (EXAMPLE / name).read_bytes() for name in
            ('fixtures.json', 'key.json', 'baseline-rule.json', 'elapsed-days-rule.json')]
        self.seal = training.freeze(self.fixtures, self.key)
        self.baseline = training.run(self.fixtures, self.old)
        self.candidate = training.run(self.fixtures, self.new)

    def test_subcoordinator_groups_same_fault_without_showing_holdout(self):
        report = training.tag(self.seal, self.fixtures, self.key, self.baseline)
        self.assertEqual(report['findings'][0]['tag'], 'wrong_value')
        self.assertEqual(report['findings'][0]['cases'], ['dev-cross-month', 'dev-next-day'])
        self.assertTrue(report['findings'][0]['repeatable'])
        self.assertNotIn('holdout-reverse', json.dumps(report))

    def test_coordinator_retests_identical_cases_and_pins_results(self):
        result = training.compare(self.seal, self.fixtures, self.key, self.baseline, self.candidate)
        self.assertEqual(result['verdict'], 'candidate_passed')
        self.assertEqual(result['recovered'], ['dev-cross-month', 'dev-next-day', 'holdout-reverse'])
        self.assertEqual(result['new_regressions'], [])
        self.assertFalse(result['answer_supported'])
        self.assertFalse(result['promoted'])

    def test_rejects_changed_input_and_incomplete_replay(self):
        changed = self.fixtures.replace(b'1904-02-28', b'1904-02-27')
        with self.assertRaisesRegex(ValueError, 'frozen'):
            training.compare(self.seal, changed, self.key, self.baseline, self.candidate)
        bad = copy.deepcopy(self.candidate)
        bad['rows'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            training.compare(self.seal, self.fixtures, self.key, self.baseline, bad)

    def test_new_unsupported_conclusion_blocks_improvement(self):
        rule = {'name': 'elapsed days', 'steps': [{'op': 'read', 'record_id': '$record', 'field': 'Opening Date'}]}
        unsafe = training.run(self.fixtures, json.dumps(rule).encode())
        result = training.compare(self.seal, self.fixtures, self.key, self.baseline, unsafe)
        self.assertEqual(result['verdict'], 'candidate_blocked')
        self.assertIn('control-partial-date', result['new_regressions'])

    def test_user_rule_cannot_include_case_specific_selector_or_call(self):
        for step in ({'op': 'read', 'record_id': 'LOG-1', 'field': 'Opening Date'},
                     {'op': 'exec', 'command': 'invalid'}):
            with self.assertRaises(ValueError):
                training.run(self.fixtures, json.dumps({'name': 'invalid', 'steps': [step]}).encode())


    def test_automatic_repair_selects_only_the_passing_objective(self):
        worked = training.repair(self.seal, self.fixtures, self.key, self.old, 'elapsed_days')
        self.assertEqual(worked['status'], 'repair_selected')
        self.assertEqual(worked['selected_rule']['steps'][0]['mode'], 'elapsed')
        denied = training.repair(self.seal, self.fixtures, self.key, self.old, 'inclusive_days')
        self.assertEqual(denied['status'], 'review_needed')
        self.assertIsNone(denied['selected_rule'])
        self.assertEqual(denied['attempts'][0]['verdict']['verdict'], 'candidate_blocked')
        unknown = training.repair(self.seal, self.fixtures, self.key, self.old, 'unknown')
        healthy = training.repair(self.seal, self.fixtures, self.key, self.new, 'elapsed_days')
        self.assertEqual(healthy['status'], 'baseline_healthy')
        self.assertEqual(healthy['attempts'], [])
        self.assertEqual(unknown['attempts'], [])
        self.assertIsNone(unknown['selected_rule'])


class TrainingApiTests(unittest.TestCase):
    def test_ai_seats_drive_replays_and_review_without_widening_support(self):
        from tempfile import TemporaryDirectory

        from mplpb_work import Denied, WorkError, WorkStore
        from mplpb_work.api import request

        def load(name):
            return (EXAMPLE / name).read_text()

        fixtures, key = load('fixtures.json'), load('key.json')
        seal = training.freeze(fixtures.encode(), key.encode())
        with TemporaryDirectory() as folder:
            store, host = WorkStore.create(folder, clock=lambda: 1000)

            def seat(name, operations, share=()):
                return store.assign(
                    host, seat=name, instance=name + '-1',
                    model={'name': 'test', 'provider': 'test', 'version': '1', 'context_policy_hash': 'unknown'},
                    contract={'operations': operations, 'tools': [], 'scopes': ['T'], 'share_with': list(share),
                              'profile': 'internal', 'expires_at': 2000}, expected_head=store.head(host)['hash']
                )['credential']

            sub = seat('sub', ['create:task', 'training:tag', 'create:training_finding'], ('coordinator', 'operator'))
            coord = seat('coordinator', ['training:compare', 'training:repair', 'create:rule_sprint'], ('sub',))
            operator = seat('operator', ['training:run'])
            view = store.snapshot(sub)
            request(store, sub, {'op': 'put', 'id': 'T', 'kind': 'task',
                                 'payload': {'goal': 'Teach calendar day counting', 'criteria': ['Preserve refusals'],
                                             'review_budget': 3, 'state': 'open', 'acceptance': {}},
                                 'dependencies': {}, 'visibility': ['sub', 'coordinator', 'operator'],
                                 'expected_revision': 0, 'expected_head': view['head']})
            before, after = [request(store, operator, {'op': 'training_replay', 'task': 'T',
                                                       'fixtures': fixtures, 'rule': load(rule)})
                             for rule in ('baseline-rule.json', 'elapsed-days-rule.json')]
            with self.assertRaises(Denied):
                request(store, sub, {'op': 'training_replay', 'task': 'T', 'fixtures': fixtures,
                                     'rule': load('elapsed-days-rule.json')})
            packet = {'op': 'training_evaluate', 'task': 'T', 'seal': seal, 'fixtures': fixtures, 'key': key,
                      'baseline': before}
            with self.assertRaises(Denied):
                request(store, operator, dict(packet, mode='tag'))
            findings = request(store, sub, dict(packet, mode='tag'))
            request(store, sub, {'op': 'training_record', 'task': 'T', 'id': 'TAG', 'artifact': findings,
                                 'share_with': ['coordinator']})
            verdict = request(store, coord, dict(packet, mode='compare', candidate=after))
            with self.assertRaisesRegex(WorkError, 'same baseline'):
                request(store, coord, {'op': 'training_record', 'task': 'T', 'id': 'BAD',
                                       'artifact': dict(verdict, baseline_sha256='sha256:' + '1' * 64),
                                       'finding_id': 'TAG'})
            view = request(store, coord, {'op': 'training_record', 'task': 'T', 'id': 'SPRINT',
                                          'artifact': verdict, 'finding_id': 'TAG', 'share_with': ['sub']})
            info = next(r for r in view['records'] if r['id'] == 'SPRINT')
            self.assertEqual(info['dependencies'], {'TAG': 1})
            self.assertEqual(info['effective_status'], 'training_record')
            self.assertEqual(info['payload']['verdict'], 'candidate_passed')
            self.assertFalse(view['answer_supported'])
            automatic = {'op': 'training_sprint', 'task': 'T', 'seal': seal, 'fixtures': fixtures,
                         'key': key, 'rule': load('baseline-rule.json'), 'objective': 'elapsed_days'}
            with self.assertRaises(Denied):
                request(store, operator, automatic)
            self.assertEqual(request(store, coord, automatic)['status'], 'repair_selected')
            self.assertNotIn('SPRINT', {r['id'] for r in store.snapshot(operator)['records']})
