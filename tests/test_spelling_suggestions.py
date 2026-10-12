"""Spelling confirmation never supplies evidence or relaxes source eligibility."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mplpb_combined import ledger as L
from tools.ledger_ui import App
from tools.grounded_chat import correction_suggestion


class SpellingSuggestionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'corpus'
        self.root.mkdir()
        self.moon = self.page('Moon', 'The Moon is about 3,474 km in diameter.')
        self.app = App(self.root, topic_base=self.base / 'topics')
        self.sid = self.app.chat({'corpus': 'custom', 'message': 'topic Moon'})['session']

    def page(self, title, body, **kwargs):
        return L.write(self.root, title=title, scope=title, body=body,
                       origin='machine', owner='synthetic fixture', source_authorship='unknown', external='no', **kwargs)

    def ask(self, message, **kwargs):
        with patch.object(self.app, 'build_search', side_effect=AssertionError('No acquisition')):
            return self.app.chat({'corpus': 'custom', 'session': self.sid, 'message': message,
                                  'auto_wiki': False, **kwargs})['response']

    def test_offer_then_explicit_confirmation_uses_exact_source(self):
        for q in ['what is its diamter?', 'waht is its diameter?', 'whats its diameter?',
                  'how big is itt?', 'how big is it plz', 'waht is its diameter']:
            with self.subTest(q=q):
                r = self.ask(q)
                s = r['spelling_suggestion']
                self.assertTrue(s['requires_confirmation'])
                self.assertEqual(r['interpretation']['original'], q)
                self.assertEqual(r['sources'], [])
                self.assertNotIn('3,474', r['message'])
                self.assertTrue(any(a['request'] == s['question'] for a in r['guidance']['actions']))
                answer = self.ask(s['question'])
                self.assertEqual(answer['kind'], 'grounded_answer')
                self.assertEqual(answer['sources'][0]['hash'], self.moon.hash)
                self.assertIn('The Moon is about 3,474 km in diameter.', answer['message'])

    def test_never_rewrites_names_numbers_negation_or_conditions(self):
        context = self.ask('how big is it?')['context']
        for q in ['how big is Moom?', 'what is Moonz diamter?', 'what is its diamter 99?',
                  'do not tell me its diamter', 'waht is not its diameter?',
                  'say "what is its diamter?"', 'repeat what is its diamter?',
                  'what is its diamter if it explodes?', 'what is its diamter and mass?',
                  'what is its diameter?', 'what is its diamter without the shell?',
                  'waht is its diameter compared with Earth?']:
            with self.subTest(q=q):
                self.assertIsNone(correction_suggestion(q, context))
        self.assertIsNone(correction_suggestion('what is its diamter?', None))

    def test_reload_topic_switch_old_suggestion_and_return(self):
        self.page('Earth', 'The Earth is 12,742 km in diameter.')
        offered = self.ask('what is its diamter?')['spelling_suggestion']['question']
        self.ask('hello')
        self.app = App(self.root, topic_base=self.base / 'topics')
        self.ask('topic Earth')
        old = self.ask(offered)
        self.assertNotEqual(old['kind'], 'grounded_answer')
        self.assertEqual(old['sources'], [])
        current = self.ask('how big is itt?')['spelling_suggestion']['question']
        self.assertIn('Earth', current)
        self.assertIn('12,742', self.ask(current)['message'])
        self.ask('topic Moon')
        self.assertIn('3,474', self.ask(offered)['message'])
        self.assertTrue(self.app.resume_chat({'session': self.sid})['chain_intact'])

    def test_bare_yes_does_not_execute_stale_suggestion(self):
        self.ask('what is its diamter?')
        self.assertNotEqual(self.ask('yes')['kind'], 'grounded_answer')
        self.ask('never mind')
        self.assertNotEqual(self.ask('yes')['kind'], 'grounded_answer')

    def test_missing_fact_and_conflicting_values_remain_unanswered(self):
        offered = self.ask('what is its hieght?')['spelling_suggestion']['question']
        self.assertEqual(self.ask(offered)['kind'], 'unsupported')
        self.page('Sphere', 'The Sphere is 10 km in diameter. The Sphere is 12 km in diameter.')
        self.ask('topic Sphere')
        offered = self.ask('what is its diamter?')['spelling_suggestion']['question']
        r = self.ask(offered)
        self.assertEqual(r['kind'], 'conflict')
        self.assertEqual(len(r['evidence']), 2)

    def test_tamper_withdraw_revise_and_profile_between_offer_and_confirmation(self):
        for change in ['tamper', 'withdraw', 'revise', 'duplicate', 'profile']:
            with self.subTest(change=change):
                title = 'Object '+change
                page = self.page(title, 'The '+title+' is 12 km in diameter.')
                self.ask('topic '+title)
                offered = self.ask('what is its diamter?')['spelling_suggestion']['question']
                kwargs = {}
                if change == 'tamper':
                    path = self.root / page.path
                    path.write_text(path.read_text().replace('12 km', '99 km'))
                elif change == 'withdraw':
                    L.withdraw(self.root, page.id)
                elif change == 'revise':
                    L.revise(self.root, page.id, body='The '+title+' is 99 km in diameter.')
                elif change == 'duplicate':
                    self.page(title, 'The '+title+' is 99 km in diameter.')
                else:
                    kwargs['profile'] = 'external'
                r = self.ask(offered, **kwargs)
                self.assertNotEqual(r['kind'], 'grounded_answer')
                self.assertEqual(r['sources'], [])

    def test_excluded_attribute_stays_excluded_after_confirmation(self):
        self.page('Restricted', 'The Restricted is 12 km in diameter.', not_for='diameter')
        self.ask('topic Restricted')
        offered = self.ask('what is its diamter?')['spelling_suggestion']['question']
        r = self.ask(offered)
        self.assertEqual(r['sources'], [])
        self.assertEqual(r['kind'], 'unsupported')

    def test_browser_auto_lookup_does_not_fetch_for_correction(self):
        import asyncio
        from unittest.mock import AsyncMock
        from browser import bridge as B
        with patch.object(B, 'app', self.app), patch.object(B, 'remote', AsyncMock(side_effect=AssertionError('No network'))) as remote:
            r = asyncio.run(B.dispatch('/api/chat', {
                'corpus': 'custom', 'session': self.sid,
                'message': 'what is its diamter?', 'auto_wiki': True}))['response']
        remote.assert_not_awaited()
        self.assertEqual(r['sources'], [])
        self.assertTrue(r['spelling_suggestion']['requires_confirmation'])
