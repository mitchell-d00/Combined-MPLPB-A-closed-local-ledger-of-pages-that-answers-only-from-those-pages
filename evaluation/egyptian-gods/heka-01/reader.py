"""Fixed synthetic-ledger driver for the frozen Heka reader snapshot."""

import hashlib
import json
import sys
from pathlib import Path

from mplpb_answers.documentary_verify import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write
from mplpb_combined.record import parse_page


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_record(root, spec):
    return write(root, doc_id=spec['id'], title='Heka synthetic report',
                 scope='archival records', origin='machine', external='yes',
                 when='2026-11-27T00:00:00Z', body_html=spec['body_html'])


def prepare(root, case):
    root.mkdir()
    for document in case['records']:
        write_record(root, document)
    if case['scenario'] == 'duplicate-writer':
        write_record(root, {**case['records'][0], 'id': 'NOTE-B'})
    if case['scenario'] == 'withdrawn':
        withdraw(root, 'NOTE-A', when='2026-11-27T00:01:00Z')


def change(root, case):
    if case['scenario'] == 'withdraw-between':
        withdraw(root, 'NOTE-A', when='2026-11-27T00:01:00Z')
    elif case['scenario'] == 'unrelated-change':
        write_record(root, {'id': 'NOTE-B', 'body_html': '<p>Cabinet inventory pending.</p>'})
    else:
        raise ValueError('Unknown source mutation')


def probe(root, case):
    snapshot = {p.relative_to(root).as_posix(): digest(p.read_bytes())
                for p in sorted(root.rglob('*')) if p.is_file()}
    answer = answer_query(root, case['question'], mode='strict').contract
    selection = answer.get('documentary_support', {}).get('named_source_selection')
    selected = None
    if selection and selection['status'] == 'verified':
        source = root / selection['path']
        source.resolve().relative_to(root.resolve())
        raw = source.read_bytes()
        record = parse_page(raw.decode(), selection['path'])
        selected = {'bytes_sha256': digest(raw), 'id': record.id,
                    'hash': record.hash_actual, 'intact': record.intact,
                    'body_html': record.body_html, 'body_text': body_text(record.body_html)}
    final_snapshot = {p.relative_to(root).as_posix(): digest(p.read_bytes())
                      for p in sorted(root.rglob('*')) if p.is_file()}
    if final_snapshot != snapshot:
        raise RuntimeError('Ledger changed during the probe')
    return {'snapshot': snapshot, 'answer': answer, 'selected': selected}


def main():
    operation, path, case_file = sys.argv[1:]
    root = Path(path)
    case = json.loads(Path(case_file).read_text())
    if operation == 'prepare':
        prepare(root, case)
    elif operation == 'change':
        change(root, case)
    elif operation == 'probe':
        print(json.dumps(probe(root, case)))
    else:
        raise ValueError('Unknown reader operation')


if __name__ == '__main__':
    main()
