"""Public development controls for scoped evidence; no independent truth claim."""
import copy
import html
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers.passages import PassageIndex
from mplpb_answers import relation_graph
from mplpb_combined.ledger import write, withdraw, Ledger, serving_view
from mplpb_combined.reader import PROFILES
from mplpb_combined.record import upsert_meta
from mplpb_work.event_candidates import inspect_events
from mplpb_work import WorkStore, WorkError, Denied
from mplpb_work.model import OPERATIONS
from mplpb_work.api import request


class ScopedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.clock=patch.dict(os.environ,{'MPLPB_NOW':'2026-11-16T00:00Z'})
        self.clock.start();self.addCleanup(self.clock.stop)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def page(self,id,body,**kw):
        return write(self.root,doc_id=id,title='Witness',scope='archive record owner location',
                     body_html='<pre>'+html.escape(body)+'</pre>',**kw)

    def query(self,field='Owner',**kw):
        return answer_query(self.root,'What is '+field+' for record CASE-1?',**kw).contract

    def test_exact_field_missing_is_not_missing_record(self):
        self.page('SRC-1','Record-ID: CASE-1\nLocation: north archive')
        result=self.query()
        self.assertEqual(result['diagnostic']['code'],'exact_field_missing')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['retrieval']['ranking'],'exact-field-no-ranking-v1')

    def test_exact_body_field_bypasses_rank_and_keeps_canonical_quote(self):
        rec=self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice')
        self.page('NOISE-1','Owner: Bob\nRecord-ID: OTHER-1')
        result=self.query()
        self.assertTrue(result['answer_supported']);self.assertEqual(result['kind'],'supported_answer')
        self.assertEqual([s['id'] for s in result['sources']],[rec.id])
        self.assertEqual(result['claims'][0]['citations'][0]['quote'],'Owner: Alice')
        self.assertEqual(answer_query(self.root,'Read owner',record_id=rec.id+'@'+rec.hash,field='Owner').legacy()['kind'],'return')

    def test_unique_value_route_retains_competing_same_identity(self):
        self.page('SRC-1','Record-ID: CASE-1\nAccession: UNIQUE-7788\nOwner: Alice')
        self.page('SRC-2','Record-ID: CASE-1\nOwner: Bob')
        result=answer_query(self.root,'Inspect owner',field='Owner',exact_value={'field':'Accession','value':'UNIQUE-7788'}).contract
        self.assertEqual(result['kind'],'conflict')
        self.assertEqual({c['citations'][0]['quote'] for c in result['claims']},{'Owner: Alice','Owner: Bob'})
        self.assertFalse(result['answer_supported'])

    def test_conflicting_passages_within_same_record_never_pruned_by_ranking(self):
        self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice\nOwner: Bob')
        result=self.query()
        self.assertEqual(result['kind'],'conflict');self.assertEqual(len(result['claims']),2)
        small=self.query(max_passages=1)
        self.assertEqual(small['diagnostic']['code'],'contradictory_passages_pruned')
        self.assertFalse(small['answer_supported']);self.assertEqual(small['retrieval']['omitted_field_passages'],1)

    def test_later_competing_field_context_cannot_be_pruned_to_keep_header_answer(self):
        self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice\n\nAdditional source context.\nOwner: Bob')
        result=self.query()
        self.assertEqual(result['kind'],'conflict');self.assertFalse(result['answer_supported'])
        self.assertEqual({c['citations'][0]['quote'] for c in result['claims']},{'Owner: Alice','Owner: Bob'})
        self.assertEqual(self.query(max_passages=1)['diagnostic']['code'],'contradictory_passages_pruned')

    def test_identifier_pin_cannot_bypass_changed_source_or_not_for(self):
        rec=self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice',not_for='payroll')
        result=answer_query(self.root,'payroll owner',record_id=rec.id,field='Owner').contract
        self.assertFalse(result['answer_supported'])
        path=self.root/rec.path;path.write_text(path.read_text().replace('Alice','Mallory'))
        self.assertFalse(self.query()['answer_supported'])
        self.assertFalse(answer_query(self.root,'Owner?',record_id=rec.id+'@'+rec.hash,field='Owner').contract['answer_supported'])

    def test_exact_field_profile_and_origin_depth_gates_still_apply(self):
        self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice',origin='machine')
        self.assertFalse(self.query(profile=PROFILES['external'])['answer_supported'])

    def test_field_examples_are_not_active_headers(self):
        self.page('SRC-1','Record-ID: CASE-1\nExample:\nOwner: Mallory')
        self.assertEqual(self.query()['diagnostic']['code'],'exact_field_missing')

    def test_assisted_exact_fields_never_become_deterministic_support(self):
        self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice')
        result=self.query(mode='assisted')
        self.assertFalse(result['answer_supported']);self.assertNotEqual(result['kind'],'supported_answer')

    def test_existing_strict_first_proof_is_labelled_strict_not_assisted(self):
        self.page('SRC-1','The kettle color is blue.')
        result=answer_query(self.root,'What is the kettle color?',mode='assisted').contract
        self.assertEqual(result['mode'],'strict');self.assertEqual(result['kind'],'supported_answer')
        self.assertTrue(result['answer_supported']);self.assertEqual(result['reader'],None)

    def test_exact_route_rechecks_source_changes_and_discards_old_quotes(self):
        rec=self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice')
        original=relation_graph.declared_fields;changed=[]
        def mutate(record):
            rows=original(record)
            if not changed:
                path=self.root/rec.path;path.write_text(path.read_text().replace('Alice','Mallory'));changed.append(True)
            return rows
        with patch.object(relation_graph,'declared_fields',side_effect=mutate):result=self.query()
        self.assertEqual(result['diagnostic']['code'],'source_changed')
        self.assertFalse(result['answer_supported']);self.assertFalse(result['claims'])
        self.assertFalse(result['retrieval']['passages'])

    def test_event_identity_refusal_and_distinct_declared_node(self):
        self.page('SRC-1','Message-ID: MSG-1\nSubject: archival record\nBody: a')
        self.page('SRC-2','Message-ID: MSG-2\nSubject: archival record\nBody: a')
        result=answer_query(self.root,'Are these the same event?').contract
        self.assertEqual(result['diagnostic']['code'],'event_identity_unresolved')
        events=inspect_events(self.root,'archival record')
        self.assertFalse(events['candidates'])
        self.assertEqual(len(events['unassigned_occurrences']),2)

    def test_shared_explicit_key_groups_distinct_appearances_only(self):
        a=self.page('SRC-1','Event-Key: DECLARED-7\nMessage-ID: MSG-1\nBody: first')
        b=self.page('SRC-2','Event-Key: DECLARED-7\nMessage-ID: MSG-1\nBody: changed')
        events=inspect_events(self.root,'archive record')
        node=events['candidates'][0]
        self.assertFalse(node['answer_supported']);self.assertTrue(node['changed_message_body'])
        self.assertEqual({o['occurrence_id'] for o in node['occurrences']},{a.id+'@'+a.hash,b.id+'@'+b.hash})
        self.assertNotIn(node['node_id'],{o['occurrence_id'] for o in node['occurrences']})

    def test_declared_event_id_cannot_collide_with_generated_shared_key_node(self):
        self.page('SRC-1','Event-ID: source-key:KEY-1\nMessage-ID: MSG-1\nBody: declared')
        self.page('SRC-2','Event-Key: KEY-1\nMessage-ID: MSG-2\nBody: appearance')
        self.page('SRC-3','Event-Key: KEY-1\nMessage-ID: MSG-3\nBody: appearance')
        nodes=inspect_events(self.root,'archive record')['candidates']
        self.assertEqual(len(nodes),2);self.assertEqual(len({n['node_id'] for n in nodes}),2)
        self.assertEqual(sorted(len(n['occurrences']) for n in nodes),[1,2])
        self.assertTrue(all(not n['answer_supported'] for n in nodes))

    def test_sealed_event_and_occurrence_declarations_are_not_answers(self):
        rec=self.page('SRC-1','Source appearance.',event_id='EVENT-7',occurrence_id='OCC-4')
        events=inspect_events(self.root,'archive record')
        node=events['candidates'][0]
        self.assertEqual(node['event_id'],'EVENT-7');self.assertFalse(node['answer_supported'])
        self.assertEqual(node['occurrences'][0]['declared_occurrence_id'],'OCC-4')
        path=self.root/rec.path;path.write_text(path.read_text().replace('EVENT-7','EVENT-8'))
        self.assertFalse(inspect_events(self.root,'archive record')['candidates'])

    def corrected(self):
        original=self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice\nLocation: north')
        correction=self.page('SRC-2','Record-ID: CASE-1\nOwner: Bob\nLocation: south',
            supersedes=[original.id+'@'+original.hash],corrects_field='Owner',
            valid_from='2026-01-01',valid_until='2027-01-01')
        return original,correction

    def test_time_scoped_correction_boundaries_and_unchanged_pins(self):
        original,correction=self.corrected()
        for date,owner in [('2025-12-31','Alice'),('2026-01-01','Bob'),('2026-12-31','Bob'),('2027-01-01','Alice')]:
            with self.subTest(date=date):
                result=self.query(as_of=date)
                self.assertTrue(result['answer_supported'],result['diagnostic'])
                self.assertEqual(result['text'],'Owner: '+owner)
        self.assertEqual(Ledger(self.root).by_id[original.id][0].hash_actual,original.hash)
        self.assertEqual(self.query('Location',as_of='2026-06-01')['text'],'Location: north')
        self.assertTrue(self.query(as_of='2025-01-01')['sources'][0]['hash']==original.hash)

    def test_withdrawal_never_resurrects_predecessor_even_outside_window(self):
        original,correction=self.corrected();withdraw(self.root,correction.id)
        for time in ('2025-01-01','2026-06-01','2027-01-01'):
            self.assertFalse(self.query(as_of=time)['answer_supported'])
        self.assertFalse(Ledger(self.root).servable())

    def test_correction_scope_unclear_is_precise(self):
        self.corrected()
        result=answer_query(self.root,'Explain this archival record correction',as_of='2026-06-01').contract
        self.assertEqual(result['diagnostic']['code'],'correction_scope_unclear')
        self.assertFalse(result['answer_supported'])

    def test_scoped_sources_require_field_gate_and_historical_views_cannot_authorize_work(self):
        from mplpb_combined.provenance_gate import gather
        original,correction=self.corrected()
        self.assertNotIn(correction.id,{s['id'] for s in gather(self.root,'archive owner').sources})
        store,_=WorkStore.create(self.root/'work')
        payload={'corpus':'archive','source_id':original.id,'source_hash':original.hash,
                 'query':'archive owner','quote':'Owner: Alice'}
        with serving_view('2025-01-01','Owner'):
            self.assertTrue(self.query(as_of='2025-01-01')['answer_supported'])
            self.assertIsNone(store._source({'corpora':{'archive':str(self.root)}},payload,'internal',{}))

    def test_invalid_window_and_wrong_predecessor_pin_fail_closed(self):
        original=self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice')
        for changes in ({'valid_from':'2027-01-01','valid_until':'2026-01-01'},{'valid_from':'yesterday'}):
            with self.assertRaises(ValueError):self.page('BAD-1','Owner: Bob',supersedes=[original.id],**changes)
        with self.assertRaises(ValueError):self.page('BAD-1','Owner: Bob',supersedes=[original.id+'@sha256:'+'0'*64],valid_from='2026-01-01')
        self.assertTrue(self.query()['answer_supported'])
        with self.assertRaises(ValueError):self.query(as_of='2026-01-01T12:00:00')
        self.assertIsNone(__import__('mplpb_combined.ledger',fromlist=['SERVING_VIEW']).SERVING_VIEW.get())

    def test_explicit_field_correction_preserves_other_fields_and_hash_pins(self):
        from mplpb_answers.corrections import correct_claim
        original=self.page('SRC-1','Record-ID: CASE-1\nOwner: Alice\nLocation: north')
        result=correct_claim(self.root,original.id,'Owner: Alice','Owner: Bob',corrects_field='Owner',
                             valid_from='2026-01-01',valid_until='2027-01-01')
        self.assertFalse(result['answer_supported'])
        self.assertEqual(self.query(as_of='2026-06-01')['text'],'Owner: Bob')
        self.assertEqual(self.query('Location',as_of='2026-06-01')['text'],'Location: north')
        self.assertEqual(Ledger(self.root).by_id[original.id][0].hash,original.hash)

    def test_concurrent_query_views_do_not_leak_or_change_stored_status(self):
        from concurrent.futures import ThreadPoolExecutor
        original,correction=self.corrected()
        before={r.path:(self.root/r.path).read_bytes() for r in Ledger(self.root).records}
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda t:self.query(as_of=t)['text'],['2025-01-01','2026-06-01']*3))
        self.assertEqual(results,['Owner: Alice','Owner: Bob']*3)
        self.assertEqual(before,{r.path:(self.root/r.path).read_bytes() for r in Ledger(self.root).records})

    def test_quoted_relation_hops_stay_non_authoritative_and_missing_quote_is_candidate(self):
        a=self.page('SRC-1','The archive is located in north room.')
        b=self.page('SRC-2','North room contains maps.')
        hops=[{'question':'Where is archive located?','source_id':a.id,'hash':a.hash,'quote':'The archive is located in north room.'},
              {'question':'What does north room contain?','source_id':b.id,'hash':b.hash,'quote':'North room contains maps.'}]
        result=answer_query(self.root,'Explore archive maps',relation_hops=hops).contract['exploration']
        self.assertEqual(result['status'],'source_quoted_edges');self.assertFalse(result['answer_supported'])
        hops[1].pop('quote')
        result=answer_query(self.root,'Explore archive maps',relation_hops=hops).contract['exploration']
        self.assertEqual(result['edges'][1]['status'],'candidate');self.assertFalse(result['answer_supported'])
        contract=answer_query(self.root,'Where is archive located?',relation_hops=hops).contract
        self.assertFalse(contract['answer_supported']);self.assertNotEqual(contract['kind'],'supported_answer')

    def test_causal_composition_reverse_question_and_source_change_never_gain_support(self):
        rec=self.page('SRC-1','Cracks come from rapid cooling.')
        hop={'question':'What causes cracks?','source_id':rec.id,'hash':rec.hash,'quote':'Cracks come from rapid cooling.'}
        result=relation_graph.explore(self.root,'cracks cooling',[hop,hop],PROFILES['internal'])
        self.assertTrue(all(e['status']=='candidate' for e in result['edges']))
        self.assertFalse(result['answer_supported'])
        path=self.root/rec.path;path.write_text(path.read_text().replace('rapid','slow'))
        result=relation_graph.explore(self.root,'cracks cooling',[hop],PROFILES['internal'])
        self.assertFalse(result['edges'][0]['quote_verified'])
        with self.assertRaises(ValueError):relation_graph.explore(self.root,'cracks',[hop]*3,PROFILES['internal'])


class WorkExtensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        self.store,self.host=WorkStore.create(root/'work')
        grant=self.store.assign(self.host,seat='worker',instance='worker-1',
            model={'name':'fixture','provider':'fixture','version':'1','context_policy_hash':'unknown'},
            contract={'operations':sorted(OPERATIONS),'tools':['fixture'],'scopes':['T1'],
                'share_with':[],'profile':'internal','expires_at':self.store.clock()+3600},
            expected_head=self.store.head(self.host)['hash'])
        self.token=grant['credential']
        self.put('T1','task',{'goal':'Fixture','criteria':['done'],'review_budget':1,'state':'open','acceptance':{}},operator_seconds=2.5)

    def put(self,id,kind,payload,**kw):
        return self.store.put(self.token,id=id,kind=kind,payload=payload,dependencies={},visibility=['worker'],
            expected_revision=0,expected_head=self.store.snapshot(self.token)['head'],**kw)

    def test_operator_seconds_are_optional_non_authoritative_and_validated(self):
        view=self.store.handoff(self.token)
        self.assertEqual(view['operator_seconds'],2.5)
        self.assertFalse(view['answer_supported']);self.assertFalse(view['content_truth_verified'])
        audit=self.store.audit(self.host)
        self.assertEqual(audit['events'][-1]['operator_seconds'],2.5)
        for bad in (True,-1,float('nan'),float('inf'),'3'):
            with self.assertRaises(WorkError):self.put('BAD','task',{},operator_seconds=bad)
        self.assertEqual(self.store.handoff(self.token)['operator_seconds'],2.5)

    def test_private_operator_events_do_not_change_an_unrelated_seat_view(self):
        grant=self.store.assign(self.host,seat='observer',instance='observer-1',
            model={'name':'fixture','provider':'fixture','version':'1','context_policy_hash':'unknown'},
            contract={'operations':[],'tools':[],'scopes':['T1'],'share_with':[],
                      'profile':'internal','expires_at':self.store.clock()+3600},
            expected_head=self.store.head(self.host)['hash'])
        view=self.store.handoff(grant['credential'])
        self.assertIsNone(view['operator_seconds']);self.assertEqual(view['operator_events'],[])
        self.assertEqual(view['external_receipts'],[])

    def test_completion_and_external_read_ack_do_not_supply_claim_support(self):
        action={'task':'T1','task_revision':1,'operation':'fixture','arguments':{},'side_effect':'local',
                'executor_seat':'worker','state':'proposed','retry_of':{},'retry_reason':''}
        self.put('A1','action',action)
        self.store.executors['fixture']=lambda r:{'result':'passed','validation':{'done':True},'artifact':'fixture',
                                                   'operator_seconds':1.25,'operator_seconds_basis':'measured'}
        result=self.store.execute(self.token,id='A1',expected_revision=1,expected_head=self.store.snapshot(self.token)['head'])
        self.assertFalse(result['receipt']['answer_supported'])
        for kind in ('READ','ACK'):
            receipt=self.store.record_external_receipt(self.host,receipt=result['receipt']['id'],kind=kind,artifact='host declaration',
                expected_head=self.store.head(self.host)['hash'])
            self.assertFalse(receipt['answer_supported']);self.assertFalse(receipt['external_world_verified'])
        view=self.store.handoff(self.token)
        self.assertEqual(view['operator_seconds'],3.75);self.assertEqual(len(view['external_receipts']),2)
        claim={'task':'T1','proposition':'Component X is available','basis':'inference','assessment':'supported_under_scope',
               'assumptions':[],'alternatives':[],'revisit_when':'new source'}
        with self.assertRaises(WorkError):self.put('C1','claim',claim)
        with self.assertRaises(WorkError):request(self.store,self.token,{'op':'record_external_receipt'})
        self.assertFalse(view['answer_supported']);self.assertFalse(view['content_truth_verified'])


if __name__=='__main__':unittest.main()
