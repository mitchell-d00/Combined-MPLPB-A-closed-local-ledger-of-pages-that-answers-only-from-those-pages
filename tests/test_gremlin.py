"""Adversarial maintenance-map checks using tiny disposable repositories."""
import json
from pathlib import Path
import tempfile
import unittest

from test_tools import gremlin as G


class GremlinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.put('product/main.py', 'engine = 1\n')
        self.put('tests/smoke.py', 'test = 1\n')
        self.put('test_tools/run.py', 'runner = 1\n')
        for id in G.DEPARTMENTS:
            self.put('docs/departments/' + id + '.md', id + '\n')
        self.write_json('docs/departments/components.json', {
            'schema': 'department-navigation-v1', 'exact_overrides': {},
            'tool_name_prefix_overrides': {},
            'root_components': {'product': 'reader', 'docs': 'delivery-operations',
                                'HANDOFF.md': 'delivery-operations', 'handoff': 'delivery-operations',
                                'tests': 'testing-evaluation', 'test_tools': 'testing-evaluation'}})
        self.write_json('docs/results.json', {'schema': 'result-test-index-v1', 'families': [
            {'family': 'tiny', 'artifacts': 'tests', 'tests': ['tests/smoke.py'],
             'runners': ['test_tools/run.py'], 'scope': 'Frozen tiny scope',
             'measurement_status': 'NOT_RUN', 'implementation_departments': ['reader']}]})
        self.registry = {'schema': 'gremlin-registry-v1', 'reviewed_on': '2026-11-27',
                         'inspected_revision': 'a' * 40,
                         'departments': {id: {'label': id, 'scopes': ['project'],
                                              'status': 'mixed', 'note': 'Declared scope'} for id in G.DEPARTMENTS},
                         'components': [
                             {'id': 'engine', 'label': 'Engine', 'paths': ['product'],
                              'scopes': ['product'], 'status': 'lab', 'evidence': ['product/main.py']},
                             {'id': 'future', 'label': 'Proposed adapter', 'paths': [],
                              'scopes': ['experiment'], 'status': 'proposed', 'evidence': ['product/main.py']}],
                         'relations': [
                             {'from': 'engine', 'to': 'ledger', 'kind': 'depends_on', 'basis': 'source',
                              'evidence': ['product/main.py'], 'note': 'Test relation'},
                             {'from': 'future', 'to': 'ledger', 'kind': 'depends_on', 'basis': 'proposal',
                              'evidence': ['product/main.py'], 'note': 'Unestablished dependency'}],
                         'open_work': [{'id': 'remember', 'component': 'engine', 'question': 'What is missing?',
                                        'revisit_when': 'Engine changes', 'evidence': ['product/main.py']}]}
        self.save_registry()

    def put(self, name, content):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def write_json(self, name, data):
        self.put(name, json.dumps(data, indent=2) + '\n')

    def save_registry(self):
        self.write_json(G.REGISTRY, self.registry)

    def names(self):
        return sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file())

    def build(self):
        return G.build(self.root, self.names())

    def test_deterministic_render_and_no_source_mutation(self):
        before = {n: (self.root / n).read_bytes() for n in self.names()}
        first = self.build()
        self.assertEqual(first, self.build())
        self.assertEqual(G.render(first), G.render(self.build()))
        self.assertEqual(before, {n: (self.root / n).read_bytes() for n in self.names()})
        self.assertEqual(next(n for n in first['nodes'] if n['id'] == 'study:tiny')['status_from_index'], 'NOT_RUN')

    def test_changed_source_is_rejected_as_stale(self):
        # Include the generated names before building to avoid testing a path-list difference alone.
        for name in G.OUTPUTS:
            self.put(name, '')
        report = self.build()
        self.put(G.OUTPUTS[0], json.dumps(report, indent=2, ensure_ascii=False) + '\n')
        self.put(G.OUTPUTS[1], G.render(report))
        G.check_outputs(self.root, self.build())
        self.put('product/main.py', 'engine = 2\n')
        with self.assertRaisesRegex(ValueError, 'Stale Gremlin'):
            G.check_outputs(self.root, self.build())

    def test_added_and_renamed_paths_change_inventory(self):
        before = self.build()
        self.put('product/extra.py', 'engine = 1\n')
        after = self.build()
        self.assertNotEqual(before['pathset_sha256'], after['pathset_sha256'])
        (self.root / 'product/extra.py').rename(self.root / 'product/renamed.py')
        self.assertNotEqual(after['pathset_sha256'], self.build()['pathset_sha256'])

    def test_new_unowned_root_is_rejected(self):
        self.put('unknown/component.py', 'x = 1\n')
        with self.assertRaisesRegex(ValueError, 'Unmapped ownership'):
            self.build()

    def test_unknown_endpoint_and_duplicate_id_are_rejected(self):
        self.registry['relations'][0]['to'] = 'nonexistent'
        self.save_registry()
        with self.assertRaisesRegex(ValueError, 'unknown component'):
            self.build()
        self.registry['relations'][0]['to'] = 'ledger'
        self.registry['components'].append(dict(self.registry['components'][0]))
        self.save_registry()
        with self.assertRaisesRegex(ValueError, 'Duplicate component'):
            self.build()

    def test_missing_evidence_and_unsafe_paths_are_rejected(self):
        self.registry['components'][0]['evidence'] = ['product/missing.py']
        self.save_registry()
        with self.assertRaisesRegex(ValueError, 'Evidence must name tracked'):
            self.build()
        for name in ('../outside', '/etc/passwd', '.git/config', 'product/../outside'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                G.relative(name)

    def test_proposed_dependency_never_becomes_established_impact(self):
        report = G.impact(self.build(), ['product/main.py'], self.root)
        self.assertIn('engine', report['direct'])
        # Touching ledger's department should reach engine, not the proposed future adapter.
        self.put('ledger/main.py', 'ledger = 1\n')
        ownership = json.loads((self.root / 'docs/departments/components.json').read_text())
        ownership['root_components']['ledger'] = 'ledger'
        self.write_json('docs/departments/components.json', ownership)
        report = G.impact(self.build(), ['ledger/main.py'], self.root)
        self.assertIn('engine', report['potential_dependents'])
        self.assertNotIn('future', report['potential_dependents'])
        self.assertEqual(G.impact(self.build(), ['unknown/new.py'], self.root)['unmapped_paths'], ['unknown/new.py'])

    def test_extracted_handoff_path_list_reproduces_explicit_inventory(self):
        self.put('HANDOFF.md', 'Generated coordination\n')
        self.write_json('handoff/manifest.json', {'files': {n: 'unused' for n in self.names()}})
        names = self.names()
        self.write_json('handoff/manifest.json', {'files': {n: 'unused' for n in names if n not in {'HANDOFF.md', 'handoff/manifest.json'}}})
        self.assertEqual(G.build(self.root), G.build(self.root, names))

    def test_external_symlink_cannot_supply_evidence(self):
        self.put('outside.txt', 'Do not traverse')
        (self.root / 'product/main.py').unlink()
        (self.root / 'product/main.py').symlink_to(self.root / 'outside.txt')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            G.safe(self.root, 'product/main.py')


if __name__ == '__main__':
    unittest.main()
