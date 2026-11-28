"""Generate deterministic Ares-01 source and interleaving cases."""
import argparse
import json
from pathlib import Path


def packet(draw):
    if draw == 'D':
        writer, reporter, author, obj = 'Hana Wren','Eli Dune','Nell Hart','the canal ledger'
        body = f'<p>Written by {writer}.</p><p>{reporter} reported that {author} wrote {obj}.</p>'
        question = f'In the report written by {writer}, which document did {reporter} say {author} wrote?'
        order = ['active','pre-check','stale-cache','restart','post-check']
    else:
        writer, reporter, author, obj = 'Mina Webb','Ivo Moss','Bea Hale','the school register'
        body = f'<p>From: {writer}</p><p>{reporter} stated that {author} wrote {obj}.</p>'
        question = f'Which document did {reporter} report that {author} wrote, in the document from {writer}?'
        order = ['stale-cache','post-check','active','restart','pre-check']
    return {'schema':'ares01-packet-v1','draw':draw,'cases':[
        {'id':f'ARES-{draw}-{i:02d}','scenario':scenario,'question':question,
         'records':[{'id':'NOTE-A','body_html':body}],
         'obligation':{'writer':writer,'reporter':reporter,'author':author,'object':obj,'source_id':'NOTE-A'}}
        for i,scenario in enumerate(order,1)
    ]}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('draw',choices=['D','F'])
    p.add_argument('path',type=Path)
    args=p.parse_args()
    with args.path.open('x') as stream:
        stream.write(json.dumps(packet(args.draw),indent=2)+'\n')
