"""Machine-readable snapshot must obey MPLPB's actual external profile."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.agent_snapshot import BUNDLED, export_public_ledger
from tools.ledger_ui import App

class AgentSnapshotTests(unittest.TestCase):
    def test_export_only_current_external_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'mplpb-public-ledger.json'
            exported = export_public_ledger(filename)
            self.assertEqual(json.loads(filename.read_text()), exported)
            self.assertEqual(exported['profile'], 'external')
            self.assertEqual([c['key'] for c in exported['corpora']], list(BUNDLED))
            app = App()
            for corpus in exported['corpora']:
                key = corpus['key']
                inventory = app.inventory(key, 'external')
                eligible_paths = {p['path'] for p in inventory['pages'] if p['eligible']}
                self.assertEqual({p['path'] for p in corpus['pages']}, eligible_paths)
                for page in corpus['pages']:
                    self.assertEqual(page['text'], app.page(key, page['path'], 'external')['text'])
