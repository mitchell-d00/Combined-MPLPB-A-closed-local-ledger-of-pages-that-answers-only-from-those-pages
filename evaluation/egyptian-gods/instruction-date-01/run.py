"""Native read-only replay. Receives only operator inputs and runtime source."""
import hashlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

runtime, inputs = sys.argv[1:]
sys.path.insert(0, runtime)

from mplpb_answers.documentary_verify import body_text
from mplpb_combined.ledger import write, withdraw
from mplpb_answers.pipeline import answer_query


def probe(case):
    with TemporaryDirectory(prefix='instruction-evidence-') as temp:
        root = Path(temp)
        records = []
        for source in case['sources']:
            record = write(root, doc_id=source['id'], title='Synthetic archive report',
                           scope='documentary evidence', origin='machine', external='yes',
                           when='2026-11-28T00:00:00Z', body_html=source['body_html'])
            records.append({'id': record.id, 'path': record.path, 'hash': record.hash_actual,
                            'file_sha256': hashlib.sha256((root / record.path).read_bytes()).hexdigest(),
                            'body': body_text(record.body_html)})
        budget = case['budget']

        def read():
            return answer_query(root, case['question'], mode='strict', max_passages=budget['passages'],
                                max_chars=budget['characters']).contract

        result = {'id': case['id'], 'records': records, 'initial': read(), 'reread': None}
        if case['withdraw_before_reread']:
            withdraw(root, 'REPORT', when='2026-11-28T00:01:00Z')
            result['reread'] = read()
        return result


for item in json.loads(Path(inputs).read_text()):
    try:
        print(json.dumps(probe(item), ensure_ascii=False), flush=True)
    except Exception as error:
        print(json.dumps({'id': item['id'], 'execution_error': repr(error)}), flush=True)
