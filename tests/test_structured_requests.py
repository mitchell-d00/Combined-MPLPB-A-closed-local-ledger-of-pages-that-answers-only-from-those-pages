import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.ledger_ui import App
from tools import structured_requests as SR, conversation_memory as CM
from tools.response_validation import validate_response


class StructuredRequestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.app=App(topic_base=Path(self.tmp.name)/'topics')
    def tearDown(self):self.tmp.cleanup()
    def send(self,q,sid=None):
        return self.app.chat({'corpus':'logic','session':sid,'message':q,'auto_wiki':False})
    def modes(self):
        for mode in ['chat mode','serious mode','free chat']:
            yield mode,self.send(mode)['session']
    def test_composed_self_requests_and_names(self):
        for mode,sid in self.modes():
            for q,name in [('Good morning I’m M how long will you remember my name','M'),
                           ('I’m Ada how long will you remember that','Ada'),
                           ('Good evening my name is Noor; what are your limitations?','Noor')]:
                r=self.send(q,sid)['response']
                self.assertIn('Hi, '+name,r['message'])
                self.assertNotIn('Tell me a little more',r['message'])
                self.assertEqual(r['response_validation']['status'],'checked')
                self.assertIn(name,self.send('What is my name?',sid)['response']['message'])
                self.assertEqual(r['sources'],[])
            r=self.send('How long will you remember my name?',sid)['response']
            self.assertIn('ephemeral' if mode=='free chat' else 'saved transcript',r['message'])
            self.assertIn('no fixed retention timer',r['message'].lower())
            self.assertEqual(self.send('What are you?',sid)['response']['authority'],'system_description')
    def test_unknown_compound_is_not_silently_swallowed(self):
        for mode,sid in self.modes():
            r=self.send('I am Ada how can I flarn the moon',sid)['response']
            self.assertEqual(r['kind'],'clarify')
            self.assertEqual(r['sources'],[])

    def test_states_are_not_names(self):
        for q in ["I'm tired", "Good morning I'm happy how long will you remember that", "I'm not Ada"]:
            self.assertIsNone(CM.introduction(q))
    def test_dictionary_senses_followups_and_fresh_validation(self):
        for mode,sid in self.modes():
            for q in ['Tell me about a dog','What is an apple?','Explain a bee','Describe an obelisk']:
                r=self.send(q,sid)['response']
                self.assertEqual(r['authority'],'lexical_reference',(mode,q,r['message']))
                self.assertTrue(r['sources']);self.assertIn('CC-BY-4.0',r['message'])
                self.assertEqual(r['response_validation']['status'],'checked')
                if len(r['senses'])>1:self.assertIn('Which sense',r['message'])
                picked=self.send('sense 1',sid)['response']
                self.assertEqual(picked['lexical_proof']['sense'],r['senses'][0]['id'])
                again=self.send('Explain that',sid)['response']
                self.assertEqual(again['message'],picked['message'])
                self.assertIn('fresh dictionary sense and exact constrained rendering',again['response_validation']['checks'])
                bad=copy.deepcopy(again);bad['message']+=' It cures every disease.'
                self.assertEqual(validate_response(self.app,bad,'internal','logic',bad['message'])['response_validation']['status'],'blocked')
                unsupported=self.send('Why does it fly?',sid)['response']
                self.assertEqual(unsupported['kind'],'unsupported')
            missing=self.send('Explain a zznonexistentwordzz',sid)['response']
            self.assertNotEqual(missing['kind'],'return')
            self.assertFalse(missing.get('lexical_proof'))
    def test_activity_and_hypothetical(self):
        for mode,sid in self.modes():
            for q in ['small calculation','Work through a small calculation','Could you help me with some arithmetic?']:
                r=self.send(q,sid)['response'];self.assertIn('expression',r['message'])
                self.assertIn('84',self.send('12 times 7',sid)['response']['message'])
            self.send('change the subject',sid)
            r=self.send('I’d like shape shifting',sid)['response']
            self.assertIn('imagined scenario',r['message']);self.assertNotIn('felt',r['message'])
            self.assertEqual(r['sources'],[])
    def test_free_chat_storage_and_network_boundaries(self):
        before=self.app.session_store.path.read_bytes() if self.app.session_store.path.exists() else None
        sid=self.send('free chat')['session']
        with patch.object(self.app,'root',side_effect=AssertionError('No ledger reads')):
            for q in ['I’m Mira how long will you remember that','Tell me about a bee','sense 1','Explain that','search secrets']:
                self.send(q,sid)
        self.assertEqual(self.app.sessions,{})
        after=self.app.session_store.path.read_bytes() if self.app.session_store.path.exists() else None
        self.assertEqual(before,after)
        self.send('leave free chat',sid)
        self.assertNotIn(sid,self.app.free_sessions)
    def test_no_negation_entity_or_context_shortcuts(self):
        for mode,sid in self.modes():
            for q in ['Tell me about a dog that is not alive','Explain a bee that causes earthquakes']:
                r=self.send(q,sid)['response']
                self.assertFalse(r.get('lexical_proof'))
            self.send('What is an apple?',sid)
            self.send('What are you?',sid)
            state=(self.app.free_sessions if mode=='free chat' else self.app.sessions)[sid]
            self.assertNotIn('lexical_discussion',state['mind'])
    def test_deterministic_replay(self):
        questions=['Good morning I’m M how long will you remember that','Explain a bee','sense 1','Explain that','small calculation','12 times 7','change the subject','I would choose invisibility']
        for mode in ['chat mode','serious mode','free chat']:
            runs=[]
            for _ in range(2):
                sid=self.send(mode)['session']
                runs.append([self.send(q,sid)['response']['message'] for q in questions])
            self.assertEqual(*runs)
    def test_browser_free_chat_never_acquires_sources(self):
        import asyncio
        from browser import bridge as B
        with patch.object(B,'app',self.app),patch.object(B,'remote',side_effect=AssertionError('network')):
            async def run():
                a=await B.dispatch('/api/chat',{'corpus':'logic','message':'free chat'})
                for q in ['What are you?','Tell me about a dog','sense 1','Explain that','search dogs','import Dog']:
                    r=await B.dispatch('/api/chat',{'corpus':'logic','session':a['session'],'message':q,'auto_wiki':True})
                    self.assertTrue(r['off_record'])
                    self.assertEqual(r['response']['response_validation']['status'],'checked')
            asyncio.run(run())
    def test_pending_input_and_unrecognized_hypothetical_do_not_invent(self):
        for mode,sid in self.modes():
            self.send('small calculation',sid)
            self.assertEqual(self.send('bananas',sid)['response']['kind'],'clarify')
            self.assertIn('undefined',self.send('4 / 0',sid)['response']['message'])
            self.send('change the subject',sid)
            r=self.send('maybe something else',sid)['response']
            self.assertIn('hypothetical',r['message']);self.assertNotIn('felt',r['message'])

    def test_live_regression_labels_and_calculation_explanations(self):
        for mode,sid in self.modes():
            r=self.send('I’m Ada how long will you remember that',sid)['response']
            self.assertIn('system description',r['support_label'].lower())
            for expression,expected in [('12 times 7','12 * 7 = 84'),('(2 + 3) * 4','2 + 3 = 5'),('1 / 3 + 1 / 6','1/3 + 1/6 = 1/2'),('4 / 0','undefined')]:
                self.send(expression,sid)
                r=self.send('Explain that',sid)['response']
                self.assertIn(expected,r['message'],(mode,r))
                self.assertEqual(r['response_structure']['intent'],'casual_calculation_explanation')
                self.assertIn('fresh bounded arithmetic and exact explanation rendering',r['response_validation']['checks'])
                self.assertEqual(r['message'],self.send('Explain that',sid)['response']['message'])
                bad=copy.deepcopy(r);bad['message']+=' Result: 999.'
                self.assertEqual(validate_response(self.app,bad,'internal','logic',bad['message'])['response_validation']['status'],'blocked')
            self.send('What is an apple?',sid)
            r=self.send('Explain that',sid)['response']
            self.assertEqual(r['authority'],'lexical_reference')
            self.send('What are you?',sid)
            self.assertFalse(self.send('Explain that',sid)['response'].get('calculation_proof'))

    def test_browser_dictionary_never_acquires_with_auto_lookup(self):
        import asyncio
        from browser import bridge as B
        with patch.object(B,'app',self.app),patch.object(B,'remote',side_effect=AssertionError('Unexpected dictionary acquisition')) as remote:
            async def run():
                for mode in ['chat mode','serious mode','free chat']:
                    a=await B.dispatch('/api/chat',{'corpus':'logic','message':mode})
                    for q in ['Tell me about a dog','sense 1','Explain that','What is an apple?','Explain a bee','define obelisk']:
                        r=await B.dispatch('/api/chat',{'corpus':'logic','session':a['session'],'message':q,'auto_wiki':True})
                        self.assertEqual(r['response']['authority'],'lexical_reference')
                        self.assertIsNone(r['response'].get('language_plan',{}).get('acquisition',{}).get('query'))
                remote.assert_not_called()
            asyncio.run(run())
