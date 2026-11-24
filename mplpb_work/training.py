"""Local sub-coordinator and coordinator for user-authored deterministic D6 rules."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from mplpb_answers.d6 import SCHEMA, compile_plan, field_selector, validate
from mplpb_answers.relation_graph import FIELD_LINE, IDENTITY_FIELDS
from mplpb_answers.support import code_pins
from mplpb_combined import ledger as ledger_module
from mplpb_combined.ledger import write
from .errors import WorkError
from .store import WorkStore, digest, implementation_pins

FIXTURES = 'mplpb-training-fixtures-v1'
KEY = 'mplpb-training-key-v1'
SEAL = 'mplpb-training-seal-v1'
RUN = 'mplpb-training-run-v1'
PARTITIONS = ('development', 'holdout', 'control')


def _packet(raw, schema):
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError('Training inputs exceed 4 MiB')
    packet = json.loads(raw)
    if not isinstance(packet, dict) or set(packet) != {'schema', 'cases'} or packet['schema'] != schema:
        raise ValueError('Invalid training packet')
    cases = packet['cases']
    if not isinstance(cases, list) or not 1 <= len(cases) <= 256:
        raise ValueError('Use 1–256 frozen training cases')
    ids = set()
    for case in cases:
        fields = {'id', 'record_id', 'body'} if schema == FIXTURES else {'id', 'partition', 'family', 'supported'}
        if not isinstance(case, dict) or not fields <= set(case) <= (fields | ({'value'} if schema == KEY else set())):
            raise ValueError('Invalid training case')
        ident = case['id']
        if not isinstance(ident, str) or not 1 <= len(ident) <= 100 or ident in ids:
            raise ValueError('Expected unique, short training case IDs')
        ids.add(ident)
        if schema == FIXTURES:
            field_selector({'record_id': case['record_id'], 'field': 'Record ID'})
            if not isinstance(case['body'], str) or not 1 <= len(case['body']) <= 12000:
                raise ValueError('Invalid training source body')
        else:
            if (case['partition'] not in PARTITIONS or not isinstance(case['family'], str)
                    or not 1 <= len(case['family'].strip()) <= 100 or type(case['supported']) is not bool
                    or ('value' in case and (not case['supported']
                                            or type(case['value']) not in (str, int, bool)))):
                raise ValueError('Invalid adjudication label')
    return cases


def freeze(fixtures, key):
    cases, labels = _packet(fixtures, FIXTURES), _packet(key, KEY)
    if {c['id'] for c in cases} != {c['id'] for c in labels}:
        raise ValueError('Frozen key and fixtures must cover the same cases')
    if ({c['partition'] for c in labels} != set(PARTITIONS)
            or not any(c['partition'] == 'control' and not c['supported'] for c in labels)
            or not any(c['partition'] == 'holdout' and c['supported'] for c in labels)):
        raise ValueError('Freeze development cases, a positive holdout, and a refusal control')
    return {'schema': SEAL, 'fixtures_sha256': sha256(fixtures).hexdigest(), 'key_sha256': sha256(key).hexdigest()}


def _bind(value, ident):
    if isinstance(value, dict):
        if 'record_id' in value and value['record_id'] != '$record':
            raise ValueError('All rule selectors must use the $record parameter')
        return {key: ident if key == 'record_id' else _bind(item, ident) for key, item in value.items()}
    if isinstance(value, list):
        return [_bind(item, ident) for item in value]
    return value


def _rule(raw):
    if len(raw) > 8000:
        raise ValueError('Training rule exceeds the rule size limit')
    rule = json.loads(raw)
    if (not isinstance(rule, dict) or set(rule) != {'name', 'steps'}
            or not isinstance(rule['name'], str) or not 1 <= len(rule['name'].strip()) <= 100
            or not isinstance(rule['steps'], list) or len(rule['steps']) != 1):
        raise ValueError('One named D6 step is required per training sprint')
    if validate({'op': 'all', 'steps': _bind(rule['steps'], 'TEST-1')}) > 32:
        raise ValueError('Training rule exceeds the D6 operation budget')
    return rule


def construct_rule(name, step):
    """Build one candidate for a D6 sprint using the existing rule validator."""
    return _rule(json.dumps({'name': name, 'steps': [step]}, ensure_ascii=False).encode())


def construct_comparison(question, first_actor, second_actor, decision):
    """Describe the evidence a recommendation comparison would need."""
    from mplpb_answers.documentary import plan

    fields = (question, first_actor, second_actor, decision)
    if any(not isinstance(value, str) or not 1 <= len(value.strip()) <= limit
           for value, limit in zip(fields, (500, 100, 100, 240))):
        raise ValueError('Supply a short question, two named actors, and a shared decision')
    question, first_actor, second_actor, decision = (value.strip() for value in fields)
    if first_actor.casefold() == second_actor.casefold():
        raise ValueError('Supply two distinct candidate actors')
    return {
        'schema': 'mplpb-semantic-rule-candidate-v1',
        'question': question,
        'intent': 'recommendation_comparison',
        'documentary_route': [goal['kind'] for goal in (plan(question) or ())],
        'decision_candidate': decision,
        'proof_obligations': [
            {'actor_candidate': actor, 'required': ['exact_source_span', 'actor_attribution',
                                                   'shared_decision', 'recommendation', 'stated_conditions']}
            for actor in (first_actor, second_actor)
        ],
        'comparison': 'Compare the attributed recommendations on the shared decision and retain stated conditions.',
        'controls': ['independently_worded_comparison', 'missing_recommendation', 'different_decision',
                     'negated_or_qualified_recommendation', 'unresolved_actor', 'ineligible_source'],
        'status': 'review_needed',
        'answer_supported': False,
        'promoted': False,
    }


def _candidate_fields(cases, minimum):
    fields = defaultdict(set)
    for case in cases:
        for line in case['body'].splitlines():
            match = FIELD_LINE.fullmatch(line)
            if not match:
                break
            label = ledger_module.field_name(match[1])
            if label in {'body', 'example', 'sample', 'quoted example'}:
                break
            if label not in IDENTITY_FIELDS:
                fields[label].add(case['record_id'].casefold())
    return sorted((label for label in fields if len(fields[label]) >= minimum),
                  key=lambda label: (-len(fields[label]), label))


def construct_corpus(fixtures):
    """Find reusable exact field reads and rank them by complete sample answers."""
    cases = _packet(fixtures, FIXTURES)
    if len(cases) > 32:
        raise ValueError('Use at most 32 development records for rule discovery')
    ranked = _candidate_fields(cases, minimum=2)
    candidates = []
    record_ids = {case['id']: case['record_id'].casefold() for case in cases}
    for label in ranked[:12]:
        rule = construct_rule(f'Read {label}', {'op': 'read', 'record_id': '$record', 'field': label})
        raw = (json.dumps(rule, indent=2, ensure_ascii=False) + '\n').encode()
        replay = run(fixtures, raw)
        complete = [row['id'] for row in replay['rows'] if row['report']['answer_supported']]
        if len({record_ids[ident] for ident in complete}) >= 2:
            candidates.append({'rule': rule, 'rule_sha256': replay['rule_sha256'],
                               'complete_cases': complete, 'replay': replay})
    candidates.sort(key=lambda item: (-len(item['complete_cases']), item['rule']['name']))
    return {'schema': 'mplpb-corpus-rule-candidates-v1', 'fixtures_sha256': sha256(fixtures).hexdigest(),
            'cases': len(cases), 'fields_omitted_by_budget': max(0, len(ranked) - 12),
            'candidates': candidates, 'status': 'review_needed', 'promoted': False}


def preview_corpus(raw, root):
    """Build a separate ledger and verify candidate field reads on the uploaded pages."""
    if len(raw) > 384000:
        raise ValueError('Use a text dump of at most 384,000 bytes')
    blocks = re.split(r'\r?\n(?:[ \t]*\r?\n)+', raw.decode('utf-8').strip('\r\n'))
    if not 1 <= len(blocks) <= 32:
        raise ValueError('Use at most 32 blank-line-separated records')
    cases = []
    for number, body in enumerate(blocks, 1):
        lines = body.splitlines()
        first = FIELD_LINE.fullmatch(lines[0]) if lines else None
        if (not first or ledger_module.field_name(first[1]) != 'record id'
                or len(body) > 12000 or any(not FIELD_LINE.fullmatch(line) for line in lines)):
            raise ValueError(f'Record {number} must start with Record-ID and contain only labelled fields')
        record_id = first[2].strip()
        field_selector({'record_id': record_id, 'field': 'Record ID'})
        cases.append({'id': f'UPLOAD-{number:03d}', 'record_id': record_id, 'body': body})
    ranked = _candidate_fields(cases, minimum=1)
    root = Path(root)
    root.mkdir()
    for case in cases:
        write(root, doc_id=case['id'], title=case['id'], scope='Spot unapproved upload preview',
              body_html='<pre>' + escape(case['body']) + '</pre>', origin='machine',
              source_authorship='unknown')
    targets = sorted({case['record_id'] for case in cases}, key=lambda value: (value.casefold(), value))
    candidates = []
    for label in ranked[:12]:
        rule = construct_rule(f'Read {label}', {'op': 'read', 'record_id': '$record', 'field': label})
        rows = []
        for record_id in targets:
            plan = {'schema': SCHEMA, 'steps': _bind(rule['steps'], record_id)}
            rows.append({'record_id': record_id, 'report': compile_plan(root, plan)})
        candidates.append({'rule': rule, 'complete': sum(row['report']['answer_supported'] for row in rows),
                           'answers': rows})
    candidates.sort(key=lambda item: (-item['complete'], item['rule']['name']))
    return {'schema': 'mplpb-spot-v1', 'upload_sha256': sha256(raw).hexdigest(),
            'status': 'unapproved_preview', 'promoted': False, 'records': len(cases),
            'fields_omitted_by_budget': max(0, len(ranked) - 12), 'candidates': candidates}


def _runtime_pin():
    package = Path(ledger_module.__file__).resolve().parent
    return digest({'answers': code_pins(), 'work': implementation_pins(),
                   'ledger': {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(package.glob('*.py'))}})


def run(fixtures, rule_bytes):
    """Execute public inputs only. The adjudication key is absent from this interface."""
    cases, rule = _packet(fixtures, FIXTURES), _rule(rule_bytes)
    runtime = _runtime_pin()
    rows = []
    for case in cases:
        with TemporaryDirectory(prefix='mplpb-rule-training-') as root:
            write(root, doc_id='TRAINING-SOURCE', title='Training source', scope='Training fixture',
                  body_html='<pre>' + escape(case['body']) + '</pre>', when='2026-11-23')
            plan = {'schema': SCHEMA, 'steps': _bind(rule['steps'], case['record_id'])}
            report = compile_plan(root, plan)
            rows.append({'id': case['id'], 'report': report})
    if _runtime_pin() != runtime:
        raise ValueError('Engine files changed during training replay')
    receipt = {'schema': RUN, 'rule_name': rule['name'], 'rule_sha256': sha256(rule_bytes).hexdigest(),
               'fixtures_sha256': sha256(fixtures).hexdigest(), 'runtime_sha256': runtime, 'rows': rows}
    return {**receipt, 'run_sha256': digest(receipt)}


def _grade(seal, fixtures, key, replay):
    if not isinstance(replay, dict) or not isinstance(replay.get('rows'), list):
        raise ValueError('Expected a replay receipt')
    if freeze(fixtures, key) != seal or replay.get('fixtures_sha256') != seal['fixtures_sha256']:
        raise ValueError('Expected the original frozen inputs and seal')
    labels = {row['id']: row for row in _packet(key, KEY)}
    rows = {row['id']: row['report'] for row in replay['rows']}
    if rows.keys() != labels.keys() or len(rows) != len(replay['rows']):
        raise ValueError('Training replay has incomplete or duplicate case coverage')
    if replay.get('schema') != RUN or digest({k: v for k, v in replay.items() if k != 'run_sha256'}) != replay.get('run_sha256'):
        raise ValueError('Training replay receipt digest differs')
    grade = {}
    for ident, expected in labels.items():
        report = rows[ident]
        steps = report['compiled'].get('steps', ())
        value = steps[0].get('value') if steps else None
        supported = report['answer_supported']
        if supported and not expected['supported']:
            diagnostic = 'unexpected_support'
        elif not supported and expected['supported']:
            diagnostic = 'support_withheld'
        elif 'value' in expected and (type(value) is not type(expected['value']) or value != expected['value']):
            diagnostic = 'wrong_value'
        else:
            diagnostic = 'match'
        grade[ident] = {**expected, 'tag': diagnostic, 'compiled': report['compiled'],
                        'citations': report['evidence']}
    return grade


def tag(seal, fixtures, key, baseline):
    """Sub-coordinator view with development errors grouped by reviewed family."""
    findings = defaultdict(list)
    grade = _grade(seal, fixtures, key, baseline)
    for ident, value in grade.items():
        if value['partition'] == 'development' and value['tag'] != 'match':
            findings[(value['family'], value['tag'])].append(ident)
    return {'schema': 'mplpb-training-findings-v1', 'baseline_sha256': baseline['run_sha256'],
            'findings': [{'family': family, 'tag': diagnostic, 'cases': ids, 'repeatable': len(ids) >= 2,
                          'evidence': [{'id': ident, 'compiled': grade[ident]['compiled'],
                                        'citations': grade[ident]['citations']} for ident in ids]}
                         for (family, diagnostic), ids in sorted(findings.items())],
            'answer_supported': False}


def compare(seal, fixtures, key, baseline, candidate):
    """Coordinator gate on the same engine and identical sealed cases."""
    old, new = (_grade(seal, fixtures, key, replay) for replay in (baseline, candidate))
    if baseline['runtime_sha256'] != candidate['runtime_sha256'] or baseline['rule_name'] != candidate['rule_name']:
        raise ValueError('Use the same pinned engine and rule name in a one-rule sprint')
    recovered = [k for k in old if old[k]['tag'] != 'match' and new[k]['tag'] == 'match']
    regressions = [k for k in old if old[k]['tag'] == 'match' and new[k]['tag'] != 'match']
    families = Counter((old[k]['family'], old[k]['tag']) for k in recovered if old[k]['partition'] == 'development')
    protected = [k for k, row in new.items() if row['partition'] in {'holdout', 'control'} and row['tag'] != 'match']
    unsupported = [k for k, row in new.items() if row['tag'] == 'unexpected_support']
    passed = (baseline['rule_sha256'] != candidate['rule_sha256'] and any(n >= 2 for n in families.values())
              and not regressions and not protected and not unsupported)
    return {'schema': 'mplpb-rule-sprint-v1', 'verdict': 'candidate_passed' if passed else 'candidate_blocked',
            'seal': seal, 'baseline_sha256': baseline['run_sha256'], 'candidate_sha256': candidate['run_sha256'],
            'candidate_rule_sha256': candidate['rule_sha256'], 'recovered': recovered,
            'new_regressions': regressions, 'protected_failures': protected, 'unexpected_support': unsupported,
            'cases': [{'id': k, 'partition': new[k]['partition'], 'before': old[k]['tag'],
                       'after': new[k]['tag']} for k in old],
            'answer_supported': False, 'promoted': False}


def record(store, credential, task, ident, artifact, *, finding_id=None, group=0, share_with=()):
    """File a digest and status through the ordinary WorkStore seat checks."""
    if not isinstance(artifact, dict) or artifact.get('answer_supported') is not False:
        raise ValueError('Only training metadata can be filed here')
    view = store.snapshot(credential)
    dependency = {}
    payload = {'task': task, 'artifact_sha256': digest(artifact), 'baseline_sha256': artifact.get('baseline_sha256')}
    if artifact.get('schema') == 'mplpb-training-findings-v1':
        if type(group) is not int or not 0 <= group < len(artifact['findings']) or finding_id is not None:
            raise ValueError('Choose one finding group')
        kind = 'training_finding'
        finding = artifact['findings'][group]
        payload.update(family=finding['family'], diagnostic=finding['tag'], cases=finding['cases'])
    elif artifact.get('schema') == 'mplpb-rule-sprint-v1' and artifact.get('promoted') is False:
        kind = 'rule_sprint'
        found = next((entry for entry in view['records'] if entry['id'] == finding_id
                      and entry['kind'] == 'training_finding'), None)
        if found is None:
            raise ValueError('Choose a visible training finding for the sprint')
        dependency = {finding_id: found['revision']}
        payload.update(verdict=artifact['verdict'], rule_sha256=artifact['candidate_rule_sha256'])
    else:
        raise ValueError('Unknown training artifact')
    return store.put(credential, id=ident, kind=kind, payload=payload, dependencies=dependency,
                     visibility=[view['contract']['seat'], *share_with], expected_revision=0,
                     expected_head=view['head'])


def repair(seal, fixtures, key, rule_bytes, objective):
    """Try a registered transformation, retaining the baseline and every attempt."""
    baseline = run(fixtures, rule_bytes)
    findings = tag(seal, fixtures, key, baseline)
    original = _rule(rule_bytes)
    result = {'schema': 'mplpb-automatic-sprint-v1', 'objective': objective, 'baseline': baseline,
              'findings': findings, 'attempts': [], 'selected_rule': None,
              'status': 'review_needed', 'answer_supported': False}
    step = original['steps'][0]
    modes = {'elapsed_days': 'elapsed', 'inclusive_days': 'inclusive'}
    known = isinstance(objective, str) and objective in modes
    if (known and step['op'] == 'day_difference' and step['mode'] == modes[objective]
            and all(row['tag'] == 'match' for row in _grade(seal, fixtures, key, baseline).values())):
        result.update(selected_rule=original, selected_rule_sha256=baseline['rule_sha256'], status='baseline_healthy')
        return result
    if known and step['op'] == 'year_difference' and any(
            f['repeatable'] and f['tag'] == 'wrong_value' for f in findings['findings']):
        proposal = construct_rule(original['name'], {**step, 'op': 'day_difference',
                    'calendar': 'proleptic_gregorian', 'mode': modes[objective]})
        candidate = run(fixtures, json.dumps(proposal, sort_keys=True, indent=2).encode() + b'\n')
        sprint = compare(seal, fixtures, key, baseline, candidate)
        result['attempts'].append({'rule': proposal, 'replay': candidate, 'verdict': sprint})
        if sprint['verdict'] == 'candidate_passed':
            result.update(selected_rule=proposal, selected_rule_sha256=candidate['rule_sha256'],
                          status='repair_selected')
    return result


def orchestrate(fixtures, key, rule_bytes, *, candidate_rule=None, objective=None):
    """Freeze, diagnose, and optionally compare one candidate under custody."""
    if candidate_rule is not None and objective is not None:
        raise ValueError('Choose a candidate rule or a registered objective')
    seal = freeze(fixtures, key)
    if objective is not None:
        sprint = repair(seal, fixtures, key, rule_bytes, objective)
        return {**sprint, 'seal': seal, 'promoted': False}
    baseline = run(fixtures, rule_bytes)
    result = {'schema': 'mplpb-advanced-training-v1', 'seal': seal, 'baseline': baseline,
              'findings': tag(seal, fixtures, key, baseline), 'candidate': None,
              'comparison': None, 'status': 'baseline_recorded',
              'answer_supported': False, 'promoted': False}
    if candidate_rule is not None:
        candidate = run(fixtures, candidate_rule)
        comparison = compare(seal, fixtures, key, baseline, candidate)
        result.update(candidate=candidate, comparison=comparison, status=comparison['verdict'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    paths = {'freeze': ('fixtures', 'key'), 'run': ('fixtures', 'rule'),
             'tag': ('seal', 'fixtures', 'key', 'baseline'),
             'compare': ('seal', 'fixtures', 'key', 'baseline', 'candidate'),
             'repair': ('seal', 'fixtures', 'key', 'rule')}
    for name, inputs in paths.items():
        command = sub.add_parser(name)
        for path in (*inputs, 'output'):
            command.add_argument(path, type=Path)
        if name == 'repair':
            command.add_argument('--objective', required=True)
    constructor = sub.add_parser('construct', help='Build a D6 candidate from one declarative step')
    constructor.add_argument('name')
    constructor.add_argument('step', type=Path, help='JSON file containing one D6 expression')
    constructor.add_argument('output', type=Path)
    comparison = sub.add_parser('construct-comparison', help='Draft a recommendation comparison for review')
    comparison.add_argument('question')
    comparison.add_argument('first_actor')
    comparison.add_argument('second_actor')
    comparison.add_argument('decision')
    comparison.add_argument('output', type=Path)
    corpus = sub.add_parser('construct-corpus', help='Rank repeated field candidates on development records')
    corpus.add_argument('fixtures', type=Path)
    corpus.add_argument('output', type=Path)
    preview = sub.add_parser('spot', help='Build an isolated strict preview of a text dump')
    preview.add_argument('dump', type=Path)
    preview.add_argument('ledger', type=Path, help='New directory for the isolated preview')
    preview.add_argument('output', type=Path)
    filing = sub.add_parser('record')
    filing.add_argument('workstore', type=Path)
    filing.add_argument('task')
    filing.add_argument('id')
    filing.add_argument('artifact', type=Path)
    filing.add_argument('--finding')
    filing.add_argument('--group', type=int, default=0)
    filing.add_argument('--share-with', action='append', default=[])
    args = parser.parse_args()
    if args.command == 'record':
        token = os.environ.get('MPLPB_WORK_TOKEN', '')
        view = record(WorkStore(args.workstore), token, args.task, args.id,
                      json.loads(args.artifact.read_bytes()), finding_id=args.finding,
                      group=args.group, share_with=args.share_with)
        print(json.dumps({'id': args.id, 'head': view['head'], 'answer_supported': False}))
        return 0
    if args.command == 'construct':
        with args.step.open('rb') as stream:
            step = stream.read(8001)
        if len(step) > 8000:
            raise ValueError('Training rule exceeds the rule size limit')
        result = construct_rule(args.name, json.loads(step))
    elif args.command == 'construct-comparison':
        result = construct_comparison(args.question, args.first_actor, args.second_actor, args.decision)
    elif args.command == 'construct-corpus':
        with args.fixtures.open('rb') as stream:
            result = construct_corpus(stream.read(4 * 1024 * 1024 + 1))
    elif args.command == 'spot':
        if args.output.exists():
            raise ValueError('Choose a new output report path')
        with args.dump.open('rb') as stream:
            result = preview_corpus(stream.read(384001), args.ledger)
    else:
        result = _training_command(args, paths)
    with args.output.open('x') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write('\n')
    if args.command == 'compare':
        print(result['verdict'])
        return int(result['verdict'] != 'candidate_passed')
    if args.command == 'repair':
        print(result['status'])
        return int(result['status'] not in ('repair_selected', 'baseline_healthy'))
    return 0


def _training_command(args, paths):
    data = {name: getattr(args, name).read_bytes() for name in paths[args.command]}
    for name in ('seal', 'baseline', 'candidate'):
        if name in data:
            data[name] = json.loads(data[name])
    if 'rule' in data:
        data['rule_bytes'] = data.pop('rule')
    if args.command == 'repair':
        data['objective'] = args.objective
    return {'freeze': freeze, 'run': run, 'tag': tag, 'compare': compare, 'repair': repair}[args.command](**data)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, WorkError) as exc:
        raise SystemExit(f'Training stopped: {exc}') from exc
