import json
import tempfile
import unittest
from pathlib import Path
from tools.ledger_ui import App
from tools.exploration_store import source_url

class ExplorationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name) / 'topics'
        self.app = App(topic_base=self.base)
    def tearDown(self): self.temp.cleanup()
    def make(self, name): return self.app.create_collection({'name': name})['corpus']
    def add(self, key, text='Dinosaurs lived long ago.'):
        return self.app.import_source({'corpus': key, 'title': 'Dinosaurs', 'url': 'https://example.org/dinosaurs', 'text': text})

    def test_collections_isolate_sources_and_restore_sessions(self):
        first, second = self.make('Fossils'), self.make('Computers')
        self.add(first)
        self.assertEqual(self.app.query({'corpus':first, 'question':'Dinosaurs'})['reader']['kind'], 'return')
        self.assertEqual(self.app.query({'corpus':second, 'question':'Dinosaurs'})['reader']['kind'], 'not_in_corpus')
        turn = self.app.chat({'corpus':first, 'message':'remember museum'})
        restored = App(topic_base=self.base)
        self.assertEqual(restored.resume_chat({'session':turn['session']})['notes'], ['museum'])
        self.assertEqual(restored.page(first, self.app.inventory(first,'internal')['pages'][0]['path'],'internal')['title'], 'Dinosaurs')

    def test_source_conflicts_and_html_are_data_not_instructions(self):
        key = self.make('Animals'); self.add(key, '<script>alert(1)</script> Dinosaurs are animals.')
        self.add(key, 'Dinosaurs have fossil evidence.')
        pages = self.app.inventory(key,'internal')['pages']
        self.assertEqual(len(pages), 2)
        self.assertEqual(sum(p['eligible'] for p in pages), 1)
        captures = self.app.collections.entries()[key]['captures']
        source = self.app.collections.path(key) / 'captures' / captures[0]['id'] / 'source.bin'
        source.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'source bytes differ'): self.app.root(key)
        blocked = next(c for c in self.app.state()['corpora'] if c['key'] == key)
        self.assertEqual(blocked['eligible'], 0)
        self.assertIn('blocked', blocked['label'])

    def test_reset_only_selected_collection_and_retains_archive(self):
        first, second = self.make('One'), self.make('Two'); self.add(first); self.add(second)
        a = self.app.chat({'corpus':first, 'message':'remember first'})
        b = self.app.chat({'corpus':second, 'message':'remember second'})
        self.app.reset_collection({'corpus':first})
        self.assertNotIn(first, self.app.collections.entries())
        self.assertEqual(self.app.resume_chat({'session':b['session']})['notes'], ['second'])
        with self.assertRaises(ValueError): self.app.resume_chat({'session':a['session']})
        self.assertTrue(list((self.base.parent/'collections/archives').glob('*')))

    def test_bulk_clear_some_then_all_retains_archived_chats(self):
        first,second,third=[self.make(n) for n in ('One','Two','Three')]
        a=self.app.chat({'corpus':first,'message':'remember first'})
        b=self.app.chat({'corpus':third,'message':'remember third'})
        result=self.app.reset_collections({'corpora':[first,second]})
        self.assertEqual(result['count'],2)
        self.assertEqual(set(self.app.collections.entries()),{third})
        self.assertEqual(self.app.resume_chat({'session':b['session']})['notes'],['third'])
        archives=list((self.base.parent/'collections/archives').glob('*/reset-metadata.json'))
        self.assertTrue(any(a['session'] in json.loads(p.read_text())['content']['sessions'] for p in archives))
        self.app.reset_collections({'corpora':list(self.app.collections.entries())})
        self.assertEqual(self.app.collections.entries(),{})
        self.assertIn('studio',self.app.roots())

    def test_bulk_clear_invalid_selection_changes_nothing(self):
        key=self.make('One')
        turn=self.app.chat({'corpus':key,'message':'remember retained'})
        for keys in ([key,'studio'],[key,key],[],None):
            with self.assertRaises(ValueError):self.app.reset_collections({'corpora':keys})
        self.assertIn(key,self.app.collections.entries())
        self.assertEqual(self.app.resume_chat({'session':turn['session']})['notes'],['retained'])

    def test_bulk_clear_registry_failure_restores_every_collection_and_chat(self):
        from unittest.mock import patch
        first,second=self.make('One'),self.make('Two')
        turn=self.app.chat({'corpus':first,'message':'remember retained'})
        with patch.object(self.app.collections,'save',side_effect=OSError('write blocked')):
            with self.assertRaises(OSError):self.app.reset_collections({'corpora':[first,second]})
        self.assertEqual(set(self.app.collections.entries()),{first,second})
        self.assertTrue(self.app.collections.path(first).is_dir())
        self.assertTrue(self.app.collections.path(second).is_dir())
        self.assertEqual(self.app.resume_chat({'session':turn['session']})['notes'],['retained'])

    def test_same_title_from_two_sites_keeps_both_sources(self):
        key = self.make('Dinosaurs'); self.add(key)
        self.app.import_source({'corpus':key,'title':'Dinosaurs','url':'https://other.example/dinosaurs','text':'A second separate dinosaur source.'})
        self.assertEqual(sum(p['eligible'] for p in self.app.inventory(key,'internal')['pages']),2)
        self.assertEqual(self.app.query({'corpus':key,'question':'Dinosaurs'})['reader']['kind'],'ambiguous')

    def test_private_urls_inventory_injection_and_index_tamper_refuse(self):
        for url in ['file:///tmp/data','https://127.0.0.1/a','https://user:pass@example.org','http://example.org','https://localhost','https://10.0.0.1']:
            with self.assertRaises(ValueError): source_url(url)
        key = self.make('One'); self.add(key)
        path = self.app.collections.index
        data = json.loads(path.read_text()); data['content'][key]['name']='tamper'; path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'index integrity'): self.app.collections.entries()
