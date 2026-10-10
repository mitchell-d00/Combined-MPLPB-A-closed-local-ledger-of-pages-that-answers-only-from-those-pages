import json
import tempfile
import unittest
from pathlib import Path
from mplpb_combined.ledger import write
from tools.answer_support import supported_answer
from tools.evaluate_ownership import evaluate

class AnswerSupportTests(unittest.TestCase):
    def test_body_support_and_absence_of_scope_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp,doc_id='T-0001',title='What is the kettle color?',scope='kettle color',body='The kettle color is unknown.')
            r=supported_answer(tmp,'What is the kettle color?')
            self.assertEqual(r.kind,'not_in_corpus');self.assertEqual(r.text,'');self.assertEqual(r.citation(),'')
            self.assertTrue(r.candidates)

    def test_only_supported_span_is_returned(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp,doc_id='T-0001',title='kettle',scope='kettle color',body='The kettle color is blue. A stranger owns a car.')
            r=supported_answer(tmp,'What is the kettle color?')
            self.assertEqual(r.kind,'return');self.assertEqual(r.text,'The kettle color is blue.')
            self.assertEqual(r.to_dict()['answer_support']['status'],'supported')

    def test_expanded_frozen_suite_and_coverage(self):
        root=Path(__file__).resolve().parents[1]/'evaluation'/'ownership'
        r=evaluate(root/'expanded-input.jsonl')
        self.assertEqual(r,json.loads((root/'expanded-results.json').read_text()))
        m=r['summary']['arms']['supported_reader']
        self.assertEqual(m['n'],600);self.assertEqual(m['wrong_ownership'],0)
        self.assertEqual(m['wrong_refusal'],0)
        self.assertAlmostEqual(m['return_coverage'],150/600)

    def test_relation_paraphrases_preserve_entity_direction_and_support(self):
        from types import SimpleNamespace
        from tools.answer_support import statement_support
        cases = [
            ('When did the Zephyr workshop open?', 'The Zephyr workshop opened in 1997.', 'The Zephyr workshop closed in 1997.'),
            ('Who owns the Juniper press?', 'Amara owns the Juniper press.', 'The Juniper press owns Amara.'),
            ('How long is the violet cable?', 'The violet cable is 17 feet long.', 'The violet cable is 17 feet wide.'),
            ('Which colour was chosen for the amber room?', 'Green was chosen for the amber room.', 'Green was chosen for the other room.'),
            ('Why did the Nacre studio close?', 'The Nacre studio closed because its lease ended.', 'The Nacre studio closed at noon.'),
        ]
        for question, positive, wrong in cases:
            with self.subTest(question=question):
                def check(body):
                    return statement_support(question, SimpleNamespace(body_html='<p>'+body+'</p>'))
                self.assertEqual(check(positive)['status'], 'supported')
                for body in (wrong, 'If approved, '+positive, 'Say that '+positive,
                             '"'+positive+'"', positive.replace(' owns ', ' possibly owns ')):
                    if body != positive:
                        self.assertEqual(check(body)['status'], 'unsupported', body)
                self.assertEqual(check(positive+' '+positive.replace('1997','2001').replace('Amara','Zuri').replace('17','18').replace('Green','Blue').replace('lease ended','funding ended'))['status'], 'conflict')

    def test_imported_heading_does_not_merge_with_answer(self):
        from types import SimpleNamespace
        from tools.answer_support import statement_support
        record = SimpleNamespace(body_html='<h1>Dinosaurs</h1><h2>Dinosaurs</h2><p>Dinosaurs are a source fixture.</p>')
        self.assertEqual(statement_support('What is Dinosaurs?', record)['status'], 'supported')
        record.body_html='<h2>Dinosaurs are a source fixture.</h2><p>No definition recorded.</p>'
        self.assertEqual(statement_support('What is Dinosaurs?', record)['status'], 'unsupported')
