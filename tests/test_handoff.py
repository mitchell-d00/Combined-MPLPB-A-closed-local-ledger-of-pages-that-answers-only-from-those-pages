import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import build_handoff as H


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        subprocess.run(['git','-C',str(self.root),'config','user.email','fixture@example.org'],check=True)
        subprocess.run(['git','-C',str(self.root),'config','user.name','Fixture'],check=True)
        (self.root/'handoff').mkdir()
        (self.root/'AGENTS.md').write_text('Build a handoff for every update.')
        self.record=dict(instruction='Fix the latest request.',scope=['Implemented a fixture'],validation=['Not yet tested'],limitations=['Synthetic'],next_steps=['Review'])
        (self.root/'handoff/update.json').write_text(json.dumps(self.record))
        (self.root/'source.py').write_text('value = 1\n')
        self.git('add','.')
        self.git('commit','-qm','Fixture')
    def git(self,*args):
        return subprocess.run(['git','-C',str(self.root),*args],check=True,capture_output=True)
    def test_freshness_staging_commit_and_extracted_zip(self):
        H.build(self.root);H.check(self.root)
        self.git('add','.');self.git('commit','-qm','Handoff')
        H.check(self.root)  # Commit identity must not create a self-reference loop.
        shutil.rmtree(self.root/'.git')
        H.check(self.root)
        (self.root/'source.py').write_text('value = 2\n')
        with self.assertRaisesRegex(ValueError,'stale'):H.check(self.root)
    def test_changed_instruction_and_tampered_handoff(self):
        H.build(self.root)
        self.record['instruction']='New user instruction.'
        (self.root/'handoff/update.json').write_text(json.dumps(self.record))
        with self.assertRaises(ValueError):H.check(self.root)
        H.build(self.root)
        self.assertIn('New user instruction.',(self.root/'HANDOFF.md').read_text())
        (self.root/'HANDOFF.md').write_text('Invented success')
        with self.assertRaises(ValueError):H.check(self.root)
    def test_new_tracked_file_invalidates_and_no_secret_collection(self):
        H.build(self.root)
        (self.root/'untracked-secret').write_text('private fixture')
        H.check(self.root)
        (self.root/'new.py').write_text('pass\n');self.git('add','new.py')
        with self.assertRaises(ValueError):H.check(self.root)
        H.build(self.root)
        self.assertNotIn('untracked-secret',H.check(self.root)['files'])
    def test_extracted_inventory_cannot_escape_root(self):
        H.build(self.root);shutil.rmtree(self.root/'.git')
        path=self.root/'handoff/manifest.json';m=json.loads(path.read_text());m['files']['../elsewhere']='bad';path.write_text(json.dumps(m))
        with self.assertRaises(ValueError):H.check(self.root)
