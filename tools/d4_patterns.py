"""Tabulate D4 before/after patterns and retain every case decision."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from tools import d4
from tools import dpercent as D


def compare(public, before, after, acceptance, destination):
    public, before, after, acceptance, destination = map(Path, (public, before, after, acceptance, destination))
    old, new, gate = (D.read(report) for report in (before, after, acceptance))
    if (old['study_sha256'] != new['study_sha256']
            or D.sha((public/'study.json').read_bytes()) != old['study_sha256']
            or old['rows'].keys() != new['rows'].keys()
            or gate['revision'] != new['revision']
            or not new['strict_gate_passed'] or not gate['strict_gate_passed']):
        raise ValueError('Reports must pin one frozen study and a passing candidate')
    study = D.read(public/'study.json')
    destination.mkdir(parents=True, exist_ok=True)
    old_families, new_families = (report['cohorts']['family'] for report in (old, new))
    families = {}
    for family in sorted(study['family_counts']):
        families[family] = {'planned': study['family_counts'][family],
                            'before': old_families[family], 'after': new_families[family],
                            'focus': family in d4.FOCUS}
    diagnostics = {}
    transitions = Counter()
    by_task = {}
    by_task_and_form = {}
    for ident, row in new['rows'].items():
        if row['family'] not in d4.FOCUS:
            continue
        family = row['family']
        diagnostics.setdefault(family, Counter())[row['diagnostic']] += 1
        transitions[old['rows'][ident]['outcome'] + ' → ' + row['outcome']] += 1
        task = row['features']['d4_task']
        by_task.setdefault(task, {'before': Counter(), 'after': Counter()})
        by_task[task]['before'][old['rows'][ident]['outcome']] += 1
        by_task[task]['after'][row['outcome']] += 1
        forms = by_task_and_form.setdefault(task, {})
        counts = forms.setdefault(str(row['features']['d4_question_form']), {'before': Counter(), 'after': Counter()})
        counts['before'][old['rows'][ident]['outcome']] += 1
        counts['after'][row['outcome']] += 1
    result = {
        'title': d4.TITLE, 'schema': 'd4-class-patterns-v1', 'study_sha256': new['study_sha256'],
        'baseline_revision': old['revision'], 'candidate_revision': new['revision'],
        'score_hashes': {name: D.sha(path.read_bytes()) for name, path in
                         (('before', before), ('after', after), ('gate', acceptance))},
        'study_cases': study['cases'], 'family_count': len(families),
        'focus_before': old['focus'], 'focus_after': new['focus'],
        'mixed_before': old['mixed'], 'mixed_after': new['mixed'],
        'unchanged_mixed_cases': sum(new['mixed'].values()),
        'mixed_case_changes': new['mixed_changes_from_baseline'],
        'graph_obligation_failures': new['graph_obligation_failures'],
        'graph_budget_stops': new['graph_budget_stops'],
        'gate': {'cases': len(gate['rows']), 'focus': gate['focus'], 'mixed': gate['mixed'],
                 'strict_gate_passed': gate['strict_gate_passed']},
        'by_family': families, 'by_task': by_task, 'by_task_and_question_form': by_task_and_form,
        'focus_transitions': dict(transitions),
        'focus_diagnostics_by_family': diagnostics,
        'cohorts_before': old['cohorts'], 'cohorts_after': new['cohorts'],
        'independent_semantic_review': 'NOT RUN',
    }
    D.save(destination/'patterns.json', result)
    D.save(destination/'study.json', study)
    with (destination/'cases.jsonl.gz').open('xb') as stream:
        with gzip.GzipFile(fileobj=stream, filename='', mode='wb', mtime=0) as compressed:
            for shard in study['shards']:
                payloads = sorted((public/shard['name']/'packets').iterdir())
                for path in payloads:
                    ident = path.name
                    case = D.read(path/'case.json')
                    data = {'id': ident, 'question': case['question'], 'profile': case['profile'],
                            'budget': case['budget'], 'before': old['rows'][ident], 'after': new['rows'][ident]}
                    compressed.write((json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n').encode('utf-8'))
    print(json.dumps({key: result[key] for key in (
        'study_cases', 'family_count', 'focus_before', 'focus_after', 'mixed_before', 'mixed_after',
        'graph_budget_stops', 'gate', 'by_task')}, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('public', 'before', 'after', 'acceptance', 'destination'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    compare(args.public, args.before, args.after, args.acceptance, args.destination)


if __name__ == '__main__':
    main()
