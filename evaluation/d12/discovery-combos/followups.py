"""Compare ordinary and graph discovery on the 40 historical follow-ups."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from replay import BUDGET, DATA, FAMILIES, PROFILE, ROOT, fuse, retrieve, visible
from mplpb_answers.passages import PassageIndex
from mplpb_answers.synonym_graph import build, open_index
from test_tools.historical_patterns import ARMS, PANEL
from tools.unprepared_challenge import frozen, read, save, sha
from tools.unprepared_sources import import_corpus

out = Path(sys.argv[1])
panel_sha = sha(PANEL.read_bytes())
assert panel_sha == PANEL.with_suffix('.sha256').read_text().split()[0]
rows = []
with TemporaryDirectory() as folder:
    root = Path(folder)
    build(root/'graph.db', read(DATA/'catalog.json'))
    with open_index(root/'graph.db') as graph:
        for name, (relative, seal) in FAMILIES.items():
            frozen(ROOT/relative, seal)
            ledger = root/name
            import_corpus(ROOT/relative, ledger)
            for group in read(PANEL)['groups']:
                if group['corpus'] != name:
                    continue
                first = group['anchors'][0]['quote']
                questions = {'quote':f'Which source contains the exact words "{first}"?',**group['questions']}
                for arm in ARMS:
                    q = questions[arm]
                    index = PassageIndex(ledger,q,PROFILE)
                    normal = retrieve(index,q)
                    ids = graph.lookup(name,q)['records']
                    hinted = retrieve(index,q,ids) if ids else normal
                    combo = fuse([normal,hinted], BUDGET)
                    anchors = group['anchors'][:1] if arm=='quote' else group['anchors']
                    rows.append({'id':group['id']+'-'+arm,'arm':arm,'anchor_count':len(anchors),
                                 'matches':{arm:visible(anchors,{'passages':p}) for arm,p in
                                            [('ordinary',normal),('graph',hinted),('combined',combo)]}})
assert len(rows)==40
summary = {}
for variant in ('all','direct_and_paraphrase'):
    selected = [row for row in rows if variant=='all' or row['arm'] in ('direct','paraphrase')]
    summary[variant] = {}
    for method in ('ordinary','graph','combined'):
        summary[variant][method] = {
            'cases':len(selected),
            'complete':sum(row['matches'][method]==row['anchor_count'] for row in selected),
            'anchors':sum(row['matches'][method] for row in selected),
            'improved':sum(row['matches'][method]>row['matches']['ordinary'] for row in selected),
            'regressed':sum(row['matches'][method]<row['matches']['ordinary'] for row in selected)}
result={'panel_sha256':panel_sha,'summary':summary,'cases':rows}
save(out, result)
print(json.dumps(summary,indent=2))
