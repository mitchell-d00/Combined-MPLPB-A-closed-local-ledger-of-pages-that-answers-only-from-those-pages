"""Capture integrity failures must stop before retrieval or live scoring."""
import copy
import json
import hashlib
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
        for page in self.payload['query']['pages'].values():
            rev = page['revisions'][0]
            rev['sha1'] = hashlib.sha1(page['extract'].encode()).hexdigest()
            rev['slots'] = {'main': {'contentmodel': 'wikitext', '*': page['extract'],
                                     'sha1': rev['sha1']}}
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

    def test_same_revision_changed_wikitext_stops_before_reader(self):
        changed = copy.deepcopy(self.payload)
        self.change_source(changed, 'A changed feline animal.')
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)), \
                patch.object(W.R, 'answer') as reader:
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertIn('revision-slot source changed', ' '.join(result['errors']))
        row = result['live'][0]
        self.assertEqual(row['expected']['revid'], row['observed']['revid'])
        self.assertTrue(row['same_revision_conflict'])
        self.assertNotEqual(row['expected']['wikitext_sha256'], row['observed']['wikitext_sha256'])
        reader.assert_not_called()

    def test_unchanged_extract_changed_payload_stops(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['pageid'] = 99
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)), \
                patch.object(W.R, 'answer') as reader:
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        reader.assert_not_called()

    def test_missing_slot_sha1_pin_cannot_be_fabricated(self):
        manifest = self.manifest()
        del manifest['pages'][0]['slot_sha1']
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
        self.change_source(changed, 'Changed source.')
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
        self.change_source(changed, 'A newly observed feline extract.')
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
        self.change_source(changed, 'Changed.')
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

    def change_source(self, payload, text, revid=None):
        rev = payload['query']['pages']['1']['revisions'][0]
        rev['slots']['main']['*'] = text
        rev['slots']['main']['sha1'] = hashlib.sha1(text.encode()).hexdigest()
        rev['sha1'] = rev['slots']['main']['sha1']
        if revid is not None:
            rev['revid'] = revid

    def changed_response(self):
        changed = copy.deepcopy(self.payload)
        self.change_source(changed, 'A changed feline animal.', revid=12)
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
        self.change_source(changed, 'Changed again.')
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

    def test_generated_extract_change_does_not_change_source_or_scored_body(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['extract'] = 'Unrelated generated intro.'
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)):
            result = W.check(self.snapshot)
        self.assertTrue(result['scored'], result['errors'])
        self.assertEqual(result['failures'], 0)
        self.assertNotIn('archive', result)
        self.assertTrue(result['renderer_observations'][0]['source_match'])
        rec = W.L.Ledger(self.snapshot / 'corpus').by_id['WIKI-0001'][0]
        self.assertIn('feline', rec.body_html)
        self.assertNotIn('Unrelated generated intro', rec.body_html)

    def test_same_revision_conflict_cannot_be_promoted_by_sync(self):
        changed = copy.deepcopy(self.payload)
        self.change_source(changed, 'A conflicting stored revision.')
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)) as network:
            result = W.sync(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertIn('archive', result)
        self.assertEqual(network.call_count, 1)
        self.assertFalse((self.root / 'head.json').exists())

    def test_wrong_advertised_slot_sha1_is_archived_incomplete_and_not_scored(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['revisions'][0]['slots']['main']['sha1'] = '0' * 40
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)):
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertIn('SHA-1 disagrees', result['live'][0]['invalid_source'])
        archive = Path(result['archive']['observed_archive'])
        self.assertTrue((archive / 'observation.json').exists())

    def test_missing_main_slot_cannot_be_scored(self):
        changed = copy.deepcopy(self.payload)
        del changed['query']['pages']['1']['revisions'][0]['slots']
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)):
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertIn('archive', result)

    def test_new_revision_id_with_unchanged_text_is_a_new_source_version(self):
        changed = copy.deepcopy(self.payload)
        changed['query']['pages']['1']['revisions'][0]['revid'] = 12
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)):
            result = W.check(self.snapshot)
        self.assertFalse(result['scored'])
        self.assertFalse(result['live'][0]['same_revision_conflict'])
        self.assertEqual(result['live'][0]['expected']['wikitext_sha256'],
                         result['live'][0]['observed']['wikitext_sha256'])

    def test_retained_wikitext_tamper_stops_before_network(self):
        path = self.snapshot / self.manifest()['pages'][0]['wikitext_path']
        path.write_bytes(path.read_bytes() + b'changed')
        self.assert_stops_locally()

    def test_main_slot_pins_and_renderer_are_retained_independently(self):
        manifest = self.manifest()
        self.assertEqual(manifest['schema'], 3)
        self.assertEqual(manifest['renderer'], W.renderer_pin())
        entry = manifest['pages'][0]
        self.assertEqual(entry['slot_sha1'], hashlib.sha1(b'A feline animal.').hexdigest())
        self.assertEqual(entry['wikitext_sha256'], W.digest(b'A feline animal.'))
        self.assertNotIn('payload_sha256', entry)
        self.assertNotIn('raw_extract_sha256', entry)
        self.assertIn('oldid=11', entry['revision_url'])

    def test_revision_request_never_requests_generated_extracts(self):
        from urllib.parse import parse_qs, urlparse
        query = parse_qs(urlparse(W.request_url(W.APIS['simple'], ['Cat'])).query)
        self.assertEqual(query['prop'], ['revisions'])
        self.assertEqual(query['rvslots'], ['main'])
        self.assertIn('slotsha1', query['rvprop'][0].split('|'))
        self.assertNotIn('explaintext', query)

    def test_local_render_is_deterministic_and_does_not_expand_templates(self):
        from tools.wiki_render import render
        text = "{{Infobox|nested={{value}}}}\n'''Cat''' is a [[feline|small feline]].<ref>Reference</ref>\n==History==\nLater section."
        self.assertEqual(render(text), 'Cat is a small feline.')
        self.assertEqual(render(text), render(text))

    def test_response_envelope_and_unpinned_metadata_do_not_move_source(self):
        changed = copy.deepcopy(self.payload)
        changed['batchcomplete'] = True
        changed['query']['pages']['1']['revisions'][0]['parentid'] = 7
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)):
            result = W.check(self.snapshot)
        self.assertTrue(result['scored'], result['errors'])
        self.assertNotIn('archive', result)

    def test_fresh_run_cannot_repin_a_known_same_revision_conflict(self):
        changed = copy.deepcopy(self.payload)
        self.change_source(changed, 'Conflicting same-revision wikitext.')
        response = json.dumps(changed).encode(), self.metadata
        with patch.object(W, 'request', return_value=response) as network, \
                patch.object(W, 'capture', wraps=self.capture_small), \
                patch.object(W.R, 'answer') as reader:
            result = W.run(self.root / 'conflict')
        self.assertFalse(result['scored'])
        self.assertEqual(network.call_count, 1)
        reader.assert_not_called()
        manifest = json.loads((self.root / 'conflict/manifest.json').read_text())
        self.assertEqual(manifest['status'], 'archived revision conflict; not scored')
        self.assertTrue(manifest['same_revision_conflicts'])

    def test_further_archive_drift_stays_in_the_same_revision_tree_root(self):
        kit = self.root / 'wiki'
        snap = kit / 'captures' / 'original'
        with patch.object(W, 'request', return_value=(self.raw, self.metadata)):
            self.capture_small(snap, W.APIS['simple'])
        with patch.object(W, 'request', return_value=self.changed_response()):
            first = W.check(snap)
        archive = Path(first['archive']['observed_archive']).resolve()
        changed = copy.deepcopy(self.payload)
        self.change_source(changed, 'A later source revision.', revid=13)
        with patch.object(W, 'request', return_value=(json.dumps(changed).encode(), self.metadata)):
            second = W.check(archive)
        successor = Path(second['archive']['observed_archive']).resolve()
        self.assertEqual(archive.parent, (kit / 'archives').resolve())
        self.assertEqual(successor.parent, archive.parent)


ORIGINAL_CAPTURE = W.capture
