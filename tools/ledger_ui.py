#!/usr/bin/env python3
"""Local browser UI: python3 tools/ledger_ui.py [--root /path/to/corpus]."""
import argparse
import base64
import hashlib
import re
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mplpb_combined import ledger as L, reader as R, provenance_gate as G
from mplpb_combined.delivery import external_restriction
from mplpb_combined.record import text_of
from tools import wiki_live_eval as W


class App:
    def __init__(self, custom=None):
        self.corpora = {
            'canned': ('Patch canned · uneven names', ROOT / 'examples/patch-canned'),
            'studio': ('Pottery studio', ROOT / 'examples/studio'),
            'gate': ('D&D and budget · separate sources', ROOT / 'examples/provenance-gate/separate'),
            'dogs': ('Dog clarification', ROOT / 'examples/clarification-dogs'),
        }
        if custom:
            custom = Path(custom).resolve()
            if not custom.is_dir():
                raise ValueError('Custom corpus folder does not exist')
            self.corpora['custom'] = ('Your local corpus', custom)

    def roots(self):
        roots = dict(self.corpora)
        try:
            roots['wiki'] = ('Wiki · active local head', W.latest() / 'corpus')
        except (OSError, ValueError):
            pass
        return roots

    def root(self, key):
        if key not in self.roots():
            raise ValueError('Unknown corpus')
        return self.roots()[key][1]

    def state(self):
        corpora = []
        for key, (label, root) in self.roots().items():
            ledger = L.Ledger(root)
            corpora.append({'key': key, 'label': label, 'records': len(ledger.records),
                            'eligible': len(ledger.servable())})
        return {'corpora': corpora, 'profiles': list(R.PROFILES),
                'notice': 'Local lexical retrieval. Source declarations are not authenticated authorship.'}

    def inventory(self, corpus, profile):
        root = self.root(corpus)
        if profile not in R.PROFILES:
            raise ValueError('Unknown profile')
        policy = R.PROFILES[profile]
        ledger = L.Ledger(root)
        current = {r.path for r in ledger.servable()}
        pages = []
        for rec in ledger.records:
            depth = ledger.depth(rec)
            reason = ledger.quarantine_reason(rec)
            eligible = rec.path in current
            if not reason and not eligible:
                reason = 'retired' if ledger.effective_status(rec) == 'retired' else 'not current or valid lineage'
            if eligible and external_restriction(rec, policy):
                eligible, reason = False, 'withheld by external profile'
            if eligible and policy.max_depth is not None and depth > policy.max_depth:
                eligible, reason = False, 'withheld by depth limit'
            pages.append({'id': rec.id, 'path': rec.path, 'title': rec.title,
                          'scope': rec.scope, 'status': ledger.effective_status(rec),
                          'origin': rec.origin, 'depth': depth, 'intact': rec.intact,
                          'eligible': eligible, 'reason': reason})
        return {'pages': pages, 'profile': profile,
                'eligible': sum(p['eligible'] for p in pages),
                'notice': 'Inventory lists local records; eligibility does not certify their claims.'}

    def query(self, data):
        question = data.get('question')
        if not isinstance(question, str) or not question.strip() or len(question) > 4000:
            raise ValueError('Enter a question of 1–4000 characters')
        root = self.root(data.get('corpus'))
        name = data.get('profile', 'internal')
        if name not in R.PROFILES:
            raise ValueError('Unknown profile')
        profile = R.PROFILES[name]
        answer = R.answer(root, question, profile)
        reader = answer.to_dict()
        reader['citation'] = answer.citation()
        if answer.record:
            reader['title'] = answer.record.title
        gate = G.gather(root, question, profile).to_dict()
        return {'reader': reader, 'gate': gate, 'live_verified_by_this_query': False}

    def page(self, corpus, path, profile):
        root = self.root(corpus)
        if profile not in R.PROFILES:
            raise ValueError('Unknown profile')
        ledger = L.Ledger(root)
        records = [r for r in ledger.servable() if r.path == path]
        if len(records) != 1:
            raise ValueError('Page is absent, altered or not current')
        rec = records[0]
        p = R.PROFILES[profile]
        if external_restriction(rec, p) or (p.max_depth is not None and ledger.depth(rec) > p.max_depth):
            raise ValueError('Page is withheld by this profile')
        return {'id': rec.id, 'title': rec.title, 'path': rec.path, 'text': text_of(rec.body_html),
                'hash': rec.hash, 'fields': rec.fields, 'depth': ledger.depth(rec)}

    def history(self):
        head_path = W.KIT / 'head.json'
        head = json.loads(head_path.read_text()) if head_path.exists() else None
        versions = []
        for folder in ('captures', 'archives'):
            for path in sorted((W.KIT / folder).glob('*/manifest.json'), reverse=True):
                manifest = json.loads(path.read_text())
                rel = path.parent.relative_to(W.KIT).as_posix()
                versions.append({'path': rel, 'active': bool(head and head['snapshot'] == rel),
                    'schema': manifest.get('schema'), 'source': manifest.get('api'),
                    'observed_at': manifest.get('request', {}).get('retrieved_at'),
                    'renderer': manifest.get('renderer'), 'pages': manifest.get('pages', []),
                    'history': manifest.get('history'), 'status': manifest.get('status', 'retained capture'),
                    'code_matches_now': not W.code_errors(manifest.get('code', {}))})
        versions.sort(key=lambda item: item.get('observed_at') or '', reverse=True)
        return {'head': head, 'versions': versions,
                'notice': 'Capture and verification dates are separate. Stored passes are historical; this view makes no live request.'}

    def experiment(self):
        base = ROOT / 'docs/patch-canned/supplied'
        return {'report': json.loads((base / 'experiment/results.json').read_text()),
                'note': (base / 'EXPERIMENT.md').read_text(),
                'status': 'Supplied experiment, preserved unchanged; live claims not independently rerun.'}


