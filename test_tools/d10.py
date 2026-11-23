"""Freeze, run, and score matched D10 draws for the D% exact-anchor suite."""
import argparse
from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import random
import re
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from test_tools.d10_capture import sample
from test_tools.d10_index import digest
from test_tools.primary_book_test import controls, question_digest, read_json, write_json


SCHEMA = 'mplpb-d10-exact-anchor-v1'


def capture_inputs(folder, seed):
    receipt = read_json(folder / 'manifest.json')
    original = (folder / 'source.bin').read_bytes()
    excerpt = (folder / 'sample.txt').read_bytes()
    source_pin = sha256(original).hexdigest()
    span = receipt['sample']
    if (receipt['schema'] != 'mplpb-d10-capture-v1' or receipt['seed'] != seed
            or receipt['source']['sha256'] != source_pin or receipt['source']['bytes'] != len(original)
            or span['sha256'] != sha256(excerpt).hexdigest()
            or sample(original, seed, source_pin) != (span['byte_start'], excerpt)
            or span['byte_end'] != span['byte_start'] + len(excerpt)):
        raise ValueError('Frozen source, seed, or exact sample failed verification')
    return receipt, original, excerpt


def prepare(plan_file, captures, output, custody):
    plan = read_json(plan_file)
    if (plan['schema'] != 'mplpb-d10-draw-plan-v1' or plan['suite'] != 'exact_anchor'
            or len(plan['draws']) != 10):
        raise ValueError('Provide a ten-draw exact_anchor plan')
    ids = [row['id'] for row in plan['draws']]
    if ids != [f'D10-{n:02}' for n in range(1, 11)] or not set(captures) <= set(ids) or not captures:
        raise ValueError('Provide at least one unique capture mapped to an ID in the ten-draw plan')
    output, custody = output.resolve(), custody.resolve()
    if output.exists() or custody.exists() or output in custody.parents or custody in output.parents or output == custody:
        raise ValueError('Choose two new, disjoint output and custody directories')

    frozen = {key: capture_inputs(captures[key], plan['seed']) for key in ids if key in captures}
    if len({receipt['source']['sha256'] for receipt, _, _ in frozen.values()}) != len(frozen):
        raise ValueError('Each filled draw needs a distinct captured original')
    seed = int(digest({'plan': plan, 'captures': [receipt['sample']['sha256']
                                                for receipt, _, _ in frozen.values()]}), 16)
    questions, expected = controls(random.Random(seed), {key: data[2].decode('utf-8')
                                                         for key, data in frozen.items()})
    manifest = {'schema': SCHEMA, 'plan_sha256': digest(plan), 'questions_sha256': question_digest(questions),
                'key_cases_sha256': digest(expected),
                'draws': [dict(row, status='filled' if row['id'] in frozen else 'unfilled') for row in plan['draws']],
                'sources': {key: receipt for key, (receipt, _, _) in frozen.items()}}
    output.mkdir()
    custody.mkdir(mode=0o700)
    for key, (_, original, excerpt) in frozen.items():
        (output / f'{key}.txt').write_bytes(excerpt)
        (custody / f'{key}.bin').write_bytes(original)
    write_json(output / 'manifest.json', manifest)
    write_json(output / 'questions.json', questions)
    write_json(custody / 'key.json', {'packet_sha256': digest(manifest), 'cases': expected})


def read_inputs(inputs):
    manifest, questions = (read_json(inputs / name) for name in ('manifest.json', 'questions.json'))
    if (manifest['schema'] != SCHEMA or not questions
            or question_digest(questions) != manifest['questions_sha256']
            or len({row['id'] for row in questions}) != len(questions)):
        raise ValueError('Invalid packet or changed questions')
    return manifest, questions


def source_records(inputs, manifest, ledger):
    records = {}
    for ident, receipt in sorted(manifest['sources'].items()):
        if not re.fullmatch(r'D10-(?:0[1-9]|10)', ident):
            raise ValueError('Invalid source identifier')
        raw = (inputs / f'{ident}.txt').read_bytes()
        if sha256(raw).hexdigest() != receipt['sample']['sha256']:
            raise ValueError('Source sample does not match the frozen packet')
        record = write(ledger, doc_id=ident, title=f'D10 source {ident}', scope='quotation location',
                       body_html=f'<pre>{escape(raw.decode("utf-8"))}</pre>',
                       when='2026-11-23T00:00Z', origin='machine')
        records[ident] = (record, body_text(record.body_html))
    return records


