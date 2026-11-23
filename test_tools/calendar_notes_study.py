"""Replay calendar controls, WorkStore note discovery, and real lexical data."""
import argparse
from html import escape
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.d6 import SCHEMA, compile_plan
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_work import WorkStore
from mplpb_work.thesaurus import lookup, probe


def calendar_cases():
    rows = []
    for year, leap in ((1600, True), (1700, False), (1900, False),
                       (2000, True), (2100, False), (2400, True)):
        def field(label):
            return {'record_id': 'DAY-1', 'field': label}

        calendar = {'calendar': 'proleptic_gregorian'}
        interval = {'op': 'day_difference', 'left': field('Event Date'), 'right': field('End Date'), **calendar}
        month = {'op': 'add_months', 'anchor': field('Month Start Date'), 'months': 1, **calendar}
        relative = {'op': 'relative_date', 'anchor': field('Event Date'), 'relative': field('Event Relative Date'), **calendar}
        feb = f'{year}-02-{29 if leap else 28}'
        cases = (
            ('elapsed', {**interval, 'mode': 'elapsed'}, 2 if leap else 1),
            ('inclusive', {**interval, 'mode': 'inclusive'}, 3 if leap else 2),
            ('reverse', {**interval, 'mode': 'elapsed', 'left': field('End Date'), 'right': field('Event Date')},
             -2 if leap else -1),
            ('same-day', {**interval, 'mode': 'inclusive', 'right': field('Event Date')}, 1),
            ('month-clamp', {**month, 'overflow': 'clamp'}, feb),
            ('month-reject', {**month, 'overflow': 'reject'}, None),
            ('next-day', relative, f'{year}-02-29' if leap else f'{year}-03-01'),
            ('wrong-date-role', {**relative, 'anchor': field('Publication Date')}, None),
        )
        text = (f'Record-ID: DAY-1\nEvent Date: {year}-02-28\nEnd Date: {year}-03-01\n'
                f'Month Start Date: {year}-01-31\nEvent Relative Date: the next day\nPublication Date: {year}-07-12')
        with TemporaryDirectory() as ledger:
            write(ledger, doc_id='CALENDAR-1', title='Fictional dated entry', scope='Calendar controls',
                  body_html='<pre>' + escape(text) + '</pre>', when='2026-11-23')
            for label, step, expected in cases:
                report = compile_plan(ledger, {'schema': SCHEMA, 'steps': [step]})
                got = report['compiled']['steps'][0].get('value')
                rows.append({'year': year, 'case': label, 'expected': expected, 'value': got,
                             'passed': got == expected and report['answer_supported'] == (expected is not None)})
    return rows


def note_cases():
    labels = ('alder', 'birch', 'cedar', 'dogwood', 'elm', 'fir', 'hemlock', 'juniper', 'larch', 'maple', 'oak', 'pine')
    facets = ('date_roles', 'conditions', 'corrections', 'recorded_stage', 'causal_scope', 'literal_values')
    with TemporaryDirectory() as temp:
        root = Path(temp)
        ledger = root/'ledger'
        pages, questions = [], []
        for i, label in enumerate(labels):
            question = f'What does the manuscript report about the {label} assignment?'
            questions.append(question)
            write(ledger, doc_id=f'DETOUR-{i}', title='Catalog cross reference', scope='Archive material',
                  body=f'The {label} assignment appears in this manuscript catalog. The catalog indexes manuscript reports.',
                  when='2026-11-23')
            pages.append(write(ledger, doc_id=f'REGISTER-{i}', title='Inspected folio', scope='Archive material',
                               body=f'The third folio records a review entry numbered {30+i}.', when='2026-11-23'))
        exact = 'What is the Count for record INVENTORY-7?'
        write(ledger, doc_id='INVENTORY', title='Checked inventory', scope='Archive material',
              body_html='<pre>Record-ID: INVENTORY-7\nCount: 12</pre>', when='2026-11-23')
        plain = [PassageIndex(ledger, q).retrieve([q], 1, 1000) for q in questions]
        strict = [answer_query(ledger, q).contract for q in [*questions, exact]]
        store, host = WorkStore.create(root/'work', {'archive': ledger}, clock=lambda: 1000)
        seat = store.assign(host, seat='reviewer', instance='reviewer-1',
                            model={'name': 'reviewer', 'provider': 'study', 'version': '1', 'context_policy_hash': 'unknown'},
                            contract={'operations': ['create:task', 'create:evidence', 'create:source_note', 'search:source_note'],
                                      'tools': [], 'scopes': ['TASK'], 'share_with': [], 'profile': 'internal',
                                      'expires_at': 2000}, expected_head=store.head(host)['hash'])
        token = seat['credential']
        view = store.snapshot(token)

        def put(ident, kind, payload, dependencies):
            nonlocal view
            view = store.put(token, id=ident, kind=kind, payload=payload, dependencies=dependencies,
                             visibility=['reviewer'], expected_revision=0, expected_head=view['head'])

        put('TASK', 'task', {'goal': 'Navigate inspection notes', 'criteria': ['Locate exact strips'],
                            'review_budget': 1, 'state': 'open', 'acceptance': {}}, {})
        for i, (label, page) in enumerate(zip(labels, pages, strict=True)):
            put(f'E-{i}', 'evidence', {'task': 'TASK', 'corpus': 'archive', 'source_id': page.id,
                                      'source_hash': page.hash, 'quote': f'The third folio records a review entry numbered {30+i}.',
                                      'query': 'Archive material'}, {})
            put(f'N-{i}', 'source_note', {'task': 'TASK', 'body_start': 0, 'rule': facets[i % len(facets)],
                                          'keywords': [label], 'comment': 'Check the pinned folio.', 'state': 'active'}, {f'E-{i}': 1})
        rows = []
        for question, page, before, expected in zip(questions, pages, plain, strict[:-1], strict=True):
            notes = store.source_note_search(token, task='TASK', corpus='archive', question=question,
                                             max_passages=1, max_chars=1000)
            rows.append({'question': question, 'source_id': page.id,
                         'ordinary_hit': any(hit['source_id'] == page.id for hit in before['passages']),
                         'note_hit': any(hit['source_id'] == page.id for hit in notes['candidates']),
                         'rule_order': notes['rule_order'], 'note_snapshot': notes['note_snapshot'],
                         'strict_unchanged': answer_query(ledger, question).contract == expected})
        return rows, strict[-1]['answer_supported'] and answer_query(ledger, exact).contract == strict[-1]


