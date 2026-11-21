"""Generate and run the Primary Book Test from pinned public-domain editions."""
import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import random
import re
import secrets
from tempfile import TemporaryDirectory
from urllib.request import urlopen
from xml.etree import ElementTree as ET


BOOKS = (
    ('darwin', 'Charles Darwin', 'The Voyage of the Beagle',
     'charles-darwin_the-voyage-of-the-beagle', 'e87d0e1b863a76e02cc7500a0771c586eebcd52c',
     ('b3d64175fb0c722abb3314257cc136fbcded8be139e341733763e4c8540aeaad',
      '0a75258582da985e0ae20579374fc4cd96dc24ca2d933ee81c832a42d0f5a0a1')),
    ('seacole', 'Mary Seacole', 'Wonderful Adventures of Mrs. Seacole in Many Lands',
     'mary-seacole_wonderful-adventures-of-mrs-seacole-in-many-lands', 'dfb3dcf4b1902e22bb6be78af82fd5a5b37ed4dc',
     ('ea3d3c9ae5c9aa788b980897470a24df595e837c6d43cf8a93fafa8f027a48f5',
      'b898a306c328bbe77e695fcd312b59f88a8f36a4d80fa5d9c19c05ef5e778315')),
    ('washington', 'Booker T. Washington', 'Up from Slavery',
     'booker-t-washington_up-from-slavery', '199eff4264acb3d0f97fccd55d8b9e2e4ebae794',
     ('ed369b8ebf81ead543f71f3f7366df868c54888e4a7b470a05a69ecabf5581f5',
      '864ba98c29ea0121e074f9661d7631bdfd22f3596d002c13e027901716d3793c')),
)
RIGHTS = 'https://creativecommons.org/publicdomain/zero/1.0/'


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_chapter(slug, repo, revision, chapter, digest, source_dir):
    name = f'{slug}-chapter-{chapter}.xhtml'
    url = f'https://raw.githubusercontent.com/standardebooks/{repo}/{revision}/src/epub/text/chapter-{chapter}.xhtml'
    if source_dir is None:
        with urlopen(url, timeout=20) as response:
            raw = response.read(256_001)
    else:
        raw = (source_dir / name).read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f'Chapter checksum mismatch for {name}')
    return name, url, raw


def windows(raw):
    paragraphs = ET.fromstring(raw).findall('.//{*}body//{*}p')
    text = ['' if p.get('{http://www.idpf.org/2007/ops}type') in {'title', 'se:bridgehead'}
            else ''.join(p.itertext()).strip() for p in paragraphs]
    return [(index, first + '\n\n' + second)
            for index, (first, second) in enumerate(zip(text, text[1:]), start=1)
            if 350 <= len(first) + len(second) <= 3500 and min(len(first), len(second)) >= 120]


def controls(rng, excerpts):
    cases = []
    text = {ident: body.casefold() for ident, body in excerpts.items()}
    for ident, body in excerpts.items():
        options = []
        for match in re.finditer(r'(?=(\b[A-Za-z]+(?: [A-Za-z]+){5}\b))', body):
            quote = match[1]
            prefix, one, two = quote.rsplit(' ', 2)
            altered = f'{prefix} {two} {one}'
            if (sum(quote.casefold() in excerpt for excerpt in text.values()) == 1
                    and all(altered.casefold() not in excerpt for excerpt in text.values())):
                options.append((quote, altered))
        if not options:
            raise ValueError(f'No distinct quote controls for {ident}')
        quote, altered = rng.choice(options)
        cases.extend(((quote, ident), (altered, None)))
    rng.shuffle(cases)
    questions, key = [], []
    for index, (phrase, source) in enumerate(cases, start=1):
        case_id = f'quote-{index:02}'
        questions.append({'id': case_id, 'question': f'Which source contains the exact words "{phrase}"?'})
        key.append({'id': case_id, 'source_id': source, 'quote': phrase if source else None})
    return questions, key


def question_digest(questions):
    return sha256(json.dumps(questions, sort_keys=True).encode('utf-8')).hexdigest()


def generate(output, seed, source_dir=None):
    rng = random.Random(int(seed, 16))
    selected, excerpts, sources = [], {}, []
    for slug, author, title, repo, revision, digests in BOOKS:
        chapter = rng.choice((1, 2))
        digest = digests[chapter - 1]
        name, url, raw = read_chapter(slug, repo, revision, chapter, digest, source_dir)
        paragraph, body = rng.choice(windows(raw))
        ident = f'BOOK-{slug.upper()}'
        selected.append((name, raw))
        excerpts[ident] = body
        sources.append({'id': ident, 'author': author, 'title': title,
                        'chapter': chapter, 'paragraphs_in_xhtml': [paragraph, paragraph + 1],
                        'url': url, 'rights_url': RIGHTS, 'revision': revision,
                        'original': name, 'original_sha256': digest,
                        'excerpt_sha256': sha256(body.encode('utf-8')).hexdigest()})
    questions, key = controls(rng, excerpts)
    output.mkdir()
    inputs, custodian = output / 'engine-inputs', output / 'custodian'
    inputs.mkdir()
    (custodian / 'originals').mkdir(parents=True)
    for name, raw in selected:
        (custodian / 'originals' / name).write_bytes(raw)
    for ident, body in excerpts.items():
        (inputs / f'{ident}.txt').write_bytes(body.encode('utf-8'))
    batch_id = sha256(f'primary-book-test-v1:{seed}'.encode('ascii')).hexdigest()
    write_json(inputs / 'sources.json', {'schema': 'primary-book-test-v1', 'batch_id': batch_id, 'sources': sources})
    write_json(inputs / 'questions.json', questions)
    write_json(custodian / 'answer-key.json', {'seed': seed, 'batch_id': batch_id,
                                              'questions_sha256': question_digest(questions), 'cases': key})


