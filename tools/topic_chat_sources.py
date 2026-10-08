"""Explicit Wikipedia search/import with immutable source captures and local heads."""
import hashlib
import html
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from mplpb_combined import ledger as L
from tools import wiki_live_eval as W


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
        json.dump(value, stream, indent=2); stream.write('\n'); temp = stream.name
    os.replace(temp, path)


class TopicStore:
    def __init__(self, base):
        self.base = Path(base).resolve()
        self.lock = threading.RLock()

    def path(self, relative):
        path = (self.base / relative).resolve()
        if self.base not in path.parents:
            raise ValueError('Topic path escapes store')
        return path

    def search(self, query, wiki='simple'):
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= 160:
            raise ValueError('Search needs 1–160 characters')
        if wiki not in W.APIS:
            raise ValueError('Unknown Wikipedia site')
        url = W.APIS[wiki] + '?' + urllib.parse.urlencode(dict(
            action='query', format='json', list='search', srsearch=query.strip(),
            srnamespace=0, srlimit=6, srprop='snippet|timestamp'))
        req = urllib.request.Request(url, headers={'User-Agent': W.UA})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('Search response too large')
        payload = json.loads(raw)
        if payload.get('error'):
            raise ValueError('Wiki search failed: ' + str(payload['error']))
        return {'query': query, 'wiki': wiki, 'searched_at': now(),
                'notice': 'Remote search suggestions, not local evidence. Choose a title to import.',
                'results': [{'title': p['title'], 'pageid': p['pageid'],
                             'snippet': html.unescape(re.sub('<[^>]*>', '', p.get('snippet', ''))),
                             'timestamp': p.get('timestamp')}
                            for p in payload['query']['search']]}

    def head(self):
        path = self.base / 'head.json'
        if not path.exists():
            return None
        head = json.loads(path.read_text())
        manifest_path = self.path(head['bundle'] + '/manifest.json')
        if W.digest(manifest_path.read_bytes()) != head['manifest_sha256']:
            raise ValueError('Topic head manifest pin differs')
        return head, json.loads(manifest_path.read_text())

    def root(self):
        loaded = self.head()
        if not loaded:
            raise ValueError('No imported topics yet')
        if (self.base / 'blocked.json').exists():
            raise ValueError('A source revision conflict blocks this topic collection; import a newer revision')
        head, bundle = loaded
        root = self.path(head['bundle'] + '/corpus')
        conflicts = [json.loads(p.read_text()) for p in (self.base / 'captures').glob('*/manifest.json')]
        for item in bundle['sources']:
            if any(m.get('same_revision_conflicts') and any(c['title'] == item['title']
                       and c['expected']['revid'] == item['source_pin']['revid']
                       for c in m['same_revision_conflicts']) for m in conflicts):
                raise ValueError('Retained same-revision conflict blocks this source')
            snapshot = self.path(item['capture'])
            manifest_bytes = (snapshot / 'manifest.json').read_bytes()
            if W.digest(manifest_bytes) != item['capture_manifest_sha256']:
                raise ValueError('Imported source manifest pin differs')
            manifest = json.loads(manifest_bytes)
            errors = W.stored_errors(snapshot, manifest) + W.code_errors(manifest['code'])
            if errors:
                raise ValueError('Imported topic provenance invalid: ' + '; '.join(errors))
            if W.digest((root / item['path']).read_bytes()) != item['served_page_sha256']:
                raise ValueError('Imported local page bytes differ')
        if {p.name for p in root.glob('*.html')} != {i['path'] for i in bundle['sources']}:
            raise ValueError('Topic inventory differs from head pin')
        return root

    def import_title(self, title, wiki='simple'):
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 200 or any(c in title for c in '|\n\r'):
            raise ValueError('Import one exact Wikipedia title of 1–200 characters')
        if wiki not in W.APIS:
            raise ValueError('Unknown Wikipedia site')
        raw, metadata = W.request(W.APIS[wiki], [title.strip()])
        pages = W.pages(raw)
        if len(pages) != 1:
            raise ValueError('Title missing or ambiguous; select a search result')
        page = next(iter(pages.values())); title = page['title']; pin = W.source_pin(page)
        key = hashlib.sha256((W.APIS[wiki] + '\0' + title).encode()).hexdigest()[:16]
        with self.lock:
            loaded = self.head()
            active = {i['key']: i for i in loaded[1]['sources']} if loaded else {}
            if key not in active and len(active) >= 20:
                raise ValueError('Topic collection limit is 20 sources')
            old = active.get(key)
            history = None
            # Compare every retained observation, not only the current head.
            for manifest_path in (self.base / 'captures').glob('*/manifest.json'):
                prior = json.loads(manifest_path.read_text())
                if prior['api'] != W.APIS[wiki] or prior['pages'][0]['title'] != title:
                    continue
                p = prior['pages'][0]
                if p['revid'] == pin['revid'] and any(p[k] != pin[k] for k in pin):
                    history = W.history_link(manifest_path.parent, prior, metadata, 'same revision source conflict')
                    break
            if not history and old:
                prior_path = self.path(old['capture'])
                history = W.history_link(prior_path, json.loads((prior_path / 'manifest.json').read_text()), metadata, 'topic refresh')
            capture = self.base / 'captures' / W.stamp()
            W.capture_response(capture, W.APIS[wiki], {'fetched': [title], 'absent': []}, raw, metadata, history)
            manifest = json.loads((capture / 'manifest.json').read_text())
            if manifest.get('same_revision_conflicts'):
                blocked = json.loads((self.base / 'blocked.json').read_text()) if (self.base / 'blocked.json').exists() else {}
                blocked[key] = {'title': title, 'revid': pin['revid'], 'capture': str(capture.relative_to(self.base))}
                atomic_json(self.base / 'blocked.json', blocked)
                raise ValueError('Same revision returned different source bytes. Observation archived; head not promoted.')
            errors = W.stored_errors(capture, manifest)
            if errors:
                raise ValueError('Captured source invalid: ' + '; '.join(errors))
            if old:
                prior = json.loads((self.path(old['capture']) / 'manifest.json').read_text())['pages'][0]
                if (page['revisions'][0]['timestamp'] < prior['source_revision_at']
                        or pin['revid'] < prior['revid']):
                    raise ValueError('Older source revision archived; it cannot lead')
            active[key] = {'key': key, 'capture': str(capture.relative_to(self.base)),
                           'capture_manifest_sha256': W.digest((capture / 'manifest.json').read_bytes())}
            bundle_path = self.base / 'bundles' / W.stamp()
            bundle_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=bundle_path.parent, prefix='.topic-') as tmp:
                stage = Path(tmp) / 'bundle'; stage.mkdir(); sources = []
                for entry in sorted(active.values(), key=lambda i: i['key']):
                    entry = {k: entry[k] for k in ('key', 'capture', 'capture_manifest_sha256')}
                    saved = self.path(entry['capture'])
                    prior = json.loads((saved / 'manifest.json').read_text())
                    if W.stored_errors(saved, prior):
                        raise ValueError('An existing topic source is altered')
                    p = next(iter(W.pages((saved / 'response.json').read_bytes()).values()))
                    rec = L.write(stage / 'corpus', title=p['title'], scope=p['title'], when_to_use=p['title'],
                                  body=W.source_body(p, prior['api']), doc_id='TOPIC-' + entry['key'],
                                  origin='machine', source_authorship='unknown', external='no', owner='unknown',
                                  when=prior['request']['retrieved_at'])
                    sources.append({**entry, 'title': p['title'], 'id': rec.id, 'path': rec.path,
                                    'source_pin': W.source_pin(p), 'observed_at': prior['request']['retrieved_at'],
                                    'served_page_sha256': W.digest((stage / 'corpus' / rec.path).read_bytes())})
                bundle = {'sources': sources, 'created_at': now(), 'previous': loaded[0] if loaded else None,
                          'verification': 'source slot and local bytes checked; not an evaluation score'}
                atomic_json(stage / 'manifest.json', bundle)
                os.rename(stage, bundle_path)
            atomic_json(self.base / 'head.json', {'bundle': str(bundle_path.relative_to(self.base)),
                        'manifest_sha256': W.digest((bundle_path / 'manifest.json').read_bytes()), 'updated_at': now()})
            if (self.base / 'blocked.json').exists():
                blocked = json.loads((self.base / 'blocked.json').read_text())
                if key in blocked and blocked[key]['revid'] != pin['revid']:
                    del blocked[key]
                if blocked:
                    atomic_json(self.base / 'blocked.json', blocked)
                else:
                    (self.base / 'blocked.json').unlink()
            return {'corpus': 'topics', 'title': title, 'source_pin': pin,
                    'observed_at': metadata['retrieved_at'], 'capture': str(capture.relative_to(self.base)),
                    'notice': 'Imported pinned revision locally. No truth certification or evaluation score.'}

    def history(self):
        loaded = self.head()
        return {'head': loaded[0] if loaded else None,
                'blocked': json.loads((self.base / 'blocked.json').read_text()) if (self.base / 'blocked.json').exists() else {},
                'captures': [json.loads(p.read_text()) for p in sorted((self.base / 'captures').glob('*/manifest.json'), reverse=True)],
                'notice': 'User-imported sources, separate from the published wiki evaluation kit.'}
