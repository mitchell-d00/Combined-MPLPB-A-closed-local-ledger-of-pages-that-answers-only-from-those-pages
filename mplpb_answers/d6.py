"""Compile typed evidence plans with the strict MPLPB field reader."""
import argparse
from datetime import date
import json
from pathlib import Path
import re

from mplpb_combined import provenance_gate
from mplpb_combined.ledger import field_name, serving_view
from mplpb_combined.reader import PROFILES
from .passage_admission import output_budget
from .pipeline import answer_query
from .relation_graph import exact_request

SCHEMA = 'mplpb-d6-v1'
_FIELDS = {'record_id', 'field'}
_SHAPES = {
    'read': _FIELDS,
    'match': _FIELDS | {'value'},
    'not_match': _FIELDS | {'value'},
    'year_difference': {'left', 'right'},
    'if': {'when', 'then', 'else'},
    'all': {'steps'},
}
_MONTHS = ('january february march april may june july august september october november december').split()


def field_selector(expression):
    for key in _FIELDS:
        if not isinstance(expression.get(key), str) or not expression[key]:
            raise ValueError('Each field selector needs an explicit record ID and body field')
    exact_request('Inspect a declared source field', expression['record_id'], expression['field'])


def validate(expression, depth=0):
    if not isinstance(expression, dict) or depth > 6:
        raise ValueError('Expected a D6 step within the nesting limit')
    op = expression.get('op')
    if not isinstance(op, str) or op not in _SHAPES or set(expression) != _SHAPES[op] | {'op'}:
        raise ValueError('Unknown D6 operation or unexpected step attributes')
    if op in ('read', 'match', 'not_match'):
        field_selector(expression)
        if op != 'read' and (not isinstance(expression['value'], str) or not expression['value'].strip()
                             or len(expression['value']) > 400):
            raise ValueError('A comparison needs a nonblank literal value of at most 400 characters')
        return 1
    if op == 'year_difference':
        for selector in (expression['left'], expression['right']):
            if not isinstance(selector, dict) or set(selector) != _FIELDS:
                raise ValueError('Year difference needs two explicit field selectors')
            field_selector(selector)
        return 3
    if op == 'if':
        condition = expression['when']
        if not isinstance(condition, dict) or condition.get('op') not in ('match', 'not_match'):
            raise ValueError('A D6 condition must compare a declared field with a literal')
        children = [condition, expression['then'], expression['else']]
    else:
        children = expression['steps']
        if not isinstance(children, list) or not 1 <= len(children) <= 12:
            raise ValueError('A D6 group needs 1–12 steps')
    return 1 + sum(validate(child, depth + 1) for child in children)


def recorded_date(text):
    if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', text):
        parts = [int(k) for k in text.split('-')]
    elif match := re.fullmatch(r'([A-Za-z]+) ([0-9]{1,2}),? ([0-9]{4})', text):
        month, day, year = match.groups()
        names = {alias: i for i, name in enumerate(_MONTHS, 1) for alias in (name, name[:3])}
        if month.casefold() not in names:
            return None
        parts = [int(year), names[month.casefold()], int(day)]
    else:
        return None
    try:
        return date(*parts)
    except ValueError:
        return None


def recorded_year_number(text):
    return int(text) if re.fullmatch(r'[0-9]{4}', text) and text != '0000' else None


def field_year(selector, value):
    label = field_name(selector['field']).split()[-1]
    if label == 'year':
        return recorded_year_number(value)
    if label == 'date':
        exact = recorded_date(value)
        return exact.year if exact is not None else None
    return None


def node(op, status, why, **detail):
    return {'operation': op, 'status': status, 'why': why, **detail}