def handler(app):
    html = (ROOT / 'index.html').read_bytes()
    scripts = re.findall(rb'<script>(.*?)</script>', html, re.DOTALL)
    script_pins = ' '.join("'sha256-" + base64.b64encode(hashlib.sha256(script.replace(b'\r\n', b'\n').replace(b'\r', b'\n')).digest()).decode() + "'" for script in scripts)
    class Handler(BaseHTTPRequestHandler):
        def send(self, status, body, mime='application/json; charset=utf-8'):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src " + script_pins + "; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def local(self):
            port = self.server.server_port
            return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

        def do_GET(self):
            if not self.local():
                return self.send(403, {'error': 'Local host required'})
            route = urlsplit(self.path)
            try:
                if route.path in ('/', '/index.html'):
                    return self.send(200, html, 'text/html; charset=utf-8')
                if route.path == '/api/inventory':
                    q = parse_qs(route.query)
                    return self.send(200, app.inventory(q['corpus'][0], q.get('profile', ['internal'])[0]))
                if route.path == '/api/state':
                    return self.send(200, app.state())
                if route.path == '/api/history':
                    return self.send(200, app.history())
                if route.path == '/api/experiment':
                    return self.send(200, app.experiment())
                if route.path == '/api/page':
                    q = parse_qs(route.query)
                    return self.send(200, app.page(q['corpus'][0], q['path'][0], q.get('profile', ['internal'])[0]))
                return self.send(404, {'error': 'Not found'})
            except (OSError, ValueError, TypeError, KeyError) as exc:
                return self.send(400, {'error': str(exc)})

        def do_POST(self):
            if not self.local():
                return self.send(403, {'error': 'Local host required'})
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.send(403, {'error': 'Origin rejected'})
            if self.path != '/api/query':
                return self.send(404, {'error': 'Not found'})
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.send(415, {'error': 'JSON required'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16384:
                    raise ValueError('Invalid request size')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('Request must be an object')
                return self.send(200, app.query(data))
            except (OSError, ValueError, TypeError, KeyError) as exc:
                return self.send(400, {'error': str(exc)})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--open', action='store_true', help='Open the local UI in your default browser')
    args = parser.parse_args()
    app = App(args.root)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(app))
    print(f'Local ledger UI: http://127.0.0.1:{server.server_port}', flush=True)
    if args.open:
        import threading
        import webbrowser
        browser_url = f'http://127.0.0.1:{server.server_port}'
        if args.root:
            browser_url += '?corpus=custom'
        threading.Thread(target=webbrowser.open, args=(browser_url,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
