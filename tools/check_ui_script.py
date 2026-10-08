#!/usr/bin/env python3
"""Check frontend logic locally with Node (optional developer check, no browser)."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.ledger_ui import App


def main():
    node = shutil.which('node')
    if not node:
        raise SystemExit('Node is needed for this optional script check, not for running the UI.')
    workspace = tempfile.TemporaryDirectory()
    app = App(topic_base=workspace.name)
    data = {'state': app.state(), 'inventory': {}, 'queries': {}, 'pages': {},
            'history': app.history(), 'experiment': app.experiment(), 'chats': {}}
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
    sid = None
    for message in ('relate Dungeons and Dragons -> game', 'who made you?', 'guide me'):
        data['chats'][message] = app.chat(dict(corpus='logic', message=message, session=sid))
        sid = data['chats'][message]['session']
    data['resume'] = app.resume_chat(dict(session=sid))
    data['queries']['canned|internal|How do I clear mplpb some or all?']=app.query(dict(corpus='canned',question='How do I clear mplpb some or all?'))
    result = subprocess.run([node, str(ROOT / 'tools/check_ui_script.cjs'), str(ROOT / 'index.html')],
                          input=json.dumps(data), text=True, cwd=ROOT).returncode
    workspace.cleanup()
    return result


if __name__ == '__main__':
    raise SystemExit(main())
