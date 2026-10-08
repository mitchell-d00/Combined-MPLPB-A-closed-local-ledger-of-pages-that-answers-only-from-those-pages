#!/usr/bin/env python3
"""Build controlled HTML examples for the separate-source provenance gate."""
import hashlib
import html
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from mplpb_combined import ledger as L

DEST = HERE / 'examples/provenance-gate'
WHEN = '2026-10-08T00:00Z'
GAME = ('Gary Gygax and Dave Arneson wrote the original Dungeons & Dragons. '
        'TSR published the boxed set in 1974. Its fantasy rules grew from miniature wargaming.')
BUDGET = ('A general budget records expected income and planned expense categories. '
          'A planning template can separate editing, printing, and distribution. '
          'This is a synthetic general example and supplies no historical game costs.')


def build(destination):
    def game(root, both=False):
        extra = ('\n\nSynthetic test only: a budget exercise for this game lists editing, '
                 'printing, and distribution categories. These are fictional demonstration '
                 'categories, not a documented 1974 production budget.') if both else ''
        return L.write(root, doc_id='GAME-0001', title='Dungeons & Dragons · 1974',
            scope='1974 dungeons dragons game publication', when_to_use='D&D; dnd',
            body=GAME + extra, origin='machine', owner='Codex synthetic fixture',
            directory='games', when=WHEN)

    def budget(root):
        return L.write(root, doc_id='BUDGET-0001', title='General publishing budget template',
            scope='budget income expense planning template', body=BUDGET,
            origin='machine', owner='Codex synthetic fixture', directory='budgets', when=WHEN)

    for name in ('separate', 'both', 'missing', 'tampered', 'attached-source'):
        root = destination / name
        root.mkdir(parents=True)
        game(root, both=name == 'both')
        if name in ('separate', 'both', 'tampered'):
            rec = budget(root)
            if name == 'tampered':
                path = root / rec.path
                path.write_text(path.read_text().replace('expected income', 'altered income'))
        if name == 'attached-source':
            text = (DEST / 'sources/MPLPB_Cost_of_Visibility_v2.txt').read_text(encoding='utf-8')
            parent = L.write(root, doc_id='SOURCE-COST-0012',
                title='MPLPB and the Cost of Visibility · supplied paper',
                scope='MPLPB visibility consumer infrastructure economics',
                body_html='<pre>' + html.escape(text) + '</pre>', origin='human',
                owner='Mitchell D. McPhetridge (declared author in supplied paper)',
                directory='sources', when='2026-08-26T00:00Z',
                note='Verbatim supplied human-authored text; machine transport wrapper; identity not authenticated.')
            start = text.index('The residual costs are the ones')
            end = text.index('\n\nBoth reference implementations', start)
            extract = text[start:end]
            L.derive(root, [parent.id], doc_id='BUDGET-COST-0001',
                title='MPLPB consumer budget · source excerpt',
                scope='MPLPB consumer budget infrastructure cost',
                body_html='<pre>' + html.escape(extract) + '</pre>',
                owner='Codex excerpt from supplied source', directory='budgets', when=WHEN)
        L.build_index(root, 'Provenance gate · ' + name)


def main():
    with tempfile.TemporaryDirectory(prefix='mplpb-gate-demo-') as tmp:
        destination = Path(tmp)
        build(destination)
        files = {DEST / p.relative_to(destination): p.read_bytes()
                 for p in destination.rglob('*') if p.is_file()}
        for path, data in files.items():
            if path.exists() and path.read_bytes() != data:
                raise SystemExit('Preserve or explicitly remove edited demo file: ' + str(path))
        for path, data in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        lock = {str(p.relative_to(DEST)): hashlib.sha256(data).hexdigest()
                for p, data in sorted(files.items())}
        lock['sources/MPLPB_Cost_of_Visibility_v2.txt'] = hashlib.sha256(
            (DEST / 'sources/MPLPB_Cost_of_Visibility_v2.txt').read_bytes()).hexdigest()
        (DEST / 'fixture-sha256.json').write_text(json.dumps(lock, indent=2) + '\n')
    print('Built five provenance scenarios. The tampered scenario is intentionally invalid.')


if __name__ == '__main__':
    main()
