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

