"""Fail-closed worker isolation and actual Linux namespace integration."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import historical_study as study
from tools import study_sandbox as sandbox


class StudySandboxTests(unittest.TestCase):
    def test_missing_isolator_never_falls_back_to_direct_execution(self):
        with patch.object(sandbox.shutil,'which',return_value=None),patch.object(study,'execute') as direct:
            with self.assertRaises(ValueError):sandbox.execute_sandboxed('/unused')
            direct.assert_not_called()

    def test_failed_isolation_never_accepts_worker_output(self):
        with patch.object(sandbox.subprocess,'run',return_value=type('Result',(),{'returncode':1})()):
            with self.assertRaises(ValueError):sandbox.invoke(['unavailable'])


@unittest.skipUnless(sys.platform=='linux','Linux isolation not supported on this platform')
class LinuxStudySandboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        if not shutil.which('bwrap'):
            if os.environ.get('MPLPB_REQUIRE_SANDBOX')=='1':self.fail('Required bubblewrap isolator is missing')
            self.skipTest('Bubblewrap unavailable; isolation not tested')
        self.root=Path(self.tmp.name)
        self.code=self.root/'code';self.inputs=self.root/'inputs';self.outputs=self.root/'outputs'
        for path in (self.code,self.inputs,self.outputs):path.mkdir()
        probe=[shutil.which('bwrap'),'--unshare-all','--die-with-parent']
        for path in ('/usr','/lib','/lib64'):
            if Path(path).exists():probe+=['--ro-bind',path,path]
        probe+=['--','/usr/bin/true']
        try:sandbox.invoke(probe)
        except ValueError:
            if os.environ.get('MPLPB_REQUIRE_SANDBOX')=='1':self.fail('Required Linux namespaces are unavailable')
            self.skipTest('Host denies required namespaces; execution remains fail-closed')

    def test_worker_cannot_read_gold_write_inputs_or_use_host_network(self):
        secret=self.root/'private-gold.txt';secret.write_text('private test value')
        (self.inputs/'corpus.json').write_text('public')
        program='''import os,socket
from pathlib import Path
assert not Path(HOST_SECRET).exists()
assert not Path('/study/private').exists()
assert 'MPLPB_SANDBOX_TEST_SECRET' not in os.environ
for path in ('/app/changed','/study/corpus.json'):
 try:Path(path).write_text('forbidden')
 except OSError:pass
 else:raise AssertionError('read-only input was writable')
try:socket.create_connection(('1.1.1.1',443),timeout=0.3)
except OSError:pass
else:raise AssertionError('network access succeeded')
Path('/scratch/allowed').write_text('scratch')
Path('/output/probe.json').write_text('{"isolation_verified":true}')
'''.replace('HOST_SECRET',repr(str(secret)))
        with patch.dict(os.environ,{'MPLPB_SANDBOX_TEST_SECRET':'must not reach worker'}):
            sandbox.invoke(sandbox.command(shutil.which('bwrap'),self.code,self.inputs,self.outputs,program))
        self.assertEqual((self.inputs/'corpus.json').read_text(),'public')
        self.assertTrue(json.loads((self.outputs/'probe.json').read_text())['isolation_verified'])

    def test_real_study_runs_without_mounting_gold(self):
        directory=self.root/'study';study.prepare(directory)
        questions=self.root/'questions.json'
        study.save(questions,{'cases':[{'id':'Q1','question':'Trace Local Web declared relations','required_source_ids':['ORIGINAL-0001']}]})
        study.seal(directory,questions)
        result=sandbox.execute_sandboxed(directory)
        receipt=study.read(directory/'sandbox-receipt.json')
        self.assertEqual(result['status'],'awaiting_external_review')
        self.assertFalse(receipt['private_gold_mounted'])
        self.assertTrue(receipt['network_namespace_isolated'])
        self.assertFalse(receipt['host_administrator_isolated'])
        self.assertEqual(receipt['run_sha256'],study.digest(result))


if __name__=='__main__':unittest.main()
