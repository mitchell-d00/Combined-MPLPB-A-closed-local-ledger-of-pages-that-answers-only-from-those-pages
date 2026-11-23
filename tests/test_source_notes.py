"""Tests for live search-only notes stored under WorkStore capabilities."""
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write
from mplpb_work import Denied, WorkError, WorkStore
from mplpb_work.api import request


class SourceNoteTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'corpus'
        self.root.mkdir()
        self.work = Path(temp.name) / 'work'
        self.store, self.host = WorkStore.create(self.work, {'archive': self.root}, clock=lambda: 1000)
        self.editor = self.seat('editor', ['create:task', 'create:evidence', 'create:source_note',
                                         'revise:source_note', 'search:source_note'], share=['reader'])
        self.reader = self.seat('reader', ['search:source_note'])
        self.observer = self.seat('observer', [])
        self.put('T', 'task', {'goal': 'Inspect harbor holdings', 'criteria': ['Check source'],
                                'review_budget': 2, 'state': 'open', 'acceptance': {}},
                 visibility=['editor', 'reader'])
        self.text = 'The transfer of the slip was drafted. A margin note leaves its outcome open.'
        self.page = self.write('REGISTER-1', self.text)
        self.record_evidence('E', self.page, self.text)

    def seat(self, name, operations, share=None, scopes=None):
        return self.store.assign(
            self.host, seat=name, instance=name + '-1',
            model={'name': name, 'provider': 'test', 'version': '1', 'context_policy_hash': 'unknown'},
            contract={'operations': operations, 'tools': [], 'scopes': scopes or ['T'],
                      'share_with': share or [], 'profile': 'internal', 'expires_at': 2000},
            expected_head=self.store.head(self.host)['hash'])['credential']

    def write(self, ident, text, **options):
        return write(self.root, doc_id=ident, title='Harbor holding', scope='Harbor holding record',
                     body_html='<pre>' + escape(text) + '</pre>', when='2026-11-23', **options)

    def put(self, ident, kind, payload, dependencies=None, visibility=None, revision=0):
        return self.store.put(self.editor, id=ident, kind=kind, payload=payload,
                              dependencies=dependencies or {}, visibility=visibility or ['editor'],
                              expected_revision=revision, expected_head=self.store.snapshot(self.editor)['head'])

    def record_evidence(self, ident, record, quote):
        return self.put(ident, 'evidence', {'task': 'T', 'corpus': 'archive', 'source_id': record.id,
                                           'source_hash': record.hash, 'quote': quote,
                                           'query': 'Harbor holding record'}, visibility=['editor', 'reader'])

    def note(self, ident='N', evidence='E', **overrides):
        result = {'task': 'T', 'body_start': 0, 'rule': 'recorded_stage',
                  'keywords': ['final outcome', 'transfer'], 'comment': 'Check the status line.', 'state': 'active'}
        result.update(overrides.pop('fields', {}))
        return self.put(ident, 'source_note', result, {evidence: 1}, **overrides)

    def search(self, token=None, **options):
        return request(self.store, token or self.editor, {
            'op': 'source_note_search', 'task': 'T', 'corpus': 'archive',
            'question': 'Was the transfer completed?', **options
        })

    def test_workflow_rereads_source_and_orders_rules(self):
        self.assertEqual(self.search()['candidates'], [])
        self.note(fields={'comment': 'Instruction-like text stays in the workspace.'})
        report = self.search()
        self.assertEqual(report, self.search())
        candidate = report['candidates'][0]
        self.assertEqual(candidate['quote'], self.text)
        self.assertEqual(candidate['source_hash'], self.page.hash)
        self.assertEqual(candidate['note_revision'], 1)
        self.assertEqual(report['rule_order'][0]['rule'], 'recorded_stage')
        self.assertFalse(report['answer_supported'])
        self.assertNotIn('Instruction-like text', str(report))
        self.assertEqual(self.search(question='When did the exhibition open?')['candidates'], [])

    def test_visibility_and_explicit_operation_are_enforced(self):
        self.note()
        empty = self.search(self.reader)
        self.assertEqual(empty['candidates'], [])
        self.note(ident='SHARED', visibility=['editor', 'reader'])
        self.assertEqual([r['note_id'] for r in self.search(self.reader)['candidates']], ['SHARED'])
        with self.assertRaises(Denied):
            self.search(self.observer)

    def test_offset_and_source_revisions_are_checked(self):
        with self.assertRaisesRegex(WorkError, 'span|offset'):
            self.note(fields={'body_start': 1})
        self.note()
        replacement = self.write('REGISTER-2', 'The transfer was completed.', supersedes=[self.page.id])
        self.assertEqual(self.search()['candidates'], [])
        self.record_evidence('E2', replacement, 'The transfer was completed.')
        self.note('NEW', 'E2')
        self.assertEqual(self.search()['candidates'][0]['source_id'], replacement.id)

    def test_revisions_and_withdrawals_change_live_search(self):
        self.note()
        old = self.search()
        self.note(revision=1, fields={'rule': 'corrections'})
        new = self.search()
        self.assertNotEqual(old['note_snapshot'], new['note_snapshot'])
        self.assertEqual(new['rule_order'][0]['rule'], 'corrections')
        self.note(revision=2, fields={'state': 'withdrawn'})
        self.assertEqual(self.search()['candidates'], [])
        record = next(r for r in self.store.snapshot(self.editor)['records'] if r['id'] == 'N')
        self.assertEqual(len(record['history']), 3)

    def test_stale_read_discards_candidates(self):
        self.note()
        original = PassageIndex.unchanged

        def change(index):
            withdraw(self.root, self.page.id)
            return original(index)

        with patch.object(PassageIndex, 'unchanged', change):
            report = self.search()
        self.assertEqual(report['status'], 'source_changed')
        self.assertEqual(report['candidates'], [])

    def test_notes_do_not_change_native_answers_or_citation_budgets(self):
        question = 'Was the transfer completed?'
        baseline = answer_query(self.root, question).contract
        self.note()
        self.note('DUPLICATE')
        self.assertEqual(len(self.search()['candidates']), 1)
        self.assertEqual(self.search(max_chars=20)['candidates'], [])
        self.assertEqual(answer_query(self.root, question).contract, baseline)
