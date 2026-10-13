import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mplpb_combined import ledger as L
from tools.ledger_ui import App
from tools import conversation_repairs as RP, conversation_continuity as CC


class ConversationRepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'corpus';self.root.mkdir()
        self.page=L.write(self.root,title='Moon',scope='Moon',body='The Moon is 3474 km in diameter. The Moon is 4.5 billion years old.',origin='machine',owner='unknown',source_authorship='unknown',external='no')
        self.app=App(self.root,topic_base=self.base/'topics')
        self.sid=self.app.chat({'corpus':'custom','message':'chat mode'})['session']
    def ask(self,q,**kw):
        with patch.object(self.app,'build_search',side_effect=AssertionError('no network')):
            return self.app.chat({'corpus':'custom','session':self.sid,'message':q,'auto_wiki':False,**kw})['response']
    def test_screenshot_sequence_reload_and_original(self):
        r=self.ask('Hi how are you to ight')
        self.assertIn('functional',r['message']);self.assertEqual(r['sources'],[])
        self.app=App(self.root,topic_base=self.base/'topics')
        q='Sorry I meant tonight';r=self.ask(q)
        self.assertIn('you meant tonight',r['message']);self.assertEqual(r['authority'],'conversation_structure')
        self.assertEqual(r['interpretation']['original'],q)
        self.assertEqual(r['interpretation']['conversational_repair']['source_turn'],2)
        self.assertTrue(self.app.resume_chat({'session':self.sid})['chain_intact'])
    def test_compositional_social_classes(self):
        for prefix in ['', 'Hi ', 'Hello! ', 'Hey, ']:
            for stem in ['how are you','how are you doing','how have you been',"how's it going",'how r u']:
                for when in ['today','tonight','to night','to ight','tonihgt','this evning']:
                    with self.subTest(prefix=prefix,stem=stem,when=when):
                        parsed=RP.wellbeing_frame(prefix+stem+' '+when)
                        self.assertIsNotNone(parsed)
                        self.assertEqual(parsed['intent'],'wellbeing')
    def test_no_clause_dropping_negation_literal_or_source_misclassification(self):
        for q in ['say how are you tonight','not how are you tonight','how are you today according to this document',
                  'how are you tonight and what is its mass','how are your pages verified',
                  'how are you not','how are you 100','Hi how are you on Mars','I wonder how are you today',
                  'how are you tonight without source checks']:
            self.assertIsNone(RP.wellbeing_frame(q),q)
        self.assertIsNone(RP.interpret('I meant not tonight',{}))
    def test_missing_and_stale_repairs_clarify(self):
        for q in ['Sorry I meant tonight','I meant its age','and mass?']:
            r=self.ask(q);self.assertIn('resend the whole sentence',r['message']);self.assertEqual(r['sources'],[])
        self.ask('how are you today');self.ask('what is 2 plus 2')
        self.assertIn('resend the whole sentence',self.ask('I meant tonight')['message'])
        self.ask('how are you today')
        for _ in range(3):self.ask('thanks')
        self.assertIn('resend the whole sentence',self.ask('I meant tonight')['message'])
    def test_attribute_repair_and_followup_always_check_sources(self):
        self.ask('topic Moon');self.ask('how big is it?')
        self.ask('hello')
        r=self.ask('Sorry I meant age');self.assertEqual(r['kind'],'grounded_answer')
        self.assertIn('4.5 billion',r['message']);self.assertEqual(r['sources'][0]['hash'],self.page.hash)
        self.assertEqual(self.ask('and mass?')['kind'],'unsupported')
        self.assertEqual(self.ask('and diameter?')['kind'],'grounded_answer')
        r=self.ask('what about its age?');self.assertEqual(r['kind'],'grounded_answer')
    def test_changed_pages_profiles_and_topics_do_not_supply_stale_answers(self):
        self.ask('topic Moon');self.ask('how big is it?')
        p=self.root/self.page.path;p.write_text(p.read_text().replace('4.5','9.9'))
        r=self.ask('and age?');self.assertEqual(r['sources'],[]);self.assertNotEqual(r['kind'],'grounded_answer')
    def test_ambiguous_rank_abstains_and_same_state_is_identical(self):
        with patch.object(RP,'temporal_candidates',return_value=[{'value':'today','score':85},{'value':'tonight','score':85}]):
            self.assertIsNone(RP.unique_time('test')[0])
        session={'mind':{},'log':[],'context':None}
        a=CC.prepare('Hi how are you to ight',copy.deepcopy(session))
        b=CC.prepare('Hi how are you to ight',copy.deepcopy(session))
        self.assertEqual(a,b)
        self.assertFalse(a['conversational_repair']['scores_are_probabilities'])
    def test_browser_social_repairs_do_not_trigger_auto_acquisition(self):
        import asyncio
        from unittest.mock import AsyncMock
        from browser import bridge as B
        async def dialogue():
            for q in ['Hi how are you to ight','Sorry I meant tonight']:
                r=await B.dispatch('/api/chat',{'corpus':'custom','session':self.sid,'message':q,'auto_wiki':True})
                self.assertEqual(r['response']['sources'],[])
                self.assertEqual(r['response']['authority'],'conversation_structure')
        with patch.object(B,'app',self.app),patch.object(B,'remote',AsyncMock(side_effect=AssertionError('no network'))) as remote:
            asyncio.run(dialogue())
        remote.assert_not_awaited()
    def test_topic_switch_and_delivery_profile_block_old_attribute_frame(self):
        L.write(self.root,title='Earth',scope='Earth',body='The Earth is 12 km in diameter. The Earth is 10 years old.',
                origin='machine',owner='unknown',source_authorship='unknown',external='no')
        self.ask('topic Moon');self.ask('how big is it?');self.ask('topic Earth')
        r=self.ask('and age?');self.assertEqual(r['sources'],[])
        self.assertNotIn('4.5 billion',r['message'])
        self.ask('how big is it?')
        r=self.ask('and age?',profile='external');self.assertEqual(r['sources'],[])
