import copy
from pathlib import Path
import tempfile
import unittest
from tools.chat_phrasing import request_form
from tools import conversation_continuity as CC
from tools.chat_guidance import guidance
from tools.ledger_ui import App


class NaturalGuidanceTests(unittest.TestCase):
    def test_topic_paraphrases_keep_subject_bytes(self):
        forms=['give me an overview of {}','give me a quick overview of {}',
               'tell me a little about {}','help me understand {}',
               "I'd like to learn about {}",'can we talk about {}',
               'what do you know about {}','switch to {}','how about {}']
        for subject in ['Moon','Japan','Apple Inc.','cool stars',"O’Keeffe"]:
            for form in forms:
                text=form.format(subject)
                with self.subTest(text=text):
                    self.assertEqual(request_form(text)[0],'Tell me about '+subject)

    def test_leadins_and_politeness_compose(self):
        for prefix in ['Cool, ','Great ','Hey, ','Thanks! ','Got it; ']:
            for text in ['could you please give me an overview of Moon','can we talk about Moon','give me a quick overview of Moon']:
                raw=prefix+text
                frame=CC.prepare(raw,{'mind':{},'log':[],'context':None})
                self.assertEqual(frame['resolved'],'Tell me about Moon',raw)
                self.assertEqual(frame['original'],raw)

    def test_no_rewrite_of_negated_literal_or_unrecognized_requests(self):
        for text in ["don't tell me about Moon",'could you not search for Moon',
                     'say give me an overview of Moon','repeat "look up Moon"',
                     'cool stars are bright','what if Moon vanished?',
                     'help me understand you','what about its mass?',
                     'switch to chat mode','switch to serious mode',
                     'I want to learn about fossils','Can you summarize this?',
                     'how about you?','can we talk about nothing?',
                     "let's talk about it",'walk me through it',
                     'help me understand why the sky is blue',
                     'search for Moon without using the internet']:
            value,_=request_form(text)
            if text.startswith('search for'):
                self.assertIn('without using the internet',value)
            else:self.assertEqual(value,text)

    def test_lookup_and_source_paraphrases(self):
        for text,expected in [('look up Moon','search Moon'),
                              ('another word for happy','synonyms happy'),
                              ('what is the meaning of orbit','define orbit'),
                              ('where did you get that?','show source'),
                              ('keep going','tell me more')]:
            self.assertEqual(request_form(text)[0],expected)

    def test_guidance_changes_with_available_evidence(self):
        result={'kind':'federated_answers','sources':[{'id':'x'}],
                'response_structure':{'subject':'Moon','intent':'source_exploration'},
                'has_more_source_text':True,'suggestions':['How big is Moon?']}
        original=copy.deepcopy(result)
        first=guidance(result)
        self.assertIn('Read more',[a['label'] for a in first['actions']])
        self.assertEqual(result,original)
        result.update(source_exhausted=True,has_more_source_text=False)
        next_=guidance(result)
        self.assertNotIn('Read more',[a['label'] for a in next_['actions']])
        self.assertIn('Find more sources',[a['label'] for a in next_['actions']])
        self.assertNotEqual(first,next_)

    def test_reference_and_clarification_actions(self):
        reference=guidance({'reference_topic':'dictionary','headword':'run','suggestions':['next senses']})
        self.assertIn('next senses',[a['request'] for a in reference['actions']])
        self.assertIn('synonyms run',[a['request'] for a in reference['actions']])
        choice=guidance({'kind':'ambiguous','suggestions':['topic Apple','topic Apple Inc.']})
        self.assertEqual([a['request'] for a in choice['actions'][:2]],['topic Apple','topic Apple Inc.'])
        self.assertTrue(any(a['mode']=='draft' and a['request']=='' for a in choice['actions']))

    def test_dictionary_does_not_capture_system_question_and_guidance_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            args={'topic_base':Path(tmp)/'topics'};app=App(**args)
            sid=app.chat({'corpus':'logic','message':'topic dictionary'})['session']
            result=app.chat({'corpus':'logic','session':sid,'message':'what does MPLPB mean?'})['response']
            self.assertEqual(result['support_label'],'System description')
            self.assertEqual(result['sources'],[])
            app=App(**args)
            resumed=app.resume_chat({'session':sid})
            self.assertTrue(resumed['chain_intact'])
            self.assertEqual(resumed['turns'][-1]['payload']['response']['guidance'],result['guidance'])

    def test_paraphrased_reference_uses_normal_planner(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            r=app.chat({'corpus':'logic','message':'Great, could you please give me the definition of orbit'})['response']
            self.assertEqual(r['authority'],'lexical_reference')
            self.assertEqual(r['headword'],'orbit')
            self.assertTrue(r['reply_plan']['subplans'])
            self.assertFalse(r['language_plan']['acquisition']['query'])
