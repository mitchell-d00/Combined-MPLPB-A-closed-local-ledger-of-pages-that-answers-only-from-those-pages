#!/usr/bin/env python3
"""Build frozen topic HTML fixtures without modifying the reader.

python3 tools/build_topic_examples.py
python3 tools/build_topic_examples.py --check
"""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from mplpb_combined.ledger import write, build_index


def build(destination):
    spec_path = HERE / 'evaluation/topics/spec.json'
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    manifest = {'provenance': spec['provenance'], 'domains': []}
    hashes = {}
    for domain in spec['domains']:
        root = destination / domain['name']
        root.mkdir(parents=True)
        for page in domain['pages']:
            kwargs = {k: v for k, v in page.items() if k != 'sources'}
            rec = write(root, **kwargs, origin='machine', owner='Codex synthetic fixture',
                        when='2026-10-08T00:00Z')
            hashes[domain['name'] + '/' + rec.path] = rec.hash_actual
        build_index(root, domain['title'])
        probe_bytes = (json.dumps({'probes': domain['probes']}, indent=2,
                                 ensure_ascii=False) + '\n').encode('utf-8')
        (root / 'probes.json').write_bytes(probe_bytes)
        manifest['domains'].append({'name': domain['name'],
            'root': '../../examples/topics/' + domain['name'],
            'probes': '../../examples/topics/' + domain['name'] + '/probes.json',
            'sha256': hashlib.sha256(probe_bytes).hexdigest()})
    return manifest, {'spec_sha256': hashlib.sha256(spec_path.read_bytes()).hexdigest(),
                      'corpus_hashes': hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify committed fixture bytes')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='mplpb-topics-') as tmp:
        generated = Path(tmp) / 'topics'
        manifest, hashes = build(generated)
        files = {HERE / 'examples/topics' / p.relative_to(generated): p.read_bytes()
                 for p in generated.rglob('*') if p.is_file()}
        for name, data in [('manifest.json', manifest), ('corpus-lock.json', hashes)]:
            files[HERE / 'evaluation/topics' / name] = (
                json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
        extra = {p for p in (HERE / 'examples/topics').rglob('*') if p.is_file()} - set(files)
        if extra:
            raise SystemExit('Unexpected files in generated fixture directory: ' +
                             ', '.join(str(p) for p in sorted(extra)))
        for path, data in files.items():
            if path.exists() and path.read_bytes() != data:
                raise SystemExit('Fixture differs; preserve it or remove it explicitly: ' + str(path))
            if args.check:
                if not path.exists():
                    raise SystemExit('Missing fixture: ' + str(path))
        if not args.check:
            for path, data in files.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    print(('Verified' if args.check else 'Built') + ' 30 pages, 6 indexes, and 90 frozen probes.')


if __name__ == '__main__':
    main()
