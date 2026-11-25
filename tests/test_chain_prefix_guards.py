"""Authority and state guards for useful documentary chain partials."""
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from mplpb_combined import ledger
from mplpb_combined.reader import PROFILES
from mplpb_answers.pipeline import answer_query
from mplpb_answers import documentary_links
Q='What is established and missing in the request, dispatch and reported receipt chain in sources REQUEST, DISPATCH and RECEIPT?'
class ChainPrefixGuards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  texts=['Mara Flint requested that Len Kay send the water chart to the west landing.','In response to request source REQUEST, Len Kay sent the water chart to the west landing.','Referring to dispatch source DISPATCH, Bea Park reported receiving the water chart at the west landing from Len Kay.']
  for i,t in zip(['REQUEST','DISPATCH','RECEIPT'],texts):ledger.write(self.root,doc_id=i,title='Record',scope='archive',body_html='<p>'+t+'</p>',external='yes',origin='human')
 def test_no_prose_profile_cannot_gain_chain_claims(self):
  result=answer_query(self.root,Q,PROFILES['external']).contract
  self.assertFalse(result['claims']);self.assertFalse(result['answer_supported'])
 def test_late_withdrawal_discards_prefix(self):
  original=documentary_links.chain
  def changed(*args,**kw):
   result=original(*args,**kw);ledger.withdraw(self.root,'DISPATCH');return result
  with patch.object(documentary_links,'chain',changed):result=answer_query(self.root,Q).contract
  self.assertFalse(result['claims']);self.assertFalse(result['answer_supported'])
 def test_derived_source_cannot_hide_unit_budget(self):
  ledger.write(self.root,doc_id='HINT',title='Hint',scope='archive',body_html='<p>'+'Noise. '*1001+'</p>',derived_from=['REQUEST'])
  result=answer_query(self.root,Q).contract
  self.assertFalse(result['claims']);self.assertIn('budget',result['diagnostic']['code'])
