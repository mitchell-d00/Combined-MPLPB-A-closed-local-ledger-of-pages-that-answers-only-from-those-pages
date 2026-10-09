import json
import tempfile
import unittest
import sys
import types
import hashlib
from urllib.parse import urlsplit, parse_qs
from pathlib import Path
from unittest.mock import AsyncMock, patch
from tools.ledger_ui import App
from browser import bridge as B
from tools import wiki_live_eval as W
from tools.build_browser_runtime import build

class BrowserBridgeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = B.app
        B.app = App(topic_base=Path(self.temp.name)/'topics')

    def tearDown(self):
        B.app = self.previous
        self.temp.cleanup()

    async def test_web_capture_keeps_raw_pin_and_strips_executable_html(self):
        key = B.app.create_collection({'name':'Web sources'})['corpus']
        raw = b'<html><head><title>Bad head</title></head><body><script>evil()</script><p>Fossils show ancient life.</p></body></html>'
        response = types.SimpleNamespace(status=200, headers={'content-type':'text/html; charset=utf-8'}, bytes=AsyncMock(return_value=raw))
        fetch = AsyncMock(return_value=response)
        with patch.dict(sys.modules, {'pyodide.http':types.SimpleNamespace(pyfetch=fetch)}):
            result = await B.dispatch('/api/source/fetch', {'corpus':key,'title':'Fossils','url':'https://example.org/fossils'})
            with self.assertRaises(ValueError):
                await B.dispatch('/api/source/fetch', {'corpus':key,'title':'Private','url':'https://127.0.0.1'})
        self.assertEqual(fetch.await_count, 1)
        self.assertEqual(fetch.call_args.kwargs['redirect'],'error')
        self.assertEqual(result['capture']['source_sha256'], W.digest(raw))
        answer = B.app.query({'corpus':key,'question':'Fossils'})['reader']['text']
        self.assertIn('ancient life', answer)
        self.assertNotIn('evil()', answer)

    async def test_blocked_web_fetch_does_not_create_a_page(self):
        key = B.app.create_collection({'name':'Blocked'})['corpus']
        with patch.dict(sys.modules, {'pyodide.http':types.SimpleNamespace(pyfetch=AsyncMock(side_effect=ValueError('CORS blocked')))}):
            with self.assertRaisesRegex(ValueError, 'CORS blocked'):
                await B.dispatch('/api/source/fetch', {'corpus':key,'title':'Fossils','url':'https://example.org/fossils'})
        self.assertEqual(B.app.inventory(key,'internal')['pages'], [])

    async def test_transport_error_is_short_and_does_not_expose_traceback(self):
        result = json.loads(await B.call_json('/api/source/import', json.dumps({'corpus':'missing'})))
        self.assertEqual(result['_browser_transport_error'], 'Unknown MPLPB collection')
        self.assertNotIn('Traceback', result['_browser_transport_error'])

    async def test_search_crawls_wiki_builds_and_preserves_previous_session(self):
        prior= B.app.chat({'corpus':'logic','message':'remember old collection'})
        B.app.chat({'corpus':'logic','session':prior['session'],'message':'guide me'})
        texts={'Cat':'Cat is an animal. [[Dog]] [[File:ignored.png]]', 'Dog':'Dog is an animal. [[Mouse]]', 'Mouse':'Mouse is an animal.'}
        async def remote(url):
            q=parse_qs(urlsplit(url).query)
            if 'srsearch' in q: raw=json.dumps({'query':{'search':[{'title':'Cat','pageid':1,'snippet':'suggestion only'}]}}).encode()
            else:
                title=q['titles'][0]; text=texts[title]
                raw=json.dumps({'query':{'pages':{'1':{'title':title,'pageid':1,'revisions':[{'revid':100,'timestamp':'2026-10-08T12:00:00Z','slots':{'main':{'*':text,'sha1':hashlib.sha1(text.encode()).hexdigest(),'contentmodel':'wikitext'}}}]}}}}).encode()
            return raw,{'url':url,'retrieved_at':'2026-10-08T12:01:00Z','http_status':200}
        with patch.object(B,'remote',remote):
            result=await B.dispatch('/api/chat',{'corpus':'logic','session':prior['session'],'message':'search cat','wiki':'simple'})
        self.assertEqual(result['response']['kind'],'built')
        self.assertTrue(B.app.sessions[result['session']]['mind']['guide']['active'])
        self.assertEqual(B.app.sessions[result['session']]['mind']['guide']['step'],2)
        self.assertNotEqual(result['session'],prior['session'])
        self.assertEqual(len(B.app.inventory(result['corpus'],'internal')['pages']),3)
        self.assertTrue(result['response']['crawl']['edges'])
        self.assertEqual(B.app.resume_chat({'session':prior['session']})['notes'],['old collection'])
        answer=await B.dispatch('/api/chat',{'corpus':result['corpus'],'session':result['session'],'message':'what is it?'})
        self.assertEqual(answer['response']['kind'],'return')
        self.assertIn('Cat',answer['response']['message'])

    async def test_automatic_topic_lookup_captures_wiki_and_preserves_mode(self):
        async def remote(url):
            q=parse_qs(urlsplit(url).query)
            if 'srsearch' in q:
                raw=json.dumps({'query':{'search':[{'title':'Zorb','pageid':1,'snippet':'not evidence'}]}}).encode()
            else:
                text='Zorb is a fictional test topic.'
                raw=json.dumps({'query':{'pages':{'1':{'title':'Zorb','pageid':1,'revisions':[{'revid':100,'timestamp':'2026-10-08T12:00:00Z','slots':{'main':{'*':text,'sha1':hashlib.sha1(text.encode()).hexdigest(),'contentmodel':'wikitext'}}}]}}}}).encode()
            return raw,{'url':url,'retrieved_at':'2026-10-08T12:01:00Z','http_status':200}
        initial=B.app.chat({'corpus':'logic','message':'load MPLPB'})
        with patch.object(B,'remote',remote):
            r=await B.dispatch('/api/chat',{'corpus':'logic','session':initial['session'],'message':'Can you chat about Zorb','wiki':'simple','auto_wiki':True})
        self.assertEqual(r['session'],initial['session'])
        self.assertEqual(r['response']['environment']['mode'],'focus')
        self.assertIn('logic',r['response']['environment']['corpora'])
        self.assertTrue(r['response']['sources']);self.assertIn('fictional test topic',r['response']['message'])
        self.assertTrue(B.app.resume_chat({'session':r['session']})['chain_intact'])
        with patch.object(B,'remote',AsyncMock(side_effect=AssertionError('Local first; no remote'))):
            local=await B.dispatch('/api/chat',{'corpus':'logic','session':r['session'],'message':'Can you chat about Zorb','wiki':'simple','auto_wiki':True})
            self.assertTrue(local['response']['sources'])
            await B.dispatch('/api/chat',{'corpus':'logic','session':r['session'],'message':'I feel sad','wiki':'simple','auto_wiki':True})

    async def test_automatic_lookup_can_be_disabled_and_failure_preserves_chain(self):
        data={'corpus':'logic','message':'Can you chat about unlisted zorb topic','wiki':'simple','default_chat':True}
        with patch.object(B,'remote',AsyncMock(side_effect=ValueError('offline'))) as fetch:
            result=await B.dispatch('/api/chat',{**data,'auto_wiki':False})
            self.assertEqual(fetch.await_count,0)
            failed=await B.dispatch('/api/chat',{**data,'session':result['session'],'auto_wiki':True})
            self.assertEqual(failed['automatic_lookup']['status'],'failed')
            self.assertTrue(B.app.resume_chat({'session':result['session']})['chain_intact'])

    async def test_general_web_build_is_automatic_and_token_not_logged(self):
        raw=b'Dinosaurs lived in the past.'
        plan={'schema':1,'query':'dinosaurs','sources':[{'title':'Dinosaurs','url':'https://example.org/dinosaurs','raw':raw,'text':raw.decode(),'source_sha256':W.digest(raw),'observed_at':'2026-10-08T12:00:00Z'}], 'edges':[], 'failures':[], 'limits':{'pages':5}}
        with patch.object(B,'web_plan',AsyncMock(return_value=plan)):
            result=await B.dispatch('/api/chat',{'corpus':'canned','message':'search dinosaurs','wiki':'web','crawl_token':'private-test-token'})
        self.assertEqual(result['response']['kind'],'built')
        answer=await B.dispatch('/api/chat',{'corpus':result['corpus'],'session':result['session'],'message':'what is it?','wiki':'web'})
        self.assertEqual(answer['response']['kind'],'return')
        exported=B.app.export_chat({'session':result['session']})
        self.assertNotIn('private-test-token',json.dumps(exported))
        restored=App(topic_base=Path(self.temp.name)/'topics')
        self.assertTrue(restored.resume_chat({'session':result['session']})['chain_intact'])
        self.assertEqual(restored.inventory(result['corpus'],'internal')['eligible'],1)

    async def test_unconfigured_web_crawl_is_explicitly_unavailable(self):
        with self.assertRaisesRegex(ValueError,'configured hosted crawler'):
            await B.dispatch('/api/chat',{'corpus':'canned','message':'search fossils','wiki':'web'})
        self.assertEqual(B.app.collections.entries(),{})

    async def test_web_crawler_payload_pin_mismatch_cannot_build(self):
        import base64
        plan={'schema':1,'query':'cat','sources':[{'url':'https://example.org/cat','title':'Cat','mime':'text/plain','raw_base64':base64.b64encode(b'Cat').decode(),'source_sha256':'0'*64}]}
        response=types.SimpleNamespace(status=200,bytes=AsyncMock(return_value=json.dumps(plan).encode()))
        with patch.dict(sys.modules,{'pyodide.http':types.SimpleNamespace(pyfetch=AsyncMock(return_value=response))}):
            with self.assertRaisesRegex(ValueError,'differ from returned pin'):
                await B.dispatch('/api/chat',{'corpus':'logic','message':'search cat','wiki':'web','crawl_backend':'https://crawler.example.org/crawl','crawl_token':'test-token'})
        self.assertEqual(B.app.collections.entries(),{})

    async def test_wiki_failed_seed_does_not_promote_second_result(self):
        search=json.dumps({'query':{'search':[{'title':'Cat','pageid':1},{'title':'Dog','pageid':2}]}}).encode()
        async def remote(url):
            if 'list=search' in url:return search,{'retrieved_at':'2026-10-08T12:01:00Z'}
            self.assertIn('titles=Cat',url)
            raise ValueError('HTTP 429')
        with patch.object(B,'remote',remote):
            result=await B.dispatch('/api/chat',{'corpus':'logic','message':'search animals','wiki':'simple'})
        self.assertEqual(result['response']['kind'],'crawl_failed')
        self.assertEqual(B.app.collections.entries(),{})

    async def test_reader_and_saved_memory_same_engine(self):
        answer = await B.dispatch('/api/query', {'corpus':'canned','question':'Phrynomedusa vanzolinii Hyundai Engineering and Construction'})
        self.assertEqual(answer['reader']['kind'], 'ambiguous')
        first = await B.dispatch('/api/chat', {'corpus':'logic','message':'remember dinosaurs'})
        resumed = await B.dispatch('/api/chat/resume', {'session':first['session']})
        self.assertEqual(resumed['notes'], ['dinosaurs'])
        self.assertTrue(resumed['chain_intact'])

    async def test_no_arbitrary_url_or_file_read(self):
        for url in ('https://example.com/api/state', '/api/file', 'file:///etc/passwd'):
            with self.assertRaises(ValueError): await B.dispatch(url)
        with self.assertRaises(ValueError):
            await B.dispatch('/api/page?corpus=canned&path=../../README.md')

    async def test_search_transport_is_explicit_and_not_evidence(self):
        payload = json.dumps({'query':{'search':[{'title':'Cat','pageid':1,'snippet':'<b>animal</b>'}]}}).encode()
        remote = AsyncMock(return_value=(payload, {'retrieved_at':'2026-10-08T00:00:00Z'}))
        original = B.app.topics.search
        with patch.object(B, 'remote', remote):
            result = await B.dispatch('/api/chat', {'corpus':'logic','message':'find cat'})
        self.assertEqual(result['response']['sources'], [])
        self.assertEqual(result['response']['search']['results'][0]['snippet'], 'animal')
        self.assertIn('origin=%2A', remote.call_args[0][0])
        self.assertEqual(B.app.topics.search, original)
        self.assertFalse((B.app.topics.base/'head.json').exists())

    async def test_network_failure_creates_no_import_or_save(self):
        with patch.object(B,'remote',AsyncMock(side_effect=ValueError('HTTP 429'))):
            with self.assertRaises(ValueError):
                await B.dispatch('/api/chat',{'corpus':'logic','message':'import Cat'})
        self.assertFalse(B.app.sessions)
        self.assertFalse((B.app.topics.base/'head.json').exists())

    async def test_ordinary_chat_has_no_network(self):
        with patch.object(B,'remote',AsyncMock(side_effect=AssertionError('network'))) as remote:
            result = await B.dispatch('/api/chat',{'corpus':'logic','message':'relate Dungeons and Dragons -> game'})
        remote.assert_not_called()
        self.assertEqual(result['response']['kind'], 'relations')

    async def test_external_withholding(self):
        result = await B.dispatch('/api/query',{'corpus':'canned','profile':'external','question':'Phrynomedusa vanzolinii'})
        self.assertNotEqual(result['reader']['kind'], 'return')
        self.assertEqual(result['gate']['sources'], [])

    async def test_import_retains_revision_pins_and_conflict_stops(self):
        from tests.test_topic_chat_sources import response
        original = W.request
        with patch.object(B, 'remote', AsyncMock(return_value=response())):
            imported = await B.dispatch('/api/chat', {'corpus':'logic','message':'import Cat'})
        self.assertIs(W.request, original)
        self.assertEqual(imported['corpus'], 'topics')
        root = B.app.topics.root()
        result = await B.dispatch('/api/chat', {'corpus':'topics','session':imported['session'],'message':'what is it?'})
        self.assertEqual(result['response']['kind'], 'return')
        head = (B.app.topics.base/'head.json').read_bytes()
        with patch.object(B, 'remote', AsyncMock(return_value=response(text="Cat is changed synthetic source bytes."))):
            with self.assertRaises(ValueError):
                await B.dispatch('/api/chat', {'corpus':'topics','session':imported['session'],'message':'import Cat'})
        self.assertIs(W.request, original)
        self.assertEqual((B.app.topics.base/'head.json').read_bytes(), head)
        with self.assertRaises(ValueError): B.app.topics.root()

    async def test_browser_adapter_is_separately_pinned(self):
        pins = B.browser_code_pins()
        self.assertIsNone(pins['base_revision'])
        self.assertEqual(B.browser_code_errors(pins), [])
        pins['browser_adapter_sha256'] = 'bad'
        self.assertIn('browser adapter bytes differ from capture pin', B.browser_code_errors(pins))

    async def test_bad_runtime_archive_is_refused(self):
        path = Path(self.temp.name)/'bad.tar';path.write_bytes(b'bad')
        with self.assertRaises(ValueError): build(path,Path(self.temp.name)/'index.html')
