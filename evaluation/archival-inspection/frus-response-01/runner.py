"""Read only operator fixtures. Score and held expectations stay separate."""
import hashlib
import html
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write


def main():
    corpus, packet, output = map(Path,sys.argv[1:])
    public=json.loads(corpus.read_text())['sources']
    rows=[]
    for case in json.loads(packet.read_text()):
        try:
            evidence=[]
            with TemporaryDirectory(prefix='response-diagnostic-') as root:
                for source in case['records'] or public:
                    doc_id=source['id']
                    record=write(root,doc_id=doc_id,title=source.get('original_path','Synthetic correspondence'),
                                 scope='original historical document',origin='machine',
                                 body_html='<pre>'+html.escape(source['text'])+'</pre>',
                                 when='2026-11-16T00:00Z')
                    evidence.append({'id':doc_id,'path':record.path,'hash':record.hash_actual,
                                     'body':body_text(record.body_html),'withdrawn':doc_id==case['withdraw']})
                if case['withdraw']:
                    withdraw(root,case['withdraw'],when='2026-11-17T00:00Z')
                answer=answer_query(root,case['question'],max_passages=12,max_chars=8000).contract
            rows.append({'id':case['id'],'answer':answer,'records':evidence})
        except (OSError, ValueError, KeyError) as error:
            rows.append({'id':case['id'],'error':repr(error)})
    with output.open('x') as stream:
        json.dump({'input_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'rows':rows},stream,ensure_ascii=False)
        stream.write('\n')


if __name__ == '__main__':
    main()