def run(inputs):
    manifest, questions = read_inputs(inputs)
    with TemporaryDirectory() as folder:
        source_records(inputs, manifest, folder)
        rows = [{'id': row['id'], 'answer': answer_query(folder, row['question'], mode='strict').contract}
                for row in questions]
    return {'schema': SCHEMA, 'packet_sha256': digest(manifest), 'cases': rows}


def valid_cite(cite, records):
    match = records.get(cite.get('source_id'))
    if match is None:
        return False
    record, body = match
    start, end = cite.get('body_start'), cite.get('body_end')
    return (cite.get('path') == record.path and cite.get('hash') == record.hash_actual
            and type(start) is int and type(end) is int and 0 <= start < end <= len(body)
            and cite.get('quote') == body[start:end])


def score(inputs, report, key):
    manifest, questions = read_inputs(inputs)
    pin = digest(manifest)
    if (report['schema'] != SCHEMA or any(data['packet_sha256'] != pin for data in (report, key))
            or digest(key['cases']) != manifest['key_cases_sha256']):
        raise ValueError('Run and key must match the frozen packet')
    expected = {row['id']: row for row in key['cases']}
    actual = {row['id']: row['answer'] for row in report['cases']}
    items = {row['id']: row['question'] for row in questions}
    if (len(expected) != len(key['cases']) or len(actual) != len(report['cases'])
            or not (expected.keys() == actual.keys() == items.keys())):
        raise ValueError('Question coverage differs from the frozen question set')
    rows = []
    with TemporaryDirectory() as folder:
        records = source_records(inputs, manifest, folder)
        for ident, answer in actual.items():
            target = expected[ident]
            cites = [cite for claim in answer['claims'] for cite in claim['citations']]
            if answer['question'] != items[ident] or not all(valid_cite(cite, records) for cite in cites):
                outcome = 'invalid_evidence'
            elif target['source_id'] is None:
                outcome = 'false_support' if answer['answer_supported'] else 'withheld'
            elif not answer['answer_supported']:
                outcome = 'missed'
            elif any(cite['source_id'] == target['source_id'] and target['quote'] in cite['quote'] for cite in cites):
                outcome = 'exact_source_and_quote'
            else:
                outcome = 'incorrect_support'
            rows.append({'id': ident, 'outcome': outcome, 'native_kind': answer['kind']})
    totals = dict(Counter(row['outcome'] for row in rows))
    return {'schema': SCHEMA, 'packet_sha256': pin, 'draws': manifest['draws'], 'totals': totals,
            'filled': len(manifest['sources']), 'unfilled': len(manifest['draws']) - len(manifest['sources']),
            'cases': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_args = commands.add_parser('prepare')
    prepare_args.add_argument('--plan', type=Path, required=True)
    prepare_args.add_argument('--capture', action='append', metavar='DRAW=DIR', required=True)
    for name in ('run', 'score'):
        command = commands.add_parser(name)
        command.add_argument('--inputs', type=Path, required=True)
        if name == 'score':
            command.add_argument('--run', type=Path, required=True)
            command.add_argument('--key', type=Path, required=True)
        command.add_argument('--output', type=Path, required=True)
    prepare_args.add_argument('--output', type=Path, required=True)
    prepare_args.add_argument('--custody', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            captures = dict((key, Path(path)) for key, path in (item.split('=', 1) for item in args.capture))
            if len(captures) != len(args.capture):
                raise ValueError('Duplicate capture mapping')
            prepare(args.plan, captures, args.output, args.custody)
        elif args.command == 'run':
            write_json(args.output, run(args.inputs))
        else:
            outcome = score(args.inputs, read_json(args.run), read_json(args.key))
            write_json(args.output, outcome)
            return int(any(outcome['totals'].get(key, 0) != outcome['filled']
                           for key in ('exact_source_and_quote', 'withheld')))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'{exc}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
