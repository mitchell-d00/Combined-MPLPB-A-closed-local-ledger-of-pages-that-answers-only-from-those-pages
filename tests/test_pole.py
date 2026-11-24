"""Pole custody, replay and independently worded regression controls."""
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write, withdraw
from tools import pole
from tools import dpercent as D
from tools import dpercent_weaknesses as W


class PoleTests(unittest.TestCase):
    def test_catalog_assigns_every_inherited_family_once(self):
        self.assertEqual(set(pole.CLASS_TIERS), set(W.FAMILIES))
        self.assertEqual(set(pole.CLASS_TIERS.values()), set(pole.TIERS))

    def test_seed_replays_and_pinning_preserves_bytes_and_key(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            options = dict(seed=7, count=2, levels=('easy',), suite='focus')
            first = pole.prepare(root / 'one', root / 'key-one', **options)
            pole.prepare(root / 'two', root / 'key-two', **options)
            self.assertEqual(D.files(root / 'one'), D.files(root / 'two'))
            self.assertEqual(D.files(root / 'key-one'), D.files(root / 'key-two'))
            selected = next(iter(first))
            mixed = pole.prepare(root / 'mixed', root / 'key-mixed', **(options | {'seed': 8}),
                                 pinned=(root / 'one', root / 'key-one', [selected]))
            self.assertEqual(len(mixed), 3)
            self.assertEqual(mixed[selected]['cohort'], 'pinned')
            self.assertEqual(D.files(root / 'one' / 'packets' / selected),
                             D.files(root / 'mixed' / 'packets' / selected))
            self.assertEqual(pole.load_keys(root / 'key-one')[selected],
                             pole.load_keys(root / 'key-mixed')[selected])
            source = root / 'one' / 'packets' / selected / 'sources' / 'item-01.txt'
            source.write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError, 'Frozen packet bytes changed'):
                pole.load_packet(root / 'one', root / 'key-one')


class RecordedFieldRegression(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.page('SOURCE-1', 'DEPOT-71', 'Gold')
        self.page('SOURCE-2', 'DEPOT-72', 'Blue')

    def page(self, doc, record, value):
        text = f'Record-ID: {record}\nClearance Code: {value}'
        return write(self.root, doc_id=doc, title='Dispatch slip', scope='dispatch',
                     body_html='<pre>' + escape(text) + '</pre>', origin='machine')

    def test_recorded_value_requires_the_named_record_and_field(self):
        for question in (
            'What is the value stated for clearance code in occurrence DEPOT-71?',
            'What value is recorded for clearance code on record DEPOT-71?',
        ):
            with self.subTest(question=question):
                result = answer_query(self.root, question).contract
                self.assertTrue(result['answer_supported'])
                self.assertEqual(result['question'], question)
                self.assertEqual(result['claims'][0]['text'], 'Clearance Code: Gold')
                self.assertEqual(result['claims'][0]['citations'][0]['source_id'], 'SOURCE-1')
                self.assertFalse(result['question_normalization']['normalization_is_evidence'])

    def test_scope_is_preserved(self):
        base = 'What value is listed for clearance code on record DEPOT-71'
        for question in (
            base + ' before the revision?',
            base + ' according to the porter?',
            base + ' and who approved it?',
            base + ' if the permit was granted?',
            base.replace('clearance code', 'clearance code and owner') + '?',
            base.replace('DEPOT-71', 'DEPOT-99') + '?',
        ):
            with self.subTest(question=question):
                self.assertFalse(answer_query(self.root, question).contract['answer_supported'])

    def test_competing_sources_and_withdrawal_are_rechecked(self):
        question = 'What is the value listed for clearance code in record DEPOT-71?'
        self.page('SOURCE-3', 'DEPOT-71', 'Violet')
        result = answer_query(self.root, question).contract
        self.assertEqual(result['kind'], 'conflict')
        self.assertFalse(result['answer_supported'])
        withdraw(self.root, 'SOURCE-3')
        self.assertTrue(answer_query(self.root, question).contract['answer_supported'])
        withdraw(self.root, 'SOURCE-1')
        self.assertFalse(answer_query(self.root, question).contract['answer_supported'])