class _Evaluation:
    def __init__(self, root, question, profile):
        self.root, self.question, self.profile = root, question, profile
        self.evidence = []
        self.views = {}

    def snapshot(self):
        return provenance_gate.gather(self.root, self.question, self.profile).corpus_snapshot

    def read_field(self, selector):
        record, field = selector['record_id'], selector['field']
        native = answer_query(self.root, self.question, self.profile, mode='strict',
                              record_id=record, field=field)
        answer = native.contract
        normalized = field_name(field)
        key = (record, normalized)
        observed = (native.gate.get('corpus_snapshot'), native.gate.get('policy'))
        self.views.setdefault(key, observed)
        if self.views[key] != observed or answer['diagnostic']['code'] == 'source_changed':
            raise _SourceChanged
        citations = [cite for claim in answer['claims'] for cite in claim['citations']]
        if (not answer['answer_supported'] or len(answer['sources']) != 1 or len(citations) != 1
                or citations[0].get('field') != normalized):
            return node('read', 'unresolved', f'{field} on {record} did not resolve to one verified field value. '
                        + answer['diagnostic']['message'], diagnostic=answer['diagnostic']['code'])
        cite = citations[0]
        if cite not in self.evidence:
            self.evidence.append(cite)
        return node('read', 'resolved', f'{field} on {record} is declared as {cite["value"]!r}.',
                    value=cite['value'], evidence=[self.evidence.index(cite) + 1])

    def execute(self, expression):
        op = expression['op']
        if op in ('read', 'match', 'not_match'):
            child = self.read_field(expression)
            if op == 'read':
                return child
            if child['status'] != 'resolved':
                return node(op, 'unresolved', 'The comparison needs a verified value.', steps=[child])
            actual, expected = child['value'], expression['value']
            label = field_name(expression['field']).split()[-1]
            parser = {'date': recorded_date, 'year': recorded_year_number}.get(label)
            if parser:
                actual, expected = parser(actual), parser(expected)
                if actual is None or expected is None:
                    return node(op, 'unresolved', 'The comparison requires two valid values at the named date or year precision.',
                                steps=[child])
            same = actual == expected
            value = same if op == 'match' else not same
            action = 'matches' if same else 'differs from'
            return node(op, 'resolved', f'The comparison is {str(value).lower()}. '
                        f'The recorded value {action} {expression["value"]!r}.', value=value, steps=[child])
        if op == 'year_difference':
            children = [self.read_field(expression[key]) for key in ('left', 'right')]
            years = [field_year(expression[key], child.get('value', ''))
                     for key, child in zip(('left', 'right'), children)]
            if any(year is None for year in years):
                return node(op, 'unresolved', 'Use two declared Year or Date fields with valid values.',
                            steps=children)
            value = years[1] - years[0]
            return node(op, 'resolved', f'{years[1]} minus {years[0]} is {value}. This compares year numbers.',
                        value=value, steps=children)
        if op == 'if':
            condition = self.execute(expression['when'])
            if condition['status'] != 'resolved':
                return node(op, 'unresolved', 'The condition is unresolved, so neither branch ran.',
                            steps=[condition])
            branch = 'then' if condition['value'] else 'else'
            outcome = self.execute(expression[branch])
            return node(op, outcome['status'], f'The verified condition is {str(condition["value"]).lower()}. Ran the {branch} branch.',
                        branch=branch, steps=[condition, outcome])
        children = [self.execute(child) for child in expression['steps']]
        complete = all(child['status'] == 'resolved' for child in children)
        return node(op, 'resolved' if complete else 'unresolved',
                    'Every required step resolved.' if complete else 'At least one required step remains unresolved.',
                    steps=children)

    def recheck(self):
        for (_, field), (snapshot, policy) in self.views.items():
            with serving_view(None, field):
                current = provenance_gate.gather(self.root, self.question, self.profile)
            if current.corpus_snapshot != snapshot or current.policy != policy:
                raise _SourceChanged


class _SourceChanged(Exception):
    pass


def compile_plan(root, plan, profile=None, max_passages=12, max_chars=8000):
    if not isinstance(plan, dict) or set(plan) != {'schema', 'steps'} or plan['schema'] != SCHEMA:
        raise ValueError('Expected a mplpb-d6-v1 plan containing steps')
    question = 'Check declared evidence for this D6 plan ' + json.dumps(plan, sort_keys=True, ensure_ascii=False)
    if len(question) > 4000:
        raise ValueError('D6 plan exceeds the question budget')
    expression = {'op': 'all', 'steps': plan['steps']}
    if validate(expression) > 32:
        raise ValueError('D6 plan exceeds 32 operations and field reads')
    if type(max_passages) is not int or not 1 <= max_passages <= 64:
        raise ValueError('Invalid D6 passage budget')
    if type(max_chars) is not int or not 1000 <= max_chars <= 64000:
        raise ValueError('Invalid D6 character budget')
    run = _Evaluation(root, question, profile or PROFILES['internal'])
    before = run.snapshot()
    try:
        result = run.execute(expression)
        run.recheck()
        if run.snapshot() != before:
            raise _SourceChanged
    except _SourceChanged:
        result = node('all', 'unresolved', 'The source or serving policy changed during the plan. Run it again.')
        run.evidence.clear()
    if output_budget({'claims': [{'citations': run.evidence}], 'missing': [], 'verification': {}}, max_passages, max_chars):
        result = node('all', 'unresolved', 'The combined evidence exceeds the plan budget.')
        run.evidence.clear()
    return {'schema': SCHEMA, 'answer_supported': result['status'] == 'resolved',
            'compiled': result, 'evidence': run.evidence, 'truth_verified': False}


def render(report):
    lines = ['D6 evidence plan ' + ('complete' if report['answer_supported'] else 'incomplete')]

    def show(step, depth):
        refs = ' ' + ' '.join(f'[{i}]' for i in step['evidence']) if step.get('evidence') else ''
        lines.append('  ' * depth + '- ' + step['why'] + refs)
        for child in step.get('steps', []):
            show(child, depth + 1)

    show(report['compiled'], 0)
    for i, cite in enumerate(report['evidence'], 1):
        lines.extend(['', f'[{i}] {cite["source_id"]} ({cite["path"]})',
                      f'    {cite["hash"]} · body characters {cite["body_start"]}–{cite["body_end"]}',
                      f'    “{cite["quote"]}”'])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--profile', choices=sorted(PROFILES), default='internal')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    report = compile_plan(args.ledger, json.loads(args.plan.read_bytes()), PROFILES[args.profile])
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render(report))


if __name__ == '__main__':
    main()
