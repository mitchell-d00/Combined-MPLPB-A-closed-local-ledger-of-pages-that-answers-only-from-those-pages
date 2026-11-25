"""Opt-in tags cannot promote stale, ineligible or unsupported source claims."""
import copy
import hashlib
import html
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers import source_tags
from mplpb_combined.ledger import write, withdraw
from mplpb_combined.reader import PROFILES

FIXTURE=Path(__file__).resolve().parents[1]/'evaluation/source-tags/2026-11-25/development/inputs/ST-D-001'


class SourceTagGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'ledger';shutil.copytree(FIXTURE/'ledger',self.root)
        self.packet=json.loads((FIXTURE/'tags.json').read_text())
        self.question=json.loads((FIXTURE/'question.json').read_text())['question']

    def verify(self,**kwargs):return source_tags.verify_proposals(self.root,self.question,self.packet,**kwargs)
    def rejected(self,result):
        self.assertEqual(result['status'],'rejected');self.assertEqual(result['verified_relations'],[])

    def test_valid_native_witness_and_raw_contract_unchanged(self):
        before=answer_query(self.root,self.question).contract
        out=self.verify();self.assertEqual(out['status'],'accepted')
        self.assertFalse(out['authoritative']);self.assertFalse(out['changes_host_access'])
        self.assertEqual(answer_query(self.root,self.question).contract,before)

    def test_withdrawn_source(self):
        withdraw(self.root,'SOURCE-1');self.rejected(self.verify())

    def test_corrupt_source(self):
        p=self.root/self.packet['source']['path'];p.write_text(p.read_text().replace('wrote','forged'))
        self.rejected(self.verify())

    def test_unavailable_source(self):
        (self.root/self.packet['source']['path']).unlink();self.rejected(self.verify())

    def test_forged_policy_cannot_grant_external_access(self):
        other=Path(self.tmp.name)/'restricted'
        original=(self.root/self.packet['source']['path']).read_text()
        from mplpb_combined.record import parse_page
        r=parse_page(original,self.packet['source']['path'])
        write(other,doc_id='SOURCE-1',title='Restricted original',scope='documentary originals',
              body_html=r.body_html,origin='machine',external='no')
        self.root=other;self.packet['source']['visibility']='public'
        self.rejected(self.verify(profile=PROFILES['external']))
        self.assertFalse(answer_query(other,self.question,PROFILES['external']).contract['answer_supported'])

    def test_unsupported_execution_question_cannot_use_report_tags(self):
        self.question='Do these records independently establish that the attributed writer actually completed the work?'
        self.rejected(self.verify())

    def test_record_budget_includes_unrelated_pages(self):
        for i in range(8):write(self.root,doc_id='OTHER-'+str(i),title='Other leaf',scope='documentary originals',body='Unrelated cabinet record.',origin='machine')
        self.rejected(self.verify())

    def test_eligible_conflicting_report_is_not_pruned(self):
        from mplpb_combined.record import parse_page
        record=parse_page((self.root/self.packet['source']['path']).read_text(),self.packet['source']['path'])
        author=self.packet['relations'][0]['proposition']['author']
        write(self.root,doc_id='CONFLICT',title='Competing original',scope='documentary originals',
              body_html=record.body_html.replace(author,'Petra Moran'),origin='machine',external='yes')
        self.assertEqual(answer_query(self.root,self.question).contract['kind'],'conflict')
        self.rejected(self.verify())

    def test_original_role_span_must_belong_to_its_governing_statement(self):
        from mplpb_answers.body_text import body_text
        from mplpb_combined.record import parse_page
        old=parse_page((self.root/self.packet['source']['path']).read_text(),self.packet['source']['path'])
        reporter=self.packet['relations'][0]['proposition']['reporter']
        text=body_text(old.body_html)+'\n'+reporter
        self.root=Path(self.tmp.name)/'expanded'
        record=write(self.root,doc_id='SOURCE-1',title='Synthetic archive',scope='documentary originals',
                     body_html='<pre>'+html.escape(text)+'</pre>',origin='machine',external='yes')
        self.packet['source']={'id':record.id,'path':record.path,'hash':record.hash_actual,
                              'body_html_sha256':hashlib.sha256(record.body_html.encode()).hexdigest()}
        self.packet['nodes'][0]['body_end']=len(body_text(record.body_html))
        for node in self.packet['nodes'][1:]:
            a=record.body_html.index(html.escape(node['quote']))
            node['original_start_byte']=len(record.body_html[:a].encode())
            node['original_end_byte']=len(record.body_html[:a+len(html.escape(node['quote']))].encode())
        self.assertEqual(self.verify()['status'],'accepted')
        node=self.packet['nodes'][2];a=record.body_html.rindex(reporter)
        node['original_start_byte']=len(record.body_html[:a].encode())
        node['original_end_byte']=len(record.body_html[:a+len(reporter)].encode())
        self.rejected(self.verify())

    def test_scan_character_budget(self):
        write(self.root,doc_id='LONG',title='Long record',scope='documentary originals',body='x'*200001,origin='machine')
        self.rejected(self.verify())

    def test_scan_unit_budget(self):
        write(self.root,doc_id='UNITS',title='Unit record',scope='documentary originals',body_html='<p>Cabinet leaf.</p>'*1001,origin='machine')
        self.rejected(self.verify())

    def test_source_mutation_after_native_proof_discards_certificate(self):
        original=source_tags._validate
        def mutate(*args):
            result=original(*args);withdraw(self.root,'SOURCE-1');return result
        with patch.object(source_tags,'_validate',side_effect=mutate):self.rejected(self.verify())

    def test_duplicate_ids_and_duplicate_relations(self):
        original=copy.deepcopy(self.packet)
        self.packet['nodes'].append(copy.deepcopy(self.packet['nodes'][1]));self.rejected(self.verify())
        self.packet=original;self.packet['relations']*=2;self.rejected(self.verify())

    def test_malformed_and_unknown_labels_remain_unverified(self):
        original=copy.deepcopy(self.packet)
        for value in [[],None,'public']:
            with self.subTest(source=value):
                self.packet=copy.deepcopy(original);self.packet['source']=value;self.rejected(self.verify())
        for kind in ['famous','date','verified_person']:
            with self.subTest(kind=kind):
                self.packet=copy.deepcopy(original);self.packet['nodes'][2]['kind']=kind;self.rejected(self.verify())

    def test_proposal_budget(self):
        self.packet['nodes'][1]['quote']='x'*64001;self.rejected(self.verify())


if __name__=='__main__':unittest.main()
