"""Counterevidence, full-source budgets and final eligibility for corrections."""
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from mplpb_combined import ledger
from mplpb_answers.pipeline import answer_query
from mplpb_answers import documentary_correction
Q='What count does the later statement correct, and which destination does it retain?'
class CountCorrectionGuards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def add(self,i,text,**kw):return ledger.write(self.root,doc_id=i,title='Record',scope='archive',body_html='<p>'+text+'</p>',**kw)
 def pair(self):
  self.add('ORIGINAL','This letter was written on May 2, 1880. The cargo contains four crates for the west depot.')
  self.add('CORRECTION','In my letter of May 2, 1880, the count should read seven crates. The destination remains the west depot.')
 def test_final_withdrawal_discards_correction(self):
  self.pair();original=documentary_correction.PassageIndex.unchanged
  called=[]
  def changed(index):
   if not called:ledger.withdraw(self.root,'CORRECTION');called.append(True)
   return original(index)
  with patch.object(documentary_correction.PassageIndex,'unchanged',changed):r=answer_query(self.root,Q).contract
  self.assertFalse(r['claims']);self.assertFalse(r['answer_supported'])
 def test_full_source_units_count_even_when_derived(self):
  self.pair();r=self.add('HINT','Noise. '*1001,derived_from=['ORIGINAL'])
  result=answer_query(self.root,Q).contract
  self.assertFalse(result['answer_supported']);self.assertIn('budget',result['diagnostic']['code'])
 def test_original_question_policy_not_rewritten(self):
  self.pair();self.add('RESTRICTED','In my letter of May 2, 1880, the count should read eight crates. The destination remains the west depot.',not_for='destination')
  result=answer_query(self.root,Q).contract
  self.assertEqual(result['claims'][0]['proposition']['replacement_count'],'seven')