def lexical_cases(database):
    cases = (
        ('deed', 'n:06545137', 'synonym', 'deed of conveyance', 'The deed of conveyance is entered in the third folio.'),
        ('car', 'n:02958343', 'synonym', 'automobile', 'The automobile crossed the makeshift bridge at dusk.'),
        ('canal', 'n:02947212', 'broader', 'waterway', 'The waterway flooded the adjoining fields.'),
        ('canal', 'n:02947212', 'has_part', 'lock', 'The lock gates remained open throughout the inspection.'),
        ('bank', 'n:09213565', 'narrower', 'riverbank', 'The embankment inspection marked the riverbank for repair.'),
        ('deed', 'n:06545137', 'broader', 'legal document', 'The legal document bears a date on its final page.'),
    )
    rows = []
    for term, sense, relation, expected, witness in cases:
        with TemporaryDirectory() as ledger:
            write(ledger, doc_id='DECOY', title='Catalog only', scope='Archive material',
                  body=f'The {term} appears in the catalog index.', when='2026-11-23')
            write(ledger, doc_id='WITNESS', title='Inspected source', scope='Archive material',
                  body=witness, when='2026-11-23')
            question = f'What is recorded about the {term}?'
            before = answer_query(ledger, question).contract
            result = probe(database, ledger, question, term, sense, relation=relation, max_passages=1)
            root = lookup(database, term, sense=sense)
            rows.append({'term': term, 'sense': sense, 'relation': relation, 'expansion': result['expansion'],
                         'expected_in_expansion': expected in result['expansion'],
                         'moby_has_associations': bool(root['reference_associations']),
                         'ordinary_hit': result['baseline']['passages'][0]['source_id'] == 'WITNESS',
                         'lexical_hit': result['expanded']['passages'][0]['source_id'] == 'WITNESS',
                         'edge_span_hit': any(p['source_id'] == 'WITNESS' for p in result['edge_hits']),
                         'strict_unchanged': answer_query(ledger, question).contract == before,
                         'source_pins': root['sources']})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--thesaurus', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    notes, exact = note_cases()
    data = {'calendar': calendar_cases(), 'notes': notes, 'strict_exact_unchanged': exact}
    if args.thesaurus:
        data['lexical'] = lexical_cases(args.thesaurus)
    with args.output.open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print('Calendar:', sum(row['passed'] for row in data['calendar']), '/', len(data['calendar']))
    print('Notes: ordinary', sum(row['ordinary_hit'] for row in notes), 'with notes', sum(row['note_hit'] for row in notes))
    if args.thesaurus:
        rows = data['lexical']
        print('Lexical edges checked:', sum(row['expected_in_expansion'] for row in rows), '/', len(rows))
        print('Lexical discovery: ordinary', sum(row['ordinary_hit'] for row in rows), 'expanded', sum(row['lexical_hit'] for row in rows),
              'edge spans', sum(row['edge_span_hit'] for row in rows))
    return int(not exact or not all(row['passed'] for row in data['calendar'])
               or not all(row['note_hit'] and row['strict_unchanged'] for row in notes)
               or not all(row['expected_in_expansion'] and row['strict_unchanged'] for row in data.get('lexical', [])))


if __name__ == '__main__':
    raise SystemExit(main())
