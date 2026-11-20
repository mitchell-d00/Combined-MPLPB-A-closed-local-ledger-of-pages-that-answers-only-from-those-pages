"""Checks for the D4 generator and custody boundary."""
import tempfile
from pathlib import Path
import unittest

from tools import d4
from tools import dpercent as D
from tools import dpercent_weaknesses as W


class D4Tests(unittest.TestCase):
    def test_every_focus_class_has_expected_polarity_and_witnesses(self):
        dice = D.Dice(521)
        for number, family in enumerate(d4.FOCUS, 1):
            with self.subTest(family=family):
                case, docs, key = d4.material(number, family, dice)
                self.assertNotIn('expected', case)
                self.assertEqual(len(case['sources']), len(docs))
                self.assertEqual(key['expected'], 'answer' if family in d4.ANSWERS else 'refuse')
                self.assertEqual(bool(key['required_witnesses']), family in d4.ANSWERS)
                for ident, witnesses in key['required_witnesses'].items():
                    _, raw = docs[int(ident.split('-')[1])-1]
                    self.assertTrue(all(witness in raw.decode().replace('\r\n', '\n') for witness in witnesses))

    def test_mixed_study_is_deterministic_and_retains_all_legacy_families(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            one = d4.prepare(root/'public-a', root/'private-a', count=155, seed=320, shard_size=40)
            two = d4.prepare(root/'public-b', root/'private-b', count=155, seed=320, shard_size=40)
            self.assertEqual(one, two)
            self.assertEqual(set(one['family_counts']), set(W.FAMILIES) | set(d4.FOCUS))
            self.assertEqual(D.files(root/'public-a'), D.files(root/'public-b'))
            self.assertFalse(any(path.name in {'key.json', 'dice.json'} for path in (root/'public-a').rglob('*')))
            for shard in one['shards']:
                D.verify(root/'public-a'/shard['name'], root/'private-a'/shard['name'])

    def test_packet_tampering_and_custody_overlap_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                d4.prepare(root/'public', root/'public'/'private', count=1)
            d4.prepare(root/'public', root/'private', count=1)
            packet = root/'public'/'shard-0001'
            casefile = next(packet.rglob('case.json'))
            casefile.write_text('{}\n')
            with self.assertRaises(ValueError):
                D.verify(packet, root/'private'/'shard-0001')
