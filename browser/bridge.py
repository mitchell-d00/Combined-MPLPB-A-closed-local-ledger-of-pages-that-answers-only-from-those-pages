"""Browser transport only. All ownership/gating/session decisions use App unchanged."""
import html
import base64
import hashlib
import sys
from pathlib import Path
import json
import re
from urllib.parse import parse_qs, urlsplit, urlencode
from datetime import datetime, timezone
from html.parser import HTMLParser
from tools.exploration_store import source_url
from tools import topic_crawl as TC
from tools.ledger_ui import App
from tools import wiki_live_eval as W

def browser_code_pins():
    # WebAssembly has no git subprocess. Record actual bytes and explicit adapter,
    # with no fabricated checkout revision.
    return {'engine_sha256': W.engine_hash(), 'checker_sha256': W.digest(Path(W.__file__).read_bytes()),
            'renderer_sha256': W.renderer_pin()['sha256'], 'base_revision': None,
            'browser_adapter_sha256': W.digest(Path(__file__).read_bytes()),
            'transport': 'browser-pyfetch-v1',
            'notice': 'Browser transport; byte consistency only, not authenticated authorship or independent validation.'}

_original_code_errors = W.code_errors

def browser_code_errors(pins):
    errors = _original_code_errors(pins)
    if 'browser_adapter_sha256' in pins and pins['browser_adapter_sha256'] != W.digest(Path(__file__).read_bytes()):
        errors.append('browser adapter bytes differ from capture pin')
    return errors

if sys.platform == 'emscripten':
    W.code_pins = browser_code_pins
    W.code_errors = browser_code_errors

app = App()

def plain_source(body):
    class Text(HTMLParser):
        def __init__(self): super().__init__(); self.parts=[]; self.skip=0
        def handle_starttag(self, tag, attrs):
            if tag in {'script','style','head','noscript'}: self.skip += 1
        def handle_endtag(self, tag):
            if tag in {'script','style','head','noscript'}: self.skip=max(0,self.skip-1)
        def handle_data(self, value):
            if not self.skip and value.strip(): self.parts.append(value.strip())
    parser = Text(); parser.feed(body); return '\n'.join(parser.parts)

async def web_plan(query, data):
    endpoint = data.get('crawl_backend','').strip()
    if not endpoint: raise ValueError('General web crawl needs a configured hosted crawler URL. Open crawler settings. No collection was built.')
    source_url(endpoint)
    token = data.get('crawl_token','')
    if not token: raise ValueError('Enter the crawler access token in crawler settings; it is not saved to chat.')
    from pyodide.http import pyfetch
    response = await pyfetch(endpoint, method='POST', credentials='omit', redirect='error',
                             headers={'Content-Type':'application/json','Authorization':'Bearer '+token},
                             body=json.dumps({'query':query}))
    raw = await response.bytes()
    if len(raw)>4_000_000: raise ValueError('Crawler result exceeds 4 MB')
    plan = json.loads(raw)
    if response.status != 200 or plan.get('error'): raise ValueError(plan.get('error','Crawler HTTP '+str(response.status)))
    if plan.get('schema')!=1 or plan.get('query')!=query or len(plan.get('sources',[]))>5:
        raise ValueError('Crawler returned an invalid plan')
    sources=[]
    for item in plan['sources']:
        source_url(item['url'])
        payload=base64.b64decode(item['raw_base64'], validate=True)
        if len(payload)>512*1024 or hashlib.sha256(payload).hexdigest()!=item['source_sha256']:
            raise ValueError('Crawler source bytes differ from returned pin')
        if item['mime'] not in {'text/html','text/plain'}: raise ValueError('Unsupported crawl payload')
        text=payload.decode('utf-8', errors='replace')
        if item['mime']=='text/html': text=plain_source(text)
        if not text.strip(): continue
        sources.append({**item,'raw':payload,'text':text[:100000]})
    return {**plan,'sources':sources}

