"""Reject corrupted recovered-positive certificates before accepting a gain."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import verify_bounded_repair as original
from tools.verify_bounded_reported_content import HOME, reported_match


class BoundedReportAuditTests(unittest.TestCase):
    def test_full_witness_and_tampering_controls(self):
        key = json.loads((HOME / 'positive-witness-key.json').read_text())[0]
        result = json.loads((HOME / 'target-readback/run' / key['id'] / 'result.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            packets = original.unpack_inputs(original.PACKETS, Path(directory))
            folder = packets / 'packets' / key['id']
            self.assertTrue(reported_match(folder, result, key))
            for field, value in [('reporter', 'Wrong Person'), ('author', 'Wrong Person'),
                                 ('inner_negative', True), ('outer_negative', True),
                                 ('conditions', ['If permission is granted']),
                                 ('source_writer_or_unknown', 'Wrong Person'),
                                 ('completion_established', True),
                                 ('historical_truth_independently_verified', True)]:
                with self.subTest(field=field):
                    changed = copy.deepcopy(result)
                    changed['answer']['claims'][0]['proposition'][field] = value
                    self.assertFalse(reported_match(folder, changed, key))
            for mutation in ['qualifiers', 'canonical', 'original', 'missing']:
                with self.subTest(mutation=mutation):
                    changed = copy.deepcopy(result);claim = changed['answer']['claims'][0]
                    if mutation == 'qualifiers':claim['qualifiers'] = []
                    elif mutation == 'canonical':claim['citations'][0]['body_end'] -= 1
                    elif mutation == 'original':claim['citations'][0]['original_witness']['start_byte'] += 1
                    else:changed['answer']['missing'] = ['Unresolved obligation']
                    self.assertFalse(reported_match(folder, changed, key))


if __name__ == '__main__':unittest.main()
