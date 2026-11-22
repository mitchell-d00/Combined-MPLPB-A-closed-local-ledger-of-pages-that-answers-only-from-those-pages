"""SQLite storage, deterministic paths, and ambiguity checks for synonym lookup."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from test_tools.graph_synonym_index import GraphSynonymIndex, build, load_catalog
from test_tools.synonym_index import CATALOG, SynonymIndex


def catalog(links, extra=False):
    fields = {'Catalog Number': ['catalogue number']}
    if extra:
        fields['Shelf Code'] = ['shelf label']
    return {'schema': 'mplpb-synonym-index-v1', 'collections': {
        'museum': {'records': {'ITEM-4': ['display fish']}, 'fields': fields,
                   'links': {'fields': links}},
        'elsewhere': {'records': {'ITEM-5': ['display fish']}, 'fields': fields},
    }}


class GraphSynonymIndexTests(unittest.TestCase):
    def lookup(self, data, query):
        with closing(sqlite3.connect(':memory:')) as db:
            load_catalog(db, data)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            return GraphSynonymIndex(db).lookup('museum', query)

    def test_persistent_directed_path_and_collection_scope(self):
        data = catalog({'inventory code': ['catalog identifier'],
                        'catalog identifier': ['catalogue number'],
                        'catalogue number': ['inventory code']})
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'graph.sqlite'
            build(path, data)
            with self.assertRaises(FileExistsError):
                build(path, data)
            with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
                graph = GraphSynonymIndex(db)
                result = graph.lookup('museum', 'Inventory code for the display fish?')
                self.assertEqual(result['status'], 'candidate')
                self.assertEqual(result['records'], {'ITEM-4': ['display fish']})
                self.assertEqual(result['paths']['fields']['Catalog Number'][0]['phrases'],
                                 ['inventory code', 'catalog identifier', 'catalogue number'])
                self.assertEqual(graph.lookup('elsewhere', 'Inventory code for the display fish?')['status'],
                                 'incomplete')
                self.assertNotIn('answer_supported', result)

    def test_competing_targets_and_directed_edges(self):
        data = catalog({'identifier': ['shelf label', 'catalogue number'],
                        'only earlier label': ['catalogue number']}, extra=True)
        result = self.lookup(data, 'Identifier for the display fish?')
        self.assertEqual(result['status'], 'ambiguous')
        self.assertEqual(list(result['fields']), ['Catalog Number', 'Shelf Code'])
        result = self.lookup(data, 'Catalogue number for the display fish?')
        self.assertEqual(result['status'], 'candidate')
        self.assertEqual(result['paths']['fields']['Catalog Number'][0]['phrases'], ['catalogue number'])

    def test_budget_withholds_partial_graph_results(self):
        data = catalog({**{f'path {i}': [f'path {i+1}'] for i in range(6)},
                        'path 6': ['catalogue number']})
        result = self.lookup(data, 'Path 0 for the display fish?')
        self.assertEqual(result['status'], 'limited')
        self.assertEqual(result['records'], {})
        self.assertEqual(result['fields'], {})

    def test_builder_discards_a_failed_new_database(self):
        data = catalog({'wrong alias type': 'catalogue number'})
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'graph.sqlite'
            with self.assertRaisesRegex(ValueError, 'lists of strings'):
                build(path, data)
            self.assertFalse(path.exists())

    def test_original_catalog_lookup_parity(self):
        data = json.loads(CATALOG.read_bytes())
        flat = SynonymIndex(data)
        with closing(sqlite3.connect(':memory:')) as db:
            load_catalog(db, data)
            graph = GraphSynonymIndex(db)
            question = 'What catalogue number belongs to the coelacanth display specimen?'
            result = graph.lookup('coelacanth', question)
            self.assertEqual({k: v for k, v in result.items() if k != 'paths'},
                             flat.lookup('coelacanth', question))
