"""4score20: trace question interpretation, passage discovery, and strict proof."""
import argparse
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.documentary import plan
from mplpb_answers.documentary_verify import units
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from tools.unprepared_sources import inside, load, save, sha

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'evaluation/d12/solo-post-freeze'
CASES = ('P05-1', 'P06-2', 'P02-4')
PROFILE = PROFILES['internal']
MAX_CHARS = 8000


def verify_inputs(pilot):
    for name in ('pre-run.sha256', 'inputs.sha256'):
        for line in (pilot / name).read_text().splitlines():
            expected, filename = line.split(maxsplit=1)
            if sha(inside(pilot, filename).read_bytes()) != expected:
                raise ValueError(f'Frozen input changed: {filename}')


def import_packet(pilot, sources, ledger):
    for source in sources:
        ident = source['id']
        path = inside(pilot, f'inputs/sources/{ident}.txt')
        if sha(path.read_bytes()) != source['text_sha256']:
            raise ValueError(f'Source projection changed: {ident}')
        body = ''.join('<p>' + escape(paragraph) + '</p>'
                       for paragraph in path.read_text().strip().split('\n\n'))
        write(ledger, doc_id=ident, title=f'Imported record {ident}',
              scope='public historical records', body_html=body, origin='machine',
              when='2026-11-23T00:00Z')


def summary(answer):
    return {'kind': answer['kind'], 'diagnostic': answer['diagnostic']['code'],
            'supported': answer['answer_supported'], 'claims': answer['claims']}


def containing(anchors, passages):
    return [[passage['id'] for passage in passages
             if passage['source_id'] == anchor['source'] and anchor['quote'] in passage['text']]
            for anchor in anchors]


def quote_probe(ledger, source_id, phrase):
    question = f'Which source contains the exact words “{phrase}”?'
    result = answer_query(ledger, question, PROFILE).contract
    located = any(cite['source_id'] == source_id and phrase in cite['quote']
                  for claim in result['claims'] for cite in claim['citations'])
    return {'expected_source': source_id, 'question': question,
            'expected_span_cited': located, 'answer': summary(result)}


def trace(pilot, cases):
    verify_inputs(pilot)
    questions = {row['id']: row for row in load(pilot / 'inputs/questions.json')}
    packets = {row['id']: row for row in load(pilot / 'inputs/sources.json')}
    rows = []
    runtime = None
    # Make all unassisted decisions before opening the reference key.
    native = []
    with TemporaryDirectory(prefix='mplpb-4score20-') as tmp:
        for ident in cases:
            item = questions[ident]
            sources = packets[item['packet']]['sources']
            ledger = Path(tmp) / ident
            import_packet(pilot, sources, ledger)
            question = item['question']
            goals = plan(question)
            index = PassageIndex(ledger, question, PROFILE)
            top_three = index.retrieve([question], 3, MAX_CHARS)['passages']
            top_twelve = index.retrieve([question], 12, MAX_CHARS)['passages']
            answer = answer_query(ledger, question, PROFILE).contract
            runtime = answer['code_sha256']
            native.append((ident, question, ledger, goals, index, top_three, top_twelve, answer))

        references = {row['id']: row for row in load(pilot / 'custody/key.json')}
        for ident, question, ledger, goals, index, top_three, top_twelve, answer in native:
            key = references[ident]
            anchors = key['anchors']
            indexed = containing(anchors, index.passages)
            selected = {passage_id for hits in indexed for passage_id in hits[:1]}
            # Sealed key-assisted original passage pointers. These supply only
            # locations to the existing hint boundary, never a proof or rule.
            hints = [dict(p, suggestion_class='explicit_reference')
                     for p in index.passages if p['id'] in selected]
            hinted = answer_query(ledger, question, PROFILE, source_hints=hints).contract
            bodies = {record.id: body_text(record.body_html) for record in index.records}
            quotes = []
            for anchor in anchors:
                source_id, phrase = anchor['source'], anchor['quote']
                whole = quote_probe(ledger, source_id, phrase)
                body = bodies.get(source_id, '')
                start = body.find(phrase)
                end = start + len(phrase)
                if start >= 0 and body.count(phrase) == 1:
                    parts = [body[max(a, start):min(b, end)].strip()
                             for a, b, _ in units(body) if a < end and start < b]
                    if len(parts) > 1 and all(len(part) >= 2 for part in parts):
                        whole['split_unit_controls'] = [quote_probe(ledger, source_id, part)
                                                        for part in parts]
                quotes.append(whole)
            rows.append({
                'case': ident, 'question': question,
                'understand': {'documentary_plan': goals, 'reference_expected': key['expected']},
                'find': {'anchors': anchors, 'indexed': indexed,
                         'first_3': containing(anchors, top_three),
                         'first_12': containing(anchors, top_twelve)},
                'check': {'strict': summary(answer), 'strict_with_reference_locations': summary(hinted),
                          'locations_supplied': len(hints), 'exact_quote_controls': quotes},
            })
    return {'test': '4score20', 'runtime_sha256': sha(str(sorted(runtime.items())).encode()),
            'questions_sha256': sha((pilot / 'inputs/questions.json').read_bytes()), 'cases': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', type=Path, default=PILOT)
    parser.add_argument('--case', action='append', dest='cases')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = args.cases or CASES
    if len(set(cases)) != len(cases):
        parser.error('choose each case once')
    save(args.output, trace(args.pilot, cases))


if __name__ == '__main__':
    main()