def build_web(query, plan):
    if not plan['sources']:
        return None, {'kind':'crawl_failed','message':'No source pages were fetched. No MPLPB was built.',
                      'crawl':{k:v for k,v in plan.items() if k!='sources'},'sources':[],'context':None,'reasoning':['Search snippets are not evidence.']}
    collection=app.collections.create(query[:80]); key=collection['corpus']; imported=[]
    failures=list(plan.get('failures',[]))
    for item in plan['sources']:
        try:
            saved=app.collections.add(key,item['title'][:200],item['url'],item['text'],raw=item['raw'],transport='configured-web-crawler-v1; source fetch reported by server')
            imported.append({**saved,'server_observed_at':item.get('observed_at'), 'server_source_sha256':item['source_sha256'],'source_url':item['url']})
        except Exception as exc: failures.append({'url':item['url'],'reason':str(exc)})
    crawl={k:v for k,v in plan.items() if k!='sources'}
    crawl['failures']=failures
    crawl['imported']=[{k:s[k] for k in ('title','capture','server_observed_at','server_source_sha256','source_url')} for s in imported]
    from tools import chat_logic as C
    app.collections.record_crawl(key,crawl)
    if not imported:
        return key, {'kind':'crawl_failed','message':'Source imports failed. The empty collection and failure record were retained.', 'crawl':crawl,'context':None,'sources':[],'reasoning':['No source answer or evaluation score claimed.']}
    context=C.context_for(app.root(key),imported[0]['title'],'internal')
    return key, {'kind':'built','message':'Built MPLPB “'+collection['name']+'” from '+str(len(imported))+' web pages. '+
                 ('Some fetches failed. ' if failures else '')+'Starting topic: '+context['title']+'. Ask “what is it?” or “summarize it”.',
                 'crawl':crawl,'context':context,'sources':[context],'reasoning':['Search rank and crawl edges are navigation, not proof of relationships.',
                 'Raw bytes checked against server-returned SHA-256 and sealed locally. Site download is a server report, not independently verified authorship.']}

