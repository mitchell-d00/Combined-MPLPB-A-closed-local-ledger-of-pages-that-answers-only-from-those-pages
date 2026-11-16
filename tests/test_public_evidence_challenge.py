"""The public challenge must preserve gaps, measurements and inspectable inputs."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.evaluate_public_evidence import run, SUITE


class PublicEvidenceChallengeTests(unittest.TestCase):
    def test_all_52_public_requirements_pass_without_a_false_supported_bridge(self):
        report=run()
        failures=[{'id':r['id'],'expected':r['expected'],'actual':r['actual'],'status':r['status']}
                  for r in report['rows'] if r['status']!='pass']
        self.assertEqual(failures,[])
        self.assertEqual(report['summary'],{'pass':52})
        self.assertEqual(report['false_supported_bridges'],0)

    def test_manifest_is_frozen_and_all_eight_families_are_public(self):
        raw=SUITE.read_bytes()
        declared=(SUITE.parent/'public-cases.sha256').read_text().split()[0]
        self.assertEqual(hashlib.sha256(raw).hexdigest(),declared)
        cases=json.loads(raw)['cases']
        self.assertEqual(len({c['family'] for c in cases}),8)
        self.assertEqual(len(cases),52)
        self.assertEqual(len({c['id'] for c in cases}),len(cases))
        self.assertTrue(all(c['requirement'] and c['expected'] and c['score'] for c in cases))

    def test_missing_capability_is_not_relabelled_as_pass_or_unknown_human_measurement(self):
        manifest=json.loads(SUITE.read_text())
        selected={'event-candidates','burden-metrics','event-occurrences'}
        manifest['cases']=[c for c in manifest['cases'] if c['id'] in selected]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'cases.json';path.write_text(json.dumps(manifest))
            with patch('tools.evaluate_public_evidence.inspect_events',None):
                report=run(path)
        rows={r['id']:r for r in report['rows']}
        self.assertEqual(rows['event-candidates']['status'],'gap')
        self.assertIsNone(rows['event-candidates']['observed']['event_candidate_schema'])
        self.assertEqual(len(rows['event-occurrences']['observed']['source_occurrences']),2)
        measurement=rows['burden-metrics']['measurement']
        self.assertIsNone(measurement['human_labeling_seconds'])
        self.assertIsNone(measurement['human_correction_seconds'])
        self.assertGreater(measurement['source_text_read_bytes'],0)
        self.assertGreater(measurement['peak_python_allocated_bytes'],0)
        self.assertEqual(report['configuration']['hidden_questions'],0)


if __name__=='__main__':unittest.main()
