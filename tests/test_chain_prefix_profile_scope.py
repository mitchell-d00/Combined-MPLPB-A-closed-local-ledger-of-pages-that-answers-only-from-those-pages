"""Scope matches must not turn a no-prose profile into a synthesis profile."""
from pathlib import Path
import unittest,tempfile
from tests.test_chain_prefix_guards import Q
from mplpb_combined import ledger
from mplpb_combined.reader import PROFILES
from mplpb_answers.pipeline import answer_query
class ScopedPrefixProfileGuard(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def test_scope_matches_do_not_authorize_prose_chain_synthesis(self):
  texts=['Mara Flint requested that Len Kay send the water chart to the west landing.','In response to request source REQUEST, Len Kay sent the water chart to the west landing.','Referring to dispatch source DISPATCH, Bea Park reported receiving the water chart at the west landing from Len Kay.']
  for i,t in zip(['REQUEST','DISPATCH','RECEIPT'],texts):ledger.write(self.root,doc_id=i,title='Record',scope=Q,body_html='<p>'+t+'</p>',external='yes',origin='human')
  result=answer_query(self.root,Q,PROFILES['external']).contract
  self.assertFalse(result['claims']);self.assertFalse(result['answer_supported'])
