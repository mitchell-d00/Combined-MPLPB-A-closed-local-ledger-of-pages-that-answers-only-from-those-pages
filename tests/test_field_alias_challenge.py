"""Holdout protocol invariants, not independent semantic judgments."""
from pathlib import Path
import tempfile
import unittest
from tools import dpercent as D
from tools.field_alias_challenge import prepare


class AliasChallengeTests(unittest.TestCase):
    def test_deterministic_seal_and_key_separation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = prepare(root/'public-a', root/'key-a', 30, 2769)
            b = prepare(root/'public-b', root/'key-b', 30, 2769)
            self.assertEqual(a, b)
            D.verify(root/'public-a', root/'key-a')
            self.assertNotIn('key.json', D.files(root/'public-a'))
            keys = D.read(root/'key-a/key.json')['cases']
            self.assertEqual(sum(k['expected']=='answer' for k in keys), 8)
            self.assertEqual(sum(k['expected']=='refuse' for k in keys), 22)
            for p in (root/'public-a/packets').iterdir():
                case = D.read(p/'case.json')
                self.assertNotIn('expected', case)

    def test_new_structures_are_not_filtered_by_runtime_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepare(root/'public', root/'key', 240, 91237)
            keys = D.read(root/'key/key.json')['cases']
            self.assertTrue(any(k['expected']=='answer' and k['features']['question_form'] >= 4
                                for k in keys))
            p = next((root/'public/packets').rglob('leaf.txt'))
            p.write_bytes(p.read_bytes()+b'altered')
            with self.assertRaises(ValueError): D.verify(root/'public', root/'key')

    def test_invalid_counts_and_nested_custody(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in (0, 4097, True):
                with self.assertRaises(ValueError): prepare(root/'public', root/'key', n, 1)
            with self.assertRaises(ValueError): prepare(root/'public', root/'public/key', 1, 1)


if __name__ == '__main__': unittest.main()
