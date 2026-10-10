import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.chat_phrasing import conversational_request
from tools.ledger_ui import App


class SocialLeadInTests(unittest.TestCase):
    def test_complete_request_is_preserved(self):
        for prefix in ['Cool ', 'Great, ', 'Okay! ', 'Nice; ', 'Awesome ', 'Thanks, ',
                       'All right, ', 'Sure, ', 'Cool, thanks! ']:
            for request in ['tell me about the Moon', 'how big is it?',
                            'tell me about Great Britain', 'tell me why not to use it',
                            'describe an apple', 'summarize the Moon', 'teach me about Mars']:
                with self.subTest(prefix=prefix, request=request):
                    self.assertEqual(conversational_request(prefix + request)[0], request)

    def test_content_negation_and_literals_are_not_discarded(self):
        for text in ['Cool water', 'Great Britain', 'Nice is a city', 'Thanks',
                     'Cool Moon', 'say cool tell me about the Moon',
                     'repeat exactly Great, tell me', 'Cool, do not search Moon',
                     'Not great, tell me about the Moon', 'If cool, tell me about the Moon',
                     '"Cool, tell me about the Moon"', 'Tell me about cool stars']:
            self.assertEqual(conversational_request(text), (text, None), text)

    def test_screenshot_routes_identically_even_during_social_chat(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = App(topic_base=Path(tmp) / 'topics')
            with patch.object(app, 'build_search', side_effect=AssertionError('network')):
                for mode in ['just chat', 'load MPLPB']:
                    for prefix in ['', 'Cool ', 'Great, ', 'Okay! ']:
                        sid = app.chat({'corpus': 'logic', 'message': mode})['session']
                        app.chat({'corpus': 'logic', 'session': sid, 'message': 'I had a bad day'})
                        q = prefix + 'Tell me about the Moon'
                        r = app.chat({'corpus': 'logic', 'session': sid, 'message': q})['response']
                        self.assertEqual(r['interpretation']['original'], q)
                        self.assertEqual(r['interpretation']['resolved'], 'Tell me about the Moon')
                        self.assertNotEqual(r.get('response_structure', {}).get('intent'), 'social_followup')
                        comparable = (r['kind'], r['authority'], r['message'], r['sources'])
                        if not prefix:
                            expected = copy.deepcopy(comparable)
                        else:
                            self.assertEqual(comparable, expected)
                        self.assertEqual(app.export_chat({'session': sid})['turns'][-1]['payload']['question'], q)

    def test_followup_keeps_selected_topic_and_literal_echo(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = App(topic_base=Path(tmp) / 'topics')
            sid = app.chat({'corpus': 'logic', 'message': 'topic Budget guide'})['session']
            r = app.chat({'corpus': 'logic', 'session': sid, 'message': 'Cool, how big is it?'})['response']
            self.assertEqual(r['context']['title'], 'Budget guide')
            self.assertEqual(r['kind'], 'unsupported')
            app.chat({'corpus': 'logic', 'session': sid, 'message': 'just chat'})
            r = app.chat({'corpus': 'logic', 'session': sid, 'default_chat': True,
                          'message': 'say exactly Cool, tell me about the Moon'})['response']
            self.assertEqual(r['message'], 'Cool, tell me about the Moon')
