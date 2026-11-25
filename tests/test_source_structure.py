"""Non-authoritative structure must retain native policy, pins and byte budgets."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from mplpb_combined import ledger
from mplpb_combined.reader import PROFILES
from mplpb_answers import source_structure as structure
Q='Who wrote the tidal index?'
class SourceStructureGuards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def record(self,body):return ledger.write(self.root,doc_id='SOURCE',title='Archive',scope=Q,body_html=body,origin='human',external='yes',when='2026-11-25T00:00Z')
 def test_oversized_previous_proposal_rejected(self):
  self.record('<p>'+('Filler '*280+'.</p><p>')*64+'End.</p>')
  packet=json.loads((Path(__file__).resolve().parents[1]/'evaluation/cryptid/nessie/safety-guards/oversized-proposal-v1.json').read_text())
  self.assertGreater(len(json.dumps(packet)),64000)
  self.assertEqual(structure.verify_proposals(self.root,Q,packet)['status'],'rejected')
 def test_unknown_policy_and_identity_labels_rejected(self):
  r=self.record('<p>Mara Flint wrote the tidal index.</p>');p=structure.propose(r);p['private']=False;p['famous']=True
  self.assertEqual(structure.verify_proposals(self.root,Q,p)['status'],'rejected')
 def test_scope_matching_no_prose_profile_cannot_validate_role_tree(self):
  r=self.record('<p>Mara Flint wrote the tidal index.</p>')
  self.assertEqual(structure.verify_proposals(self.root,Q,structure.propose(r),PROFILES['external'])['status'],'rejected')
 def test_late_withdrawal_discards_structure_certificate(self):
  r=self.record('<p>Mara Flint wrote the tidal index.</p>');p=structure.propose(r);old=structure.propose
  def revoke(record):result=old(record);ledger.withdraw(self.root,'SOURCE');return result
  with patch.object(structure,'propose',revoke):result=structure.verify_proposals(self.root,Q,p)
  self.assertEqual(result['status'],'rejected');self.assertFalse(result['source_support_established'])
 def test_folded_and_duplicate_headers_do_not_gain_boundary_authority(self):
  for text in ['From: Owen Kestrel\nTo: Vera Moss\n If approved\n','From: Owen Kestrel\nTo: Vera Moss\nFrom: Ivo Calder\n']:
   from types import SimpleNamespace
   self.assertFalse(structure.closed_header(SimpleNamespace(body_html='<pre>'+text+'</pre><p>Mara Flint wrote the tidal index.</p>')))
