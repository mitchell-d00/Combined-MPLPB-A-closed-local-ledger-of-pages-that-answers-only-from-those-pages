"""Authored development minimal pairs, not independent human validation."""
import tempfile
import unittest
from mplpb_combined.ledger import write, revise
from mplpb_answers.support import supported_answer
from mplpb_answers.pipeline import answer_query as query


class PolarityTests(unittest.TestCase):
    def check_case(self, q, positive, negative):
        for separate in (False, True):
            with self.subTest(q=q, separate=separate), tempfile.TemporaryDirectory() as root:
                write(root, doc_id='NEW-001', title='Unknown collection', scope='notes',
                      body=positive if separate else positive+' '+negative)
                if separate:
                    write(root, doc_id='NEW-002', title='Other', scope='notes', body=negative)
                result = supported_answer(root, q)
                self.assertEqual(result.kind, 'ambiguous', result.text)
                self.assertFalse(result.text)
                checks = result.support['candidate_checks']
                self.assertTrue(any(c.get('negative_spans') for c in checks))
                self.assertEqual(query(root, q).contract['kind'], 'conflict')

    def test_predicate_negation_across_relations_and_domains(self):
        for q, pos, neg in (
            ('Where should we store museum accession cards?',
             'Store museum accession cards in blue archive drawer.',
             'Do not store museum accession cards in blue archive drawer.'),
            ('What is bag code XT7 for?', 'Bag code XT7 is for sculpture.',
             'Bag code XT7 is not for sculpture.'),
            ('Where is zephyron located?', 'Zephyron is located in amber vault.',
             'Zephyron is not located in amber vault.'),
            ('What does nimbus contain?', 'Nimbus contains violet lenses.',
             'Nimbus does not contain violet lenses.'),
            ('When is quillon due?', 'Quillon is due on 2028-04-02.',
             'Quillon is not due on 2028-04-02.'),
            ('Who owns observatory?', 'Mira owns observatory.',
             'Mira does not own observatory.'),
        ):
            self.check_case(q,pos,neg)

    def test_paraphrases_changed_values_and_citations(self):
        for entity, value in (('quillon foils','amber cabinet'), ('lunar bearings','violet locker')):
            for q in (f'Where should we keep {entity}?',f'Where should {entity} be kept?'):
                body=f'{entity.capitalize()} must be stored in {value}.'
                with tempfile.TemporaryDirectory() as root:
                    write(root,doc_id='NEW-001',title='Notes',scope='notes',body=body)
                    a=supported_answer(root,q)
                    self.assertEqual(a.text,body)
                    result=query(root,q).contract
                    citation=result['claims'][0]['citations'][0]
                    self.assertEqual(citation['quote'],body)
                    self.assertEqual(citation['source_id'],'NEW-001')
                    revise(root,'NEW-001',body=body.replace(value,'silver vault'))
                    self.assertIn('silver vault',supported_answer(root,q).text)
                    self.assertNotIn(value,supported_answer(root,q).text)

    def test_unrelated_negative_does_not_invalidate(self):
        for neg in ('Do not store other foils in amber cabinet.',
                    'Do not store quillon foils in violet cabinet.'):
            with tempfile.TemporaryDirectory() as root:
                body='Store quillon foils in amber cabinet.'
                write(root,doc_id='NEW-001',title='Notes',scope='notes',body=body+' '+neg)
                self.assertEqual(supported_answer(root,'Where should we store quillon foils?').text,body)
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='NEW-001',title='Notes',scope='notes',
                  body='Mira owns observatory. Sol does not own observatory.')
            self.assertEqual(supported_answer(root,'Who owns observatory?').kind,'return')

    def test_missing_context_headings_qualifiers_and_near_misses(self):
        for body in ('<h1>Store quillon foils in amber cabinet.</h1>Unknown.',
                     'If wet, store quillon foils in amber cabinet.',
                     'Store quillon foils in amber cabinet until Friday.',
                     'It must be stored in amber cabinet.',
                     'Quillon foils might be stored in amber cabinet.',
                     'Do not store quillon foils in amber cabinet.'):
            with tempfile.TemporaryDirectory() as root:
                write(root,doc_id='NEW-001',title='Notes',scope='quillon foils',body=body)
                self.assertNotEqual(supported_answer(root,'Where should we store quillon foils?').kind,'return')
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='NEW-001',title='Notes',scope='notes',body='Store quillon foils in amber cabinet.')
            self.assertNotEqual(supported_answer(root,'Where are quillon foils manufactured?').kind,'return')

    def test_scoped_denial_requests_context_instead_of_ignoring_it(self):
        for scope in ('If wet', 'When sealed', 'Unless dry'):
            with tempfile.TemporaryDirectory() as root:
                write(root,doc_id='NEW-001',title='Notes',scope='notes',
                      body='Store quillon foils in amber cabinet. '
                      +scope+', do not store quillon foils in amber cabinet.')
                result=supported_answer(root,'Where should we store quillon foils?')
                self.assertNotEqual(result.kind,'return')
                self.assertTrue(result.support['unresolved'])

    def test_cli_and_native_application_keep_conflict(self):
        import json
        import subprocess
        import sys
        from pathlib import Path
        from tools.ledger_ui import App
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='NEW-001',title='Notes',scope='notes',body=
                  'Store quillon foils in amber cabinet. Do not store quillon foils in amber cabinet.')
            q='Where should we store quillon foils?'
            cli=subprocess.run([sys.executable,'-m','mplpb_answers','ask',root,q,'--json'],
                               capture_output=True,text=True)
            self.assertEqual(cli.returncode,2,cli.stderr)
            self.assertEqual(json.loads(cli.stdout)['kind'],'ambiguous')
            app=App(topic_base=Path(root)/'topics')
            # Register an explicit local test collection through the same corpus
            # mapping consumed by App.query; no production collection changes.
            app.corpora['polarity'] = ('Polarity collection', Path(root))
            result=app.query({'corpus':'polarity','question':q})
            self.assertEqual(result['reader']['kind'],'ambiguous')
            self.assertFalse(result['reader']['answer_supported'])

    def test_withdrawn_denial_no_longer_competes(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='NEW-001',title='Notes',scope='notes',body='Store quillon foils in amber cabinet.')
            write(root,doc_id='NEW-002',title='Other',scope='notes',body='Do not store quillon foils in amber cabinet.')
            q='Where should we store quillon foils?'
            self.assertEqual(supported_answer(root,q).kind,'ambiguous')
            revise(root,'NEW-002',body='No storage decision is recorded.')
            self.assertEqual(supported_answer(root,q).kind,'return')
