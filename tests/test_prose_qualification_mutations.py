"""Unparsed passive/attribution alternatives must block complete acceptance."""
import html
from pathlib import Path
import tempfile
import unittest
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write


class QualificationMutationTests(unittest.TestCase):
    def test_retrieved_sentence_keeps_absolute_source_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=('The archive cupboard contained an unrelated inventory leaf beside its wool cover.\n\n'*180
                    +'Quentin Moss surveyed the basalt basin.')
            write(root,doc_id='ARCHIVE-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(source)+'</pre>')
            result=answer_query(root,'Who surveyed the basalt basin?').contract
            self.assertTrue(result['answer_supported'])
            self.assertGreater(result['claims'][0]['citations'][0]['body_start'],1000)

    def test_irregular_passive_denials_and_hedges_are_not_lost(self):
        for active,base,participle in [('wrote','write','written'),('sent','send','sent')]:
            for alternative in [f'The basalt chart was not {participle} by Quentin Moss.',
                                f'The basalt chart was reportedly {participle} by Quentin Moss.',
                                f'It was not {participle} by Quentin Moss.']:
                with self.subTest(active=active,alternative=alternative):
                    with tempfile.TemporaryDirectory() as tmp:
                        root=Path(tmp)
                        for n,body in enumerate([f'Quentin Moss {active} the basalt chart.',alternative]):
                            write(root,doc_id='ARCHIVE-'+str(n),title='Archive',scope='archive',
                                  body_html='<pre>'+html.escape(body)+'</pre>')
                        result=answer_query(root,f'Who {active} the basalt chart?').contract
                        self.assertFalse(result['answer_supported'])
                        self.assertTrue(result['missing'])

    def test_unresolved_self_refutation_stops_complete_action_answer(self):
        for denial in ['This statement is false.','That earlier account was mistaken.',
                       'It never happened.','I was wrong.']:
            with self.subTest(denial=denial),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);body='Quentin Moss wrote the basalt chart. '+denial
                write(root,doc_id='ARCHIVE-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
                result=answer_query(root,'Who wrote the basalt chart?').contract
                self.assertFalse(result['answer_supported'])
                self.assertTrue(result.get('documentary_support',{}).get('alternative_evidence'))

    def test_unresolved_refutation_also_stops_source_cause_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);body='The dock inspection was postponed because of ice. This account is false.'
            write(root,doc_id='ARCHIVE-1',title='Archive',scope='archive',body_html='<pre>'+html.escape(body)+'</pre>')
            result=answer_query(root,'Why was the dock inspection postponed?').contract
            self.assertFalse(result['answer_supported'])
            self.assertTrue(result.get('documentary_support',{}).get('alternative_evidence'))