async def remote(url):
    from pyodide.http import pyfetch
    response = await pyfetch(url, method='GET', credentials='omit')
    if response.status != 200:
        raise ValueError('Wikipedia HTTP ' + str(response.status) + '; no import or score claimed')
    raw = await response.bytes()
    if len(raw) > 2_000_000:
        raise ValueError('Wikipedia response exceeds 2 MB')
    return raw, {'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                 'http_status': response.status, 'content_type': response.headers.get('content-type', response.headers.get('Content-Type', ''))}

async def dispatch(url, data=None):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        raise ValueError('Only local API routes accepted')
    q = parse_qs(parsed.query)
    route = parsed.path
    if data is None:
        if route == '/api/state': return app.state()
        if route == '/api/history': return app.history(q.get('corpus', [None])[0])
        if route == '/api/experiment': return app.experiment()
        if route == '/api/inventory': return app.inventory(q['corpus'][0], q.get('profile', ['internal'])[0])
        if route == '/api/page': return app.page(q['corpus'][0], q['path'][0], q.get('profile', ['internal'])[0])
    else:
        if not isinstance(data, dict): raise ValueError('JSON object required')
        if route == '/api/source/fetch':
            target = source_url(data.get('url', ''))
            from pyodide.http import pyfetch
            response = await pyfetch(target, method='GET', credentials='omit', mode='cors', redirect='error')
            if response.status != 200: raise ValueError('Source HTTP ' + str(response.status))
            raw = await response.bytes()
            if len(raw) > 2_000_000: raise ValueError('Source exceeds 2 MB')
            mime = response.headers.get('content-type', response.headers.get('Content-Type', '')).split(';')[0].strip().lower()
            if mime not in {'text/html', 'text/plain'}: raise ValueError('Import supports HTML or plain text')
            body = raw.decode('utf-8', errors='replace')
            if mime == 'text/html':
                body = plain_source(body)
            return app.collections.add(data.get('corpus'), data.get('title'), target, body, raw=raw, transport='browser-cors-fetch-v1')
        operations = {'/api/query': app.query, '/api/chat/resume': app.resume_chat,
                      '/api/collections/create': app.create_collection, '/api/collections/reset': app.reset_collection, '/api/source/import': app.import_source,
                      '/api/chat/reset': app.reset_chat, '/api/chat/export': app.export_chat}
        if route in operations: return operations[route](data)
        if route == '/api/chat':
            message = data.get('message', '')
            if not isinstance(message, str): raise ValueError('Message must be text')
            wiki = data.get('wiki', 'simple')
            if wiki=='web' and message.casefold().startswith('search '):
                query=message[7:].strip()
                if not 1<=len(query)<=160: raise ValueError('Search needs 1–160 characters')
                plan=await web_plan(query,data)
                original=app.build_search
                try:
                    app.build_search=lambda q,w: build_web(q,plan)
                    return app.chat(data)
                finally: app.build_search=original
            if wiki not in W.APIS:
                if message.casefold().startswith(('import ','find ')): raise ValueError('Choose a Wikipedia source for manual title imports/search suggestions')
                wiki='simple'
            if message.casefold().startswith(('search ', 'find ')):
                automatic=message.casefold().startswith('search ')
                query = message[7 if automatic else 5:].strip()
                if not 1 <= len(query) <= 160: raise ValueError('Search needs 1–160 characters')
                url = W.APIS[wiki] + '?' + urlencode(dict(action='query', format='json', list='search',
                    srsearch=query, srlimit=6, origin='*'))
                raw, metadata = await remote(url)
                payload = json.loads(raw)
                if payload.get('error'): raise ValueError('Wiki search failed')
                found = {'query': query, 'wiki': wiki, 'searched_at': metadata['retrieved_at'],
                         'notice': 'Remote suggestions only. Import explicitly to retain evidence.',
                         'results': [{'title': p['title'], 'pageid': p['pageid'],
                                      'snippet': html.unescape(re.sub('<[^>]*>', '', p.get('snippet', ''))),
                                      'timestamp': p.get('timestamp')} for p in payload['query']['search']]}
                if automatic:
                    async def fetch(title): return await remote(W.request_url(W.APIS[wiki],[title])+'&origin=*')
                    plan=await TC.collect(found,fetch)
                    original=app.prepare_search
                    try:
                        app.prepare_search=lambda *_:plan
                        return app.chat(data)
                    finally: app.prepare_search=original
                store = app.topic_store(data.get('corpus'))
                original = store.search
                try:
                    # Collection TopicStore instances are ephemeral; replace the selector narrowly.
                    select = app.topic_store
                    store.search = lambda *_: found
                    app.topic_store = lambda *_: store
                    return app.chat(data)
                finally:
                    store.search = original
                    app.topic_store = select
            if message.casefold().startswith('import '):
                title = message[7:].strip()
                if not 1 <= len(title) <= 200 or any(c in title for c in '|\n\r'):
                    raise ValueError('Import one exact title of 1–200 characters')
                raw, metadata = await remote(W.request_url(W.APIS[wiki], [title]) + '&origin=*')
                W.pages(raw)
                original = W.request
                def supplied(api, titles):
                    if api != W.APIS[wiki] or titles != [title]: raise ValueError('Import request differs')
                    return raw, metadata
                try:
                    W.request = supplied
                    return app.chat(data)
                finally: W.request = original
            return app.chat(data)
    raise ValueError('Unknown API route')

async def call_json(url, payload):
    try:
        result = await dispatch(url, json.loads(payload) if payload else None)
    except Exception as exc:
        result = {'_browser_transport_error': str(exc)}
    return json.dumps(result, ensure_ascii=False)
