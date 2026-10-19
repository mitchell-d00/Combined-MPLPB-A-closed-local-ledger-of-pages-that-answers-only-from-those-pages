"""Export a build-time, externally eligible snapshot of bundled pages only.

This file is not a second reader: it delegates profile eligibility and page
serialization to the actual MPLPB App. Browser-local imports are never read.
"""
import json
from pathlib import Path
from tools.ledger_ui import App

BUNDLED = ('canned', 'studio', 'gate', 'dogs', 'system', 'logic', 'reference')

def export_public_ledger(target):
    app = App()
    roots = app.roots()
    output = {
        'schema': 'mplpb-published-external-pages-v1',
        'profile': 'external',
        'notice': 'Build-time snapshot of externally eligible bundled pages. Not the live browser ledger. Source declarations do not authenticate truth or authorship.',
        'corpora': []
    }
    for key in BUNDLED:
        if key not in roots:
            continue
        inventory = app.inventory(key, 'external')
        pages = []
        for row in inventory['pages']:
            if not row['eligible']:
                continue
            page = app.page(key, row['path'], 'external')
            pages.append({field: page[field] for field in
                          ('id', 'title', 'path', 'text', 'hash', 'depth')})
        output['corpora'].append({'key': key, 'label': roots[key][0],
                                  'eligible': len(pages), 'pages': pages})
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')) + '\n',
                      encoding='utf-8')
    return output
