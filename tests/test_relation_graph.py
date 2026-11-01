"""Graph assertions, changed subjects, frozen examples, provenance and near misses."""
import tempfile
import unittest
from pathlib import Path

from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_answers.support import supported_answer
from mplpb_answers import relation_graph as G


class RelationGraphTests(unittest.TestCase):
    def ask(self, question, body, **kwargs):
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='GRAPH-001', title='Neutral reference',
                  scope='reference notes', body=body, **kwargs)
            return supported_answer(root, question)

    def test_changed_codes_quantities_and_durations(self):
        cases = (
            ('What is bag code XT7 for?',
             'Grogged basalt, bag code XT7, is for sculpture and large wall panels.'),
            ('What is code UV9 for?',
             'Bag code UV9 is for sample transfer labels.'),
            ('What causes crawling?',
             'Crawling comes from dust or grease on the bisque, or a coat put on too thick that cracked as it dried.'),
            ("Ram's head or spiral?",
             "Ram's head for small amounts, spiral for anything over two kilos."),
            ('How do I check the coat with a pin?',
             'The coat should be the thickness of a postcard: scratch through with a pin to check.'),
            ('Horizontal or vertical?',
             'Horizontal for narrow frames, vertical for wide frames.'),
            ('How do I check the seal with a gauge?',
             'The seal should be flush: measure across with a gauge to check.'),
            ('How long does thick sculpture need?',
             'Thick sculpture needs two weeks, not two days.'),
            ('How much Epsom salt solution?',
             'If the batch has hard-panned, add a teaspoon of Epsom salt solution and sieve again.'),
            ('How much archival sealant?',
             'Add two teaspoons of archival sealant before filing.'),
            ('How long should I slake powders before stirring?',
             'Leave powders to slake for twenty minutes before stirring.'),
            ('How long should I dry records before binding?',
             'Leave records to dry for two days before binding.'),
        )
        for q, body in cases:
            with self.subTest(q=q):
                result = self.ask(q, body)
                self.assertEqual(result.kind, 'return', result.reason)
                self.assertEqual(result.text, body)
                self.assertEqual(result.support['frame']['version'], G.VERSION)
                graph = result.support['graph']
                self.assertTrue(any(edge['type'] == 'declares' for edge in graph['edges']))
                self.assertTrue(any(edge['type'] == 'supplies_value' for edge in graph['edges']))
                self.assertFalse(graph['world_verified'])
                self.assertFalse(graph['multi_hop_inference'])
                self.assertEqual(next(n for n in graph['nodes'] if n['kind'] == 'statement')['quote'], body)

    def test_near_miss_denials_and_unsafe_suffixes_do_not_return(self):
        rows = (
            ('What is bag code XT7 for?', 'Bag code XT8 is for sculpture.'),
            ('What is bag code XT7 for?', 'Bag code XT7 is not for sculpture.'),
            ('What causes crawling?', 'Crazing comes from glaze-body mismatch.'),
            ('Horizontal or vertical?', 'Horizontal for wide frames, diagonal for narrow frames.'),
            ('How do I check the coat with a pin?', 'The coat should be thin: scratch through with a brush to check.'),
            ('How long does thick sculpture need?', 'Thin sculpture needs two weeks.'),
            ('How much Epsom salt solution?', 'Add three teaspoons of magnesium solution.'),
            ('How much Epsom salt solution?', 'Perhaps add a teaspoon of Epsom salt solution.'),
            ('How long should I slake powders before stirring?', 'Leave clay to slake for twenty minutes before stirring.'),
            ('How long should I slake powders before stirring?', 'Leave powders to soak for twenty minutes before stirring.'),
            ('How long should I dry records before binding?', 'Leave records to dry for two days before sealing.'),
            ('How much archival sealant?', '<h1>Add three teaspoons of archival sealant.</h1>Not recorded.'),
        )
        for q, body in rows:
            with self.subTest(q=q, body=body):
                self.assertNotEqual(self.ask(q, body).kind, 'return')
        for q in (
            'How much archival sealant if the label is damaged?',
            'What is code XT7 for tomorrow?',
            'How long should I dry records before binding if torn?',
            'How much archival sealant not required?',
        ):
            self.assertIsNone(G.parse(q), q)

    def test_competing_sources_ambiguity_without_top_one(self):
        q = 'What is bag code J7 for?'
        for competitor in ('Bag code J7 is for packing.',
                           'Bag code J7 is for storage.'):
            with tempfile.TemporaryDirectory() as root:
                write(root, doc_id='GRAPH-001', title='One',
                      scope='first page', body='Bag code J7 is for packing.')
                write(root, doc_id='GRAPH-002', title='Two',
                      scope='second page', body=competitor)
                result = supported_answer(root, q)
                self.assertEqual(result.kind, 'ambiguous')
                self.assertFalse(result.text)

    def test_provenance_seals_not_for_external(self):
        q = 'How much archival sealant?'
        body = 'Add two teaspoons of archival sealant before filing.'
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='GRAPH-001', title='Private',
                  scope='inventory', body=body, external='no')
            self.assertNotEqual(supported_answer(root, q, PROFILES['external']).kind, 'return')
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='GRAPH-001', title='Excluded',
                  scope='reference notes', body=body, not_for='sealant')
            self.assertNotEqual(supported_answer(root, q).kind, 'return')
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='GRAPH-001', title='Damaged',
                  scope='reference notes', body=body)
            path = next(Path(root).glob('*.html'))
            path.write_text(path.read_text().replace('two teaspoons', 'three teaspoons'))
            self.assertNotEqual(supported_answer(root, q).kind, 'return')

    def test_existing_studio_source_without_changing_frozen_files(self):
        root = Path(__file__).resolve().parents[1] / 'examples' / 'studio'
        examples = (
            ('What is bag code CR for?', 'STUDIO-0017',
             'Grogged crank, CR, is for sculpture and large slab work and tolerates uneven drying.'),
            ('How much Epsom salt solution?', 'STUDIO-0013',
             'If it has hard-panned, add a teaspoon of Epsom salt solution and sieve again.'),
            ('What causes crawling?', 'STUDIO-0012',
             'Crawling comes from dust or grease on the bisque, or a coat put on too thick that cracked as it dried.'),
            ('How long does thick sculpture need?', 'STUDIO-0016',
             'Thick sculpture needs two weeks, not two days.'),
            ("Ram's head or spiral?", 'STUDIO-0015',
             "Ram's head for small amounts, spiral for anything over two kilos."),
            ('How do I check the coat with a pin?', 'STUDIO-0010',
             'The coat should be the thickness of a postcard: scratch through with a pin to check.'),
        )
        for q, rec_id, sentence in examples:
            with self.subTest(q=q):
                answer = supported_answer(root, q)
                self.assertEqual(answer.kind, 'return', answer.reason)
                self.assertEqual(answer.record.id, rec_id)
                self.assertEqual(answer.text, sentence)

    def test_source_diagnostics_distinguish_graph_from_truth(self):
        q = 'How much archival sealant?'
        result = self.ask(q, 'Add three teaspoons of archival sealant before filing.')
        proof = result.support['graph']
        self.assertEqual(proof['proof_kind'], 'exact_source_statement')
        self.assertFalse(proof['independent_sources_verified'])
        self.assertFalse(proof['execution_verified'])
        self.assertEqual(proof['nodes'][3]['record_id'], 'GRAPH-001')

if __name__ == '__main__':
    unittest.main()
