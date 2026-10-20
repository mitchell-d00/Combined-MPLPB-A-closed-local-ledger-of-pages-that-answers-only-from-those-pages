"""Tests for deterministic candidate release evidence, independent of network."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.release_evidence import GATES, create, verify


class ReleaseEvidenceTests(unittest.TestCase):
    COMMIT = 'a' * 40
    TREE = 'b' * 40

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        source = b'PK\x03\x04example-archive'
        digest = hashlib.sha256(source).hexdigest()
        (self.folder / 'commit.sha').write_text(self.COMMIT + '\n')
        (self.folder / 'tree.sha').write_text(self.TREE + '\n')
        (self.folder / 'mplpb-repository.zip').write_bytes(source)
        (self.folder / 'mplpb-repository.zip.sha256').write_text(digest + '  mplpb-repository.zip\n')
        (self.folder / 'mplpb-candidate-preview.html').write_text('<!doctype html><title>MPLPB</title>')
        lines = ['Git commit packaged: ' + self.COMMIT, 'ZIP SHA-256: ' + digest]
        lines.extend(GATES)
        (self.folder / 'validation-report.txt').write_text('\n'.join(lines) + '\n')

    def test_create_and_verify_exact_candidate(self):
        evidence = create(self.folder, self.COMMIT)
        self.assertEqual(evidence['commit_sha'], self.COMMIT)
        self.assertEqual(evidence['status'], 'candidate_checks_passed_not_deployed')
        self.assertEqual(verify(self.folder, self.COMMIT), evidence)
        self.assertEqual(json.loads((self.folder / 'release-evidence.json').read_text()), evidence)

    def test_rejects_wrong_pr_head(self):
        with self.assertRaisesRegex(ValueError, 'exact candidate'):
            create(self.folder, 'c' * 40)

    def test_rejects_archive_checksum_mismatch(self):
        (self.folder / 'mplpb-repository.zip').write_bytes(b'modified')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            create(self.folder, self.COMMIT)

    def test_rejects_missing_gate(self):
        report = self.folder / 'validation-report.txt'
        report.write_text(report.read_text().replace(GATES[3], 'Chromium published-live baseline: FAIL'))
        with self.assertRaisesRegex(ValueError, 'passed gate'):
            create(self.folder, self.COMMIT)

    def test_rejects_tampering_after_manifest_creation(self):
        create(self.folder, self.COMMIT)
        (self.folder / 'mplpb-candidate-preview.html').write_text('replacement')
        with self.assertRaisesRegex(ValueError, 'differs'):
            verify(self.folder, self.COMMIT)

    def test_rejects_empty_or_symlinked_preview(self):
        preview = self.folder / 'mplpb-candidate-preview.html'
        preview.unlink()
        preview.write_bytes(b'')
        with self.assertRaisesRegex(ValueError, 'empty'):
            create(self.folder, self.COMMIT)
        preview.unlink()
        preview.symlink_to(self.folder / 'mplpb-repository.zip')
        with self.assertRaisesRegex(ValueError, 'symlinked'):
            create(self.folder, self.COMMIT)

    def test_rejects_forged_manifest_fields(self):
        create(self.folder, self.COMMIT)
        target = self.folder / 'release-evidence.json'
        evidence = json.loads(target.read_text())
        evidence['status'] = 'deployed_and_verified'
        target.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, 'differs'):
            verify(self.folder, self.COMMIT)


if __name__ == '__main__':
    unittest.main()
