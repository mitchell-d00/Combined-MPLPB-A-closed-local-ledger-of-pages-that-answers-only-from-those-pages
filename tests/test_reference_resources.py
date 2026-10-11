import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import reference_resources as F
from tools.ledger_ui import App

class ReferenceTests(unittest.TestCase):
    def test_downloads_have_complete_local_pins(self):
        m=F.verify()
        self.assertEqual(m['wordnet_counts']['synsets'],107558)
        self.assertEqual(len(list(F.encyclopedia_root().glob('*.html'))),23)

    def test_dictionary_senses_are_separate_and_do_not_select_topic(self):
        with tempfile.TemporaryDirectory() as p:
            app=App(topic_base=p)
            first=app.chat({'corpus':'logic','message':'topic Budget guide'})
            with patch.object(app,'build_search',side_effect=AssertionError('offline lookup')):
                result=app.chat({'corpus':'logic','session':first['session'],'message':'define dog'})['response']
            self.assertEqual(result['authority'],'lexical_reference')
            self.assertEqual(result['context'],first['response']['context'])
            self.assertGreater(len(result['senses']),1)
            self.assertIn('02086723-n',[s['id'] for s in result['senses']])
            self.assertEqual(result['sources'][0]['hash'],F.manifest()['resources'][0]['sha256'])
            self.assertEqual(app.collections.entries(),{})

    def test_missing_entry_and_manifest_tampering_stop(self):
        self.assertEqual(F.handle('define zzzzzunknown',None)['kind'],'reference_missing')
        with tempfile.TemporaryDirectory() as p:
            base=Path(p);(base/'manifest.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'manifest pin'):F.verify(base)

    def test_encyclopedia_internal_selection_and_external_withholding(self):
        with tempfile.TemporaryDirectory() as p:
            app=App(topic_base=p)
            selected=app.chat({'corpus':'reference','message':'topic Fossil'})['response']
            self.assertEqual(selected['context']['title'],'Fossil')
            self.assertEqual(app.query({'corpus':'reference','profile':'external','question':'Fossil'})['reader']['kind'],'not_in_corpus')

    def test_world_questions_are_not_dictionary_commands(self):
        self.assertIsNone(F.handle('How did dinosaurs become extinct?',None))
        self.assertIsNone(F.handle('what are you?',None))

    def test_plural_fallback_requires_an_existing_headword(self):
        headword,senses,_=F.lookup_forms('dogs')
        self.assertEqual(headword,'dog');self.assertTrue(senses)
        self.assertFalse(F.lookup_forms('zzzzunknowns')[1])


    def test_complete_headword_index_includes_nonletter_and_capital_entries(self):
        m=F.verify();archive=m['resources'][0]
        index=F.headword_index(str(F.BASE/archive['path']),archive['sha256'])
        self.assertEqual(sum(map(len,index.values())),m['wordnet_counts']['entries'])
        for word in ['Japan','japan','.22',"'hood",'100 mL']:
            with self.subTest(word=word):self.assertTrue(F.lookup(word)[0])

    def test_all_senses_are_reachable_without_duplicates(self):
        session={'mind':{},'context':None}
        F.topic('topic dictionary',session)
        result=F.topic('What does run mean?',session);ids=[]
        total=result['sense_page']['total'];self.assertGreater(total,12)
        while True:
            ids.extend(s['id'] for s in result['senses'])
            if 'next senses' not in result['suggestions']:break
            result=F.topic('next senses',session)
        self.assertEqual(len(ids),total);self.assertEqual(len(set(ids)),total)
        self.assertEqual(set(ids),{s['id'] for s in F.lookup('run')[0]})
        previous=F.topic('previous senses',session)
        self.assertLess(previous['sense_page']['offset'],result['sense_page']['offset'])

    def test_reference_topic_persists_and_preserves_ledger_context(self):
        with tempfile.TemporaryDirectory() as p:
            args={'topic_base':Path(p)/'topics','session_path':Path(p)/'save.json'}
            app=App(**args)
            first=app.chat({'corpus':'logic','message':'topic Budget guide'})
            sid=first['session'];context=first['response']['context']
            app.chat({'corpus':'logic','session':sid,'message':'topic dictionary'})
            app=App(**args)
            with patch.object(app,'build_search',side_effect=AssertionError('offline lookup')):
                result=app.chat({'corpus':'logic','session':sid,'message':'Japan'})['response']
            self.assertEqual(result['reference_topic'],'dictionary')
            self.assertEqual(result['authority'],'lexical_reference')
            self.assertEqual(result['context'],context)
            self.assertFalse(result['language_plan']['acquisition']['query'])
            self.assertEqual(app.collections.entries(),{})

    def test_thesaurus_and_explicit_exit(self):
        session={'mind':{},'context':None}
        F.topic('thesaurus',session)
        result=F.topic('happy',session)
        self.assertEqual(result['reference_topic'],'thesaurus')
        self.assertIn('Synonyms in this sense:',result['message'])
        F.topic('leave thesaurus',session)
        self.assertNotIn('reference_topic',session['mind'])
        self.assertIsNone(F.topic('happy',session))

    def test_topic_does_not_swallow_conversation_or_user_meanings(self):
        with tempfile.TemporaryDirectory() as p:
            app=App(topic_base=p)
            sid=app.chat({'corpus':'logic','message':'When I say flarn I mean a floating garden'})['session']
            app.chat({'corpus':'logic','session':sid,'message':'topic dictionary'})
            r=app.chat({'corpus':'logic','session':sid,'message':'What does flarn mean?'})['response']
            self.assertEqual(r['authority'],'user_declaration')
            self.assertIn('floating garden',r['message'])
        for question in ['cool tell me about the moon','How are you today?','help','chat mode']:
            session={'mind':{},'context':None}
            F.topic('dictionary',session)
            self.assertIsNone(F.topic(question,session))

    def test_missing_reference_is_bounded_and_does_not_acquire(self):
        with tempfile.TemporaryDirectory() as p:
            app=App(topic_base=p)
            sid=app.chat({'corpus':'logic','message':'topic dictionary'})['session']
            result=app.chat({'corpus':'logic','session':sid,'message':'zzzzunknown'})['response']
            self.assertEqual(result['kind'],'reference_missing')
            self.assertFalse(result['language_plan']['acquisition']['query'])
