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

    def test_basic_help_teaches_without_searching_or_losing_topic(self):
        from unittest.mock import patch
        first=self.chat('topic Dungeons and Dragons')
        with patch.object(self.app,'prepare_search',side_effect=AssertionError('help must not crawl')):
            for question in ('Hi!', 'How do I use this?', 'How do I search?', 'How do I search for fossils?', 'How do I save?', 'What does reset do?', 'Thanks', 'What can you do?'):
                answer=self.chat(question,first['session'])['response']
                self.assertEqual(answer['kind'],'smalltalk' if question=='Hi!' else 'help',question)
                self.assertEqual(answer['sources'],[])
                self.assertEqual(answer['context'],first['response']['context'])
        self.assertEqual(self.app.collections.entries(),{})
        self.assertEqual(self.chat('what is it?',first['session'])['response']['kind'],'return')

    def test_help_does_not_claim_web_is_deployed_or_export_is_backup(self):
        search=self.chat('How do I search?')['response']['message']
        self.assertIn('deployed crawler',search)
        self.assertIn('Wikipedia mode needs neither',search)
        save=self.chat('How do I export?')['response']['message']
        self.assertIn('not a full source-store backup',save)
        reset=self.chat('How do I reset?')['response']['message']
        self.assertIn('retaining its source pages',reset)

    def test_help_keeps_unknown_world_questions_in_reader(self):
        from tools import deterministic_mind as M
        self.assertIsNone(M.help_reply('Who discovered fossils?',None))
        self.assertIsNone(M.help_reply('Are dogs mammals?',None))
        self.assertIsNone(M.help_reply('Reset my collection now',None))
        self.assertNotEqual(self.chat('Who discovered fossils?')['response']['kind'],'help')

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
