import copy
from pathlib import Path
import tempfile
import unittest

from mplpb_combined.ledger import write, withdraw
from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_work.sorter import sort_directory
from tools.sorter_first_study import locate, adapter
from tools.unprepared_challenge import sha


class SorterFirstStudyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.ledger = self.root/'ledger'; self.raw = self.root/'raw'; self.raw.mkdir()
        self.record = write(self.ledger, doc_id='DOC-101', title='Redwood records', scope='Redwood records',
                            origin='human', body_html='<p>Mara wrote the Redwood memorandum.</p>')
        self.text = body_text(self.record.body_html)
        (self.raw/'original.txt').write_bytes(self.text.encode())
        self.graph = sort_directory(self.raw, mode='compare')
        self.bindings = {'original.txt': {'id': self.record.id, 'hash': self.record.hash_actual,
                                          'projection_sha256': sha(self.text.encode())}}
        self.question = 'Who wrote the Redwood memorandum?'

    def pack(self, graph=None, bindings=None):
        index = PassageIndex(self.ledger, self.question)
        base = index.retrieve([self.question], 12, 8000)
        return locate(index, graph or self.graph, bindings or self.bindings, base, 12, 8000)

    def test_locations_are_existing_original_passages_and_bounded(self):
        pack, trace = self.pack()
        self.assertTrue(trace['selected_hints'])
        self.assertLessEqual(len(pack['passages']), 12)
        self.assertLessEqual(sum(len(p['text']) for p in pack['passages']), 8000)
        for p in pack['passages']:
            self.assertEqual(self.text[p['body_start']:p['body_start']+len(p['text'])], p['text'])
            self.assertEqual(p['hash'], self.record.hash_actual)
        self.assertFalse(trace['answer_supported'])

    def test_forged_qualifying_span_is_rejected(self):
        graph = copy.deepcopy(self.graph)
        for n in graph['nodes']:
            if n['kind'] == 'statement': n['span']['text'] = 'Mara did not write the Redwood memorandum.'
        _, trace = self.pack(graph=graph)
        self.assertFalse(trace['selected_hints']); self.assertTrue(trace['invalid_hints'])

    def test_stale_original_pin_is_rejected(self):
        bindings = copy.deepcopy(self.bindings); bindings['original.txt']['hash'] = 'sha256:'+'0'*64
        _, trace = self.pack(bindings=bindings)
        self.assertFalse(trace['selected_hints']); self.assertTrue(trace['invalid_hints'])

    def test_retired_source_is_not_restored(self):
        withdraw(self.ledger, self.record.id, note='Source withdrawn')
        _, trace = self.pack()
        self.assertFalse(trace['selected_hints'])
        with adapter(self.graph, self.bindings, []):
            answer = answer_query(self.ledger, self.question).contract
        self.assertFalse(answer['answer_supported']); self.assertFalse(answer['claims'])

    def test_exact_route_is_unchanged(self):
        index = PassageIndex(self.ledger, 'What is Owner for record DOC-101?')
        self.assertTrue(index.exact_status)
        base = index.retrieve([index.question], 12, 8000)
        pack, trace = locate(index, self.graph, self.bindings, base, 12, 8000)
        self.assertEqual(pack, base); self.assertEqual(trace['status'], 'exact_route_preserved')

    def test_actual_strict_reader_checks_original_and_adapter_restores(self):
        from mplpb_answers import prose_retrieval
        original = prose_retrieval.retrieve; traces = []
        before = answer_query(self.ledger, self.question).contract
        with adapter(self.graph, self.bindings, traces):
            after = answer_query(self.ledger, self.question).contract
        self.assertIs(prose_retrieval.retrieve, original)
        self.assertEqual(before['kind'], after['kind'])
        self.assertEqual(before['claims'], after['claims'])
        self.assertTrue(traces)
        for claim in after['claims']:
            for c in claim['citations']:
                self.assertEqual(c['hash'], self.record.hash_actual)


if __name__ == '__main__': unittest.main()
