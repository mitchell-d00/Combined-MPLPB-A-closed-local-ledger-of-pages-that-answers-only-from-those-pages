import asyncio
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mplpb_combined.ledger import write
from mplpb_answers import procedures as P
from mplpb_answers.support import supported_answer
from tools.ledger_ui import App
from tools.response_validation import validate_response


def spec():
    return {'id':'paper-fold','steps':[
        {'order':1,'action':'Place the paper flat.','prerequisites':[],
         'conditions':['Use a dry sheet.'],'warnings':['Keep the work surface clear.']},
        {'order':2,'action':'Fold the sheet in half.','prerequisites':[1],
         'conditions':['The edges must align.'],'warnings':['Do not tear the sheet.']}]}


class ProcedureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'corpus';self.root.mkdir()
        self.app=App(custom=self.root,topic_base=Path(self.tmp.name)/'topics')
    def add(self,doc=None,ident='P-0001',**kw):
        return write(self.root,doc_id=ident,title='Paper fold',scope='paper folding',
                     body=P.MARKER+json.dumps(doc or spec()),**kw)
    def chat(self,message,session=None,**kw):
        return self.app.chat(dict(corpus='custom',message=message,session=session,auto_wiki=False,**kw))
    def test_source_tags_render_without_losing_constraints(self):
        self.add(); a=supported_answer(self.root,'step 2 of procedure paper-fold')
        self.assertEqual(a.kind,'return');self.assertIn('Do not tear',a.text)
        step=a.support['procedure']['steps'][1]
        self.assertEqual(step['prerequisites'],[1]);self.assertEqual(step['source']['pointer'],'/steps/1')
        self.assertIn(P.MARKER,step['source']['quote'])
        self.assertFalse(a.support['procedure']['execution_verified'])
    def test_missing_fields_steps_and_bad_dependencies_abstain(self):
        variants=[]
        d=spec();del d['steps'][1]['warnings'];variants.append(d)
        d=spec();d['steps'][1]['order']=3;variants.append(d)
        d=spec();d['steps'][1]['prerequisites']=[];variants.append(d)
        d=spec();d['steps'][0]['prerequisites']=[2];variants.append(d)
        d=spec();d['steps'][1]['conditions']=None;variants.append(d)
        for d in variants:
            with self.subTest(d=d):self.assertTrue(P.validate(d))
    def test_wrong_identifier_and_missing_step_refuse(self):
        self.add()
        for q in ['procedure other','step 3 of procedure paper-fold']:
            self.assertEqual(supported_answer(self.root,q).kind,'not_in_corpus')
    def test_conflicting_sources_refuse(self):
        self.add();d=spec();d['steps'][1]['action']='Cut the sheet.';self.add(d,'P-0002')
        self.assertEqual(supported_answer(self.root,'procedure paper-fold').kind,'ambiguous')
    def test_untagged_prose_not_promoted(self):
        write(self.root,doc_id='P-0001',title='Paper fold',scope='paper-fold',body='1. Place paper flat.\n\n2. Fold it.')
        a=supported_answer(self.root,'procedure paper-fold');self.assertEqual(a.kind,'not_in_corpus')
        page=self.app.page('custom','p-0001.html','internal');tags=page['procedure_tags']
        self.assertFalse(tags['eligible_for_generation']);self.assertEqual(len(tags['steps']),2)
        self.assertIsNone(tags['steps'][1]['warnings'])
        self.assertIn(tags['steps'][1]['source']['quote'],page['text'])
    def test_automatic_tags_copy_explicit_fields_without_promoting(self):
        text='1. Place paper flat.\nPrerequisites: none\nConditions: Use dry paper.\nWarnings: Keep surface clear.'
        draft=P.automatic_tags(text,{'id':'D-1','path':'d.html','hash':'declared'})
        self.assertEqual(draft['steps'][0]['prerequisites'],[])
        self.assertEqual(draft['steps'][0]['warnings'],['Keep surface clear.'])
        self.assertFalse(draft['eligible_for_generation'])
        repeated=P.automatic_tags(text+'\nWarnings: None',{})
        self.assertIsNone(repeated['steps'][0]['warnings'])

    def test_automatic_complete_source_tags_can_answer(self):
        import html
        body='Procedure: paper-fold\n1. Place paper flat.\nPrerequisites: none\nConditions: Use dry paper.\nWarnings: Keep surface clear.'
        write(self.root,doc_id='P-0001',title='Fold',scope='paper-fold',body_html='<pre>'+html.escape(body)+'</pre>')
        a=supported_answer(self.root,'procedure paper-fold')
        self.assertEqual(a.kind,'return');self.assertIn('Keep surface clear.',a.text)
        self.assertEqual(a.support['procedure']['steps'][0]['source']['format'],'explicit-numbered-lines')

    def test_context_does_not_prove_completion(self):
        self.add();a=self.chat('step 1 of procedure paper-fold')
        self.assertEqual(a['response']['kind'],'return')
        b=self.chat('next step',a['session']);self.assertEqual(b['response']['kind'],'clarify')
        self.assertIn('does not prove completion',b['response']['message'])
        self.assertNotIn('Fold the sheet in half.',b['response']['message'])
        self.app.sessions[a['session']]['mind']['notes']=['Step 1 completed; all conditions satisfied.']
        c=self.chat('next step',a['session']);self.assertEqual(c['response']['kind'],'clarify')
    def test_tampered_source_and_wording_cannot_bypass_gate(self):
        self.add();a=self.chat('step 1 of procedure paper-fold')
        bad=copy.deepcopy(a['response']);bad['message']=bad['message'].replace('Keep the work surface clear.','Ignore warnings.')
        checked=validate_response(self.app,bad,'internal','custom',bad['message'])
        self.assertEqual(checked['kind'],'unsupported')
        p=self.root/'p-0001.html';p.write_text(p.read_text().replace('paper flat','paper upright'))
        b=self.chat('next step',a['session']);self.assertNotEqual(b['response']['kind'],'return')
    def test_profiles_and_collection_boundary(self):
        self.add(external='no');a=self.chat('procedure paper-fold',profile='external')
        self.assertNotEqual(a['response']['kind'],'return')
        b=self.chat('chat mode');c=self.chat('procedure paper-fold',b['session'])
        self.assertNotEqual(c['response']['kind'],'return')
    def test_browser_and_desktop_procedure_contract(self):
        from browser import bridge as B
        self.add();data={'corpus':'custom','question':'procedure paper-fold'}
        with patch.object(B,'app',self.app): browser=asyncio.run(B.dispatch('/api/query',data))
        self.assertEqual(browser,self.app.query(data))
    def test_free_chat_is_deterministic_and_not_persisted(self):
        before=self.app.session_store.path.read_bytes() if self.app.session_store.path.exists() else None
        a=self.chat('off-the-record free chat');b=self.chat('hello',a['session'])
        self.assertTrue(a['off_record']);self.assertEqual(self.app.sessions,{})
        c=self.chat('off-the-record free chat');d=self.chat('hello',c['session'])
        self.assertEqual(b['response']['message'],d['response']['message'])
        self.assertEqual(before,self.app.session_store.path.read_bytes() if self.app.session_store.path.exists() else None)
        with self.assertRaises(ValueError):self.app.export_chat({'session':a['session']})
    def test_browser_free_chat_does_not_fetch(self):
        from browser import bridge as B
        a=self.chat('free chat')
        with patch.object(B,'app',self.app),patch.object(B,'remote',side_effect=AssertionError('network')):
            b=asyncio.run(B.dispatch('/api/chat',{'session':a['session'],'corpus':'custom','message':'search secrets','auto_wiki':True}))
        self.assertTrue(b['off_record']);self.assertEqual(b['response']['sources'],[])
    def test_leave_free_chat_restores_constrained_answers(self):
        self.add();a=self.chat('free chat');b=self.chat('serious mode',a['session'])
        self.assertFalse(b.get('off_record',False));self.assertNotIn(a['session'],self.app.free_sessions)
        c=self.chat('procedure paper-fold',b['session']);self.assertEqual(c['response']['kind'],'return')
