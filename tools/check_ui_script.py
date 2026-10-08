#!/usr/bin/env python3
"""Check frontend logic locally with Node (optional developer check, no browser)."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.ledger_ui import App


def main():
    node = shutil.which('node')
    if not node:
        raise SystemExit('Node is needed for this optional script check, not for running the UI.')
    app = App()
    data = {'state': app.state(), 'inventory': {}, 'queries': {}, 'pages': {},
            'history': app.history(), 'experiment': app.experiment()}
    for corpus in ('canned', 'dogs'):
        for profile in ('internal', 'external'):
            data['inventory'][corpus + '|' + profile] = app.inventory(corpus, profile)
            questions = (['Phrynomedusa vanzolinii Hyundai Engineering and Construction',
                          'Phrynomedusa vanzolinii'] if corpus == 'canned' else ['dog'])
            for q in questions:
                data['queries'][corpus + '|' + profile + '|' + q] = app.query(
                    dict(corpus=corpus, profile=profile, question=q))
            for rec in data['inventory'][corpus + '|' + profile]['pages']:
                if rec['eligible']:
                    data['pages'][corpus + '|' + profile + '|' + rec['path']] = app.page(
                        corpus, rec['path'], profile)
    return subprocess.run([node, str(ROOT / 'tools/check_ui_script.cjs'), str(ROOT / 'index.html')],
                          input=json.dumps(data), text=True, cwd=ROOT).returncode


if __name__ == '__main__':
    raise SystemExit(main())
