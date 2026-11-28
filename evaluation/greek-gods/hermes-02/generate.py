"""Generate the two deterministic synthetic Hermes-02 operator packets."""
import argparse
import json
from pathlib import Path


def packet(draw):
    if draw == 'D':
        first, peer = 'A', 'B'
        writer, reporter, author, obj = 'Eda Rill', 'Pia Vale', 'Cal Snow', 'the quarry inventory'
        question = f'In the report written by {writer}, which document did {reporter} say {author} wrote?'
        body = f'<p>Written by {writer}.</p><p>{reporter} reported that {author} wrote {obj}.</p>'
        contrasts = [('foreign', 'grant'), ('mutated', 'grant'), ('foreign', 'absent'),
                     ('local', 'absent'), ('local', 'revoke')]
    else:
        first, peer = 'B', 'A'
        writer, reporter, author, obj = 'Nora Thorne', 'Sam Cairn', 'Ada Keel', 'the kiln register'
        question = f'Which document did {reporter} report that {author} wrote, in the document from {writer}?'
        body = f'<p>From: {writer}</p><p>{reporter} stated that {author} wrote {obj}.</p>'
        contrasts = [('mutated', 'grant'), ('local', 'revoke'), ('foreign', 'grant'),
                     ('foreign', 'absent'), ('local', 'absent')]
    phases = [(first, 'local', 'grant'), *((peer, mode, auth) for mode, auth in contrasts),
              (peer, 'local', 'grant'), (first, 'repeat', 'grant'), (peer, 'repeat', 'grant')]
    return {'schema':'hermes02-packet-v1','draw':draw,'donor':first,'peer':peer,
            'records':[{'id':'NOTE-A','body_html':body}],'question':question,
            'obligation':{'writer':writer,'reporter':reporter,'author':author,'object':obj,'source_id':'NOTE-A'},
            'phases':[{'id':f'HERMES02-{draw}-{i:02d}','target':dest,'binding':mode,'authority':auth}
                      for i,(dest,mode,auth) in enumerate(phases,1)]}


if __name__ == '__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('draw',choices=['D','F'])
    cli.add_argument('output',type=Path)
    args=cli.parse_args()
    with args.output.open('x') as out:
        out.write(json.dumps(packet(args.draw),indent=2)+'\n')
