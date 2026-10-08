#!/usr/bin/env python3
"""Evaluate the topic fixtures and create an offline HTML report.

python3 tools/test_topic_examples.py
python3 tools/test_topic_examples.py --serve --port 8765
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
from mplpb_combined.evaluate import run
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import answer, Profile, PROFILES, terms

EVAL = HERE / 'evaluation/topics'
CORPUS = HERE / 'examples/topics'
PROFILES_TO_TEST = {
    'internal': PROFILES['internal'],
    'scope-only': Profile('scope-only', 1, False),
    'ignore-not-for': Profile('ignore-not-for', 1, True, False),
    'external': PROFILES['external'],
}


def inspect(root, query, profile):
    result = answer(root, query, PROFILES_TO_TEST[profile]).to_dict()
    result.pop('root')
    result['content_terms'] = sorted(terms(query))
    return result


def evaluate():
    spec_bytes = (EVAL / 'spec.json').read_bytes()
    spec = json.loads(spec_bytes)
    lock = json.loads((EVAL / 'corpus-lock.json').read_text(encoding='utf-8'))
    if hashlib.sha256(spec_bytes).hexdigest() != lock['spec_sha256']:
        raise ValueError('Frozen specification hash mismatch')
    actual = {}
    for domain in spec['domains']:
        led = Ledger(CORPUS / domain['name'])
        errors = [str(f) for f in led.findings() if f.level == 'error']
        if errors:
            raise ValueError('\n'.join(errors))
        for rec in led.records:
            if rec.kind == 'index':
                continue
            if rec.origin != 'machine' or led.depth(rec) != 1 or not rec.intact:
                raise ValueError('Fixture provenance or integrity changed: ' + rec.path)
            actual[domain['name'] + '/' + rec.path] = rec.hash_actual
    if actual != lock['corpus_hashes']:
        raise ValueError('Frozen corpus changed')
    results = run(EVAL / 'manifest.json')
    (EVAL / 'results.json').write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
    for domain, result in zip(spec['domains'], results['domains']):
        domain['metrics'] = result['arms']
        for probe, row in zip(domain['probes'], result['rows']):
            probe['arms'] = row['arms']
            probe['profiles'] = {name: inspect(CORPUS / domain['name'], probe['q'], name)
                                 for name in PROFILES_TO_TEST}
    payload = {'provenance': spec['provenance'], 'domains': spec['domains']}
    (EVAL / 'trace-results.json').write_text(json.dumps(payload, indent=2,
                                                     ensure_ascii=False) + '\n')
    template = (EVAL / 'viewer.html').read_text(encoding='utf-8')
    data = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c')
    report = template.replace('/* FROZEN_DATA */null', data)
    (EVAL / 'index.html').write_text(report, encoding='utf-8')
    for domain in results['domains']:
        s = domain['arms']['ledger']
        print(f"{domain['name']:20} {s['correct']:2}/{domain['n']} correct; "
              f"{s['wrong_return']} wrong returns; {s['wrong_refusal']} wrong refusals")
    return payload


def serve(payload, port):
    domains = {d['name'] for d in payload['domains']}

    class Handler(BaseHTTPRequestHandler):
        def send(self, status, data, mime):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path in ('/', '/index.html'):
                return self.send(200, (EVAL / 'index.html').read_bytes(), 'text/html; charset=utf-8')
            prefix = '/examples/topics/'
            if path.startswith(prefix):
                target = (CORPUS / path[len(prefix):]).resolve()
                if CORPUS.resolve() in target.parents and target.suffix == '.html' and target.is_file():
                    return self.send(200, target.read_bytes(), 'text/html; charset=utf-8')
            self.send(404, b'Not found', 'text/plain')

        def do_POST(self):
            if self.path != '/api/ask':
                return self.send(404, b'Not found', 'text/plain')
            # Only same-origin requests; an unrelated website cannot run local queries.
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.send(403, b'Origin rejected', 'text/plain')
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 16384:
                    raise ValueError('Invalid request size')
                body = json.loads(self.rfile.read(size))
                domain, query, profile = body['domain'], body['query'], body['profile']
                if domain not in domains or profile not in PROFILES_TO_TEST:
                    raise ValueError('Unknown topic or profile')
                if not isinstance(query, str) or len(query) > 4000:
                    raise ValueError('Question must be at most 4000 characters')
                data = json.dumps(inspect(CORPUS / domain, query, profile)).encode('utf-8')
                return self.send(200, data, 'application/json; charset=utf-8')
            except (ValueError, KeyError, TypeError) as exc:
                return self.send(400, json.dumps({'error': str(exc)}).encode(), 'application/json')

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'Live query bench: http://127.0.0.1:{port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    payload = evaluate()
    if args.serve:
        serve(payload, args.port)


if __name__ == '__main__':
    main()
