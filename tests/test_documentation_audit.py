import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tools.audit_documentation import audit


class DocumentationAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.names = ['README.md', 'history.md']
        self.write('README.md', '# Guide\n\nLast reviewed: 2026-11-02.\n')
        self.write('history.md', 'Original 2020 measurement\n')
        self.write('tests/check.py', 'pass\n')
        self.write('tools/reproduce.py', 'pass\n')
        for folder in ('evaluation/experiment', 'killtest'):
            (self.root / folder).mkdir(parents=True)
        self.catalog = {'schema': 'documentation-review-v1', 'reviewed_on': '2026-11-02', 'inspected_revision': 'fixture', 'documents': {
            'README.md': {'classification': 'current', 'reason': 'Active guide', 'reviewed_on': '2026-11-02'},
            'history.md': {'classification': 'historical', 'reason': 'Frozen run', 'sha256': hashlib.sha256((self.root / 'history.md').read_bytes()).hexdigest()}}}
        self.registry = {'schema': 'result-test-index-v1', 'reviewed_on': '2026-11-02', 'families': [
            {'family': name, 'artifacts': path, 'tests': ['tests/check.py'], 'runners': ['tools/reproduce.py'], 'scope': 'Fixture only', 'measurement_status': 'Historical, not rerun'}
            for name, path in [('root', 'evaluation'), ('killtest', 'killtest'), ('experiment', 'evaluation/experiment')]]}
        self.save()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def save(self):
        self.write('docs/documentation.json', json.dumps(self.catalog))
        self.write('docs/results.json', json.dumps(self.registry))

    def check(self):
        return audit(self.root, self.names, as_of='2026-11-02')

    def test_current_review_does_not_redate_history(self):
        self.assertEqual(self.check()['evaluation_families'], 3)
        self.write('history.md', 'Original 2020 measurement\nReviewed today\n')
        with self.assertRaisesRegex(ValueError, 'Historical/vendor bytes changed'):
            self.check()

    def test_stale_or_duplicate_marker_is_rejected(self):
        for body in ['Last reviewed: 2026-10-31.\n', 'Last reviewed: 2026-11-02.\nLast reviewed: 2026-11-02.\n']:
            self.write('README.md', body)
            with self.assertRaisesRegex(ValueError, 'review marker'):
                self.check()

    def test_new_result_and_missing_test_require_coverage(self):
        (self.root / 'tests/check.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing result/test'):
            self.check()
        self.write('tests/check.py', 'pass\n')
        (self.root / 'evaluation/unindexed').mkdir()
        with self.assertRaisesRegex(ValueError, 'Unindexed'):
            self.check()

    def test_unclassified_docs_and_broken_current_links(self):
        self.names.append('new.md')
        with self.assertRaisesRegex(ValueError, 'Unclassified'):
            self.check()
        self.names.pop()
        self.write('README.md', 'Last reviewed: 2026-11-02.\n[missing](absent.md)\n')
        with self.assertRaisesRegex(ValueError, 'Broken current guide'):
            self.check()

    def test_extracted_inventory_uses_pinned_manifest(self):
        self.write('handoff/manifest.json', json.dumps({'files': {p: '' for p in self.names}}))
        self.write('HANDOFF.md', 'Last reviewed: 2026-11-02.\n')
        self.catalog['documents']['HANDOFF.md'] = copy.deepcopy(self.catalog['documents']['README.md'])
        self.save()
        self.assertEqual(audit(self.root)['documents'], 3)
