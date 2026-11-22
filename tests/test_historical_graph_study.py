"""Protect the graph study's record scope and evidence measurements."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_combined.ledger import write
from test_tools.historical_graph_study import discovery, visible


class HistoricalGraphStudyTests(unittest.TestCase):
    def test_record_hint_changes_only_discovery_and_ignores_unavailable_ids(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for ident, body in [('TOPIC-A', 'The harbor authority opened the gate in June.'),
                                ('TOPIC-B', 'The harbor authority inspected the warehouse.')]:
                write(root, doc_id=ident, title=ident, scope='harbor study', body=body)
            question = 'What did the harbor authority inspect?'
            base, guided, selected, fields = discovery(root, question, ['TOPIC-B', 'ABSENT-9'])
            self.assertEqual(selected, {'TOPIC-B'})
            self.assertEqual(fields, set())
            self.assertEqual({p['source_id'] for p in guided['passages']}, {'TOPIC-B'})
            self.assertEqual({p['source_id'] for p in base['passages']}, {'TOPIC-A', 'TOPIC-B'})
            anchor = [{'source_id': 'TOPIC-A', 'quote': 'opened the gate'}]
            self.assertEqual(visible(anchor, base), 1)
            self.assertEqual(visible(anchor, guided), 0)
            base, guided, selected, _ = discovery(root, question, ['ABSENT-9'])
            self.assertEqual(base, guided)
            self.assertFalse(selected)