def run(inputs, questions):
    from mplpb_answers.pipeline import answer_query
    from mplpb_combined.ledger import write

    manifest = read_json(inputs / 'sources.json')
    if manifest['schema'] != 'primary-book-test-v1':
        raise ValueError('Unknown Primary Book Test format')
    if not isinstance(questions, list) or not questions:
        raise ValueError('Expected a nonempty list of questions')
    if not all(isinstance(row, dict) and isinstance(row.get('id'), str) and row['id'].strip()
               and isinstance(row.get('question'), str) and row['question'].strip()
               for row in questions):
        raise ValueError('Every question needs a nonempty id and question')
    if len({row['id'] for row in questions}) != len(questions):
        raise ValueError('Question IDs must be unique')
    valid_ids = {f'BOOK-{book[0].upper()}' for book in BOOKS}
    with TemporaryDirectory(prefix='mplpb-primary-books-') as ledger:
        for source in manifest['sources']:
            ident = source['id']
            if ident not in valid_ids:
                raise ValueError(f'Unknown book source ID: {ident}')
            raw = (inputs / f'{ident}.txt').read_bytes()
            if sha256(raw).hexdigest() != source['excerpt_sha256']:
                raise ValueError(f'Excerpt checksum mismatch for {ident}')
            body = ''.join(f'<p>{escape(part)}</p>' for part in raw.decode('utf-8').split('\n\n'))
            write(ledger, doc_id=ident, title=f"{source['title']}, chapter {source['chapter']}",
                  scope=f"{source['title']} {source['author']}", body_html=body, origin='machine',
                  source_authorship='declared-human')
        cases = [{'id': row['id'], 'answer': answer_query(ledger, row['question'], mode='strict').contract}
                 for row in questions]
    return {'schema': 'primary-book-test-run-v1', 'batch_id': manifest['batch_id'],
            'questions_sha256': question_digest(questions), 'cases': cases}


def score(report, key):
    if any(report[field] != key[field] for field in ('batch_id', 'questions_sha256')):
        raise ValueError('Run and answer key are from different question batches')
    expected = {row['id']: row for row in key['cases']}
    ids = [row['id'] for row in report['cases']]
    if not ids or len(ids) != len(set(ids)) or len(key['cases']) != len(expected) or set(ids) != set(expected):
        raise ValueError('Run and answer key must have the same unique question IDs')
    details = []
    for case in report['cases']:
        row = expected[case['id']]
        answer = case['answer']
        if row['source_id'] is None:
            outcome = 'false_support' if answer['answer_supported'] else 'withheld'
        elif not answer['answer_supported']:
            outcome = 'missed'
        else:
            cites = [cite for claim in answer['claims'] for cite in claim['citations']]
            matched = any(cite['source_id'] == row['source_id'] and row['quote'] in cite['quote'] for cite in cites)
            outcome = 'correct_source_and_quote' if matched else 'incorrect_support'
        details.append({'id': case['id'], 'outcome': outcome, 'diagnostic': answer['diagnostic']['code']})
    return details


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('generate', help='Draw new passages and quote controls')
    build.add_argument('--output', required=True, type=Path)
    build.add_argument('--seed', help='Reuse a hexadecimal seed')
    build.add_argument('--source-dir', type=Path, help='Use local copies of the pinned chapter files')
    execute = commands.add_parser('run', help='Run strict answers using engine inputs only')
    execute.add_argument('--inputs', required=True, type=Path)
    execute.add_argument('--questions', type=Path, help='Override the default quote controls with authored questions')
    execute.add_argument('--output', required=True, type=Path)
    grade = commands.add_parser('score', help='Score the automatic quote controls')
    grade.add_argument('--run', required=True, type=Path)
    grade.add_argument('--key', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'generate':
            if args.seed is not None and not re.fullmatch(r'[0-9a-fA-F]{1,32}', args.seed):
                parser.error('--seed must contain 1 to 32 hexadecimal digits')
            seed = args.seed.lower().zfill(32) if args.seed else secrets.token_hex(16)
            generate(args.output, seed, args.source_dir)
            print(f'Primary Book Test seed {seed}')
        elif args.command == 'run':
            questions = read_json(args.questions or args.inputs / 'questions.json')
            if args.output.exists():
                raise FileExistsError(args.output)
            write_json(args.output, run(args.inputs, questions))
        else:
            results = score(read_json(args.run), read_json(args.key))
            print(json.dumps(results, indent=2))
            return int(any(row['outcome'] not in {'withheld', 'correct_source_and_quote'} for row in results))
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
