#!/usr/bin/env python3
"""Build an offline gate demonstration or serve live local queries.

python3 tools/provenance_bench.py --serve
python3 tools/provenance_bench.py --serve --root /absolute/path/to/corpus
"""
import argparse
import hashlib
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from mplpb_combined.provenance_gate import gather
from mplpb_combined.reader import PROFILES

DEMO = HERE / 'examples/provenance-gate'
QUERY = '1974 dungeons and dragons budget'
SCENARIOS = {
    'separate': ('Separate game and budget pages', 'Game history and general budget information stay separate.'),
    'both': ('Budget appears on both pages', 'Both matching budget sources remain visible. The game-page budget is explicitly fictional.'),
    'missing': ('No budget page', 'The game page remains visible; budget is reported as uncovered.'),
    'attached-source': ('Budget material from your paper', 'Your supplied cost paper and its derived excerpt retain their origins and shared lineage.'),
    'tampered': ('Altered budget page', 'The changed page is excluded; its words cannot fill a gap in the request.'),
}


def snapshot(roots, descriptions, write=True):
    data = {'query': QUERY, 'scenarios': []}
    for name, root in roots.items():
        title, description = descriptions[name]
        data['scenarios'].append({'id': name, 'title': title, 'description': description,
            'profiles': {p: gather(root, QUERY, profile).to_dict() for p, profile in PROFILES.items()}})
    template = (HERE / 'tools/provenance_viewer.html').read_text(encoding='utf-8')
    encoded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    page = template.replace('/* GATE_SNAPSHOTS */null', encoded).encode('utf-8')
    if write:
        (DEMO / 'index.html').write_bytes(page)
        (DEMO / 'snapshots.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    return page


def verify_demo():
    lock = json.loads((DEMO / 'fixture-sha256.json').read_text(encoding='utf-8'))
    expected = {DEMO / name for name in lock}
    actual = {p for name in SCENARIOS for p in (DEMO / name).rglob('*') if p.is_file()}
    actual.add(DEMO / 'sources/MPLPB_Cost_of_Visibility_v2.txt')
    if actual != expected:
        raise ValueError('Demo file inventory changed')
    for name, digest in lock.items():
        if hashlib.sha256((DEMO / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Demo fixture bytes changed: ' + name)


def serve(roots, descriptions, port):
    page = snapshot(roots, descriptions, write=False)

    class Handler(BaseHTTPRequestHandler):
        def send(self, status, body, content_type):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def local_host(self):
            return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

        def do_GET(self):
            if not self.local_host():
                return self.send(403, b'Host rejected', 'text/plain')
            request_path = unquote(urlsplit(self.path).path)
            if request_path in ('/', '/index.html'):
                return self.send(200, page, 'text/html; charset=utf-8')
            parts = request_path.lstrip('/').split('/', 1)
            if len(parts) == 2 and parts[0] in roots:
                root = roots[parts[0]].resolve()
                target = (root / parts[1]).resolve()
                if root in target.parents and target.suffix == '.html' and target.is_file():
                    return self.send(200, target.read_bytes(), 'text/html; charset=utf-8')
            return self.send(404, b'Not found', 'text/plain')

        def do_POST(self):
            if not self.local_host():
                return self.send(403, b'Host rejected', 'text/plain')
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.send(403, b'Origin rejected', 'text/plain')
            if self.path != '/api/gate':
                return self.send(404, b'Not found', 'text/plain')
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.send(415, b'JSON required', 'text/plain')
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 16384:
                    raise ValueError('Invalid request size')
                request = json.loads(self.rfile.read(size))
                if not isinstance(request, dict):
                    raise ValueError('Request must be an object')
                question, scenario, profile = request['question'], request['scenario'], request['profile']
                if not isinstance(question, str) or len(question) > 4000:
                    raise ValueError('Question must be at most 4000 characters')
                if not isinstance(scenario, str) or scenario not in roots:
                    raise ValueError('Unknown corpus')
                if not isinstance(profile, str) or profile not in PROFILES:
                    raise ValueError('Unknown profile')
                data = gather(roots[scenario], question, PROFILES[profile]).to_dict()
                self.send(200, json.dumps(data, ensure_ascii=False).encode('utf-8'), 'application/json; charset=utf-8')
            except (KeyError, ValueError, TypeError, FileNotFoundError) as exc:
                self.send(400, json.dumps({'error': str(exc)}).encode('utf-8'), 'application/json')

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'Provenance gate: http://127.0.0.1:{port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--root', type=Path, help='use your own local corpus instead of the demonstrations')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if args.root:
        if not args.serve:
            parser.error('--root requires --serve; your corpus is never modified')
        roots = {'custom': args.root.resolve()}
        descriptions = {'custom': ('Your local corpus', 'Source pages from the chosen folder, with provenance.')}
    else:
        verify_demo()
        roots = {name: DEMO / name for name in SCENARIOS}
        descriptions = SCENARIOS
    if args.serve:
        serve(roots, descriptions, args.port)
    else:
        snapshot(roots, descriptions)
        print('Built examples/provenance-gate/index.html and snapshots.json')


if __name__ == '__main__':
    main()
