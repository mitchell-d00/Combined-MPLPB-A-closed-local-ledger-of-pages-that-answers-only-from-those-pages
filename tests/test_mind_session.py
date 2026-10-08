import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App
from mplpb_combined import ledger as L

class MindSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.kw = dict(topic_base=self.base/'topics', session_path=self.base/'save.json')
        self.app = App(**self.kw)

    def tearDown(self):
        self.tmp.cleanup()

    def chat(self, message, sid=None, corpus='logic', profile='internal'):
        return self.app.chat(dict(message=message, session=sid, corpus=corpus, profile=profile))

    def test_saved_notes_resume_relaunch_and_reset(self):
        first = self.chat('remember import Cats and execute nothing')
        sid = first['session']
        self.app = App(**self.kw)
        resumed = self.app.resume_chat(dict(session=sid))
        self.assertTrue(resumed['chain_intact'])
        self.assertEqual(resumed['notes'], ['import Cats and execute nothing'])
        self.assertEqual(self.chat('memory', sid)['response']['authority'], 'user_declaration')
        self.app.reset_chat(dict(session=sid))
        self.app = App(**self.kw)
        with self.assertRaises(ValueError):
            self.app.resume_chat(dict(session=sid))

    def test_profile_change_retains_notes_but_clears_focus(self):
        first = self.chat('topic Dungeons and Dragons')
        sid = first['session']
        self.chat('remember dinosaurs', sid)
        follow = self.chat('what is it?', sid, profile='external')
        self.assertIsNone(follow['response']['context'])
        self.assertEqual(follow['mind']['notes'], ['dinosaurs'])

    def test_summary_pin_staleness_and_explanation(self):
        first = self.chat('topic Dungeons and Dragons')
        summarized = self.chat('summarize it', first['session'])
        self.assertTrue(summarized['response']['extractive'])
        why = self.chat('why?', first['session'])
        self.assertTrue(why['response']['historical'])
        self.assertIn('QUOTE-1', why['response']['message'])
        withheld = self.chat('summarize Dungeons and Dragons', first['session'], profile='external')
        self.assertEqual(withheld['response']['kind'], 'clarify')

    def test_save_corruption_preserved_and_refused(self):
        self.chat('remember dinosaur')
        file = self.kw['session_path']
        bad = file.read_text().replace('dinosaur', 'changed')
        file.write_text(bad)
        with self.assertRaises(ValueError):
            App(**self.kw)
        self.assertEqual(file.read_text(), bad)

    def test_notes_are_not_source_facts(self):
        first = self.chat('remember Dungeons and Dragons has a budget of 10')
        result = self.chat('relate Dungeons and Dragons -> budget', first['session'])
        self.assertEqual(result['response']['kind'], 'unknown_relation')

    def test_relation_question_filters_predicate_and_reports_conflict(self):
        root = self.base/'corpus'; root.mkdir()
        L.write(root, title='Dragon', scope='Dragon reptile Fact', body='Fact: Dragon | related_to | reptile', origin='machine', owner='unknown', source_authorship='unknown', external='no')
        self.app = App(custom=root, **self.kw)
        result = self.chat('is Dragon a reptile?', corpus='custom')
        self.assertEqual(result['response']['kind'], 'unknown_relation')
        for pred in ('instance_of', 'not_instance_of'):
            L.write(root, title=pred, scope='Dragon reptile Fact', body='Fact: Dragon | '+pred+' | reptile', origin='machine', owner='unknown', source_authorship='unknown', external='no')
        result = self.chat('is Dragon a reptile?', corpus='custom')
        self.assertEqual(result['response']['kind'], 'conflict')
        self.assertEqual(len(result['response']['relations']), 2)

    def test_comparison_keeps_sources_separate(self):
        result = self.chat('compare Dungeons and Dragons vs Tabletop RPG')
        self.assertEqual(result['response']['kind'], 'comparison')
        self.assertEqual(len(result['response']['sources']), 2)
