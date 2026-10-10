import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch
from browser import bridge as B
from tools.ledger_ui import App


class LiveAcquisitionRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_dictionary_does_not_block_enabled_wiki_for_prefixed_apple(self):
        calls = []
        async def remote(url):
            q = parse_qs(urlsplit(url).query); calls.append(q)
            if 'srsearch' in q:
                self.assertEqual(q['srsearch'], ['apple'])
                payload = {'query': {'search': [{'title': 'Apple', 'pageid': 1}]}}
            else:
                body = 'An apple is an edible fruit. Apples grow on trees.'
                payload = {'query': {'pages': {'1': {'title': 'Apple', 'pageid': 1,
                    'revisions': [{'revid': 100, 'timestamp': '2026-10-10T12:00:00Z',
                    'slots': {'main': {'*': body, 'sha1': hashlib.sha1(body.encode()).hexdigest(),
                                        'contentmodel': 'wikitext'}}}]}}}}
            return json.dumps(payload).encode(), {'url': url, 'retrieved_at': '2026-10-10T12:01:00Z', 'http_status': 200}
        with tempfile.TemporaryDirectory() as tmp, patch.object(B, 'app', App(topic_base=Path(tmp)/'topics')):
            data = {'corpus': 'logic', 'message': 'cool tell me about an apple', 'default_chat': True, 'wiki': 'english'}
            with patch.object(B, 'remote', remote):
                off = await B.dispatch('/api/chat', {**data, 'auto_wiki': False})
                self.assertEqual(calls, [])
                self.assertEqual(off['response']['authority'], 'lexical_reference')
                on = await B.dispatch('/api/chat', {**data, 'auto_wiki': True})
            self.assertEqual(on['automatic_lookup']['status'], 'captured')
            self.assertTrue(on['response']['sources'])
            self.assertNotEqual(on['response']['authority'], 'lexical_reference')
            self.assertEqual(on['response']['interpretation']['original'], data['message'])
            self.assertTrue(B.app.export_chat({'session': on['session']})['chain_intact'])

    async def test_prefixed_search_uses_async_browser_transport(self):
        async def remote(url):
            q = parse_qs(urlsplit(url).query)
            self.assertEqual(q['srsearch'], ['Moon'])
            return b'{"query":{"search":[]}}', {'url': url, 'retrieved_at': '2026-10-10T12:01:00Z', 'http_status': 200}
        with tempfile.TemporaryDirectory() as tmp, patch.object(B, 'app', App(topic_base=Path(tmp)/'topics')):
            with patch.object(B, 'remote', remote):
                r = await B.dispatch('/api/chat', {'corpus': 'logic', 'message': 'Cool, find Moon', 'wiki': 'english'})
            self.assertEqual(r['response']['kind'], 'search')

    async def test_failed_automatic_lookup_backs_off_without_changing_evidence(self):
        from unittest.mock import AsyncMock
        with tempfile.TemporaryDirectory() as tmp, patch.object(B, 'app', App(topic_base=Path(tmp)/'topics')):
            data={'corpus':'logic','message':'Tell me about unlisted zorb topic','auto_wiki':True,'wiki':'english','default_chat':True}
            with patch.object(B,'remote',AsyncMock(side_effect=ValueError('Wikipedia HTTP 429'))) as remote:
                first=await B.dispatch('/api/chat',data)
                second=await B.dispatch('/api/chat',{**data,'session':first['session']})
            self.assertEqual(remote.await_count,1)
            self.assertEqual(first['automatic_lookup']['status'],'failed')
            self.assertEqual(second['automatic_lookup']['status'],'deferred')
            self.assertEqual(B.app.collections.entries(),{})
            self.assertEqual(second['response']['sources'],[])
