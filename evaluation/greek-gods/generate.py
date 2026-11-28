"""Generate Heka's Greek follow-up operator packets deterministically."""
import argparse
import json
from pathlib import Path

D = [
    ('ATHENA', 'positive', 'different-writer'),
    ('ATHENA', 'wrong-reporter', 'different-writer'),
    ('ATHENA', 'withdrawn', 'single'),
    ('ATHENA', 'withdraw-between', 'different-writer'),
    ('HERMES', 'advice-only', 'single'),
    ('HERMES', 'revoked', 'single'),
    ('HERMES', 'wrong-receipt', 'single'),
    ('HERMES', 'conflicting-grants', 'controller'),
    ('HERMES', 'stale-receipt', 'controller'),
    ('HEPHAESTUS', 'restart-completed', 'single'),
    ('HEPHAESTUS', 'restart-failed', 'single'),
    ('HEPHAESTUS', 'restart-interrupted', 'single'),
]

F = [
    ('ATHENA', 'positive', 'different-writer'),
    ('ATHENA', 'duplicate-writer', 'single'),
    ('ATHENA', 'withdraw-between', 'single'),
    ('ATHENA', 'unrelated-change', 'single'),
    ('HERMES', 'missing-grant', 'single'),
    ('HERMES', 'wrong-target', 'single'),
    ('HERMES', 'wrong-action', 'controller'),
    ('HERMES', 'conflicting-receipts', 'controller'),
    ('HERMES', 'wrong-receipt', 'different-writer'),
    ('HEPHAESTUS', 'restart-interrupted', 'different-writer'),
    ('HEPHAESTUS', 'restart-failed', 'different-writer'),
    ('HEPHAESTUS', 'unavailable-store', 'single'),
    ('HEPHAESTUS', 'restart-completed', 'different-writer'),
]


def packet(draw):
    plans = D if draw == 'D' else F
    cases = []
    positions = {}
    for set_name, scenario, layout in plans:
        n = positions.get(set_name, 0) + 1
        positions[set_name] = n
        ident = f'GREEK-{set_name}-{draw}-{n:02d}'
        if draw == 'D':
            writer, reporter, author, other = 'Neri Vale', 'Iris Salt', 'Arlo Bay', 'Tova Dale'
            item = 'the glasshouse log'
            requested = other if scenario == 'wrong-reporter' else reporter
            question = f'In the report written by {writer}, which document did {requested} say {author} wrote?'
            byline = f'Written by {writer}.'
            statement = f'{reporter} reported that {author} wrote {item}.'
        else:
            writer, reporter, author, other = 'Nia Harlow', 'Sami Finch', 'Jo Pike', 'Mira Dart'
            item = 'the observatory chart'
            requested = reporter
            question = f'Which document did {reporter} report that {author} wrote, in the document from {writer}?'
            byline = f'From: {writer}'
            statement = f'{reporter} stated that {author} wrote {item}.'
        records = [{'id':'NOTE-A','body_html':f'<p>{byline}</p><p>{statement}</p>'}]
        if layout == 'different-writer':
            # This source has its own printed writer and can never satisfy the
            # requested byline, even if it has the requested embedded speaker.
            quote = (f'{other} reported that {author} wrote the attic inventory.'
                     if scenario == 'wrong-reporter'
                     else f'{reporter} stated that {author} wrote the spare inventory.')
            records.append({'id':'NOTE-Q','body_html':f'<p>Written by Ella Snow.</p><p>{quote}</p>'})
        cases.append({'id':ident,'set':set_name,'lane':'controller' if layout == 'controller' else 'bridge',
                      'scenario':scenario,'question':question,'records':records,
                      'obligation':{'writer':writer,'reporter':requested,'author':author,'object':item,'source_id':'NOTE-A'}})
    return {'schema':'greek-sprint-packet-v1','draw':draw,'cases':cases}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('draw', choices=['D','F'])
    p.add_argument('path',type=Path)
    args=p.parse_args()
    with args.path.open('x') as out:
        out.write(json.dumps(packet(args.draw),indent=2)+'\n')
