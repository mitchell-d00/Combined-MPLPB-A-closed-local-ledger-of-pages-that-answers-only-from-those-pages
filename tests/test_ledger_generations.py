"""Process termination at every publication checkpoint; no power-loss claim."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_work import classing,ledger_generations as gen


@unittest.skipUnless(os.name=='posix','Atomic pointer publisher requires POSIX')
class GenerationTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name);self.ledger=self.root/'original';self.store=self.root/'store'
        write(self.ledger,doc_id='OLD-1',title='Old',scope='old record',body='Owner: Alice')
        self.old=gen.initialize(self.ledger,self.store)['generation']
        self.dump=self.root/'dump';self.dump.mkdir()
        (self.dump/'a.txt').write_text('Message-ID: NEW-1\nOwner: Bob\n\nA complete new record.')
        self.review=classing.propose(self.dump,auto_accept_clean=True)

    def test_native_reader_accepts_pointer_and_delivery_rules(self):
        result=gen.build(self.review,self.dump,self.store)
        for profile in ('lab','internal','external'):
            old=answer_query(self.store/'current','What is owner for record OLD-1?',profile=PROFILES[profile]).contract
            new=answer_query(self.store/'current','What is owner for record NEW-1?',profile=PROFILES[profile]).contract
            self.assertTrue(old['answer_supported'])
            self.assertEqual(new['answer_supported'],profile!='external')
        self.assertEqual(result['parent'],self.old)
        self.assertEqual(gen.validate_generation(self.store,self.old)[0].name,'ledger')
        self.assertTrue((self.ledger/'old-1.html').exists())

    def test_termination_never_publishes_a_partial_generation(self):
        review=self.root/'review.json';review.write_text(json.dumps(self.review))
        program='''import json,os,sys
from mplpb_work import ledger_generations as g
g._checkpoint=lambda step: os._exit(73) if step==sys.argv[4] else None
g.build(json.load(open(sys.argv[1])),sys.argv[2],sys.argv[3])
'''
        for step in gen.STEPS:
            with self.subTest(step=step):
                gen.recover(self.store,self.old)
                p=subprocess.run([sys.executable,'-c',program,str(review),str(self.dump),str(self.store),step],
                                 stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
                self.assertEqual(p.returncode,73,p.stderr.decode())
                ident,ledger,_=gen.current(self.store)
                expected_new=step in {'pointer_replaced','store_synced'}
                self.assertEqual(ident!=self.old,expected_new)
                result=answer_query(self.store/'current','What is owner for record NEW-1?').contract
                self.assertEqual(result['answer_supported'],expected_new)
                self.assertFalse(gen.inspect(self.store)['automatic_recovery_performed'])
                # Dead writer locks are released by the OS; recovery needs no TTL wait.
                gen.recover(self.store,self.old)

    def test_generation_tampering_is_refused_not_recovered_by_similarity(self):
        _,ledger,_=gen.current(self.store)
        p=ledger/'old-1.html';p.write_text(p.read_text().replace('Alice','Mallory'))
        with self.assertRaisesRegex(ValueError,'bytes changed'):gen.current(self.store)
        self.assertIsNone(gen.inspect(self.store)['current'])

    def test_pointer_escape_and_missing_pointer_fail_closed(self):
        (self.store/'current').unlink()
        self.assertIsNone(gen.inspect(self.store)['current'])
        os.symlink('../original',self.store/'current')
        with self.assertRaisesRegex(ValueError,'escapes'):gen.current(self.store)


if __name__=='__main__':unittest.main()
