"""Score Scout against committed anchors and explicitly reviewed native claims."""
import argparse
from pathlib import Path
from collections import Counter

from mplpb_answers.evidence_contract import pin
from run import verify_files
from tools.unprepared_sources import load, save, sha


def normalize(text):
    return ' '.join(text.casefold().split())


def covered(anchor, passages):
    return any(p['source_id'] == anchor['source'] and normalize(anchor['quote']) in normalize(p['text'])
               for p in passages)


def score(bundle, raw):
    verify_files(bundle, 'pre-run.sha256')
    verify_files(bundle, 'inputs.sha256')
    key = {case['id']: case for case in load(bundle / 'custody/key.json')}
    question_by_id = {case['id']: case['question'] for case in load(bundle / 'inputs/questions.json')}
    review = load(bundle / 'review.json')['nonempty_native_cases']
    if raw['inputs_sha256'] != sha((bundle / 'inputs.sha256').read_bytes()):
        raise ValueError('Native output used different inputs')
    if len(raw['cases']) != len(key) or {row['id'] for row in raw['cases']} != set(key):
        raise ValueError('Native and key case lists differ')
    rows, claim_cases = [], set()
    for case in raw['cases']:
        ident = case['id']
        if case['question'] != question_by_id[ident]:
            raise ValueError(f'{ident} question differs from frozen input')
        expected, native = key[ident], case['strict']
        anchors = expected['anchors']
        if native['claims'] or native['answer_supported']:
            claim_cases.add(ident)
            decision = [native['kind'], native['answer_supported'], native['claims']]
            if ident not in review or review[ident]['native_decision_sha256'] != pin(decision):
                raise ValueError(f'{ident} needs source review')
            grade = review[ident]['grade']
        else:
            grade = 'justified_withhold' if expected['family'] == 'missing' else 'missed_answer'
        passes = case['advanced_passes']
        paths = [(p['inspection'] or {}).get('path') for p in passes]
        if any(p['strict'] != native or p['flag_sync']['status'] != 'matched' for p in passes):
            raise ValueError(f'{ident} graph-scoped proof differs')
        rows.append({
            'id': ident, 'family': expected['family'], 'native_kind': native['kind'],
            'diagnostic': native['diagnostic']['code'], 'documentary_plan': case['plan'],
            'grade': grade, 'anchors': len(anchors),
            'matched': {arm: sum(covered(a, passages) for a in anchors)
                        for arm, passages in case['discovery'].items()},
            'advanced_paths': paths, 'verified_expert_observations': len(case['expert']['verification']['verified']),
            'traversed_expert_links': sum(link['status'] == 'traversed' for link in case['expert']['relations']),
        })
    if claim_cases != set(review):
        raise ValueError('Post-run review does not match nonempty case set')
    answerable = [row for row in rows if row['family'] != 'missing']
    relations = [row for row in rows if row['family'] == 'relationship']
    arms = list(rows[0]['matched'])
    discovery = {}
    for label, grouping in [('all_cases', rows), ('answerable', answerable), ('relationships', relations)]:
        discovery[label] = {arm: sum(r['matched'][arm] == r['anchors'] for r in grouping) for arm in arms}
    return {'engine': raw['engine'], 'case_count': len(rows), 'answerable_count': len(answerable),
            'relationship_count': len(relations),
            'grades': dict(Counter(row['grade'] for row in rows)),
            'native_kinds': dict(Counter(row['native_kind'] for row in rows)),
            'diagnostics': dict(Counter(row['diagnostic'] for row in rows)),
            'discovery_all_anchors': discovery,
            'advanced_graph_passes_matched': 2 * len(rows),
            'advanced_second_pass_route_changes': sum(r['advanced_paths'][0] != r['advanced_paths'][1] for r in rows),
            'verified_expert_observations': sum(r['verified_expert_observations'] for r in rows),
            'traversed_expert_links': sum(r['traversed_expert_links'] for r in rows), 'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--raw', type=Path, help='Score a native replay against the same frozen packet')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    save(args.output, score(args.bundle, load(args.raw or args.bundle / 'native.json')))
