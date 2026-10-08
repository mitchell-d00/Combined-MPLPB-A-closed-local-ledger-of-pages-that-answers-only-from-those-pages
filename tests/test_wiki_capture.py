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
        row = result['live'][0]
        self.assertEqual(row['expected_revid'], row['observed_revid'])
        self.assertFalse(row['extract_match'])
        self.assertNotEqual(row['expected_payload_sha256'], row['observed_payload_sha256'])
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

    def test_fresh_run_preserves_previous_capture(self):
        old_manifest = (self.snapshot / 'manifest.json').read_bytes()
        fresh = self.root / 'fresh'
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)) as network, \
                patch.object(W, 'capture', wraps=self.capture_small):
            result = W.run(fresh)
        self.assertTrue(result['scored'], result['errors'])
        self.assertEqual(result['failures'], 0)
        self.assertEqual(network.call_count, 2)
        self.assertEqual((self.snapshot / 'manifest.json').read_bytes(), old_manifest)

    def capture_small(self, dest, api):
        return ORIGINAL_CAPTURE(dest, api, {'fetched': ['Cat', 'Dog'], 'absent': ['Violin']})

    def test_fresh_run_does_not_refetch_to_hide_second_request_mismatch(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['extract'] = 'Changed source.'
        with patch.object(W, 'request', side_effect=[(self.raw, self.metadata),
                 (json.dumps(changed).encode(), self.metadata)]) as network, \
                patch.object(W, 'capture', wraps=self.capture_small), \
                patch.object(W.R, 'answer') as reader:
            result = W.run(self.root / 'changed')
        self.assertFalse(result['scored'])
        self.assertEqual(network.call_count, 2)
        reader.assert_not_called()

    def test_capture_rate_limit_is_saved_without_scoring_or_retry(self):
        report = self.root / 'limited.json'
        dest = self.root / 'limited'
        with patch.object(W, 'request', side_effect=W.SourceUnavailable(429, '60')) as network, \
                patch.object(W.R, 'answer') as reader:
            result = W.run(dest, report=report)
        self.assertFalse(result['scored'])
        self.assertFalse(dest.exists())
        self.assertEqual(result['source_failure'], {'http_status': 429, 'retry_after': '60'})
        self.assertEqual(json.loads(report.read_text()), result)
        self.assertEqual(network.call_count, 1)
        reader.assert_not_called()

    def test_check_rate_limit_is_unavailable_not_payload_drift(self):
        with patch.object(W, 'request', side_effect=W.SourceUnavailable(429)), \
                patch.object(W.R, 'answer') as reader:
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertEqual(result['verification'], 'live source unavailable')
        self.assertEqual(result['live'], [])
        reader.assert_not_called()

    def test_request_exposes_http_rate_limit_without_retry(self):
        from urllib.error import HTTPError
        error = HTTPError('https://simple.wikipedia.org/w/api.php', 429, 'Limited',
                          {'Retry-After': '60'}, None)
        with patch.object(W.urllib.request, 'urlopen', side_effect=error) as network:
            with self.assertRaises(W.SourceUnavailable) as caught:
                W.request(W.APIS['simple'], ['Cat', 'Dog'])
        self.assertEqual(caught.exception.status, 429)
        self.assertEqual(caught.exception.retry_after, '60')
        self.assertEqual(network.call_count, 1)

    def test_run_existing_capture_refuses_before_network(self):
        with patch.object(W, 'request') as network:
            with self.assertRaises(FileExistsError):
                W.run(self.snapshot)
        network.assert_not_called()

    def test_drift_archives_observed_bytes_dates_source_and_previous_link(self):
        before = {p.relative_to(self.snapshot): p.read_bytes()
                  for p in self.snapshot.rglob('*') if p.is_file()}
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['extract'] = 'A newly observed feline extract.'
        raw = json.dumps(changed).encode()
        metadata = dict(self.metadata, retrieved_at='2026-01-02T00:00:00Z')
        with patch.object(W, 'request', return_value=(raw, metadata)) as network, \
                patch.object(W.R, 'answer') as reader:
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        network.assert_called_once()
        reader.assert_not_called()
        archive = Path(result['archive']['observed_archive'])
        self.assertEqual((archive / 'response.json').read_bytes(), raw)
        manifest = json.loads((archive / 'manifest.json').read_text())
        self.assertFalse(manifest['history']['scored'])
        self.assertEqual(manifest['history']['previous_capture'], result['snapshot'])
        self.assertEqual(manifest['history']['previous_manifest_sha256'],
                         W.digest(before[Path('manifest.json')]))
        page = manifest['pages'][0]
        self.assertEqual(page['observed_at'], metadata['retrieved_at'])
        self.assertEqual(page['source_revision_at'], '2026-01-01T00:00:00Z')
        self.assertEqual(page['source_url'], 'https://simple.wikipedia.org/wiki/Cat')
        self.assertEqual(page['revid'], 11)
        self.assertEqual(W.stored_errors(archive, manifest), [])
        self.assertEqual(before, {p.relative_to(self.snapshot): p.read_bytes()
                                  for p in self.snapshot.rglob('*') if p.is_file()})

    def test_missing_live_title_is_archived_as_incomplete_observation(self):
        changed = copy.deepcopy(self.payload)
        del changed['query']['pages']['1']
        raw = json.dumps(changed).encode()
        with patch.object(W, 'request', return_value=(raw, self.metadata)):
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        archive = Path(result['archive']['observed_archive'])
        self.assertEqual((archive / 'response.json').read_bytes(), raw)
        observation = json.loads((archive / 'observation.json').read_text())
        self.assertIn('Cat', observation['incomplete'])
        self.assertFalse((archive / 'manifest.json').exists())

    def test_repeated_drift_keeps_distinct_archives_out_of_latest_capture(self):
        kit = self.root / 'wiki'
        snap = kit / 'captures' / 'original'
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['extract'] = 'Changed.'
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)):
            self.capture_small(snap, W.APIS['simple'])
        with patch.object(W, 'KIT', kit), \
                patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)):
            first = W.check(snap)
            second = W.check(snap)
            self.assertEqual(W.latest(), snap)
        self.assertNotEqual(first['archive']['observed_archive'], second['archive']['observed_archive'])
        self.assertEqual(len(list((kit / 'archives').glob('*/manifest.json'))), 2)

    def test_fresh_capture_links_previous_same_source_with_its_pins(self):
        next_snapshot = self.root / 'next'
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)):
            self.capture_small(next_snapshot, W.APIS['simple'])
        manifest = json.loads((next_snapshot / 'manifest.json').read_text())
        old = self.manifest()
        self.assertEqual(manifest['history']['previous_response_sha256'], old['response_sha256'])
        self.assertEqual(manifest['history']['previous_manifest_sha256'],
                         W.digest((self.snapshot / 'manifest.json').read_bytes()))
        self.assertEqual(manifest['history']['reason'], 'fresh capture observation')

    def test_distinct_wiki_is_separate_history_root(self):
        next_snapshot = self.root / 'english'
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)):
            self.capture_small(next_snapshot, W.APIS['english'])
        manifest = json.loads((next_snapshot / 'manifest.json').read_text())
        self.assertNotIn('history', manifest)

    def changed_response(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['extract'] = 'A changed feline animal.'
        return json.dumps(changed).encode(), dict(self.metadata, retrieved_at='2026-01-02T00:00:00Z')

    def test_sync_verifies_successor_and_moves_head_without_rewriting_old(self):
        before = (self.snapshot / 'manifest.json').read_bytes()
        response = self.changed_response()
        with patch.object(W, 'request', return_value=response) as network:
            result = W.sync(self.snapshot)
        self.assertTrue(result['scored'], result['errors'])
        self.assertEqual(result['failures'], 0)
        self.assertEqual(network.call_count, 2)
        self.assertFalse(result['transition']['previous_scored'])
        self.assertEqual(before, (self.snapshot / 'manifest.json').read_bytes())
        with patch.object(W, 'KIT', self.root):
            self.assertEqual(W.latest(), (self.root / result['head']['current']['snapshot']).resolve())
        self.assertTrue(result['head']['promoted'])

    def test_successor_rate_limit_keeps_previous_verified_head(self):
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)):
            W.check(self.snapshot)
        before = (self.root / 'head.json').read_bytes()
        with patch.object(W, 'request', side_effect=[self.changed_response(), W.SourceUnavailable(429)]):
            result = W.sync(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertEqual(before, (self.root / 'head.json').read_bytes())

    def test_offline_replay_cannot_promote_a_head(self):
        result = W.check(self.snapshot, live=False)
        self.assertTrue(result['scored'])
        self.assertNotIn('head', result)
        self.assertFalse((self.root / 'head.json').exists())

    def test_live_recheck_of_older_capture_cannot_move_head_back(self):
        with patch.object(W, 'request', return_value=self.changed_response()):
            W.sync(self.snapshot)
        before = (self.root / 'head.json').read_bytes()
        later = dict(self.metadata, retrieved_at='2026-01-03T00:00:00Z')
        with patch.object(W, 'request', return_value=(self.raw, later)):
            result = W.check(self.snapshot)
        self.assertFalse(result['head']['promoted'])
        self.assertEqual(before, (self.root / 'head.json').read_bytes())

    def test_successor_drift_does_not_loop_or_promote(self):
        response = self.changed_response()
        changed = json.loads(response[0])
        changed['query']['pages']['1']['extract'] = 'Changed again.'
        with patch.object(W, 'request', side_effect=[response,
                 (json.dumps(changed).encode(), response[1])]) as network:
            result = W.sync(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertEqual(network.call_count, 2)
        self.assertFalse((self.root / 'head.json').exists())

    def test_new_capture_links_the_verified_archived_head(self):
        response = self.changed_response()
        with patch.object(W, 'request', return_value=response):
            result = W.sync(self.snapshot)
            fresh = self.root / 'fresh'
            self.capture_small(fresh, W.APIS['simple'])
        manifest = json.loads((fresh / 'manifest.json').read_text())
        self.assertEqual(manifest['history']['previous_capture'], result['snapshot'])


ORIGINAL_CAPTURE = W.capture
