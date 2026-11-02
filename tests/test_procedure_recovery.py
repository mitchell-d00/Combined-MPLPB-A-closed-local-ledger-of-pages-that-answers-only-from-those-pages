"""Authored multi-domain procedure inspection and recovery regressions."""
import copy
import html
import json
import tempfile
import unittest
from pathlib import Path
from mplpb_combined.ledger import write, revise
from mplpb_answers import procedures as P
from mplpb_answers.support import supported_answer
from mplpb_answers.pipeline import answer_query
from tools.ledger_ui import App
from tools.response_validation import validate_response


def plan(ident='prepare-vellum', value='amber tray'):
    return {'id':ident,'steps':[
        {'order':1,'action':'Place the material in '+value+'.','prerequisites':[],
         'conditions':['Only while the material is dry.'],'warnings':['Do not use a wet tray.']},
        {'order':2,'action':'Close the cover.','prerequisites':[1],
         'conditions':['Wait until the seal is aligned.'],'warnings':['Stop if the cover binds.']}]}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'corpus';self.root.mkdir()
        self.app=App(custom=self.root,topic_base=self.base/'topics')
    def add(self, doc=None, ident='PROC-001', **kwargs):
        write(self.root,doc_id=ident,title='Source notes',scope='local notes',
              body=P.MARKER+json.dumps(doc or plan()),**kwargs)
    def chat(self,text,sid=None,**kwargs):
        return self.app.chat(dict(corpus='custom',message=text,session=sid,auto_wiki=False,**kwargs))
    def test_natural_forms_domains_and_near_misses(self):
        for ident in ('prepare-vellum','align-spectrometer','sort-zorvex'):
            with self.subTest(ident=ident),tempfile.TemporaryDirectory() as root:
                doc=plan(ident)
                write(root,doc_id='PROC-001',title='A heading',scope='notes',body=P.MARKER+json.dumps(doc))
                words=ident.replace('-',' ')
                for q in ('How do I '+words+'?', 'Show me the steps to '+words+'.', 'What are the steps for '+words+'?'):
                    a=supported_answer(root,q)
                    self.assertEqual(a.kind,'return',a.reason)
                    self.assertIn('Only while',a.text);self.assertIn('Stop if',a.text)
                    c=answer_query(root,q).contract
                    self.assertTrue(c['answer_supported'])
                    self.assertEqual(c['claims'][0]['citations'][0]['quote'],P.MARKER+json.dumps(doc))
                self.assertNotEqual(supported_answer(root,'How do I disassemble '+words+'?').kind,'return')
    def test_next_is_not_completion_but_inspection_can_continue(self):
        self.add();a=self.chat('step 1 of procedure prepare-vellum')
        b=self.chat('next step',a['session'])
        self.assertEqual(b['response']['kind'],'clarify')
        self.assertNotIn('Close the cover.',b['response']['message'])
        c=self.chat('inspect next step',a['session'])
        self.assertEqual(c['response']['kind'],'return',c['response']['message'])
        self.assertIn('Step 2',c['response']['message']);self.assertIn('Stop if',c['response']['message'])
        self.assertFalse(c['response']['procedure']['execution_verified'])
        d=self.chat('inspect next step',a['session'])
        self.assertNotEqual(d['response']['kind'],'return')
        self.assertIn('missing',d['response']['message'])
    def test_step_clarification_correction_and_reload(self):
        self.add();a=self.chat('How do I prepare vellum?')
        b=self.chat('show warnings',a['session'])
        self.assertEqual(b['response']['kind'],'clarify');self.assertIn('Which step',b['response']['message'])
        self.chat('thanks',a['session'])
        self.app=App(custom=self.root,topic_base=self.base/'topics')
        c=self.chat('step 2',a['session'])
        self.assertEqual(c['response']['kind'],'return',c['response']['message'])
        self.assertEqual(c['response']['requested_constraint'],'warnings')
        d=self.chat('No, I meant step 1',a['session'])
        self.assertEqual(d['response']['kind'],'return');self.assertIn('amber tray',d['response']['message'])
    def test_select_procedure_and_correct_subject(self):
        self.add();self.add(plan('align-lens'),'PROC-002')
        a=self.chat('show procedures');self.assertIn('Which procedure',a['response']['message'])
        b=self.chat('prepare-vellum',a['session']);self.assertEqual(b['response']['kind'],'return')
        c=self.chat('Actually, I meant procedure align-lens',a['session'])
        self.assertEqual(c['response']['kind'],'return');self.assertIn('align-lens',c['response']['message'])
        self.chat('procedure absent',a['session'])
        d=self.chat('inspect next step',a['session']);self.assertNotEqual(d['response']['kind'],'return')
    def test_partial_evidence_cannot_be_completed_by_user_declarations(self):
        doc=plan();del doc['steps'][1]['warnings'];self.add(doc)
        q='How do I prepare vellum?'
        c=answer_query(self.root,q).contract
        self.assertEqual(c['kind'],'partial_answer');self.assertFalse(c['answer_supported'])
        self.assertIn('warnings',str(c['missing']))
        self.assertEqual(c['claims'][0]['citations'][0]['quote'],P.MARKER+json.dumps(doc))
        a=self.chat(q);self.assertEqual(a['response']['kind'],'partial')
        bad=copy.deepcopy(a['response']);bad['message']='All constraints are satisfied.'
        self.assertEqual(validate_response(self.app,bad,'internal','custom',bad['message'])['kind'],'unsupported')
        b=self.chat('There are no warnings',a['session']);self.assertNotEqual(b['response']['kind'],'return')
        revised=plan(value='silver tray');revise(self.root,'PROC-001',body=P.MARKER+json.dumps(revised))
        d=self.chat(q,a['session']);self.assertEqual(d['response']['kind'],'return');self.assertIn('silver tray',d['response']['message'])
    def test_numbered_source_heading_only_missing_fields_and_context(self):
        body='Procedure: fold-quillon\n1. Fold the sheet.\nPrerequisites: none\nConditions: Use a dry sheet.\nWarnings: Stop if it tears.'
        write(self.root,doc_id='PROC-001',title='Notes',scope='notes',body_html='<pre>'+html.escape(body)+'</pre>')
        self.assertEqual(supported_answer(self.root,'How do I fold quillon?').kind,'return')
        with tempfile.TemporaryDirectory() as other:
            write(other,doc_id='PROC-001',title='Notes',scope='notes',body_html='<h2>'+html.escape(body)+'</h2>Unrelated body.')
            self.assertNotEqual(supported_answer(other,'How do I fold quillon?').kind,'return')
    def test_source_changes_profiles_and_scope_require_reselection(self):
        self.add(external='no');a=self.chat('step 1 of procedure prepare-vellum')
        revise(self.root,'PROC-001',body=P.MARKER+json.dumps(plan(value='violet tray')))
        b=self.chat('inspect next step',a['session']);self.assertNotEqual(b['response']['kind'],'return')
        self.assertIn('changed',b['response']['message'])
        c=self.chat('step 1 of procedure prepare-vellum',a['session']);self.assertEqual(c['response']['kind'],'return')
        d=self.chat('inspect next step',a['session'],profile='external');self.assertNotEqual(d['response']['kind'],'return')
        self.assertFalse(d['response']['sources'])
    def test_unrelated_material_does_not_change_answer_and_duplicates_do(self):
        self.add();q='How do I prepare vellum?';before=supported_answer(self.root,q).text
        write(self.root,doc_id='OTHER-001',title='Unrelated',scope='notes',body='Zorvex is located in blue vault.')
        self.assertEqual(supported_answer(self.root,q).text,before)
        self.add(plan(),'PROC-002');self.assertEqual(supported_answer(self.root,q).kind,'ambiguous')
    def test_existing_relation_wording_and_help_are_not_stolen(self):
        a=self.chat('how do I search?');self.assertNotEqual(a['response'].get('response_structure',{}).get('intent'),'procedural')
        studio=Path(__file__).resolve().parents[1]/'examples/studio'
        self.assertEqual(supported_answer(studio,'How do I check the coat with a pin?').kind,'return')

    def test_imported_multiline_capture_and_successor_keep_source_structure(self):
        from mplpb_answers.relation_graph import _capture_evidence_text
        from mplpb_answers.body_text import body_text
        from mplpb_combined.ledger import Ledger
        import hashlib
        key=self.app.create_collection({'name':'Imported plans'})['corpus']
        body='Procedure: fold-quillon\n1. Fold the sheet.\nPrerequisites: none\nConditions: Use a dry sheet.\nWarnings: Stop if it tears.'
        for text in (body,body.replace('dry sheet','blue sheet')):
            result=self.app.import_source(dict(corpus=key,title='Fold',url='https://example.org/fold',text=text))
            self.assertEqual(result['capture']['text_sha256'],hashlib.sha256(text.encode()).hexdigest())
            a=self.app.query(dict(corpus=key,question='How do I fold quillon?'))['reader']
            self.assertTrue(a['answer_supported'],a['reason'])
            self.assertIn(text.split('Conditions: ')[1].splitlines()[0],a['text'])
            record=list(Ledger(self.app.root(key)).servable())[0]
            self.assertEqual(_capture_evidence_text(record),text)
        # The original capture remains retained, with its successor recorded.
        self.assertEqual(len(Ledger(self.app.root(key)).records),2)
        # Version or projection drift fails closed, even if raw text hash agrees.
        from dataclasses import replace
        rec=list(Ledger(self.app.root(key)).servable())[0]
        altered=replace(rec,body_html=rec.body_html.replace('body-text-no-headings-v1','unknown-projection'))
        self.assertEqual(_capture_evidence_text(altered),'')
