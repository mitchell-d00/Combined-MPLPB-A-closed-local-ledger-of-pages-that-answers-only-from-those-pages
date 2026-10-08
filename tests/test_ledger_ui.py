import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
from tools.ledger_ui import App, handler


class LedgerUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.topic_temp = tempfile.TemporaryDirectory()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler(App(topic_base=cls.topic_temp.name)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.topic_temp.cleanup()

    def request(self, path, data=None, headers=None):
        headers = dict(headers or {})
        if data is not None:
            headers.setdefault('Content-Type', 'application/json')
        req = Request(self.base + path, data=None if data is None else json.dumps(data).encode(), headers=headers)
        try:
            response = urlopen(req, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            body = response.read()
            return response.status, body, response.headers

    def ask(self, corpus, question, profile='internal'):
        status, body, _ = self.request('/api/query', dict(corpus=corpus, question=question, profile=profile))
        self.assertEqual(status, 200)
        return json.loads(body)

    def test_canned_pair_and_single_title(self):
        result = self.ask('canned', 'Phrynomedusa vanzolinii Hyundai Engineering and Construction')
        self.assertEqual(result['reader']['kind'], 'ambiguous')
        self.assertEqual(len(result['gate']['sources']), 2)
        self.assertFalse(result['gate']['answer_synthesized'])
        self.assertFalse(result['live_verified_by_this_query'])
        self.assertEqual(self.ask('canned', 'Phrynomedusa vanzolinii')['reader']['id'], 'CANNED-0001')

    def test_unknown_and_clarification(self):
        self.assertEqual(self.ask('canned', 'zebra')['reader']['kind'], 'not_in_corpus')
        self.assertEqual(len(self.ask('dogs', 'dog')['reader']['clarification']['choices']), 3)

    def test_external_profile_cannot_read_withheld_source(self):
        result = self.ask('canned', 'Phrynomedusa vanzolinii', 'external')
        self.assertFalse(result['gate']['sources'])
        query = urlencode(dict(corpus='canned', path='canned-0001.html', profile='external'))
        self.assertEqual(self.request('/api/page?' + query)[0], 400)
        query = urlencode(dict(corpus='canned', path='canned-0001.html', profile='internal'))
        status, body, _ = self.request('/api/page?' + query)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['id'], 'CANNED-0001')

    def test_no_arbitrary_file_read_or_unknown_corpus(self):
        query = urlencode(dict(corpus='canned', path='../../README.md'))
        self.assertEqual(self.request('/api/page?' + query)[0], 400)
        self.assertEqual(self.request('/api/query', dict(corpus='../', question='cat'))[0], 400)

    def test_foreign_host_and_origin_rejected(self):
        self.assertEqual(self.request('/api/state', headers={'Host': 'attacker.example'})[0], 403)
        self.assertEqual(self.request('/api/query', dict(corpus='canned', question='cat'),
                                      {'Origin': 'https://attacker.example'})[0], 403)

    def test_invalid_requests_fail_without_mutation(self):
        for data in ([], {}, dict(corpus='canned', question='x' * 4001),
                     dict(corpus='canned', question='cat', profile='unknown')):
            self.assertEqual(self.request('/api/query', data)[0], 400)
        self.assertEqual(self.request('/api/query', {}, {'Content-Type': 'text/plain'})[0], 415)

    def test_history_reports_retained_head_without_live_verification(self):
        status, body, _ = self.request('/api/history')
        self.assertEqual(status, 200)
        history = json.loads(body)
        self.assertTrue(history['head'])
        active = [v for v in history['versions'] if v['active']]
        self.assertEqual(len(active), 1)
        self.assertIsInstance(active[0]['code_matches_now'], bool)
        self.assertTrue(active[0]['pages'][0]['wikitext_sha256'])
        self.assertIn('no live request', history['notice'])

    def test_assets_and_supplied_experiment_are_available(self):
        for path in ('/', '/index.html', '/api/experiment'):
            status, body, headers = self.request(path)
            self.assertEqual(status, 200)
            self.assertTrue(body)
            self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        self.assertEqual(self.request('/missing')[0], 404)
        status, body, headers = self.request('/')
        import re, hashlib, base64
        scripts = re.findall(rb'<script>(.*?)</script>', body, re.DOTALL)
        self.assertEqual(len(scripts), 1)
        pin = base64.b64encode(hashlib.sha256(scripts[0].replace(b'\r\n', b'\n').replace(b'\r', b'\n')).digest()).decode()
        script_policy = headers['Content-Security-Policy'].split('script-src ')[1].split(';')[0]
        self.assertEqual(script_policy, "'sha256-" + pin + "'")
        self.assertNotIn(b'<script src=', body)

    def test_inventory_keeps_retired_records_without_serving_them(self):
        status, body, _ = self.request('/api/inventory?corpus=studio&profile=internal')
        self.assertEqual(status, 200)
        data = json.loads(body)
        retired = [p for p in data['pages'] if p['status'] == 'retired']
        self.assertEqual(len(retired), 4)
        self.assertTrue(all(not p['eligible'] for p in retired))
        self.assertTrue(all('text' not in p for p in data['pages']))
        self.assertEqual(data['eligible'], sum(p['eligible'] for p in data['pages']))
        path = retired[0]['path']
        self.assertEqual(self.request('/api/page?' + urlencode(dict(corpus='studio', path=path)))[0], 400)

    def test_inventory_uses_profile_and_detects_altered_pages(self):
        import tempfile, shutil
        from pathlib import Path
        from tools.ledger_ui import ROOT
        status, body, _ = self.request('/api/inventory?corpus=canned&profile=external')
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data['eligible'], 0)
        self.assertTrue(all('external' in p['reason'] for p in data['pages']))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'custom'
            shutil.copytree(ROOT / 'examples/patch-canned', root)
            target = root / 'canned-0001.html'
            target.write_text(target.read_text().replace('Synthetic reader fixture', 'Altered reader fixture'))
            app = App(root)
            pages = app.inventory('custom', 'internal')['pages']
            altered = next(p for p in pages if p['id'] == 'CANNED-0001')
            self.assertFalse(altered['eligible'])
            self.assertFalse(altered['intact'])
            self.assertEqual(altered['reason'], 'altered')
            with self.assertRaises(ValueError):
                app.page('custom', altered['path'], 'internal')


    def test_chat_import_followup_and_export_use_real_endpoints(self):
        from unittest.mock import patch
        from tests.test_topic_chat_sources import response
        from tools import wiki_live_eval as W
        with patch.object(W, 'request', return_value=response()):
            status, body, _ = self.request('/api/chat', dict(corpus='canned', message='import Cat'))
        self.assertEqual(status, 200)
        imported = json.loads(body)
        status, body, _ = self.request('/api/chat', dict(corpus='topics', session=imported['session'], message='what is it?'))
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['response']['reader']['title'], 'Cat')
        status, body, _ = self.request('/api/chat/export', dict(session=imported['session']))
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)['chain_intact'])
        self.assertEqual(len(json.loads(body)['turns']), 2)
        status, body, _ = self.request('/api/chat/resume', dict(session=imported['session']))
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)['chain_intact'])
        self.assertEqual(self.request('/api/chat/reset', dict(session=imported['session']))[0], 200)
        self.assertEqual(self.request('/api/chat/export', dict(session=imported['session']))[0], 400)

    def test_chat_relation_and_creator_are_separate_from_unknown_claims(self):
        status, body, _ = self.request('/api/chat', dict(corpus='logic', message='relate Dungeons and Dragons -> game'))
        self.assertEqual(status, 200)
        relation = json.loads(body)['response']['relations'][0]
        self.assertEqual(relation['status'], 'rule_inference')
        self.assertEqual(len(relation['premises']), 2)
        status, body, _ = self.request('/api/chat', dict(corpus='logic', message='relate Dungeons and Dragons -> budget'))
        self.assertEqual(json.loads(body)['response']['kind'], 'unknown_relation')
        status, body, _ = self.request('/api/chat', dict(corpus='logic', message='who made you?'))
        self.assertEqual(json.loads(body)['response']['reader']['id'], 'SELF-0003')
