"""Native regressions: full question obligations and source scope survive aliases."""
import tempfile,unittest
from pathlib import Path
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_answers.pipeline import answer_query
from mplpb_answers.support import supported_answer

class OrdinaryQuestionTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def source(self,body,ident='PAGE-1',**kw):
        return write(self.root,doc_id=ident,title='Source',scope='documentary evidence',origin='machine',external='yes',body_html=body,**kw)
    def answer(self,q):return answer_query(self.root,q,PROFILES['internal']).contract
    def test_owner_syntax_preserves_the_entity(self):
        self.source('<p>Cloud Finch Workshop is owned by Lira Snow.</p>')
        a=self.answer('Who does Cloud Finch Workshop belong to?');self.assertTrue(a['answer_supported']);self.assertEqual(a['claims'][0]['citations'][0]['quote'],'Cloud Finch Workshop is owned by Lira Snow.')
        self.assertFalse(self.answer('Who does Other Workshop belong to?')['answer_supported'])
    def test_description_confirmation_keeps_requested_value(self):
        self.source('<p>Elm Reach is a public garden.</p>')
        self.assertTrue(self.answer('Is Elm Reach a public garden?')['answer_supported'])
        self.assertFalse(self.answer('Is Elm Reach a railway station?')['answer_supported'])
    def test_standalone_only_if_is_not_erased(self):
        self.source('<p>Only if the permit is approved.</p><p>Lira Snow owns Cloud Finch Workshop.</p>')
        a=self.answer('Who does Cloud Finch Workshop belong to?');self.assertFalse(a['answer_supported']);self.assertEqual(a['claims'],[])
    def test_quotation_is_not_an_unqualified_owner(self):
        self.source('<blockquote><p>Lira Snow owns Cloud Finch Workshop.</p></blockquote>')
        self.assertFalse(self.answer('Who owns Cloud Finch Workshop?')['answer_supported'])
    def test_policy_sees_the_entire_original_question(self):
        self.source('<p>Lira Snow owns Cloud Finch Workshop.</p>',not_for='belong')
        q='Who does Cloud Finch Workshop belong to?'
        self.assertNotEqual(supported_answer(self.root,q,PROFILES['internal']).kind,'return')
        self.assertEqual(self.answer(q)['claims'],[])
    def test_instruction_keeps_recipient_and_execution_separate(self):
        self.source('<p>Lira Snow instructed the field team to inspect the eastern bridge.</p>')
        self.assertTrue(self.answer('What did Lira Snow instruct the field team to do concerning the eastern bridge?')['answer_supported'])
        self.assertFalse(self.answer('What did Lira Snow instruct the inland team to do concerning the eastern bridge?')['answer_supported'])
        self.assertFalse(self.answer('Did the field team inspect the eastern bridge?')['answer_supported'])
    def test_reporting_denial_is_not_a_falsity_claim(self):
        self.source('<p>Lira Snow did not say that Arlo Penn wrote the ridge register.</p>')
        a=self.answer('What did Lira Snow not say about Arlo Penn writing the ridge register?');self.assertTrue(a['answer_supported']);p=a['claims'][0]['proposition'];self.assertTrue(p['outer_negative']);self.assertIsNone(p['inner_negative']);self.assertFalse(p['actual_authorship_established'])
        self.assertFalse(self.answer('Did Lira Snow say something false about Arlo Penn writing the ridge register?')['answer_supported'])
    def test_opening_time_requires_named_body_fields_and_keeps_conflicts(self):
        self.source('<p>Name: Elm Reach Office</p><p>Opening time: 08:45</p>')
        a=self.answer('When does Elm Reach Office open?');self.assertTrue(a['answer_supported']);self.assertEqual(len(a['claims'][0]['citations']),2)
        self.source('<p>Name: Elm Reach Office</p><p>Opening time: 09:10</p>',ident='PAGE-2')
        a=self.answer('When does Elm Reach Office open?');self.assertFalse(a['answer_supported']);self.assertEqual(a['kind'],'conflict')
    def test_extra_obligations_and_time_scope_do_not_disappear(self):
        self.source('<p>Lira Snow owns Cloud Finch Workshop.</p>')
        for q in ['Who does Cloud Finch Workshop belong to and who operates it?','Who does Cloud Finch Workshop belong to before June 8?']:
            with self.subTest(q=q):self.assertFalse(self.answer(q)['answer_supported'])
if __name__=='__main__':unittest.main()
