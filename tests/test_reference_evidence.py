"""The published evidence must not silently omit or alter inputs/pages."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from tools import verify_reference_evidence as E


class ReferenceEvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.bundle=Path(self.tmp.name)/'bundle'
        shutil.copytree(E.BUNDLE,self.bundle)
    def test_changed_gold_pin_is_rejected(self):
        path=self.bundle/'run.json';data=json.loads(path.read_text())
        data['frozen_inputs']['reference_corpus/probes.v1.json']='0'*64
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'Frozen input differs'):E.verify(self.bundle)
    def test_changed_source_page_is_rejected(self):
        path=self.bundle/'releases/v0.3.0/ledger/ref-0001.html'
        path.write_text(path.read_text().replace('a word class','a different class'))
        with self.assertRaisesRegex(ValueError,'inventory differs'):E.verify(self.bundle)
    def test_unlisted_competing_material_is_not_silently_ignored(self):
        path=self.bundle/'releases/v0.3.0/ledger/unlisted.html'
        path.write_text('An extra candidate must not be omitted from the evidence inventory.')
        with self.assertRaisesRegex(ValueError,'inventory differs'):E.verify(self.bundle)

    def test_changed_human_readable_results_are_rejected(self):
        path=self.bundle/'results.csv'
        path.write_text(path.read_text().replace('What is noun?', 'A changed question', 1))
        with self.assertRaisesRegex(ValueError,'inventory differs'):E.verify(self.bundle)
