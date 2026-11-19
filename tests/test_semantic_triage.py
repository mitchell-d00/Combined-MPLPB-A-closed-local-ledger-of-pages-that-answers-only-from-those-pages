"""Flag schemas and source boundaries only; mocks are not model accuracy."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mplpb_answers.body_text import body_text
from mplpb_answers.local_narrator import LocalBackend
from mplpb_combined.ledger import write,withdraw
from mplpb_work.semantic_triage import flag_pairs


class TriageTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.records=[write(self.root,doc_id='SRC-'+str(i),title='Archive',scope='archive',body=text)
                      for i,text in enumerate(('Alice reported an uncertain arrival.','Bob reported a different arrival.'),1)]
        def anchor(record):
            quote=body_text(record.body_html)
            return dict(source_id=record.id,path=record.path,hash=record.hash_actual,body_start=0,body_end=len(quote),quote=quote)
        self.pairs=[{'left':anchor(self.records[0]),'right':anchor(self.records[1])}]
    def reply(self,messages,**kwargs):
        return json.dumps({'decisions':[{'pair_id':p['pair_id'],'flags':['AMBIGUOUS_LINK_CANDIDATE']}
                                       for p in json.loads(messages[1]['content'])['pairs']]})
    def test_disabled_and_flagged_modes_have_no_authority_or_source_writes(self):
        before={p.name:p.read_bytes() for p in self.root.glob('*.html')}
        with patch.object(LocalBackend,'generate',side_effect=self.reply) as model:
            disabled=flag_pairs(self.root,'archive',self.pairs)
            model.assert_not_called()
            result=flag_pairs(self.root,'archive',self.pairs,enabled=True)
        self.assertEqual(disabled['status'],'disabled');self.assertEqual(result['status'],'flagged')
        self.assertTrue(result['flags'])
        for item in [result]+result['flags']:
            for key in ('answer_supported','source_support_established','historical_truth_independently_verified'):
                self.assertIs(item[key],False)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.glob('*.html')})
        self.assertEqual(result['ledger_writes'],0)
        self.assertIsNone(result['metrics']['false_flags'])
    def test_unknown_pair_claim_and_extra_authority_fields_are_rejected(self):
        bad=[{'decisions':[{'pair_id':'invented','flags':['POTENTIAL_CONTRADICTION']}]},
             {'decisions':[{'pair_id':'P01','flags':['PROVEN_CAUSAL_LINK']}]},
             {'decisions':[{'pair_id':'P01','flags':[]}],'answer_supported':True},
             {'decisions':[]}, {'decisions':[{'pair_id':'P01','flags':[],'explanation':'Invented story'}]}]
        for value in bad:
            with self.subTest(value=value),patch.object(LocalBackend,'generate',return_value=json.dumps(value)):
                result=flag_pairs(self.root,'archive',self.pairs,enabled=True)
                self.assertEqual(result['flags'],[]);self.assertEqual(result['status'],'unavailable_or_rejected')
    def test_quoted_excerpt_without_complete_context_is_refused(self):
        pairs=copy.deepcopy(self.pairs);pairs[0]['left']['body_start']=6;pairs[0]['left']['quote']=pairs[0]['left']['quote'][6:]
        with self.assertRaises(ValueError):flag_pairs(self.root,'archive',pairs)
    def test_withdrawal_and_source_change_prevent_stale_flags(self):
        def mutate(*a,**kw):withdraw(self.root,'SRC-1');return self.reply(*a,**kw)
        with patch.object(LocalBackend,'generate',side_effect=mutate),self.assertRaisesRegex(ValueError,'changed'):
            flag_pairs(self.root,'archive',self.pairs,enabled=True)
    def test_restricted_source_never_reaches_local_model(self):
        r=write(self.root,doc_id='HIDDEN-1',title='Archive',scope='archive',body='A private archive paragraph.',external='no')
        pairs=copy.deepcopy(self.pairs);quote=body_text(r.body_html)
        pairs[0]['left']=dict(source_id=r.id,path=r.path,hash=r.hash_actual,body_start=0,body_end=len(quote),quote=quote)
        with patch.object(LocalBackend,'generate') as model,self.assertRaises(ValueError):
            flag_pairs(self.root,'archive',pairs,profile='external',enabled=True)
        model.assert_not_called()
    def test_unreachable_backend_and_pair_limits_remain_non_authoritative(self):
        with patch.object(LocalBackend,'generate',side_effect=ValueError('unavailable')):
            result=flag_pairs(self.root,'archive',self.pairs*20,enabled=True)
        self.assertFalse(result['answer_supported']);self.assertEqual(result['flags'],[])
        self.assertTrue(result['skipped'])
        self.assertEqual(result['status'],'unavailable_or_rejected')


if __name__=='__main__':unittest.main()
