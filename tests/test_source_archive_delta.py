"""Lossless archive storage must retain exact ZIP bytes and reject wrong bases."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile
from tools.cryptid_zip_delta import encode, restore, verify


class SourceArchiveDeltaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base, self.target = self.root/'base.zip', self.root/'target.zip'
        for path, changed in [(self.base, False), (self.target, True)]:
            with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('unchanged.txt', 'source witness\n'*100)
                archive.writestr('changed.txt', 'new evidence' if changed else 'old evidence')
                if changed:
                    archive.writestr('.hidden/control', 'retained hidden file')
        self.delta = self.root/'delta.gz'

    def test_exact_round_trip_with_unchanged_changed_and_hidden_members(self):
        receipt = encode(self.base, self.target, self.delta)
        self.assertGreater(receipt['copied_byte_identical_payload_bytes'], 0)
        self.assertEqual(verify(self.base, self.delta)['status'], 'PASS')
        output = self.root/'restored.zip'
        restore(self.base, self.delta, output)
        self.assertEqual(output.read_bytes(), self.target.read_bytes())

    def test_wrong_base_never_produces_an_output(self):
        encode(self.base, self.target, self.delta)
        self.base.write_bytes(self.base.read_bytes()+b'changed')
        output = self.root/'restored.zip'
        with self.assertRaisesRegex(ValueError, 'Wrong base'):
            restore(self.base, self.delta, output)
        self.assertFalse(output.exists())

    def test_existing_outputs_are_not_overwritten(self):
        encode(self.base, self.target, self.delta)
        with self.assertRaises(FileExistsError):
            encode(self.base, self.target, self.delta)
        with self.assertRaises(FileExistsError):
            restore(self.base, self.delta, self.target)
