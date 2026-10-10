import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import skill_planner as P, chat_environment as E
from tools.ledger_ui import App


class SkillPlannerTests(unittest.TestCase):
    def session(self):
        return {'mind':{'notes':[]},'context':None,'log':[],
                'environment':{'mode':'chat','corpora':[],'focus_corpus':None}}

    def test_recognition_never_renders_or_mutates(self):
        session=self.session();session['mind']['emotional']={'active':True,'style':'listen'}
        before=copy.deepcopy(session)
        with patch.object(P.M,'reply',side_effect=AssertionError('rendered during planning')), \
             patch.object(P.D,'respond',side_effect=AssertionError('discourse probe')), \
             patch.object(P.EM,'handle',side_effect=AssertionError('emotion probe')):
            for scope in ['general','focus','legacy']:
                for text in ['I am relieved','please be gentle','repeat exactly change the subject',
                             'how do I save my chat?','synonyms curious','What should we discuss?']:
                    plan=P.plan(text,session,scope)
                    self.assertEqual(plan['phase'],'before_execution')
        self.assertEqual(session,before)

    def test_losing_local_skill_does_not_execute(self):
        session=self.session()
        session['mind']['emotional']={'active':True,'style':'listen','turn':0,'no_jokes':False}
        with patch.object(P.D,'respond',side_effect=AssertionError('losing renderer')):
            result=P.execute('I am relieved',session)
        self.assertEqual(result['skill_plan']['selected']['skill'],'emotional')
        self.assertEqual(result['sources'],[])

    def test_decline_does_not_try_another_renderer_or_commit(self):
        session=self.session();before=copy.deepcopy(session)
        def decline(message,memory):
            memory['bad_mutation']=True
            return None
        with patch.object(P.D,'respond',side_effect=decline), \
             patch.object(P.S,'handle',side_effect=AssertionError('fallback renderer')):
            result=P.execute('can we talk',session)
        self.assertEqual(result['execution_issue'],'selected skill declined')
        self.assertEqual(session,before)

    def test_failed_source_attempts_do_not_leak_context(self):
        session=self.session()
        def miss(*args):
            args[2]['mind']['idea_chat']={'subject':'wrong source'}
            return None
        def general(message,state):
            self.assertNotIn('idea_chat',state['mind'])
            return P.M.reply('conversation','A local reply.',None,'TEST',authority='conversation_structure')
        with patch.object(E,'explore_sources',side_effect=miss),patch.object(E,'general',side_effect=general):
            result=E.retrieve(None,{},session,'an unfamiliar topic','logic','internal',finish=True)
        self.assertEqual(result['retrieval_plan']['steps'],['loaded_sources','general_skills'])
        self.assertEqual(result['retrieval_plan']['outcomes'][0]['status'],'no_support')
        self.assertNotIn('idea_chat',session['mind'])

    def test_source_routes_are_selected_without_reading(self):
        with patch.object(P.M,'handle',side_effect=AssertionError('source probe')):
            self.assertEqual(P.source_plan('summarize it',None)['reader'],'mind')
            self.assertEqual(P.source_plan('topic Moon',None)['reader'],'ledger')
            self.assertEqual(P.source_plan('How heavy is it?',{'title':'Moon'})['reader'],'grounded')
            self.assertEqual(P.source_plan('show source',{'title':'Moon'})['reader'],'ledger')

    def test_local_followups_and_source_focus_survive_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'topics';app=App(topic_base=base)
            start=app.chat({'corpus':'logic','message':'topic Budget guide'});sid=start['session']
            for text in ['Hello','How do I export my chat?','synonyms curious','How big is it?']:
                r=app.chat({'corpus':'logic','session':sid,'message':text})['response']
                self.assertEqual(r['context']['title'],'Budget guide')
                self.assertTrue(r['reply_plan']['subplans'])
                app=App(topic_base=base)
            self.assertEqual(r['kind'],'unsupported')
            self.assertEqual(r['sources'],[])

    def test_help_recognition_matches_renderer(self):
        # Category aliases plus independent procedural wording, with and without focus.
        requests=['Can I export some collections?','Where can I save this workspace?',
                  'How do I use its handles?','hello','help me understand its size']
        requests += [next(iter(sorted(aliases))) for aliases in P.M.HELP_ALIASES.values()]
        for context in [None,{'title':'a ceramic vessel'}]:
            for text in requests:
                self.assertEqual(bool(P.M.help_intent(text,context)),bool(P.M.help_reply(text,context)),text)
