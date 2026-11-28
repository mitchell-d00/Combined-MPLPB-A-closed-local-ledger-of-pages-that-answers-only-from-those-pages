"""Strict-only probe with Heka's original fixture and snapshot boundary."""
import json
from pathlib import Path
import sys

from mplpb_answers.documentary_verify import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw
from mplpb_combined.record import parse_page

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'heka-01'))
from reader import digest, prepare


def snapshot(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def probe(root, case):
    before = snapshot(root)
    answer = answer_query(root, case['question'], mode='strict').contract
    originals = {}
    for source in answer['sources']:
        path = source['path']
        file = root / path
        file.resolve().relative_to(root.resolve())
        raw = file.read_bytes()
        parsed = parse_page(raw.decode(), path)
        originals[path] = {'id': parsed.id, 'hash': parsed.hash_actual, 'intact': parsed.intact,
                           'bytes_sha256': digest(raw), 'body_text': body_text(parsed.body_html)}
    if before != snapshot(root):
        raise RuntimeError('Ledger changed during native reader probe')
    return {'answer': answer, 'snapshot': before, 'originals': originals}


def main():
    operation, path, input_path = sys.argv[1:]
    root = Path(path)
    case = json.loads(Path(input_path).read_text())
    if operation == 'prepare':
        prepare(root, case)
    elif operation == 'withdraw':
        withdraw(root, case['records'][0]['id'], when='2026-11-27T00:01:00Z')
    elif operation == 'probe':
        print(json.dumps(probe(root, case), ensure_ascii=False))
    else:
        raise ValueError('Unknown native operation')


if __name__ == '__main__':
    main()
