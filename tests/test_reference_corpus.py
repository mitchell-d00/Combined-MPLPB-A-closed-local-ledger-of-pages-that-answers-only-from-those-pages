"""Reference corpus admission, growth and tamper-control tests."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from mplpb_combined.ledger import Ledger, write, revise
from mplpb_combined.reader import PROFILES
from mplpb_answers.support import supported_answer
from tools import build_reference_corpus as C


class ReferenceCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.probes = C.load()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.audit = C.evaluate(cls.root / "releases", cls.catalog, cls.probes)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_catalog_and_source_admission(self):
        checks = C.validate_catalog(self.catalog, self.probes)
        self.assertEqual(checks['facts'], 73)
        self.assertEqual(checks['positive'], 73)
        self.assertEqual(checks['negative'], 20)
        self.assertFalse(checks['human_ratified'])
        self.assertFalse(checks['external_bytes_verified'])

    def test_growth_tracks_real_refusals_to_supported(self):
        metrics = [r['metrics'] for r in self.audit['versions']]
        self.assertEqual([m['correct_supported'] for m in metrics], [0, 23, 48, 73])
        self.assertEqual([m['ambiguous'] for m in metrics], [0, 0, 0, 0])
        self.assertEqual([m['wrong_returns'] for m in metrics], [0, 0, 0, 0])
        self.assertEqual([m['correct_refusals'] for m in metrics], [20] * 4)
        self.assertEqual([len(r['delta']['refusal_to_supported'])
                          for r in self.audit['versions']], [0, 23, 25, 25])

    def test_snapshot_has_pinned_deeper_lineage_and_seals(self):
        root = self.root / "releases/v0.3.0/ledger"
        ledger = Ledger(root)
        self.assertEqual(len([r for r in ledger.servable()
                              if r.id.startswith('REF-')]), 73)
        for fact in (r for r in ledger.servable() if r.id.startswith('REF-')):
            self.assertTrue(fact.intact)
            self.assertEqual(ledger.depth(fact), 2)
            self.assertFalse(fact.ratified_by)
            self.assertEqual(fact.origin, 'machine')
            self.assertEqual(fact.fields.get('external'), 'no')
            self.assertEqual(len(fact.derived_from), 1)
            parent = ledger.resolve(fact.derived_from[0])
            self.assertEqual(parent.kind, 'source')
            self.assertEqual(parent.hash_actual, fact.derived_from[0].hash)

    def test_default_internal_and_external_do_not_promote_machine_drafts(self):
        root = self.root / "releases/v0.3.0/ledger"
        for profile in (PROFILES['internal'], PROFILES['external']):
            for question in ("What is noun?", "What is solar system planet count?"):
                with self.subTest(profile=profile.name, question=question):
                    result = supported_answer(root, question, profile)
                    self.assertNotEqual(result.kind, 'return')

    def test_source_scope_duplicate_and_missing_citation_block_pre_admission(self):
        base = self.catalog
        scenarios = []
        dup = copy.deepcopy(base)
        dup['facts'][1]['subject'] = dup['facts'][0]['subject']
        scenarios.append(dup)
        origin = copy.deepcopy(base)
        origin['facts'][0]['source'] = 'unregistered-source'
        scenarios.append(origin)
        conditional = copy.deepcopy(base)
        conditional['facts'][0]['value'] = 'possibly a noun if copied'
        conditional['facts'][0]['statement'] = 'The noun is possibly a noun if copied.'
        scenarios.append(conditional)
        unapproved = copy.deepcopy(base)
        unapproved['facts'][0]['status'] = 'human_ratified'
        scenarios.append(unapproved)
        for scenario in scenarios:
            with self.subTest(case=scenario['facts'][0]['subject']):
                with self.assertRaises(ValueError):
                    C.validate_catalog(scenario, self.probes)

    def test_tampering_and_ambiguity_controls_on_separate_copies(self):
        root = self.root / "releases/v0.3.0/ledger"
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "ledger"
            shutil.copytree(root, copied)
            question = "What is noun?"
            baseline = supported_answer(copied, question, PROFILES['lab'])
            self.assertEqual(baseline.kind, 'return')
            write(copied, doc_id="ALT-0001", title="Synthetic conflict control",
                  scope="noun competing view", when_to_use=question,
                  body="The noun is a competing synthetic assertion.",
                  derived_from=["SRC-0001"], origin="machine",
                  external="no", source_authorship="declared-machine",
                  when="2026-11-01T00:00Z")
            collision = supported_answer(copied, question, PROFILES['lab'])
            self.assertEqual(collision.kind, 'ambiguous')
            self.assertEqual(collision.text, '')
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "ledger"
            shutil.copytree(root, copied)
            victim = copied / "ref-0001.html"
            self.assertTrue(victim.exists())
            victim.write_text(victim.read_text().replace("a word class", "an unsealed class"))
            self.assertNotEqual(supported_answer(copied, "What is noun?",
                                                 PROFILES['lab']).kind, 'return')
            self.assertTrue(Ledger(copied).quarantined())

    def test_revision_is_new_id_and_prior_page_remains_in_history(self):
        root = self.root / "releases/v0.3.0/ledger"
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "ledger"
            shutil.copytree(root, copied)
            successor = revise(copied, "REF-0001", new_id="REF-9001",
                               origin="machine",
                               body="The noun is a revised synthetic category.",
                               when="2026-11-01T00:01Z",
                               note="Synthetic revision rehearsal")
            self.assertTrue(successor.intact)
            self.assertEqual(len(successor.supersedes), 1)
            self.assertEqual(successor.supersedes[0].id, "REF-0001")
            ledger = Ledger(copied)
            old = ledger.by_id["REF-0001"][0]
            self.assertEqual(ledger.effective_status(old), "retired")
            self.assertTrue(old.intact)
            res = supported_answer(copied, "What is noun?", PROFILES['lab'])
            self.assertEqual(res.kind, 'return')
            self.assertEqual(res.record.id, "REF-9001")
            self.assertEqual(res.text, "The noun is a revised synthetic category.")


if __name__ == '__main__':
    unittest.main()
