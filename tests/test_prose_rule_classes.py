"""General prose classes: independent wording, mutations and no benchmark imports."""
import html
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query


class ProseRuleClassTests(unittest.TestCase):
    def result(self, sources, question, **options):
        with tempfile.TemporaryDirectory() as tmp:
            for n, source in enumerate(sources):
                write(Path(tmp), doc_id='RECORD-'+str(n), title='Archive', scope='archive',
                      body_html='<pre>'+html.escape(source)+'</pre>')
            return answer_query(Path(tmp), question, **options).contract

    def test_polite_source_question_and_safety_directive_keep_original(self):
        question='Please evaluate this using the supplied documents: Who surveyed the lower basin? Leave unverified claims unverified.'
        result=self.result(['Robin Vega surveyed the lower basin.'],question)
        self.assertTrue(result['answer_supported']);self.assertEqual(result['question'],question)

    def test_source_header_and_salutation_are_boundaries_not_actor_evidence(self):
        for prefix in ['ALMA VALE TO ROBIN VEGA. March 4, 1873\nDear colleague,\n',
                       'From: Alma Vale\nTo: Robin Vega\nDate written: March 4, 1873\nSubject: Mapping\nMessage-ID: M-8\n']:
            with self.subTest(prefix=prefix):
                result=self.result([prefix+'Celeste Frost surveyed the lower basin.'],'Who surveyed the lower basin?')
                self.assertTrue(result['answer_supported'])
                self.assertEqual(result['claims'][0]['proposition']['actor_text'],'Celeste Frost')

    def test_passive_written_with_unicode_actor_is_checked(self):
        result=self.result(['The glacial map was written by Élise Dupré.'],'Which writer does the record identify for the glacial map?')
        self.assertTrue(result['answer_supported'])
        self.assertEqual(result['claims'][0]['proposition']['actor_text'],'Élise Dupré')

    def test_named_attribution_cannot_be_erased(self):
        result=self.result(['Robin Vega surveyed the lower basin.'],'According to Celeste Frost, who surveyed the lower basin?')
        self.assertFalse(result['answer_supported'])

    def test_extra_question_or_condition_not_removed_as_politeness(self):
        for question in ['Who surveyed the lower basin, and did this cause the evacuation?',
                         'If the permit was approved, who surveyed the lower basin?',
                         'Who surveyed the lower basin? Leave the evacuation explained.']:
            with self.subTest(question=question):
                self.assertFalse(self.result(['Robin Vega surveyed the lower basin.'],question)['answer_supported'])

    def test_header_only_and_qualified_statements_do_not_supply_completed_action(self):
        for body in ['From: Robin Vega\nSubject: surveyed the lower basin\nNo action is recorded.',
                     'If approved, Robin Vega surveyed the lower basin.',
                     'Robin Vega planned to survey the lower basin.',
                     'Celeste Frost said, "Robin Vega surveyed the lower basin."',
                     'From: Celeste Frost\nTo: Alma Vale\nRobin Vega did not survey the lower basin.']:
            with self.subTest(body=body):
                self.assertFalse(self.result([body],'Who surveyed the lower basin?')['answer_supported'])

    def test_explicit_cause_completes_only_source_scoped_question(self):
        result=self.result(['The dock inspection was postponed because of damage to the stairway.'],
                           'According to the report, why was the dock inspection postponed?')
        self.assertTrue(result['answer_supported'])
        self.assertFalse(result['claims'][0]['historical_truth_independently_verified'])

    def test_causal_alternatives_and_negation_prevent_completion(self):
        question='According to the report, why was the dock inspection postponed?'
        for sources in [
            ['The dock inspection was not postponed because of damage to the stairway.'],
            ['The dock inspection was postponed because of damage to the stairway.',
             'The dock inspection was postponed because of ice.'],
            ['If approved, the dock inspection was postponed because of damage to the stairway.'],
            ['The dock inspection occurred after damage to the stairway.']]:
            with self.subTest(sources=sources):
                self.assertFalse(self.result(sources,question)['answer_supported'])

    def test_passive_conflict_and_source_budget_remain_gated(self):
        sources=['Robin Vega wrote the glacial map.','The glacial map was written by Celeste Frost.']
        self.assertFalse(self.result(sources,'Who wrote the glacial map?')['answer_supported'])
        self.assertFalse(self.result(['The glacial map was written by Robin Vega.',
                                      'The eastern survey was written by Celeste Frost.'],
                                     'Who wrote the glacial map, and who wrote the eastern survey?',
                                     max_passages=1,max_chars=1000)['answer_supported'])

    def test_qualified_passive_actor_and_pronouns_remain_unresolved(self):
        for actor in ['Perhaps Robin Vega','Possibly Robin Vega','He','I','You']:
            with self.subTest(actor=actor):
                self.assertFalse(self.result(['The glacial map was written by '+actor+'.'],
                                             'Who wrote the glacial map?')['answer_supported'])

    def test_cause_with_unresolved_pronoun_counterstatement_is_partial(self):
        self.assertFalse(self.result(['The dock inspection was postponed because of ice.',
                                      'It was not postponed.'],
                                     'Why was the dock inspection postponed?')['answer_supported'])

    def test_generic_passive_object_does_not_resolve_a_reference(self):
        self.assertFalse(self.result(['The report was written by Robin Vega.'],
                                     'Who wrote the report?')['answer_supported'])

    def test_original_delivery_exclusion_survives_question_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp),doc_id='RECORD-1',title='Archive',scope='archive',
                  body_html='<p>Robin Vega surveyed the lower basin.</p>',not_for='unverified')
            result=answer_query(Path(tmp),'Who surveyed the lower basin? Leave unverified claims unverified.').contract
            self.assertFalse(result['answer_supported']);self.assertFalse(result['claims'])
