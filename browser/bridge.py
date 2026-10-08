"""Browser transport only. All ownership/gating/session decisions use App unchanged."""
import html
import sys
from pathlib import Path
import json
import re
from urllib.parse import parse_qs, urlsplit, urlencode
from datetime import datetime, timezone
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

async def remote(url):
    from pyodide.http import pyfetch
    response = await pyfetch(url, method='GET', credentials='omit')
    if response.status != 200:
        raise ValueError('Wikipedia HTTP ' + str(response.status) + '; no import or score claimed')
    raw = await response.bytes()
    if len(raw) > 2_000_000:
        raise ValueError('Wikipedia response exceeds 2 MB')
    return raw, {'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                 'http_status': response.status, 'content_type': response.headers.get('Content-Type', '')}

async def dispatch(url, data=None):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        raise ValueError('Only local API routes accepted')
    q = parse_qs(parsed.query)
    route = parsed.path
    if data is None:
        if route == '/api/state': return app.state()
        if route == '/api/history': return app.history()
        if route == '/api/experiment': return app.experiment()
        if route == '/api/inventory': return app.inventory(q['corpus'][0], q.get('profile', ['internal'])[0])
        if route == '/api/page': return app.page(q['corpus'][0], q['path'][0], q.get('profile', ['internal'])[0])
    else:
        if not isinstance(data, dict): raise ValueError('JSON object required')
        operations = {'/api/query': app.query, '/api/chat/resume': app.resume_chat,
                      '/api/chat/reset': app.reset_chat, '/api/chat/export': app.export_chat}
        if route in operations: return operations[route](data)
        if route == '/api/chat':
            message = data.get('message', '')
            if not isinstance(message, str): raise ValueError('Message must be text')
            wiki = data.get('wiki', 'simple')
            if wiki not in W.APIS: raise ValueError('Unknown Wikipedia site')
            if message.casefold().startswith('search '):
                query = message[7:].strip()
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
                original = app.topics.search
                try:
                    app.topics.search = lambda *_: found
                    return app.chat(data)
                finally: app.topics.search = original
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
    return json.dumps(await dispatch(url, json.loads(payload) if payload else None), ensure_ascii=False)
