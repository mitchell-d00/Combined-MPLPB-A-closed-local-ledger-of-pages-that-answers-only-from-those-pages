"""Named, isolated local MPLPB collections. No discovery or automatic fetching."""
import hashlib
import json
import uuid
from pathlib import Path
from urllib.parse import urlsplit
from tools.topic_chat_sources import TopicStore, atomic_json, now
from tools import chat_logic as C
from mplpb_combined import ledger as L

def source_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Use a public HTTPS source URL without credentials')
    import ipaddress
    host = parsed.hostname.lower()
    if host == 'localhost' or '.' not in host or host.endswith(('.local', '.localhost', '.internal')):
        raise ValueError('Local addresses are not sources')
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not address.is_global: raise ValueError('Private addresses are not sources')
    if len(value) > 2000: raise ValueError('Source URL too long')
    return value

class ExplorationStore:
    def __init__(self, base):
        self.base = Path(base)
        self.index = self.base / 'index.json'

    def entries(self):
        if not self.index.exists(): return {}
        saved = json.loads(self.index.read_text())
        if saved.get('sha256') != C.digest(saved.get('content')):
            raise ValueError('Collection index integrity failed; retained unchanged')
        entries = saved['content']
        for key in entries:
            if not key.startswith('mind-') or len(key) != 37 or any(c not in '0123456789abcdef' for c in key[5:]):
                raise ValueError('Invalid collection identifier')
        return entries

    def save(self, entries):
        atomic_json(self.index, {'content': entries, 'sha256': C.digest(entries)})

    def path(self, key):
        if key not in self.entries(): raise ValueError('Unknown MPLPB collection')
        return self.base / key

    def create(self, name):
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
            raise ValueError('Collection name needs 1–80 characters')
        entries = self.entries()
        if len(entries) >= 32: raise ValueError('32 collection limit; no collection deleted')
        key = 'mind-' + uuid.uuid4().hex
        (self.base / key / 'pages').mkdir(parents=True)
        entries[key] = {'name': name.strip(), 'created_at': now()}
        self.save(entries)
        return {'corpus': key, **entries[key]}

    def topics(self, key): return TopicStore(self.path(key) / 'topics')

    def record_crawl(self, key, crawl):
        path = self.path(key) / 'crawl.json'
        atomic_json(path, {'content':crawl, 'sha256':C.digest(crawl)})
        entries=self.entries(); entries[key]['crawl_sha256']=hashlib.sha256(path.read_bytes()).hexdigest(); self.save(entries)

    def reset(self, key):
        path = self.path(key)
        archive = self.base / 'archives' / (key + '-' + uuid.uuid4().hex)
        archive.parent.mkdir(exist_ok=True)
        entries = self.entries()
        atomic_json(path / 'reset-metadata.json', {'content': entries[key], 'sha256': C.digest(entries[key])})
        path.rename(archive)
        del entries[key]
        try: self.save(entries)
        except Exception:
            archive.rename(path)
            raise
        return {'reset': True, 'notice': 'Collection removed from active workspace; prior files retained in a local reset archive.'}

    def root(self, key):
        base = self.path(key)
        # Rebuild only from pinned source records, never from arbitrary directories.
        manual = base / 'pages'
        entry = self.entries()[key]
        if entry.get('crawl_sha256') and hashlib.sha256((base / 'crawl.json').read_bytes()).hexdigest()!=entry['crawl_sha256']:
            raise ValueError('Crawl plan differs from collection pin')
        for item in entry.get('captures', []):
            path = base / 'captures' / item['id'] / 'manifest.json'
            if hashlib.sha256(path.read_bytes()).hexdigest() != item['manifest_sha256']:
                raise ValueError('Stored capture manifest differs from pin')
            manifest = json.loads(path.read_text())
            raw = (path.parent / 'source.bin').read_bytes()
            if hashlib.sha256(raw).hexdigest() != manifest['source_sha256']:
                raise ValueError('Stored source bytes differ from capture pin')
        records = L.Ledger(manual)
        if any(not r.intact for r in records.records): raise ValueError('Stored page seal differs')
        if sorted((r.id, hashlib.sha256((manual / r.path).read_bytes()).hexdigest()) for r in records.records) != sorted(tuple(r) for r in entry.get('records', [])):
            raise ValueError('Stored collection page inventory differs from pin')
        combined = base / 'combined'
        combined.mkdir(exist_ok=True)
        sources = [manual]
        topics = self.topics(key)
        if topics.head(): sources.append(topics.root())
        expected = {}
        for root in sources:
            for path in root.glob('*.html'):
                expected[path.name] = path.read_bytes()
        for path in combined.glob('*.html'):
            if path.name not in expected: path.unlink()
        for name, raw in expected.items():
            if not (combined / name).exists() or (combined / name).read_bytes() != raw:
                (combined / name).write_bytes(raw)
        return combined

    def add(self, key, title, url, text, raw=None, transport='user-pasted-text'):
        base = self.path(key)
        source_url(url)
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 200:
            raise ValueError('Title needs 1–200 characters')
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 100000:
            raise ValueError('Source text needs 1–100000 characters')
        self.root(key)  # Verify retained captures before accepting another.
        payload = raw if raw is not None else text.encode()
        capture = base / 'captures' / uuid.uuid4().hex
        capture.mkdir(parents=True)
        (capture / 'source.bin').write_bytes(payload)
        manifest = {'source_url': url, 'title': title.strip(), 'observed_at': now(),
                    'source_sha256': hashlib.sha256(payload).hexdigest(),
                    'text_sha256': hashlib.sha256(text.encode()).hexdigest(), 'transport': transport,
                    'authorship': 'unknown', 'notice': 'Captured bytes, not verified truth or authorship. Pasted text is user-supplied, not a verified download.'}
        atomic_json(capture / 'manifest.json', manifest)
        body = title.strip() + '\n' + text.strip() + '\n\nSource capture: ' + json.dumps(manifest, ensure_ascii=False)
        ledger = L.Ledger(base / 'pages')
        prefix = 'WEB-' + hashlib.sha256((url + '\0' + title.strip()).encode()).hexdigest()[:16]
        old = next((r for r in ledger.servable() if r.id.startswith(prefix + '-')), None)
        if old:
            rec = L.revise(base / 'pages', old.id, body=body, origin='machine', owner='unknown')
        else:
            rec = L.write(base / 'pages', title=title.strip(), scope=title.strip(), body=body,
                          prefix=prefix, origin='machine', owner='unknown', source_authorship='unknown', external='no')
        entries = self.entries()
        entries[key].setdefault('captures', []).append({'id': capture.name, 'manifest_sha256': hashlib.sha256((capture / 'manifest.json').read_bytes()).hexdigest()})
        entries[key]['records'] = [(r.id, hashlib.sha256((base / 'pages' / r.path).read_bytes()).hexdigest()) for r in L.Ledger(base / 'pages').records]
        self.save(entries)
        self.root(key)
        return {'corpus': key, 'title': rec.title, 'id': rec.id, 'capture': manifest}
