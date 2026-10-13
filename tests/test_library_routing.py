import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mplpb_combined.ledger import write
from mplpb_answers.library import Library
from tools.ledger_ui import App
from tools.response_validation import validate_response


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.base=Path(self.tmp.name)
        self.a=self.base/'a'; self.b=self.base/'b'
        write(self.a,doc_id='A-1',title='Kettle specification',scope='kettle color',body='The kettle color is blue.')
        write(self.a,doc_id='A-2',title='Cable specification',scope='cable length',body='The cable is 12 feet long.')
        write(self.b,doc_id='B-1',title='Kettle specification',scope='kettle color',body='The kettle color is red.')
        self.roots={'a':('Workshop A',self.a),'b':('Workshop B',self.b)}
        self.manifest={'version':1,'root':'main','nodes':[
            {'id':'main','title':'Main Index','parent':None},
            {'id':'workshops','title':'Workshop Sub-Index','parent':'main','aliases':['workshops']},
            {'id':'a','title':'Workshop A','parent':'workshops','corpus':'a','aliases':['kettle']},
            {'id':'b','title':'Workshop B','parent':'workshops','corpus':'b','aliases':['kettle']}]}
        self.lib=Library(self.roots,self.manifest)
    def tearDown(self):self.tmp.cleanup()

    def test_broad_navigation_and_ambiguous_alias_do_not_read_books(self):
        with patch.object(self.lib,'resolve',side_effect=AssertionError('No body reads during routing')):
            r=self.lib.browse()
            self.assertEqual(r['library_route']['choices'][0]['id'],'workshops')
            r=self.lib.answer('What is the kettle color?')
            self.assertEqual(r['kind'],'clarify');self.assertEqual(r['sources'],[])
            r=self.lib.answer('What is the kettle color?','kettle')
            self.assertEqual([c['id'] for c in r['library_route']['choices']],['a','b'])
            self.assertNotIn('blue',r['message']);self.assertNotIn('red',r['message'])

    def test_single_leaf_answers_with_provenance_and_return_path(self):
        accesses=[]
        self.lib.resolve=lambda c:(accesses.append(c) or self.roots[c][1])
        r=self.lib.answer('What is the kettle color?','a')
        self.assertEqual(r['kind'],'return');self.assertIn('The kettle color is blue.',r['message'])
        self.assertEqual(set(accesses),{'a'})
        self.assertEqual(r['sources'][0]['corpus'],'a');self.assertTrue(r['sources'][0]['hash'])
        self.assertEqual([p['id'] for p in r['library_route']['path_back']],['a','workshops','main'])
        self.assertEqual(len(r['library_route']['related_pages']),1)
        self.assertEqual(r['library_route']['related_pages'][0]['id'],'A-2')
        self.assertFalse(r['library_route']['metadata_is_evidence'])
        self.assertEqual(r,self.lib.answer('What is the kettle color?','a'))

    def test_conflicting_pages_and_wrong_entity_abstain(self):
        self.assertEqual(self.lib.answer('What is the kettle color?','missing')['kind'],'clarify')
        self.assertEqual(self.lib.answer('What is the other kettle color?','a')['kind'],'unsupported')
        write(self.a,doc_id='A-3',title='Other kettle record',scope='kettle color',body='The kettle color is green.')
        r=self.lib.answer('What is the kettle color?','a')
        self.assertEqual(r['kind'],'clarify');self.assertEqual(r['sources'],[])
        self.assertNotIn('The kettle color is',r['message'])

    def test_negation_and_metadata_do_not_supply_support(self):
        write(self.a,doc_id='A-3',title='The moon is cheese',scope='moon cheese',body='The moon is not cheese.')
        self.assertEqual(self.lib.answer('What is the moon?','a')['kind'],'unsupported')

    def test_invalid_trees_fail_closed(self):
        bad=[]
        duplicate=copy.deepcopy(self.manifest);duplicate['nodes'].append(duplicate['nodes'][-1]);bad.append(duplicate)
        cycle=copy.deepcopy(self.manifest);cycle['nodes'][1]['parent']='a';bad.append(cycle)
        unknown=copy.deepcopy(self.manifest);unknown['nodes'][2]['corpus']='../../secret';bad.append(unknown)
        missing=copy.deepcopy(self.manifest);missing['nodes'][2]['parent']='missing';bad.append(missing)
        for manifest in bad:
            with self.assertRaises(ValueError):Library(self.roots,manifest)

    def test_profile_and_revision_gates_still_apply(self):
        write(self.a,doc_id='A-3',title='Private related',scope='private',body='Private fixture.',external='no')
        external=self.lib.answer('What is the kettle color?','a','external')
        self.assertNotIn('Private related',external['message'])
        # A page changed outside the ledger loses eligibility immediately.
        pin=self.lib.answer('What is the kettle color?','a')['sources'][0]
        path=self.a/pin['path'];path.write_text(path.read_text().replace('is blue','is green'))
        self.assertEqual(self.lib.answer('What is the kettle color?','a')['kind'],'unsupported')

    def test_chat_pending_choice_validation_and_no_network(self):
        import asyncio
        from browser import bridge as B
        app=App(topic_base=self.base/'topics',library_manifest=self.manifest);app.corpora=self.roots
        with patch.object(B,'app',app),patch.object(B,'remote',side_effect=AssertionError('No library acquisition')):
            async def run():
                start=await B.dispatch('/api/chat',{'corpus':'a','message':'library ask: What is the kettle color?','auto_wiki':True})
                self.assertEqual(start['response']['kind'],'clarify')
                r=await B.dispatch('/api/chat',{'corpus':'a','session':start['session'],'message':'library choose a','auto_wiki':True})
                self.assertEqual(r['response']['kind'],'return',r['response'])
                self.assertIn('fresh library scope',r['response']['response_validation']['checks'][0])
                self.assertEqual(r['response']['response_validation']['status'],'checked')
                self.assertIsNone(r['response']['language_plan']['acquisition']['query'])
                bad=copy.deepcopy(r['response']);bad['message']+=' The kettle can fly.'
                self.assertEqual(validate_response(app,bad,'internal','a',bad['message'])['response_validation']['status'],'blocked')
                # A new conflicting page must invalidate the old answer, even with its old pin intact.
                write(self.a,doc_id='A-4',title='Conflicting fixture',scope='kettle color',body='The kettle color is red.')
                self.assertEqual(validate_response(app,r['response'],'internal','a',r['response']['message'])['response_validation']['status'],'blocked')
            asyncio.run(run())

    def test_free_chat_does_not_read_library(self):
        app=App(topic_base=self.base/'topics',library_manifest=self.manifest);app.corpora=self.roots
        sid=app.chat({'corpus':'a','message':'free chat'})['session']
        with patch.object(app,'root',side_effect=AssertionError('No free-chat ledger access')):
            r=app.chat({'corpus':'a','session':sid,'message':'library ask in a: What is the kettle color?'})['response']
        self.assertEqual(r['kind'],'clarify');self.assertEqual(r['sources'],[])
        self.assertEqual(app.sessions,{})

    def test_large_route_catalog_keeps_unselected_books_closed(self):
        roots={'book'+str(i):('Book '+str(i),self.a if i==0 else self.base/'absent') for i in range(2000)}
        accesses=[]
        lib=Library(roots,resolve=lambda c:(accesses.append(c) or roots[c][1]))
        r=lib.answer('What is the kettle color?','shelf-book0')
        self.assertEqual(r['kind'],'return');self.assertEqual(set(accesses),{'book0'})
        self.assertEqual(len(lib.nodes),2001)

    def test_pagination_does_not_hide_ambiguity_or_read_books(self):
        roots={'book'+str(i):('Book '+str(i),self.a) for i in range(70)}
        lib=Library(roots,resolve=lambda c: (_ for _ in ()).throw(AssertionError('No books opened')))
        first=lib.answer('What is the kettle color?')
        second=lib.answer('What is the kettle color?','main',page=2)
        self.assertEqual(first['kind'],'clarify')
        self.assertEqual(first['library_route']['choices_total'],70)
        self.assertEqual(len(first['library_route']['choices']),20)
        self.assertTrue(set(c['id'] for c in first['library_route']['choices']).isdisjoint(c['id'] for c in second['library_route']['choices']))
        self.assertIn('library choices main page 2',first['suggestions'])

    def test_revisions_are_rechecked_and_missing_related_pages_not_invented(self):
        from mplpb_combined.ledger import revise
        original=self.lib.answer('What is the kettle color?','b')
        revise(self.b,'B-1',new_id='B-2',body='The kettle color is green.')
        revised=self.lib.answer('What is the kettle color?','b')
        self.assertIn('green',revised['message']);self.assertNotIn('red.',revised['message'])
        self.assertNotEqual(original['sources'][0]['hash'],revised['sources'][0]['hash'])
        self.assertEqual(revised['library_route']['related_pages'],[])

    def test_saved_clarification_and_catalog_change(self):
        app=App(topic_base=self.base/'topics',library_manifest=self.manifest);app.corpora=self.roots
        start=app.chat({'corpus':'a','message':'library ask: What is the kettle color?'})
        reopened=App(topic_base=self.base/'topics',library_manifest=self.manifest);reopened.corpora=self.roots
        r=reopened.chat({'corpus':'a','session':start['session'],'message':'library choose b'})['response']
        self.assertEqual(r['kind'],'return');self.assertIn('red.',r['message'])
        reopened.library_manifest['nodes'][3]['title']='Renamed book'
        self.assertEqual(validate_response(reopened,r,'internal','a',r['message'])['response_validation']['status'],'blocked')

    def test_library_commands_in_chat_and_serious_modes(self):
        app=App(topic_base=self.base/'topics',library_manifest=self.manifest);app.corpora=self.roots
        for mode in ('chat mode','serious mode'):
            sid=app.chat({'corpus':'a','message':mode})['session']
            r=app.chat({'corpus':'a','session':sid,'message':'library ask in a: What is the kettle color?'})['response']
            self.assertEqual(r['kind'],'return');self.assertEqual(r['response_validation']['status'],'checked')
            self.assertEqual(r['support_label'],'Library answer · source-backed')
