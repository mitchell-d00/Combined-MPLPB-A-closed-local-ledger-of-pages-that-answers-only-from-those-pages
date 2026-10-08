import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.topic_chat_sources import TopicStore
from tools import wiki_live_eval as W
from tools.ledger_ui import App


def response(title='Cat', revision=100, text="'''Cat''' is a synthetic source.", date='2026-10-08T12:00:00Z'):
    sha = hashlib.sha1(text.encode()).hexdigest()
    raw = json.dumps({'query': {'pages': {'1': {'title': title, 'pageid': 1,
                'revisions': [{'revid': revision, 'timestamp': date,
                              'slots': {'main': {'*': text, 'sha1': sha, 'contentmodel': 'wikitext'}}}]}}}}).encode()
    return raw, {'url': W.request_url(W.APIS['simple'], [title]), 'retrieved_at': '2026-10-08T12:01:00+00:00', 'http_status': 200}


class TopicImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = TopicStore(Path(self.temp.name) / 'topics')

    def tearDown(self):
        self.temp.cleanup()

    def fetch(self, **kw):
        with patch.object(W, 'request', return_value=response(**kw)):
            return self.store.import_title(kw.get('title', 'Cat'))

    def test_import_preserves_pins_and_multiple_topics_in_one_corpus(self):
        first = self.fetch()
        raw = (self.store.base / first['capture'] / 'response.json').read_bytes()
        self.fetch(title='Dog', text="'''Dog''' is a synthetic source.")
        root = self.store.root()
        from mplpb_combined import ledger as L, reader as R
        self.assertEqual(len(L.Ledger(root).servable()), 2)
        self.assertEqual(R.answer(root, 'Cat').kind, R.RETURN)
        self.assertNotEqual(R.answer(root, 'Cat Dog').kind, R.RETURN)
        self.assertEqual((self.store.base / first['capture'] / 'response.json').read_bytes(), raw)
        self.assertEqual(len(self.store.history()['captures']), 2)

    def test_same_revision_conflict_archives_and_blocks_even_if_flag_deleted(self):
        self.fetch(); old_head = (self.store.base / 'head.json').read_bytes()
        with self.assertRaises(ValueError):
            self.fetch(text="'''Cat''' is different bytes.")
        self.assertEqual((self.store.base / 'head.json').read_bytes(), old_head)
        self.assertEqual(len(self.store.history()['captures']), 2)
        with self.assertRaises(ValueError):
            self.store.root()
        (self.store.base / 'blocked.json').unlink()
        with self.assertRaises(ValueError):
            self.store.root()
        self.fetch(revision=101, date='2026-10-08T12:02:00Z')
        self.assertTrue(self.store.root().is_dir())

    def test_older_revision_does_not_lead(self):
        self.fetch(revision=101)
        before = (self.store.base / 'head.json').read_bytes()
        with self.assertRaises(ValueError):
            self.fetch(revision=100)
        self.assertEqual((self.store.base / 'head.json').read_bytes(), before)

    def test_tampered_source_and_local_payload_stop_serving(self):
        item = self.fetch()
        source = self.store.base / item['capture'] / 'response.json'
        source.write_bytes(b'{}')
        with self.assertRaises(ValueError):
            self.store.root()

    def test_redirect_uses_canonical_title_and_chat_import_follows_context(self):
        app = App(topic_base=self.store.base)
        with patch.object(W, 'request', return_value=response(title='Cat')):
            result = app.chat(dict(corpus='canned', message='import Cats'))
        self.assertEqual(result['corpus'], 'topics')
        self.assertEqual(result['response']['context']['title'], 'Cat')
        follow = app.chat(dict(corpus='topics', session=result['session'], message='what is it?'))
        self.assertEqual(follow['response']['reader']['id'], result['response']['context']['id'])
        self.assertTrue(app.export_chat({'session': result['session']})['chain_intact'])

    def test_external_import_retains_source_but_withholds_body_and_context(self):
        app = App(topic_base=self.store.base)
        with patch.object(W, 'request', return_value=response()):
            result = app.chat(dict(corpus='canned', profile='external', message='import Cat'))
        self.assertEqual(result['response']['kind'], 'import')
        self.assertIsNone(result['response']['context'])
        self.assertEqual(result['response']['sources'], [])
        self.assertEqual(app.query(dict(corpus='topics', profile='external', question='Cat'))['reader']['kind'], 'not_in_corpus')

    def test_failed_fetch_creates_no_head_and_does_not_score(self):
        with patch.object(W, 'request', side_effect=W.SourceUnavailable(429, '37')):
            with self.assertRaises(W.SourceUnavailable):
                self.store.import_title('Cat')
        self.assertIsNone(self.store.head())

    def test_search_results_are_plain_suggestions(self):
        payload = {'query': {'search': [{'title': 'Cat', 'pageid': 1, 'snippet': '<span>cat</span>'}]}}
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, limit): return json.dumps(payload).encode()
        with patch('urllib.request.urlopen', return_value=Reply()) as request:
            data = self.store.search('cat')
        self.assertEqual(data['results'][0]['snippet'], 'cat')
        self.assertIn('not local evidence', data['notice'])
        self.assertIsNone(self.store.head())
        self.assertIn('list=search', request.call_args.args[0].full_url)
        with self.assertRaises(ValueError):
            self.store.search('cat', 'http://localhost')
