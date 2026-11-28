"""Run frozen operator inputs. Evaluator files are never passed here."""
import hashlib
import html
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from mplpb_answers.body_text import body_text
from mplpb_answers.passage_admission import Budget
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write


def run(case, corpus):
    with TemporaryDirectory(prefix='ariadne-originals-') as root:
        records = []
        for source in case['records'] or corpus:
            doc_id = source['id']
            record = write(root, doc_id=doc_id, title=source.get('original_path', 'Synthetic memorandum'),
                           scope='original historical document', origin='machine',
                           body_html=source.get('html', '<pre>'+html.escape(source['text'])+'</pre>'),
                           when='2026-11-16T00:00Z')
            records.append({'id':doc_id, 'path':record.path, 'hash':record.hash_actual,
                            'body':body_text(record.body_html), 'withdrawn':doc_id==case['withdraw']})
        if case['withdraw']:
            withdraw(root, case['withdraw'], when='2026-11-17T00:00Z')

        mutations = []
        original_offer = Budget.offer

        def observe_offer(budget, spans, role):
            admitted = original_offer(budget, spans, role)
            if admitted and role == 'exact_documentary_subject_witnesses' and case.get('withdraw_on_admission'):
                target = case['withdraw_on_admission']
                withdraw(root, target, when='2026-11-17T00:00Z')
                mutations.append({'after':role, 'withdrawn':target})
                next(r for r in records if r['id'] == target)['withdrawn'] = True
            return admitted

        with patch.object(Budget, 'offer', observe_offer):
            answer = answer_query(root, case['question'], **case.get('bounds', {})).contract
        return {'id':case['id'], 'answer':answer, 'records':records, 'mutations':mutations}


def main():
    corpus, packet, output = map(Path, sys.argv[1:])
    sources = json.loads(corpus.read_bytes())['sources']
    rows = []
    for case in json.loads(packet.read_bytes()):
        try:
            rows.append(run(case, sources))
        except Exception as error:
            rows.append({'id':case['id'], 'error':repr(error)})
    with output.open('x') as stream:
        json.dump({'input_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(), 'rows':rows},
                  stream, ensure_ascii=False)
        stream.write('\n')


if __name__ == '__main__':
    main()
