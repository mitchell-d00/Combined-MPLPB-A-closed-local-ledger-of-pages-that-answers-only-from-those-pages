import copy
import tempfile
import unittest
from pathlib import Path
from tools import proposition_chat as P
from tools.ledger_ui import App

class PropositionChatTests(unittest.TestCase):
    def test_frames_preserve_polarity_and_resolve_subject(self):
        a=P.parse('Dogs are cute',{})
        self.assertEqual((a['subject'],a['predicate'],a['act']),('dogs','cute','opinion'))
        self.assertTrue(P.parse("Dogs aren't cute",{})['negated'])
        self.assertTrue(P.parse('Are dogs cute?',{})['question'])
        self.assertEqual(P.parse('They are adorable',{'proposition':a})['subject'],'dogs')
        self.assertIsNone(P.parse('They are adorable',{}))
        self.assertEqual(P.parse('Dogs are reptiles',{})['act'],'description')
        self.assertIsNone(P.parse('Are dogs reptiles?',{}))
        for q in ['say exactly dogs are cute','I am sad','I hate myself','search dogs are cute','Dogs and cats are cute']:
            self.assertIsNone(P.parse(q,{}),q)

    def test_realization_is_deterministic_and_preserves_preferences(self):
        for q in ['Dogs are cute','Dogs are not cute','Are dogs cute?','I love music','I do not like spiders','Dogs are reptiles']:
            frame=P.parse(q,{})
            self.assertEqual(P.realize(frame,1),P.realize(copy.deepcopy(frame),1))
            self.assertNotIn('?',P.realize(frame,1,listening=True))
        self.assertIn('not keen',P.realize(P.parse('I do not like spiders',{}),1))
        self.assertNotIn('not keen',P.realize(P.parse('I do not dislike spiders',{}),1))

    def test_topic_context_and_sources_in_both_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            corpus=app.create_collection({'name':'Conversation test'})['corpus']
            app.import_source({'corpus':corpus,'title':'Otters','url':'https://example.org/otters','text':'Otters are mammals. This fixture does not establish cuteness.'})
            for mode in ['chat mode','load MPLPB']:
                first=app.chat({'corpus':corpus,'message':mode})
                sid=first['session'];env=copy.deepcopy(app.sessions[sid]['environment'])
                for q in ['Otters are cute','They are adorable','Otters are not cute','Otters are reptiles']:
                    r=app.chat({'corpus':corpus,'session':sid,'message':q})['response']
                    frame=r['response_structure']['construction']['frame']
                    self.assertEqual(frame['subject'],'otters')
                    self.assertFalse(frame['user_claim_verified'])
                    self.assertIn('Otters are mammals.',r['message'])
                    self.assertTrue(r['sources']);self.assertEqual(r['environment'],env)
                    self.assertNotIn('You said:',r['message'])
                    self.assertIsNone(r['language_plan']['acquisition']['query'])
                checked=app.chat({'corpus':corpus,'session':sid,'message':'What are otters?'})['response']
                self.assertTrue(checked['sources'])
                self.assertIn('Otters are mammals.',checked['message'])
                self.assertNotEqual(checked.get('support_label'),'User-provided context')
                self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_no_source_does_not_invent_agreement_or_popularity(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            first=app.chat({'corpus':'logic','message':'just chat'})
            r=app.chat({'corpus':'logic','session':first['session'],'message':'Zorblax are cute'})['response']
            self.assertEqual(r['sources'],[])
            self.assertNotIn('many people',r['message'])
            self.assertFalse(r['response_structure']['factual_claims'])
            self.assertIn('zorblax',r['message'].casefold())

    def test_novel_user_topic_and_description_survive_followups(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            first=app.chat({'corpus':'logic','message':'chat mode'})
            sid=first['session']
            a=app.chat({'corpus':'logic','session':sid,'message':'A flarn is my imaginary pet'})['response']
            self.assertEqual(a['response_structure']['construction']['frame']['subject'],'flarn')
            b=app.chat({'corpus':'logic','session':sid,'message':'It is glimmery'})['response']
            self.assertEqual(b['response_structure']['construction']['frame']['subject'],'flarn')
            app=App(topic_base=Path(tmp)/'topics')
            c=app.chat({'corpus':'logic','session':sid,'message':'What is a flarn?'})['response']
            self.assertEqual(c['support_label'],'User-provided context')
            self.assertIn('my imaginary pet',c['message']);self.assertIn('glimmery',c['message'])
            self.assertEqual(c['sources'],[])
            self.assertTrue(app.resume_chat({'session':sid})['chain_intact'])

    def test_dictionary_context_is_not_opinion_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=App(topic_base=Path(tmp)/'topics')
            first=app.chat({'corpus':'logic','message':'load MPLPB'})
            sid=first['session']
            app.chat({'corpus':'logic','session':sid,'message':'topic Dungeons and Dragons'})
            r=app.chat({'corpus':'logic','session':sid,'message':'Serendipity is delightful'})['response']
            self.assertTrue(all('corpus' not in source for source in r['sources']))
            self.assertEqual(r['authority'],'lexical_reference')
            self.assertEqual(r['support_label'],'Conversation + dictionary context')
            self.assertTrue(r['sources'])
            self.assertFalse(r['response_structure']['mplpb_supported'])
            self.assertFalse(r['response_structure']['construction']['frame']['user_claim_verified'])
