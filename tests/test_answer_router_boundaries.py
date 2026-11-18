"""Delivery boundaries apply to unofficial inspection as well as strict proof."""
import json
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write,withdraw
from mplpb_work import answer_router as router

class RouterBoundaryTests(unittest.TestCase):
    def test_external_and_not_for_bodies_never_reach_unofficial_reader(self):
        for kwargs,profile,q in (({'external':'no'},'external','Explain archive secret'),
                                 ({'not_for':'secret'},'internal','Explain archive secret')):
            with self.subTest(profile=profile),tempfile.TemporaryDirectory() as root:
                write(root,doc_id='SECRET-1',title='Archive',scope='archive',body='CONFIDENTIAL-NATIVE-BODY archive secret',**kwargs)
                calls=[]
                r=router.route(q,root,profile=profile,try_rewrites=False,reader=lambda *a:calls.append(a))
                self.assertNotIn('CONFIDENTIAL-NATIVE-BODY',json.dumps(r));self.assertEqual(calls,[])

    def test_external_dump_is_not_an_eligibility_bypass(self):
        with tempfile.TemporaryDirectory() as root:
            dump=Path(root)/'dump';dump.mkdir();(dump/'a.txt').write_text('Message-ID: SECRET-1\n\nSecret cargo arrived.')
            r=router.route('Explain secret cargo',None,dump,profile='external')
            self.assertIsNone(r['unofficial'])

    def test_reader_cannot_add_an_unquoted_claim(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='DOC-1',title='Archive',scope='archive',body='The archive contains an ordinary note.')
            r=router.route('Explain archive',root,try_rewrites=False,reader=lambda *a:'A war was caused by Alice.')
            self.assertNotIn('A war was caused',json.dumps(r));self.assertFalse(r['unofficial']['answer_supported'])

    def test_withdrawal_during_reader_hook_discards_old_passages(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='DOC-1',title='Archive',scope='archive',body='The archive contains an ordinary note.')
            def reader(*args):withdraw(root,'DOC-1');return 'The archive contains an ordinary note.'
            with self.assertRaisesRegex(ValueError,'changed'):
                router.route('Explain archive',root,try_rewrites=False,reader=reader)
