"""Shared entity, polarity, task-binding and counterevidence regressions."""
import tempfile
import unittest
from pathlib import Path
from mplpb_combined.ledger import write, withdraw
from mplpb_combined.reader import PROFILES
from mplpb_answers.pipeline import answer_query


class RoundTwoTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def source(self,body,ident='ONE',**kw):
        return write(self.root,doc_id=ident,title='Evidence',scope='documentary evidence',
                     origin='machine',external='yes',body_html=body,**kw)

    def answer(self,q):
        return answer_query(self.root,q,PROFILES['internal']).contract

    def test_singular_conjunction_name_with_exact_negative_witness(self):
        self.source('<p>Rain and Reed is not a public library.</p>')
        a=self.answer('Is Rain and Reed a public library?')
        self.assertTrue(a['answer_supported'])
        self.assertTrue(a['text'].startswith('No.'))
        self.assertEqual(a['claims'][0]['proposition']['polarity'],'negative')
        self.assertEqual(a['claims'][0]['citations'][0]['quote'],'Rain and Reed is not a public library.')

    def test_positive_output_is_separate_from_exact_source_quote(self):
        self.source('<p>Rain and Reed is a public library.</p>')
        a=self.answer('Is Rain and Reed a public library?')
        self.assertTrue(a['text'].startswith('Yes.'))
        self.assertEqual(a['claims'][0]['proposition']['polarity'],'positive')
        self.assertEqual(a['claims'][0]['citations'][0]['quote'],'Rain and Reed is a public library.')

    def test_coordinated_entities_and_predicates_are_not_silently_combined(self):
        self.source('<p>Rain is a library.</p><p>Reed is a library.</p>')
        for q in ['Is Rain and Reed a library?','Is Rain a library and who owns it?',
                  'Is Rain a library and a shop?']:
            self.assertFalse(self.answer(q)['answer_supported'],q)

    def test_plural_coordination_does_not_bind_a_singular_named_entity(self):
        self.source('<p>Rain and Reed are a public library.</p>')
        self.assertFalse(self.answer('Is Rain and Reed a public library?')['answer_supported'])

    def test_wrong_category_is_not_an_explicit_no(self):
        self.source('<p>Willow Hall is a public library.</p>')
        self.assertFalse(self.answer('Is Willow Hall a railway station?')['answer_supported'])

    def test_positive_negative_conflict_and_agreeing_owner_ambiguity(self):
        self.source('<p>Willow Hall is a public library.</p>')
        self.source('<p>Willow Hall is not a public library.</p>',ident='TWO')
        a=self.answer('Is Willow Hall a public library?')
        self.assertEqual(a['kind'],'conflict')
        self.assertFalse(a['answer_supported'])
        self.assertFalse(a['text'].startswith(('Yes.','No.')))

    def test_agreeing_sources_remain_ownership_ambiguous(self):
        for ident in ('ONE','TWO'):
            self.source('<p>Willow Hall is a public library.</p>',ident=ident)
        self.assertEqual(self.answer('Is Willow Hall a public library?')['kind'],'conflict')

    def test_quoted_negation_and_condition_are_not_outer_denials(self):
        self.source('<blockquote><p>Willow Hall is not a public library.</p></blockquote>')
        self.assertFalse(self.answer('Is Willow Hall a public library?')['answer_supported'])

    def test_retired_negative_does_not_support_no(self):
        self.source('<p>Willow Hall is not a public library.</p>')
        withdraw(self.root,'ONE')
        self.assertFalse(self.answer('Is Willow Hall a public library?')['answer_supported'])

    def test_narrative_prefix_cannot_hide_competing_opening_fields(self):
        self.source('<p>Inventory was updated.</p><p>Name: Willow Office</p><p>Opening time: 08:10</p>')
        self.source('<p>Name: Willow Office</p><p>Opening time: 12:30</p>',ident='TWO')
        self.assertEqual(self.answer('When does Willow Office open?')['kind'],'conflict')

    def test_other_time_role_does_not_create_opening_conflict(self):
        self.source('<p>Inventory was updated.</p><p>Name: Willow Office</p><p>Opening time: 08:10</p>')
        self.source('<p>Name: Willow Office</p><p>Publication time: 12:30</p>',ident='TWO')
        a=self.answer('At which time does Willow Office open?')
        self.assertTrue(a['answer_supported'])
        self.assertNotIn('12:30',a['text'])

    def test_reported_field_caption_is_not_outer_source_evidence(self):
        self.source('<p>The minutes clerk stated the following:</p><p>Name: Willow Office</p><p>Opening time: 12:30</p>')
        self.assertFalse(self.answer('When does Willow Office open?')['answer_supported'])
        self.source('<p>Name: Willow Office</p><p>Opening time: 08:10</p>',ident='TWO')
        self.assertTrue(self.answer('When does Willow Office open?')['answer_supported'])

    def test_quoted_reporting_caption_does_not_govern_outer_fields(self):
        self.source('<blockquote><p>The minutes clerk stated the following:</p></blockquote><p>Name: Willow Office</p><p>Opening time: 08:10</p>')
        self.assertTrue(self.answer('When does Willow Office open?')['answer_supported'])

    def test_long_reporting_caption_cannot_lose_its_source_voice(self):
        self.source('<p>The clerk reported '+('the archived inventory '*120)+':</p><p>Name: Willow Office</p><p>Opening time: 12:30</p>')
        self.assertFalse(self.answer('When does Willow Office open?')['answer_supported'])

    def test_unresolved_relevant_record_cannot_disappear_beside_clean_answer(self):
        self.source('<p>Name: Willow Office</p><p>Opening time: 08:10</p><p>Name: Hazel Office</p><p>Opening time: 09:10</p>')
        self.source('<p>Name: Willow Office</p><p>Opening time: 12:30</p>',ident='TWO')
        self.assertFalse(self.answer('When does Willow Office open?')['answer_supported'])

    def test_irrelevant_unresolved_record_does_not_block_named_answer(self):
        self.source('<p>Name: Birch Office</p><p>Opening time: 08:10</p><p>Name: Hazel Office</p><p>Opening time: 09:10</p>')
        self.source('<p>Name: Willow Office</p><p>Opening time: 12:30</p>',ident='TWO')
        self.assertTrue(self.answer('When does Willow Office open?')['answer_supported'])

    def test_different_condition_is_not_an_unqualified_time_conflict(self):
        self.source('<p>Name: Willow Office</p><p>Opening time: 08:10</p>')
        self.source('<p>Only if the permit is approved.</p><p>Name: Willow Office</p><p>Opening time: 12:30</p>',ident='TWO')
        self.assertTrue(self.answer('When does Willow Office open?')['answer_supported'])

    def test_relational_location_witnesses_keep_conflict_and_support(self):
        self.source('<p>The cenotaph is located in Birch Square.</p>')
        question = 'Where is the cenotaph located?'
        answer = self.answer(question)
        self.assertTrue(answer['answer_supported'])
        self.assertIn('Birch Square', answer['text'])
        self.source('<p>The cenotaph is located in Ash Square.</p>', ident='TWO')
        self.assertEqual(self.answer(question)['kind'], 'conflict')

    def test_object_free_task_requires_unique_actor_recipient_binding(self):
        self.source('<p>Yara Moss instructed the field team to inspect the western bridge.</p>')
        q='Which task did Yara Moss give the field team?'
        a=self.answer(q)
        self.assertTrue(a['answer_supported'])
        p=a['claims'][0]['proposition']
        self.assertFalse(p['completion_asserted_by_source'])
        self.assertEqual(p['task_object'],'the western bridge')
        self.assertFalse(self.answer('Which task did Yara Moss give the coastal crew?')['answer_supported'])
        self.source('<p>Yara Moss instructed the field team to review the southern archive.</p>',ident='TWO')
        self.assertFalse(self.answer(q)['answer_supported'])

    def test_medial_attribution_retains_original_policy_question(self):
        self.source('<p>Yara Moss owns Willow Workshop.</p>',not_for='according')
        a=self.answer('Who, according to the source, owns Willow Workshop?')
        self.assertFalse(a['answer_supported'])


if __name__=='__main__':
    unittest.main()
