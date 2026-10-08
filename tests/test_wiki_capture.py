"""Capture integrity failures must stop before retrieval or live scoring."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import wiki_live_eval as W


class WikiCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.snapshot = self.root / 'capture'
        self.payload = {'query': {'pages': {
            '1': {'pageid': 1, 'title': 'Cat', 'extract': 'A feline animal.',
                  'revisions': [{'revid': 11, 'timestamp': '2026-01-01T00:00:00Z'}]},
            '2': {'pageid': 2, 'title': 'Dog', 'extract': 'A canine animal.',
                  'revisions': [{'revid': 22, 'timestamp': '2026-01-01T00:00:00Z'}]}}}}
        self.raw = json.dumps(self.payload, indent=1).encode()
        self.metadata = {'retrieved_at': '2026-01-01T00:00:00Z', 'http_status': 200,
                         'url': W.request_url(W.APIS['simple'], ['Cat', 'Dog'])}
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)):
            W.capture(self.snapshot, spec={'fetched': ['Cat', 'Dog'], 'absent': ['Violin']})

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self):
        return json.loads((self.snapshot / 'manifest.json').read_text())

    def replace_manifest(self, manifest):
        (self.snapshot / 'manifest.json').write_text(json.dumps(manifest))

    def assert_stops_locally(self):
        with patch.object(W, 'request') as network, patch.object(W.R, 'answer') as reader:
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertTrue(result['errors'])
        network.assert_not_called()
        reader.assert_not_called()
        return result

    def test_exact_response_and_unknown_sealed_policy(self):
        self.assertEqual((self.snapshot / 'response.json').read_bytes(), self.raw)
        for recs in W.L.Ledger(self.snapshot / 'corpus').by_id.values():
            self.assertTrue(recs[0].intact)
            self.assertEqual(recs[0].fields['source-authorship'], 'unknown')
            self.assertEqual(recs[0].fields['external'], 'no')
            self.assertEqual(recs[0].origin, 'machine')

    def test_existing_capture_cannot_be_overwritten(self):
        with patch.object(W, 'request') as network:
            with self.assertRaises(FileExistsError):
                W.capture(self.snapshot)
            network.assert_not_called()
        self.assertEqual((self.snapshot / 'response.json').read_bytes(), self.raw)

    def test_matching_live_payload_scores_delivery_and_retrieval(self):
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)):
            result = W.check(self.snapshot)
        self.assertTrue(result['scored'], result['errors'])
        self.assertEqual(result['failures'], 0)
        self.assertEqual(len(result['rows']), 8)
        self.assertEqual(result['verification'], 'live')
        self.assertFalse(result['independence_verified'])

    def test_same_revision_changed_extract_stops_before_reader(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['extract'] = 'A changed feline animal.'
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)), \
                patch.object(W.R, 'answer') as reader:
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertIn('live payload changed', ' '.join(result['errors']))
        reader.assert_not_called()

    def test_unchanged_extract_changed_payload_stops(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['pageid'] = 99
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)), \
                patch.object(W.R, 'answer') as reader:
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        reader.assert_not_called()

    def test_missing_payload_pin_cannot_be_fabricated(self):
        manifest = self.manifest()
        del manifest['pages'][0]['payload_sha256']
        self.replace_manifest(manifest)
        self.assert_stops_locally()

    def test_stored_response_tamper_stops(self):
        with (self.snapshot / 'response.json').open('ab') as out:
            out.write(b' ')
        self.assert_stops_locally()

    def test_complete_local_page_tamper_stops(self):
        page = self.snapshot / 'corpus' / self.manifest()['pages'][0]['path']
        page.write_text(page.read_text().replace('feline', 'forged'))
        self.assert_stops_locally()

    def test_extra_local_page_stops(self):
        (self.snapshot / 'corpus' / 'extra.html').write_text('<p>Unexpected page</p>')
        self.assert_stops_locally()

    def test_resealed_body_and_updated_page_pin_still_require_source_binding(self):
        from mplpb_combined.record import render_page
        manifest = self.manifest()
        entry = manifest['pages'][0]
        rec = W.L.Ledger(self.snapshot / 'corpus').by_id[entry['id']][0]
        page = self.snapshot / 'corpus' / entry['path']
        page.write_text(render_page(rec.fields, rec.title, rec.body_html.replace('feline', 'forged')))
        entry['served_page_sha256'] = W.digest(page.read_bytes())
        self.replace_manifest(manifest)
        result = self.assert_stops_locally()
        self.assertIn('recorded source transformation', ' '.join(result['errors']))

    def test_resealed_human_claim_still_fails_import_contract(self):
        from mplpb_combined.record import render_page
        manifest = self.manifest()
        entry = manifest['pages'][0]
        rec = W.L.Ledger(self.snapshot / 'corpus').by_id[entry['id']][0]
        fields = dict(rec.fields)
        fields['origin'] = 'human'
        page = self.snapshot / 'corpus' / entry['path']
        page.write_text(render_page(fields, rec.title, rec.body_html))
        entry['served_page_sha256'] = W.digest(page.read_bytes())
        self.replace_manifest(manifest)
        result = self.assert_stops_locally()
        self.assertIn('metadata differs', ' '.join(result['errors']))

    def test_code_pin_mismatch_stops(self):
        manifest = self.manifest()
        manifest['code']['checker_sha256'] = '0' * 64
        self.replace_manifest(manifest)
        self.assert_stops_locally()

    def test_historical_manifest_stays_unscorable(self):
        self.replace_manifest({'pages': self.manifest()['pages']})
        self.assert_stops_locally()

    def test_offline_replay_is_not_claimed_live(self):
        with patch.object(W, 'request') as network:
            result = W.check(self.snapshot, live=False)
        network.assert_not_called()
        self.assertTrue(result['scored'])
        self.assertEqual(result['verification'], 'offline replay only')
        self.assertEqual(result['live'], [])

    def test_reports_do_not_overwrite_previous_evidence(self):
        report = self.root / 'report.json'
        W.check(self.snapshot, live=False, report=report)
        before = report.read_bytes()
        with self.assertRaises(FileExistsError):
            W.check(self.snapshot, live=False, report=report)
        self.assertEqual(report.read_bytes(), before)
