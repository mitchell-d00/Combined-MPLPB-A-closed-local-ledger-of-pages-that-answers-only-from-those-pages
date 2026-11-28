"""Generate the deterministic Apollo-01 lab operator packets."""
import argparse
import json
from pathlib import Path

D = ('valid','changed-payload','unknown-key','retired-key','wrong-namespace','unsupported','missing-grant')
F = ('retired-key','valid','unsupported','wrong-target','missing-grant','unknown-key','changed-payload')


def packet(draw):
    if draw == 'D':
        writer, reporter, author, other = 'Tess Rill','Sima Nor','Del Voss','Tara Glen'
        obj = 'the garden inventory'
        byline = f'Written by {writer}.'
        question = f'In the report written by {writer}, which document did {reporter} say {author} wrote?'
        statement = f'{reporter} reported that {author} wrote {obj}.'
    else:
        writer, reporter, author, other = 'Ona Pike','Maris Holt','Emil Senn','Dena Ward'
        obj = 'the river catalogue'
        byline = f'From: {writer}'
        question = f'Which document did {reporter} report that {author} wrote, in the document from {writer}?'
        statement = f'{reporter} stated that {author} wrote {obj}.'
    rows = []
    for i, scenario in enumerate(D if draw == 'D' else F, 1):
        name = other if scenario == 'unsupported' else reporter
        rows.append({'id':f'APOLLO-{draw}-{i:02d}','scenario':scenario,
                     'records':[{'id':'NOTE-A','body_html':f'<p>{byline}</p><p>{statement}</p>'}],
                     'question':question.replace(reporter,name),
                     'obligation':{'writer':writer,'reporter':name,'author':author,'object':obj,'source_id':'NOTE-A'}})
    return {'schema':'apollo01-packet-v1','draw':draw,'cases':rows}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draw',choices=['D','F'])
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    with args.output.open('x') as out:
        out.write(json.dumps(packet(args.draw),indent=2)+'\n')
