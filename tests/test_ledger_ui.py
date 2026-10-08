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
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler(App()))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

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
        for path in ('/', '/app.js', '/api/experiment'):
            status, body, headers = self.request(path)
            self.assertEqual(status, 200)
            self.assertTrue(body)
            self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        self.assertEqual(self.request('/missing')[0], 404)
