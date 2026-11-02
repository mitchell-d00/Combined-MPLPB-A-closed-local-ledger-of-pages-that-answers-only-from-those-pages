"""Check explicit documentation reviews, preserved history and result/test links.

No wall-clock stamping: an explicit review date is a human/developer assertion,
not evidence that historic experiments were rerun.
"""
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import subprocess

DOC_SUFFIXES = {'.md', '.txt', '.rst', '.pdf', '.tex'}


def tracked(root):
    if (root / '.git').exists():
        return subprocess.check_output(['git', 'ls-files'], cwd=root, text=True).splitlines()
    manifest = json.loads((root / 'handoff/manifest.json').read_text())
    return sorted(set(manifest['files']) | {'HANDOFF.md', 'handoff/manifest.json'})


def safe(root, name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Unsafe documentation path: ' + name)
    target = root / path
    target.resolve().relative_to(root.resolve())
    return target


def iso(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError('Invalid review date')
    return value


def audit(root, names=None, as_of=None):
    root = Path(root)
    names = tracked(root) if names is None else names
    catalog = json.loads((root / 'docs/documentation.json').read_text())
    if catalog.get('schema') != 'documentation-review-v1':
        raise ValueError('Unknown documentation inventory')
    reviewed = iso(catalog['reviewed_on'])
    if as_of and reviewed != iso(as_of):
        raise ValueError('Stale inventory review date')
    docs = {n for n in names if Path(n).suffix.lower() in DOC_SUFFIXES or n == 'CONTENTS'}
    entries = catalog['documents']
    if docs != set(entries):
        raise ValueError('Unclassified or removed documents: ' + str(sorted(docs ^ set(entries))))
    for name, entry in entries.items():
        path = safe(root, name)
        kind = entry['classification']
        if not entry.get('reason'):
            raise ValueError('Missing classification reason: ' + name)
        if kind in {'historical', 'vendor'}:
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('Historical/vendor bytes changed: ' + name)
        elif kind == 'current':
            when = iso(entry['reviewed_on'])
            if as_of and when != as_of:
                raise ValueError('Stale guide review: ' + name)
            text = path.read_text()
            markers = re.findall(r'^Last reviewed: (\d{4}-\d{2}-\d{2})\.', text, re.M)
            if markers != [when]:
                raise ValueError('Missing, duplicate or stale review marker: ' + name)
            # Only current Markdown guides: old reports retain their original links.
            if path.suffix.lower() == '.md':
                for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^\s)]+)\)', text):
                    target = target.split('#', 1)[0]
                    if not target or re.match(r'^[a-zA-Z]+:', target):
                        continue
                    dest = path.parent / target
                    dest.resolve().relative_to(root.resolve())
                    if not dest.exists():
                        raise ValueError('Broken current guide link: ' + name + ' -> ' + target)
        else:
            raise ValueError('Unknown classification: ' + name)
    registry = json.loads((root / 'docs/results.json').read_text())
    if registry.get('schema') != 'result-test-index-v1' or iso(registry['reviewed_on']) != reviewed:
        raise ValueError('Stale or unknown result index')
    families = registry['families']
    actual = {p.name for p in (root / 'evaluation').iterdir() if p.is_dir()}
    expected = actual | {'root', 'killtest'}
    if len(families) != len(expected) or {r['family'] for r in families} != expected:
        raise ValueError('Unindexed or duplicate evaluation family')
    for row in families:
        if not row.get('scope') or not row.get('measurement_status') or not row.get('tests') or not row.get('runners'):
            raise ValueError('Incomplete result/test scope: ' + row['family'])
        for name in [row['artifacts']] + row['tests'] + row['runners']:
            if not safe(root, name).exists():
                raise ValueError('Missing result/test/reproduction path: ' + name)
    return {'reviewed_on': reviewed, 'inspected_revision': catalog['inspected_revision'],
            'documents': len(docs), 'classifications': dict(Counter(e['classification'] for e in entries.values())),
            'evaluation_families': len(families),
            'meaning': 'Inventory, preserved bytes and retained test/tool paths checked; historical metrics are not rerun by this check.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--as-of', help='Require all current guides to have this explicitly recorded review date')
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.root, as_of=args.as_of), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
